#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include "drone_estimation/eskf.hpp"

using drone_estimation::ESKF;
using drone_estimation::ImuMeasurement;

class ESKFNode : public rclcpp::Node {
public:
  ESKFNode() : Node("eskf_node") {
    imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
      "/imu/data", rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::Imu::SharedPtr msg) {
        ImuMeasurement z;
        z.t   = msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9;
        z.am  = {msg->linear_acceleration.x,
                 msg->linear_acceleration.y,
                 msg->linear_acceleration.z};
        z.wm  = {msg->angular_velocity.x,
                 msg->angular_velocity.y,
                 msg->angular_velocity.z};
        eskf_.propagate(z);
        publish_odom();
      });
    odom_pub_ = create_publisher<nav_msgs::msg::Odometry>("/eskf/odom", 10);
    RCLCPP_INFO(get_logger(), "ESKF node ready.");
  }

private:
  ESKF eskf_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;

  void publish_odom() {
    const auto& s = eskf_.state();
    nav_msgs::msg::Odometry msg;
    msg.header.stamp = now();
    msg.header.frame_id = "odom";
    msg.pose.pose.position.x = s.p.x();
    msg.pose.pose.position.y = s.p.y();
    msg.pose.pose.position.z = s.p.z();
    msg.twist.twist.linear.x = s.v.x();
    msg.twist.twist.linear.y = s.v.y();
    msg.twist.twist.linear.z = s.v.z();
    odom_pub_->publish(msg);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ESKFNode>());
  rclcpp::shutdown();
  return 0;
}
