#include "drone_estimation/eskf.hpp"
#include <cmath>

namespace drone_estimation {

const Eigen::Vector3d ESKF::G_(0.0, 0.0, -9.81);

ESKF::ESKF() {
  P_.setIdentity();
  P_ *= 1e-2;
}

void ESKF::set_initial_state(
    const NominalState& x0,
    const Eigen::Matrix<double,15,15>& P0) {
  x_ = x0; P_ = P0;
}

// ── SO(3) helpers ────────────────────────────────────────────────────────────
Eigen::Matrix3d ESKF::Exp(const Eigen::Vector3d& phi) {
  double ang = phi.norm();
  if (ang < 1e-10) return Eigen::Matrix3d::Identity();
  Eigen::Vector3d ax = phi / ang;
  Eigen::Matrix3d K;
  K <<    0,  -ax.z(),  ax.y(),
      ax.z(),       0, -ax.x(),
     -ax.y(),  ax.x(),       0;
  return Eigen::Matrix3d::Identity() + std::sin(ang)*K
         + (1-std::cos(ang))*K*K;
}

Eigen::Vector3d ESKF::Log(const Eigen::Matrix3d& R) {
  double cos_a = std::clamp(0.5*(R.trace()-1.0), -1.0, 1.0);
  double ang   = std::acos(cos_a);
  if (std::abs(ang) < 1e-10)
    return Eigen::Vector3d::Zero();
  Eigen::Matrix3d S = (R - R.transpose()) / (2.0*std::sin(ang));
  return ang * Eigen::Vector3d(S(2,1), S(0,2), S(1,0));
}

// ── IMU propagation  (eq. 10-11) ────────────────────────────────────────────
void ESKF::propagate(const ImuMeasurement& imu) {
  double dt = imu.t - x_.t;
  if (dt <= 0.0 || dt > 0.1) { x_.t = imu.t; return; }

  Eigen::Vector3d a_body = imu.am - x_.ba;
  Eigen::Vector3d w_body = imu.wm - x_.bg;

  // Nominal kinematics
  Eigen::Vector3d a_world = x_.R * a_body + G_;
  x_.p += x_.v * dt + 0.5 * a_world * dt * dt;
  x_.v += a_world * dt;
  x_.R  = x_.R * Exp(w_body * dt);
  x_.t  = imu.t;
  // biases constant (random walk handled in Q)

  // Error-state covariance propagation
  auto F = build_F(imu, dt);
  auto G = build_G();
  auto Q = build_Q();
  P_ = F * P_ * F.transpose() + G * Q * G.transpose();
}

Eigen::Matrix<double,15,15> ESKF::build_F(
    const ImuMeasurement& imu, double dt) const
{
  Eigen::Matrix<double,15,15> F = Eigen::Matrix<double,15,15>::Identity();
  Eigen::Matrix3d R = x_.R;
  Eigen::Vector3d a_hat = imu.am - x_.ba;
  // Cross-product (skew) of R*a_hat
  Eigen::Matrix3d S;
  Eigen::Vector3d Ra = R * a_hat;
  S <<    0, -Ra.z(),  Ra.y(),
      Ra.z(),      0, -Ra.x(),
     -Ra.y(),  Ra.x(),       0;

  F.block<3,3>(0,3)  = Eigen::Matrix3d::Identity() * dt;  // dp/dv
  F.block<3,3>(3,6)  = -S * dt;                           // dv/dtheta
  F.block<3,3>(3,9)  = -R * dt;                           // dv/dba
  F.block<3,3>(6,12) = -R * dt;                           // dtheta/dbg
  return F;
}

Eigen::Matrix<double,15,12> ESKF::build_G() const {
  Eigen::Matrix<double,15,12> G;
  G.setZero();
  G.block<3,3>(3,0)  = x_.R;                              // accel noise
  G.block<3,3>(6,3)  = x_.R;                              // gyro noise
  G.block<3,3>(9,6)  = Eigen::Matrix3d::Identity();       // ba walk
  G.block<3,3>(12,9) = Eigen::Matrix3d::Identity();       // bg walk
  return G;
}

Eigen::Matrix<double,12,12> ESKF::build_Q() const {
  Eigen::Matrix<double,12,12> Q;
  Q.setZero();
  Q.block<3,3>(0,0) = Eigen::Matrix3d::Identity() * sigma_am_*sigma_am_;
  Q.block<3,3>(3,3) = Eigen::Matrix3d::Identity() * sigma_wm_*sigma_wm_;
  Q.block<3,3>(6,6) = Eigen::Matrix3d::Identity() * sigma_ba_*sigma_ba_;
  Q.block<3,3>(9,9) = Eigen::Matrix3d::Identity() * sigma_bg_*sigma_bg_;
  return Q;
}

bool ESKF::chi2_gate(
    const Eigen::VectorXd& r,
    const Eigen::MatrixXd& S, double thr) const
{
  double eps = r.transpose() * S.inverse() * r;
  return eps < thr;
}

// ── RTK-GNSS update (absolute position, 3-DOF) ───────────────────────────────
bool ESKF::update_gnss(const GnssMeasurement& z) {
  // Innovation
  Eigen::Vector3d r = z.pos_ecef - x_.p;
  Eigen::Matrix<double,3,15> H;
  H.setZero();
  H.block<3,3>(0,0) = Eigen::Matrix3d::Identity();
  Eigen::Matrix3d S = H * P_ * H.transpose() + z.R_pos;
  // Chi2 gate (threshold 7.815 ~ 95% 3-DOF)
  if (!chi2_gate(r, S, 7.815)) return false;
  Eigen::Matrix<double,15,3> K = P_ * H.transpose() * S.inverse();
  Eigen::Matrix<double,15,1> dx = K * r;
  // Inject error state
  x_.p  += dx.segment<3>(0);
  x_.v  += dx.segment<3>(3);
  x_.R   = x_.R * Exp(dx.segment<3>(6));
  x_.ba += dx.segment<3>(9);
  x_.bg += dx.segment<3>(12);
  P_ = (Eigen::Matrix<double,15,15>::Identity() - K*H) * P_;
  return true;
}

// ── LiDAR blade-relative update ──────────────────────────────────────────────
bool ESKF::update_lidar_blade(const LidarBladeRelative& z) {
  // Residual on position only (blade-frame position = p_rel in world)
  Eigen::Vector3d r = z.p_rel - x_.p;
  Eigen::Matrix<double,3,15> H;
  H.setZero();
  H.block<3,3>(0,0) = Eigen::Matrix3d::Identity();
  Eigen::Matrix3d S = H * P_ * H.transpose() + z.R_rel;
  if (!chi2_gate(r, S, 7.815)) return false;
  Eigen::Matrix<double,15,3> K = P_ * H.transpose() * S.inverse();
  Eigen::Matrix<double,15,1> dx = K * r;
  x_.p  += dx.segment<3>(0);
  x_.v  += dx.segment<3>(3);
  x_.R   = x_.R * Exp(dx.segment<3>(6));
  x_.ba += dx.segment<3>(9);
  x_.bg += dx.segment<3>(12);
  P_ = (Eigen::Matrix<double,15,15>::Identity() - K*H) * P_;
  return true;
}

void ESKF::reset_error_state() { /* error state is implicit; P kept */ }

} // namespace drone_estimation
