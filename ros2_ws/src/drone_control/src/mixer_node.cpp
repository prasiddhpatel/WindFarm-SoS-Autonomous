#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>

class MixerNode : public rclcpp::Node {
public:
  MixerNode() : Node("mixer_node") {
    sub_ = create_subscription<std_msgs::msg::Float64MultiArray>(
      "/cmd/motor_speeds", 10,
      [this](std_msgs::msg::Float64MultiArray::SharedPtr msg) {
        for (size_t i = 0; i < msg->data.size(); ++i)
          RCLCPP_DEBUG(get_logger(), "motor[%zu] = %.2f rad/s", i, msg->data[i]);
      });
    RCLCPP_INFO(get_logger(), "Mixer node ready.");
  }
private:
  rclcpp::Subscription<std_msgs::msg::Float64MultiArray>::SharedPtr sub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MixerNode>());
  rclcpp::shutdown();
  return 0;
}
