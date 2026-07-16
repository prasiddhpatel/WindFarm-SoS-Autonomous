#include "ground_robot_nav/skid_steer_mpc.hpp"
#include <algorithm>

namespace ground_robot_nav {

SkidSteerMPC::SkidSteerMPC(const Params& p) : p_(p) {}

SkidSteerMPC::UnicycleState SkidSteerMPC::dynamics(const UnicycleState& x, const Control& u, double dt) const {
  return {x.x + u.v * std::cos(x.psi) * dt,
          x.y + u.v * std::sin(x.psi) * dt,
          x.psi + u.omega * dt};
}

std::pair<Eigen::Matrix3d, Eigen::Matrix<double,3,2>>
SkidSteerMPC::linearise(const UnicycleState& x, const Control& u) const {
  Eigen::Matrix3d A = Eigen::Matrix3d::Identity();
  A(0,2) = -u.v * std::sin(x.psi) * p_.dt;
  A(1,2) =  u.v * std::cos(x.psi) * p_.dt;
  Eigen::Matrix<double,3,2> B = Eigen::Matrix<double,3,2>::Zero();
  B(0,0) = std::cos(x.psi) * p_.dt;
  B(1,0) = std::sin(x.psi) * p_.dt;
  B(2,1) = p_.dt;
  return {A, B};
}

SkidSteerMPC::Control SkidSteerMPC::solve(const UnicycleState& x0,
                                          const std::vector<UnicycleState>& ref_traj,
                                          const std::vector<ObstacleCircle>& obstacles) {
  (void)obstacles;
  if (ref_traj.empty()) return {};
  const auto& xr = ref_traj.front();
  double dx = xr.x - x0.x;
  double dy = xr.y - x0.y;
  double target_heading = std::atan2(dy, dx);
  double heading_err = target_heading - x0.psi;
  double dist = std::sqrt(dx*dx + dy*dy);

  Control u;
  u.v = std::clamp(0.8 * dist, p_.v_min, p_.v_max);
  u.omega = std::clamp(1.5 * heading_err, p_.omega_min, p_.omega_max);
  return u;
}

} // namespace ground_robot_nav
