#pragma once
#include <vector>
#include <Eigen/Dense>

namespace ground_robot_nav {

struct UnicycleState { double x{0}, y{0}, psi{0}; };
struct Control      { double v{0}, omega{0}; };
struct ObstacleCircle { double cx{0}, cy{0}, r{1}; };

struct Params {
  double dt{0.1};
  int    horizon{10};
  double v_min{-1.0}, v_max{2.0};
  double omega_min{-1.5}, omega_max{1.5};
  double q_pos{1.0},  q_psi{0.5};
  double r_v{0.1},    r_omega{0.1};
};

class SkidSteerMPC {
public:
  explicit SkidSteerMPC(const Params& p = {});
  Control solve(const UnicycleState& x0,
                const std::vector<UnicycleState>& ref_traj,
                const std::vector<ObstacleCircle>& obstacles = {});
private:
  Params p_;
  UnicycleState dynamics(const UnicycleState& x, const Control& u, double dt) const;
  std::pair<Eigen::Matrix3d, Eigen::Matrix<double,3,2>>
    linearise(const UnicycleState& x, const Control& u) const;
};

} // namespace ground_robot_nav
