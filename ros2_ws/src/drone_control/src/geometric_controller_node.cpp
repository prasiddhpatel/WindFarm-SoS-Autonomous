#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include "drone_control/control_allocator.hpp"

using namespace std::chrono_literals;
using namespace drone_control;

class GeometricControllerNode : public rclcpp::Node {
public:
  GeometricControllerNode()
  : Node("geometric_controller"),
    allocator_(8.54858e-6, 1.6e-7, 0.275, 100.0, 1200.0)
  {
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/eskf/odom", rclcpp::SensorDataQoS(),
      [this](nav_msgs::msg::Odometry::SharedPtr m){ odom_ = m; });
    cmd_pub_ = create_publisher<std_msgs::msg::Float64MultiArray>("/cmd/motor_speeds", 10);
    timer_ = create_wall_timer(5ms, [this](){ tick(); });
    RCLCPP_INFO(get_logger(), "Geometric controller ready.");
  }

private:
  ControlAllocator allocator_;
  nav_msgs::msg::Odometry::SharedPtr odom_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr cmd_pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  void tick() {
    const double thrust = 9.81 * 3.5;   // hover feedforward
    Eigen::Vector3d torque = Eigen::Vector3d::Zero();
    auto out = allocator_.allocate(thrust, torque);
    std_msgs::msg::Float64MultiArray msg;
    msg.data.assign(out.omega.begin(), out.omega.end());
    cmd_pub_->publish(msg);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GeometricControllerNode>());
  rclcpp::shutdown();
  return 0;
}
