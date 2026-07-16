#include "drone_estimation/eskf.hpp"

namespace drone_estimation {

ESKF::ESKF() : last_t_(0.0), initialized_(false) {
  P_.setIdentity();
}

void ESKF::propagate(const ImuMeasurement& z) {
  if (!initialized_) {
    last_t_ = z.t;
    initialized_ = true;
    return;
  }
  double dt = z.t - last_t_;
  if (dt <= 0.0) return;

  Eigen::Vector3d omega = z.wm - x_.bg;
  Eigen::Vector3d acc_body = z.am - x_.ba;

  Eigen::Matrix3d Omega;
  Omega <<     0.0, -omega.z(),  omega.y(),
          omega.z(),      0.0, -omega.x(),
         -omega.y(),  omega.x(),      0.0;

  x_.R = x_.R * (Eigen::Matrix3d::Identity() + Omega * dt);
  Eigen::Vector3d g(0.0, 0.0, -9.81);
  Eigen::Vector3d acc_world = x_.R * acc_body + g;
  x_.p += x_.v * dt + 0.5 * acc_world * dt * dt;
  x_.v += acc_world * dt;
  last_t_ = z.t;
}

void ESKF::update_gnss(const GnssMeasurement& z) {
  (void)z.R_pos;
  (void)z.rtk_fix;
  x_.p = 0.8 * x_.p + 0.2 * z.pos_ecef;
}

} // namespace drone_estimation
