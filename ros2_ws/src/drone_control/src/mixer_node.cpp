#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <sensor_msgs/msg/joint_state.hpp>

using namespace std::chrono_literals;

class MixerNode : public rclcpp::Node {
public:
  MixerNode() : Node("mixer_node") {
    sub_ = create_subscription<std_msgs::msg::Float64MultiArray>(
      "/cmd/motor_speeds", 10,
      [this](std_msgs::msg::Float64MultiArray::SharedPtr msg) {
        sensor_msgs::msg::JointState js;
        js.header.stamp = this->now();
        js.name = {"motor_1_joint", "motor_2_joint", "motor_3_joint", "motor_4_joint"};
        js.velocity = msg->data;
        pub_->publish(js);
      });
    pub_ = create_publisher<sensor_msgs::msg::JointState>("/actuator/joint_speeds", 10);
    RCLCPP_INFO(get_logger(), "Mixer node ready.");
  }
private:
  rclcpp::Subscription<std_msgs::msg::Float64MultiArray>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr pub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<MixerNode>());
  rclcpp::shutdown();
  return 0;
}
