#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/path.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include "ground_robot_nav/skid_steer_mpc.hpp"

using namespace ground_robot_nav;

class MPCPlannerNode : public rclcpp::Node {
public:
  MPCPlannerNode() : Node("mpc_local_planner_node") {
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/ugv/odom", 10, [this](nav_msgs::msg::Odometry::SharedPtr m){ odom_=m; });
    path_sub_ = create_subscription<nav_msgs::msg::Path>(
      "/ugv/reference_path", 10, [this](nav_msgs::msg::Path::SharedPtr m){ path_=m; });
    cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>("/ugv/cmd_vel", 10);
    timer_ = create_wall_timer(std::chrono::milliseconds(100), [this](){ tick(); });
  }
private:
  SkidSteerMPC mpc_;
  nav_msgs::msg::Odometry::SharedPtr odom_;
  nav_msgs::msg::Path::SharedPtr path_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr path_sub_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  void tick() {
    if (!odom_ || !path_ || path_->poses.empty()) return;
    SkidSteerMPC::UnicycleState x0{odom_->pose.pose.position.x, odom_->pose.pose.position.y, 0.0};
    std::vector<SkidSteerMPC::UnicycleState> ref;
    for (auto &p : path_->poses) ref.push_back({p.pose.position.x, p.pose.position.y, 0.0});
    while (ref.size() < 15) ref.push_back(ref.back());
    auto u = mpc_.solve(x0, ref, {});
    geometry_msgs::msg::Twist cmd;
    cmd.linear.x = u.v;
    cmd.angular.z = u.omega;
    cmd_pub_->publish(cmd);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MPCPlannerNode>());
  rclcpp::shutdown();
  return 0;
}
