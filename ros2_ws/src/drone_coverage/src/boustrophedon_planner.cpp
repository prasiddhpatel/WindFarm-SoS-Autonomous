#include "drone_coverage/boustrophedon_planner.hpp"
#include <cmath>
#include <algorithm>

namespace drone_coverage {

/**
 * LiDAR-referenced boustrophedon (lawnmower) coverage planner.
 *
 * Implements the stand-off and GSD constraint of eq.(16)-(17) in the report.
 * Input : PCL point cloud of reconstructed blade surface + sensor params.
 * Output: ordered list of 6-DOF waypoints whose optical axis is anti-parallel
 *         to the local surface normal at commanded standoff d*.
 */

std::vector<BladePose> BoustrophedonPlanner::plan(
    const BladeCloud& cloud,
    const SensorParams& sp,
    const PlannerConfig& cfg)
{
  // 1. Fit plane / extract blade principal axes via PCA
  auto [centroid, axes] = pca_blade(cloud);
  // axes[:,0] = span direction, axes[:,1] = chord direction, axes[:,2] = normal

  // 2. Project cloud onto span-chord plane, get bounding box
  auto [span_min, span_max, chord_min, chord_max] =
      bounding_box_2d(cloud, centroid, axes);

  // 3. Compute swath width from GSD budget  (eq. 16)
  //    GSD = mu * d* / phi  => d* = cfg.target_gsd * sp.focal_length / sp.pixel_pitch
  double d_star = cfg.target_gsd_m * sp.focal_length_m / sp.pixel_pitch_m;
  d_star = std::clamp(d_star, cfg.min_standoff_m, cfg.max_standoff_m);

  double swath_w = sp.pixel_pitch_m * sp.sensor_width_px / sp.focal_length_m * d_star;
  double track_spacing = swath_w * (1.0 - cfg.side_overlap);

  // 4. Generate boustrophedon tracks along span axis
  std::vector<BladePose> waypoints;
  bool left_to_right = true;
  for (double chord = chord_min + swath_w*0.5;
       chord <= chord_max;
       chord += track_spacing)
  {
    std::vector<double> span_pts;
    double s = span_min;
    while (s <= span_max) {
      span_pts.push_back(s);
      s += swath_w * (1.0 - cfg.forward_overlap);
    }
    if (!left_to_right) std::reverse(span_pts.begin(), span_pts.end());
    left_to_right = !left_to_right;

    for (double span : span_pts) {
      // Surface point closest to (span, chord) in blade frame
      Eigen::Vector3d p_blade = centroid
          + span  * axes.col(0)
          + chord * axes.col(1);

      // Query nearest surface normal from cloud
      Eigen::Vector3d normal = query_surface_normal(cloud, p_blade);

      // Waypoint (eq. 17): offset by d* along outward normal
      BladePose wp;
      wp.position   = p_blade + d_star * normal;
      wp.z_axis_body = -normal;          // camera z anti-parallel to normal
      // yaw from span direction projected to world XY
      wp.yaw        = std::atan2(axes.col(0).y(), axes.col(0).x());
      wp.standoff   = d_star;
      wp.gsd        = sp.pixel_pitch_m * d_star / sp.focal_length_m;
      waypoints.push_back(wp);
    }
  }
  return waypoints;
}

} // namespace drone_coverage
