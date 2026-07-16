#include "drone_coverage/standoff_regulator.hpp"

namespace drone_coverage {

StandoffRegulator::StandoffRegulator(const StandoffRegulatorParams& p) : p_(p) {}

double StandoffRegulator::compute(double measured_standoff, double dt) {
  double error = p_.nominal_standoff_m - measured_standoff;
  double deriv = (dt > 1e-9) ? (error - prev_error_) / dt : 0.0;
  prev_error_ = error;
  return p_.kp * error + p_.kd * deriv;
}

} // namespace drone_coverage
