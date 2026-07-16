#pragma once
namespace safety_monitor {
class RateMonotonicScheduler {
public:
  static double utilisation_bound(int n) {
    return n * (std::pow(2.0, 1.0 / n) - 1.0);
  }
};
}
