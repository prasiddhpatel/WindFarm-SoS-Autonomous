#include "drone_control/control_allocator.hpp"
#include <algorithm>
#include <cmath>

namespace drone_control {

ControlAllocator::ControlAllocator(double kf, double km, double ell,
                                   double omega_min, double omega_max)
: kf_(kf), km_(km), ell_(ell), omega_min_(omega_min), omega_max_(omega_max) {
  build_gamma();
}

void ControlAllocator::build_gamma() {
  Gamma_ << kf_, kf_, kf_, kf_,
            0.0, ell_ * kf_, 0.0, -ell_ * kf_,
            -ell_ * kf_, 0.0, ell_ * kf_, 0.0,
            km_, -km_, km_, -km_;
  Gamma_inv_ = Gamma_.inverse();
}

ControlAllocator::Output ControlAllocator::allocate(double thrust, const Eigen::Vector3d& torque) const {
  Eigen::Vector4d u;
  u << thrust, torque.x(), torque.y(), torque.z();
  Eigen::Vector4d omega_sq = Gamma_inv_ * u;

  Output out;
  for (int i = 0; i < 4; ++i) {
    double w = std::sqrt(std::max(0.0, omega_sq(i)));
    double wc = std::clamp(w, omega_min_, omega_max_);
    out.omega[i] = wc;
    if (std::abs(w - wc) > 1e-9) out.saturated = true;
  }
  return out;
}

} // namespace drone_control
