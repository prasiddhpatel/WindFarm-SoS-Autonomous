#include "drone_control/se3_controller.hpp"
#include <cmath>
#include <algorithm>

namespace drone_control {

SE3Controller::SE3Controller(double mass_kg,
                             const Eigen::Matrix3d& inertia,
                             const Gains& gains)
    : mass_(mass_kg), J_(inertia), gains_(gains) {}

void SE3Controller::reset_integral() {
  int_ep_.setZero();
}

Eigen::Vector3d SE3Controller::vee(const Eigen::Matrix3d& M) {
  return {M(2,1), M(0,2), M(1,0)};
}

Eigen::Matrix3d SE3Controller::hat(const Eigen::Vector3d& v) {
  Eigen::Matrix3d S;
  S <<     0, -v.z(),  v.y(),
       v.z(),      0, -v.x(),
      -v.y(),  v.x(),      0;
  return S;
}

SE3Controller::Output SE3Controller::compute(
    const State& x, const Reference& ref, double dt)
{
  Output out;
  const Eigen::Vector3d e3(0, 0, 1);

  // ── Position / velocity errors ─────────────────────────────────────
  Eigen::Vector3d ep = x.p - ref.pd;
  Eigen::Vector3d ev = x.v - ref.vd;

  // Anti-windup clamped integral
  int_ep_ += ep * dt;
  double int_norm = int_ep_.norm();
  constexpr double INT_MAX = 2.0;
  if (int_norm > INT_MAX) int_ep_ *= INT_MAX / int_norm;

  // Desired specific thrust vector  (eq. 13)
  Eigen::Vector3d F_des = -gains_.kp * ep
                          - gains_.kv * ev
                          - gains_.ki_p * int_ep_
                          + mass_ * g_ * e3
                          + mass_ * ref.ad;

  out.thrust = F_des.dot(x.R * e3);
  out.thrust = std::clamp(out.thrust, 0.0, mass_ * g_ * 3.0);

  // ── Desired rotation ───────────────────────────────────────────────
  Eigen::Vector3d b3d = F_des.normalized();
  Eigen::Vector3d b1c(std::cos(ref.yaw_d), std::sin(ref.yaw_d), 0.0);
  Eigen::Vector3d b2d = b3d.cross(b1c).normalized();
  Eigen::Vector3d b1d = b2d.cross(b3d);

  Eigen::Matrix3d R_des;
  R_des.col(0) = b1d;
  R_des.col(1) = b2d;
  R_des.col(2) = b3d;
  out.R_des = R_des;

  // ── Attitude error  (eq. 14) ───────────────────────────────────────
  Eigen::Matrix3d eR_mat = 0.5 * (R_des.transpose() * x.R
                                 - x.R.transpose() * R_des);
  Eigen::Vector3d eR = vee(eR_mat);

  Eigen::Vector3d omega_des = Eigen::Vector3d::Zero();
  omega_des.z() = ref.yaw_rate_d;
  Eigen::Vector3d eOmega = x.omega - x.R.transpose() * R_des * omega_des;

  // ── Torque command  (eq. 15) ───────────────────────────────────────
  out.torque = -gains_.kR * eR
               - gains_.kW * eOmega
               + x.omega.cross(J_ * x.omega);

  return out;
}

} // namespace drone_control
