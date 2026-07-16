#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include "drone_coverage/boustrophedon_planner.hpp"

using namespace drone_coverage;

class CoveragePlannerNode : public rclcpp::Node {
public:
  CoveragePlannerNode() : Node("coverage_planner_node") {
    pub_ = create_publisher<geometry_msgs::msg::PoseArray>("/coverage/waypoints", 10);
    timer_ = create_wall_timer(std::chrono::seconds(5), [this]() { publish_demo_plan(); });
    RCLCPP_INFO(get_logger(), "Coverage planner node ready.");
  }
private:
  rclcpp::Publisher<geometry_msgs::msg::PoseArray>::SharedPtr pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  void publish_demo_plan() {
    BladeCloud cloud;
    for (int i = 0; i < 100; ++i) cloud.push_back(Eigen::Vector3d(0.01*i, 0.0, 0.0));
    SensorParams sp;
    PlannerConfig cfg;
    BoustrophedonPlanner planner;
    auto plan = planner.plan(cloud, sp, cfg);

    geometry_msgs::msg::PoseArray arr;
    arr.header.stamp = now();
    arr.header.frame_id = "blade_frame";
    for (auto &wp : plan) {
      geometry_msgs::msg::Pose p;
      p.position.x = wp.position.x();
      p.position.y = wp.position.y();
      p.position.z = wp.position.z();
      p.orientation.w = 1.0;
      arr.poses.push_back(p);
    }
    pub_->publish(arr);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CoveragePlannerNode>());
  rclcpp::shutdown();
  return 0;
}
