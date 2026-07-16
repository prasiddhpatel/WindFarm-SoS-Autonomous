#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

class SlamManagerNode : public rclcpp::Node {
public:
  SlamManagerNode() : Node("slam_manager") {
    status_pub_ = create_publisher<std_msgs::msg::String>("/slam/status", 10);
    timer_ = create_wall_timer(std::chrono::seconds(2), [this] {
      std_msgs::msg::String msg;
      msg.data = "running";
      status_pub_->publish(msg);
    });
    RCLCPP_INFO(get_logger(), "SLAM manager node ready (placeholder).");
  }
private:
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SlamManagerNode>());
  rclcpp::shutdown();
  return 0;
}
