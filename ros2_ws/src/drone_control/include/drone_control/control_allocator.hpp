#pragma once
#include <array>
#include <Eigen/Dense>

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
  double kf_, km_, ell_, omega_min_, omega_max_;
  Eigen::Matrix4d Gamma_;
  Eigen::Matrix4d Gamma_inv_;
  void build_gamma();
};

} // namespace drone_control
