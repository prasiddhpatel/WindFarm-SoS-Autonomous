#pragma once
#include <vector>
#include <array>
#include <Eigen/Dense>

namespace drone_coverage {

class MinSnapTrajectory {
public:
  struct Sample {
    Eigen::Vector3d pos{Eigen::Vector3d::Zero()};
    Eigen::Vector3d vel{Eigen::Vector3d::Zero()};
    Eigen::Vector3d acc{Eigen::Vector3d::Zero()};
  };

  MinSnapTrajectory(const std::vector<Eigen::Vector3d>& waypoints,
                    const std::vector<double>& segment_times,
                    double sample_dt = 0.02);

  Sample evaluate(double t) const;
  double total_time() const;

private:
  std::vector<Eigen::Vector3d> wps_;
  std::vector<double> T_;
  double dt_;
  std::array<Eigen::MatrixXd, 3> coeffs_;

  void solve();
  Sample eval_segment(int i, double tau) const;
  static double deriv_coeff(int order, int deriv);
  static double deriv_factorial(int deriv);
};

} // namespace drone_coverage
