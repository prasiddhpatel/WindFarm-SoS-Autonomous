#pragma once
#include <Eigen/Dense>
#include <array>

namespace drone_control {

class ControlAllocator {
public:
  struct Output {
    std::array<double,4> omega{};
    bool saturated{false};
  };

  ControlAllocator(double kf, double km, double ell,
                   double omega_min, double omega_max);

  Output allocate(double thrust, const Eigen::Vector3d& torque) const;

private:
  void build_gamma();

  double kf_, km_, ell_;
  double omega_min_, omega_max_;
  Eigen::Matrix4d Gamma_;
  Eigen::Matrix4d Gamma_inv_;
};

} // namespace drone_control
