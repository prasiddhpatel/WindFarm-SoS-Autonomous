#pragma once

namespace drone_coverage {

struct StandoffRegulatorParams {
  double kp{2.0};
  double kd{0.5};
  double nominal_standoff_m{1.0};
};

class StandoffRegulator {
public:
  explicit StandoffRegulator(const StandoffRegulatorParams& p = {});
  double compute(double measured_standoff, double dt);

private:
  StandoffRegulatorParams p_;
  double prev_error_{0.0};
};

} // namespace drone_coverage
