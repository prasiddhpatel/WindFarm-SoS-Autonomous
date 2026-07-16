#pragma once
/**
 * Error-State Kalman Filter (ESKF) for UAV state estimation.
 *
 * Nominal state x = [p(3), v(3), R(9), ba(3), bg(3)]  -> 18 DOF
 * Error state  dx = [dp(3), dv(3), dtheta(3), dba(3), dbg(3)] -> 15 DOF
 *
 * Implements equations (9)-(12) of the SoS technical report.
 * Sensor sources: IMU (propagation), RTK-GNSS (absolute pos),
 *                 VIO (relative pose), LiDAR registration (blade-relative).
 *
 * Reference: Joan Sola, "A micro Lie theory for state estimation in
 *            robotics", arXiv:1812.01537 (used for SO(3) injection).
 */
#include <Eigen/Dense>
#include <Eigen/Geometry>

namespace drone_estimation {

struct ImuMeasurement {
  double   t;
  Eigen::Vector3d am;   // specific force  [m/s^2]
  Eigen::Vector3d wm;   // angular rate    [rad/s]
};

struct GnssMeasurement {
  double   t;
  Eigen::Vector3d pos_ecef;   // or ENU, depends on frame config
  Eigen::Matrix3d R_pos;      // measurement noise covariance
  bool rtk_fix{false};
};

struct VioPoseMeasurement {
  double   t;
  Eigen::Vector3d dp;         // relative position from VIO
  Eigen::Quaterniond dq;      // relative rotation
  Eigen::Matrix<double,6,6> R_vio;
};

struct LidarBladeRelative {
  double   t;
  Eigen::Vector3d p_rel;      // position relative to reconstructed blade
  Eigen::Matrix3d R_rel;
};

class ESKF {
public:
  struct NominalState {
    Eigen::Vector3d  p   = Eigen::Vector3d::Zero();
    Eigen::Vector3d  v   = Eigen::Vector3d::Zero();
    Eigen::Matrix3d  R   = Eigen::Matrix3d::Identity();
    Eigen::Vector3d  ba  = Eigen::Vector3d::Zero();
    Eigen::Vector3d  bg  = Eigen::Vector3d::Zero();
    double           t   = 0.0;
  };

  ESKF();

  // ── Propagation ──────────────────────────────────────────────────
  void propagate(const ImuMeasurement& imu);

  // ── Measurement updates ──────────────────────────────────────────
  bool update_gnss(const GnssMeasurement& z);
  bool update_vio(const VioPoseMeasurement& z);
  bool update_lidar_blade(const LidarBladeRelative& z);

  // ── Accessors ────────────────────────────────────────────────────
  const NominalState& state()       const { return x_; }
  const Eigen::Matrix<double,15,15>& cov() const { return P_; }

  void set_initial_state(const NominalState& x0,
                         const Eigen::Matrix<double,15,15>& P0);
  void reset_error_state();

private:
  NominalState x_;
  Eigen::Matrix<double,15,15> P_;

  // Process noise std-devs (tunable)
  double sigma_am_  {0.05};   // accel measurement noise
  double sigma_wm_  {0.005};  // gyro measurement noise
  double sigma_ba_  {0.001};  // accel bias random walk
  double sigma_bg_  {1e-4};   // gyro bias random walk

  static constexpr double g_ = 9.81;
  static const    Eigen::Vector3d G_;

  Eigen::Matrix<double,15,15> build_F(const ImuMeasurement& imu,
                                      double dt) const;
  Eigen::Matrix<double,15,12> build_G() const;
  Eigen::Matrix<double,12,12> build_Q() const;

  /** Chi2 gate — rejects outliers (GNSS multipath near tower) */
  bool chi2_gate(const Eigen::VectorXd& r,
                 const Eigen::MatrixXd& S, double threshold) const;

  /** SO(3) exponential map */
  static Eigen::Matrix3d Exp(const Eigen::Vector3d& phi);
  static Eigen::Vector3d Log(const Eigen::Matrix3d& R);
};

} // namespace drone_estimation
