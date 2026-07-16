#pragma once
#include <Eigen/Dense>

namespace drone_estimation {

struct State {
  Eigen::Vector3d p{Eigen::Vector3d::Zero()};
  Eigen::Vector3d v{Eigen::Vector3d::Zero()};
  Eigen::Matrix3d R{Eigen::Matrix3d::Identity()};
  Eigen::Vector3d ba{Eigen::Vector3d::Zero()};
  Eigen::Vector3d bg{Eigen::Vector3d::Zero()};
};

struct ImuMeasurement {
  double t{0.0};
  Eigen::Vector3d am{Eigen::Vector3d::Zero()};
  Eigen::Vector3d wm{Eigen::Vector3d::Zero()};
};

struct GnssMeasurement {
  double t{0.0};
  Eigen::Vector3d pos_ecef{Eigen::Vector3d::Zero()};
  Eigen::Matrix3d R_pos{Eigen::Matrix3d::Identity()};
  bool rtk_fix{false};
};

class ESKF {
public:
  ESKF();
  void propagate(const ImuMeasurement& z);
  void update_gnss(const GnssMeasurement& z);
  const State& state() const { return x_; }

private:
  State x_;
  Eigen::Matrix<double, 15, 15> P_;
  double last_t_;
  bool initialized_;
};

} // namespace drone_estimation
