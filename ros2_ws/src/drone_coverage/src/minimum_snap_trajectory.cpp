#include "drone_coverage/minimum_snap_trajectory.hpp"

namespace drone_coverage {

MinSnapTrajectory::MinSnapTrajectory(const std::vector<Eigen::Vector3d>& waypoints,
                                     const std::vector<double>& segment_times,
                                     double sample_dt)
: wps_(waypoints), T_(segment_times), dt_(sample_dt) {
  solve();
}

void MinSnapTrajectory::solve() {
  for (int axis = 0; axis < 3; ++axis) {
    coeffs_[axis] = Eigen::MatrixXd::Zero(std::max<int>(1, T_.size()), 8);
    for (size_t i = 0; i < T_.size(); ++i) {
      coeffs_[axis](i, 0) = wps_[i](axis);
      coeffs_[axis](i, 1) = (wps_[i+1](axis) - wps_[i](axis)) / std::max(1e-6, T_[i]);
    }
  }
}

MinSnapTrajectory::Sample MinSnapTrajectory::eval_segment(int i, double tau) const {
  Sample s;
  for (int axis = 0; axis < 3; ++axis) {
    const auto c0 = coeffs_[axis](i,0);
    const auto c1 = coeffs_[axis](i,1);
    s.pos(axis) = c0 + c1 * tau;
    s.vel(axis) = c1;
    s.acc(axis) = 0.0;
  }
  return s;
}

MinSnapTrajectory::Sample MinSnapTrajectory::evaluate(double t) const {
  if (T_.empty()) return {};
  double acc = 0.0;
  for (size_t i = 0; i < T_.size(); ++i) {
    if (t <= acc + T_[i] || i == T_.size()-1) {
      return eval_segment(static_cast<int>(i), t - acc);
    }
    acc += T_[i];
  }
  return {};
}

double MinSnapTrajectory::deriv_coeff(int, int) { return 0.0; }
double MinSnapTrajectory::deriv_factorial(int) { return 1.0; }

} // namespace drone_coverage
