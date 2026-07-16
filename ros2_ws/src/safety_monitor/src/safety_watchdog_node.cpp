#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/string.hpp>

class SafetyWatchdogNode : public rclcpp::Node {
public:
  SafetyWatchdogNode() : Node("safety_watchdog_node") {
    status_pub_ = create_publisher<std_msgs::msg::String>("/safety/status", 10);
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/vehicle/odom", 10, [this](nav_msgs::msg::Odometry::SharedPtr msg) {
        std_msgs::msg::String s;
        s.data = (msg->twist.twist.linear.x > 20.0) ? "overspeed" : "ok";
        status_pub_->publish(s);
      });
    RCLCPP_INFO(get_logger(), "Safety watchdog ready.");
  }
private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SafetyWatchdogNode>());
  rclcpp::shutdown();
  return 0;
}
