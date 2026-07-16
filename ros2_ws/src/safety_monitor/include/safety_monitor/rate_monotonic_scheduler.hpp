#pragma once
#include <string>
#include <vector>
#include <cmath>

namespace safety_monitor {

struct RtTask {
  std::string name;
  double period_s;
  double wcet_s;
};

class RateMonotonicScheduler {
public:
  void add_task(std::string name, double period_s, double wcet_s);
  bool utilisation_bound_check() const;
  double total_utilisation() const;
  const std::vector<RtTask>& tasks() const { return tasks_; }
private:
  std::vector<RtTask> tasks_;
};

} // namespace safety_monitor
