#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include "ground_robot_nav/skid_steer_mpc.hpp"

using namespace ground_robot_nav;

class MpcLocalPlannerNode : public rclcpp::Node {
public:
  MpcLocalPlannerNode() : Node("mpc_local_planner") {
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/ugv/odom", 10,
      [this](nav_msgs::msg::Odometry::SharedPtr msg) {
        UnicycleState x;
        x.x   = msg->pose.pose.position.x;
        x.y   = msg->pose.pose.position.y;
        x.psi = 0.0;  // yaw extraction from quaternion omitted for brevity
        UnicycleState goal{5.0, 5.0, 0.0};
        auto u = mpc_.solve(x, {goal});
        geometry_msgs::msg::Twist cmd;
        cmd.linear.x  = u.v;
        cmd.angular.z = u.omega;
        cmd_pub_->publish(cmd);
      });
    cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>("/ugv/cmd_vel", 10);
    RCLCPP_INFO(get_logger(), "MPC local planner node ready.");
  }
private:
  SkidSteerMPC mpc_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MpcLocalPlannerNode>());
  rclcpp::shutdown();
  return 0;
}
