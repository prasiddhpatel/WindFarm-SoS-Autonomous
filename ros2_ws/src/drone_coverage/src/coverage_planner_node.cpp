#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include "drone_coverage/boustrophedon_planner.hpp"
#include "drone_coverage/minimum_snap_trajectory.hpp"

using namespace drone_coverage;

class CoveragePlannerNode : public rclcpp::Node {
public:
  CoveragePlannerNode() : Node("coverage_planner") {
    path_pub_ = create_publisher<nav_msgs::msg::Path>("/coverage/path", 10);
    timer_ = create_wall_timer(
      std::chrono::seconds(5), [this]{ publish_demo_path(); });
    RCLCPP_INFO(get_logger(), "Coverage planner node ready.");
  }

private:
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr path_pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  void publish_demo_path() {
    BladeCloud cloud;
    for (int i = 0; i < 20; ++i)
      cloud.push_back(Eigen::Vector3d(i * 0.1, 0.0, 0.0));

    BoustrophedonPlanner planner;
    SensorParams sp;
    PlannerConfig cfg;
    auto poses = planner.plan(cloud, sp, cfg);

    nav_msgs::msg::Path path;
    path.header.frame_id = "world";
    path.header.stamp = now();
    for (const auto& bp : poses) {
      geometry_msgs::msg::PoseStamped ps;
      ps.header = path.header;
      ps.pose.position.x = bp.position.x();
      ps.pose.position.y = bp.position.y();
      ps.pose.position.z = bp.position.z();
      ps.pose.orientation.w = 1.0;
      path.poses.push_back(ps);
    }
    path_pub_->publish(path);
    RCLCPP_INFO(get_logger(), "Published coverage path: %zu waypoints", poses.size());
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CoveragePlannerNode>());
  rclcpp::shutdown();
  return 0;
}
