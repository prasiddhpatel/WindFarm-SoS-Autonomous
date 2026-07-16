#include "safety_monitor/rate_monotonic_scheduler.hpp"
#include <algorithm>
#include <stdexcept>

namespace safety_monitor {

void RateMonotonicScheduler::add_task(std::string name, double period_s, double wcet_s) {
  if (period_s <= 0.0 || wcet_s <= 0.0)
    throw std::invalid_argument("period and wcet must be positive");
  tasks_.push_back({std::move(name), period_s, wcet_s});
}

bool RateMonotonicScheduler::utilisation_bound_check() const {
  double U = 0.0;
  for (const auto& t : tasks_) U += t.wcet_s / t.period_s;
  double n = static_cast<double>(tasks_.size());
  double bound = n * (std::pow(2.0, 1.0/n) - 1.0);
  return U <= bound;
}

double RateMonotonicScheduler::total_utilisation() const {
  double U = 0.0;
  for (const auto& t : tasks_) U += t.wcet_s / t.period_s;
  return U;
}

} // namespace safety_monitor
