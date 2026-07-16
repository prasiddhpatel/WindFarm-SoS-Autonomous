#include "drone_coverage/minimum_snap_trajectory.hpp"
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <stdexcept>

namespace drone_coverage {

/**
 * Minimum-snap trajectory generator for the coverage waypoint list.
 *
 * Generates piecewise degree-7 polynomial trajectories p(t) such that
 * snap (4th derivative) is minimised subject to waypoint interpolation,
 * continuity to 3rd derivative, and boundary conditions.
 *
 * Returns sampled p(t), pdot(t), pddot(t) at a fixed dt for the
 * geometric controller reference generator.
 */

MinSnapTrajectory::MinSnapTrajectory(
    const std::vector<Eigen::Vector3d>& waypoints,
    const std::vector<double>&          segment_times,
    double                               sample_dt)
  : wps_(waypoints), T_(segment_times), dt_(sample_dt)
{
  if (wps_.size() < 2)
    throw std::invalid_argument("Need at least 2 waypoints");
  if (T_.size() != wps_.size()-1)
    throw std::invalid_argument("segment_times must have N-1 entries");
  solve();
}

void MinSnapTrajectory::solve() {
  // Polynomial order 7 (degree 7 => 8 coeffs per segment per axis)
  constexpr int N = 8;   // poly coefficients per segment
  int M = static_cast<int>(wps_.size()) - 1;  // number of segments

  for (int axis = 0; axis < 3; ++axis) {
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(N*M, N*M);
    Eigen::VectorXd b = Eigen::VectorXd::Zero(N*M);
    int row = 0;

    for (int i = 0; i < M; ++i) {
      double Ti = T_[i];
      // Position at start of segment
      A(row, i*N) = 1.0;
      b(row++) = wps_[i](axis);
      // Position at end of segment
      for (int k = 0; k < N; ++k)
        A(row, i*N+k) = std::pow(Ti, k);
      b(row++) = wps_[i+1](axis);

      // Continuity constraints (velocity, accel, jerk) at interior waypoints
      if (i < M-1) {
        for (int deriv = 1; deriv <= 3; ++deriv) {
          // End of segment i
          for (int k = deriv; k < N; ++k) {
            double coeff = deriv_coeff(k, deriv) * std::pow(Ti, k-deriv);
            A(row, i*N+k) = coeff;
          }
          // Start of segment i+1 (t=0)
          A(row, (i+1)*N+deriv) = -deriv_factorial(deriv);
          b(row++) = 0.0;
        }
      }
    }
    // Boundary: zero vel/acc/jerk at start and end
    for (int deriv = 1; deriv <= 3; ++deriv) {
      A(row, deriv) = deriv_factorial(deriv); b(row++) = 0.0;
      int last = (M-1)*N;
      double Te = T_[M-1];
      for (int k = deriv; k < N; ++k)
        A(row, last+k) = deriv_coeff(k,deriv)*std::pow(Te,k-deriv);
      b(row++) = 0.0;
    }

    // Solve via QR
    Eigen::VectorXd c = A.colPivHouseholderQr().solve(b);
    coeffs_[axis].resize(M, N);
    for (int i = 0; i < M; ++i)
      coeffs_[axis].row(i) = c.segment(i*N, N).transpose();
  }
}

double MinSnapTrajectory::deriv_coeff(int k, int d) {
  double c = 1.0;
  for (int j = 0; j < d; ++j) c *= (k - j);
  return c;
}

double MinSnapTrajectory::deriv_factorial(int d) {
  double c = 1.0;
  for (int j = 1; j <= d; ++j) c *= j;
  return c;
}

MinSnapTrajectory::Sample MinSnapTrajectory::evaluate(double t) const {
  // find segment
  double t_acc = 0.0;
  for (int i = 0; i < static_cast<int>(T_.size()); ++i) {
    if (t <= t_acc + T_[i] || i == static_cast<int>(T_.size())-1) {
      double tau = t - t_acc;
      return eval_segment(i, tau);
    }
    t_acc += T_[i];
  }
  return eval_segment(static_cast<int>(T_.size())-1, T_.back());
}

MinSnapTrajectory::Sample MinSnapTrajectory::eval_segment(
    int i, double tau) const
{
  constexpr int N = 8;
  Sample s;
  for (int axis = 0; axis < 3; ++axis) {
    const auto& row = coeffs_[axis].row(i);
    double p=0,v=0,a=0;
    for (int k = 0; k < N; ++k) {
      p += row(k)*std::pow(tau,k);
      if (k>=1) v += k*row(k)*std::pow(tau,k-1);
      if (k>=2) a += k*(k-1)*row(k)*std::pow(tau,k-2);
    }
    s.pos(axis)=p; s.vel(axis)=v; s.acc(axis)=a;
  }
  return s;
}

} // namespace drone_coverage
