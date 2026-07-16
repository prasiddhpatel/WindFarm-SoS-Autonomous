#pragma once
#include <Eigen/Dense>
#include <vector>

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
                    double sample_dt);

  Sample evaluate(double t) const;

private:
  void solve();
  Sample eval_segment(int i, double tau) const;
  static double deriv_coeff(int k, int d);
  static double deriv_factorial(int d);

  std::vector<Eigen::Vector3d> wps_;
  std::vector<double> T_;
  double dt_;
  std::array<Eigen::MatrixXd,3> coeffs_;
};

} // namespace drone_coverage
