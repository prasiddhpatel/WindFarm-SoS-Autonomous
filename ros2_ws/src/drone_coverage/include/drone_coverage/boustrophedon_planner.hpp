#pragma once
#include <Eigen/Dense>
#include <vector>

namespace drone_coverage {

using BladeCloud = std::vector<Eigen::Vector3d>;

struct BladePose {
  Eigen::Vector3d position;
  Eigen::Vector3d z_axis_body;
  double yaw{0.0};
  double standoff{0.0};
  double gsd{0.0};
};

struct SensorParams {
  double focal_length_m{0.012};
  double pixel_pitch_m{2.4e-6};
  double sensor_width_px{5472};
};

struct PlannerConfig {
  double target_gsd_m{1.0e-3};
  double min_standoff_m{2.0};
  double max_standoff_m{8.0};
  double forward_overlap{0.75};
  double side_overlap{0.6};
};

class BoustrophedonPlanner {
public:
  std::vector<BladePose> plan(const BladeCloud& cloud,
                              const SensorParams& sp,
                              const PlannerConfig& cfg);
private:
  std::pair<Eigen::Vector3d, Eigen::Matrix3d> pca_blade(const BladeCloud& cloud);
  std::tuple<double,double,double,double> bounding_box_2d(const BladeCloud& cloud,
      const Eigen::Vector3d& centroid, const Eigen::Matrix3d& axes);
  Eigen::Vector3d query_surface_normal(const BladeCloud& cloud, const Eigen::Vector3d& p);
};

} // namespace drone_coverage
