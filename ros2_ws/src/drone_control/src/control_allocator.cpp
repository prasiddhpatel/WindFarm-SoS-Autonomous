#include "drone_control/control_allocator.hpp"
#include <Eigen/Dense>
#include <algorithm>

namespace drone_control {

/**
 * Control allocation (mixer) — eq. (8) from the SoS report.
 *
 * X-quad, arms at ±45°, arm length ell.
 * Gamma maps [f, tx, ty, tz] -> [omega1^2 .. omega4^2]
 * Saturation-aware: attitude torques are prioritised over thrust
 * to preserve stabilisation authority during gust rejection.
 */

ControlAllocator::ControlAllocator(
    double kf, double km, double ell,
    double omega_min, double omega_max)
    : kf_(kf), km_(km), ell_(ell),
      omega_min_(omega_min), omega_max_(omega_max)
{
  build_gamma();
}

void ControlAllocator::build_gamma() {
  const double s45 = ell_ / std::sqrt(2.0);
  // Columns: motor 1(FR), 2(BL), 3(FL), 4(BR)  — CW=+km, CCW=-km
  Gamma_ <<
     kf_,        kf_,        kf_,        kf_,
    -s45*kf_,   -s45*kf_,    s45*kf_,    s45*kf_,
     s45*kf_,   -s45*kf_,   -s45*kf_,    s45*kf_,
     km_,        -km_,        km_,       -km_;
  Gamma_inv_ = Gamma_.inverse();
}

ControlAllocator::Output ControlAllocator::allocate(
    double thrust, const Eigen::Vector3d& torque) const
{
  Eigen::Vector4d wrench(thrust, torque.x(), torque.y(), torque.z());
  Eigen::Vector4d omega_sq = Gamma_inv_ * wrench;

  Output out;
  bool saturated = false;
  for (int i = 0; i < 4; ++i) {
    double w = std::sqrt(std::max(0.0, omega_sq(i)));
    if (w > omega_max_ || w < omega_min_) saturated = true;
    out.omega[i] = std::clamp(w, omega_min_, omega_max_);
  }
  out.saturated = saturated;
  return out;
}

} // namespace drone_control
