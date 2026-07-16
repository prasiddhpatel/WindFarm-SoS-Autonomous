#pragma once
#include <Eigen/Dense>
#include <vector>

namespace ground_robot_nav {

struct ObstacleCircle {
  double cx{0.0}, cy{0.0}, r{0.0};
};

class SkidSteerMPC {
public:
  struct Params {
    int horizon{15};
    double dt{0.1};
    int max_iter{5};
    double v_min{-0.5}, v_max{1.5};
    double omega_min{-1.0}, omega_max{1.0};
    double d_safe{0.75};
    Eigen::Matrix3d Q = Eigen::Matrix3d::Identity();
    Eigen::Matrix2d R = Eigen::Matrix2d::Identity() * 0.1;
    Eigen::Matrix3d Qf = Eigen::Matrix3d::Identity() * 2.0;
  };

  struct UnicycleState { double x{0}, y{0}, psi{0}; };
  struct Control { double v{0}, omega{0}; };

  explicit SkidSteerMPC(const Params& p = Params());
  Control solve(const UnicycleState& x0,
                const std::vector<UnicycleState>& ref_traj,
                const std::vector<ObstacleCircle>& obstacles);

private:
  Params p_;
  UnicycleState dynamics(const UnicycleState& x, const Control& u, double dt) const;
  std::pair<Eigen::Matrix3d, Eigen::Matrix<double,3,2>> linearise(const UnicycleState& x, const Control& u) const;

  Eigen::Vector3d state_diff(const UnicycleState& a, const UnicycleState& b) const {
    return Eigen::Vector3d(a.x-b.x, a.y-b.y, a.psi-b.psi);
  }
  Eigen::Vector3d stage_cost_grad_x(const UnicycleState& x, const UnicycleState& xr) const {
    return 2.0 * p_.Q * state_diff(x, xr);
  }
  Eigen::Vector2d stage_cost_grad_u(const Control& u) const {
    return 2.0 * p_.R * Eigen::Vector2d(u.v, u.omega);
  }
  Eigen::Vector3d terminal_cost_grad(const UnicycleState& x, const UnicycleState& xr) const {
    return 2.0 * p_.Qf * state_diff(x, xr);
  }
};

} // namespace ground_robot_nav
