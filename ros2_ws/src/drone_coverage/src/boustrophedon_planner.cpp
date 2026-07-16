#include "drone_coverage/boustrophedon_planner.hpp"
#include <algorithm>

namespace drone_coverage {

std::pair<Eigen::Vector3d, Eigen::Matrix3d> BoustrophedonPlanner::pca_blade(const BladeCloud& cloud) {
  Eigen::Vector3d centroid = Eigen::Vector3d::Zero();
  for (const auto& p : cloud) centroid += p;
  centroid /= std::max<size_t>(1, cloud.size());

  Eigen::Matrix3d C = Eigen::Matrix3d::Zero();
  for (const auto& p : cloud) {
    auto d = p - centroid;
    C += d * d.transpose();
  }
  Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> es(C);
  return {centroid, es.eigenvectors()};
}

std::tuple<double,double,double,double> BoustrophedonPlanner::bounding_box_2d(
  const BladeCloud& cloud, const Eigen::Vector3d& centroid, const Eigen::Matrix3d& axes) {
  double umin=1e9, umax=-1e9, vmin=1e9, vmax=-1e9;
  for (const auto& p : cloud) {
    Eigen::Vector3d q = axes.transpose() * (p - centroid);
    umin = std::min(umin, q.x()); umax = std::max(umax, q.x());
    vmin = std::min(vmin, q.y()); vmax = std::max(vmax, q.y());
  }
  return {umin, umax, vmin, vmax};
}

Eigen::Vector3d BoustrophedonPlanner::query_surface_normal(const BladeCloud&, const Eigen::Vector3d&) {
  return Eigen::Vector3d(0.0, 1.0, 0.0);
}

std::vector<BladePose> BoustrophedonPlanner::plan(const BladeCloud& cloud,
                                                  const SensorParams& sp,
                                                  const PlannerConfig& cfg) {
  if (cloud.empty()) return {};
  auto [centroid, axes] = pca_blade(cloud);
  auto [umin, umax, vmin, vmax] = bounding_box_2d(cloud, centroid, axes);
  (void)vmin; (void)vmax;

  const double standoff = std::clamp(cfg.target_gsd_m * sp.focal_length_m / sp.pixel_pitch_m,
                                     cfg.min_standoff_m, cfg.max_standoff_m);
  const double footprint_w = sp.sensor_width_px * sp.pixel_pitch_m * standoff / sp.focal_length_m;
  const double pass_spacing = std::max(0.05, footprint_w * (1.0 - cfg.side_overlap));
  const double step = std::max(0.05, footprint_w * (1.0 - cfg.forward_overlap));

  std::vector<BladePose> out;
  bool reverse = false;
  for (double u = umin; u <= umax + 1e-9; u += pass_spacing) {
    std::vector<double> sweep;
    for (double v = -1.0; v <= 1.0 + 1e-9; v += step) sweep.push_back(v);
    if (reverse) std::reverse(sweep.begin(), sweep.end());
    reverse = !reverse;

    for (double v : sweep) {
      Eigen::Vector3d p_local(u, v, 0.0);
      Eigen::Vector3d p_world = centroid + axes * p_local;
      Eigen::Vector3d n = query_surface_normal(cloud, p_world);
      BladePose pose;
      pose.position = p_world + standoff * n;
      pose.z_axis_body = -n.normalized();
      pose.standoff = standoff;
      pose.gsd = cfg.target_gsd_m;
      out.push_back(pose);
    }
  }
  return out;
}

} // namespace drone_coverage
