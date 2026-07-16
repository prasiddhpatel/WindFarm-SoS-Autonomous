#pragma once
namespace drone_coverage {
class StandoffRegulator {
public:
  double regulate(double measured_distance, double desired_distance) const {
    return desired_distance - measured_distance;
  }
};
}
