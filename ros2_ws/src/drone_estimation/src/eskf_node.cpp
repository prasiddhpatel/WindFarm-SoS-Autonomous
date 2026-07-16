#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include "drone_estimation/eskf.hpp"

using namespace drone_estimation;

class ESKFNode : public rclcpp::Node {
public:
  ESKFNode() : Node("eskf_node") {
    imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
      "/imu/data", rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::Imu::SharedPtr msg){ imu_cb(msg); });
    gnss_sub_ = create_subscription<geometry_msgs::msg::PoseStamped>(
      "/gnss/rtk_pose", 10,
      [this](geometry_msgs::msg::PoseStamped::SharedPtr msg){ gnss_cb(msg); });
    odom_pub_ = create_publisher<nav_msgs::msg::Odometry>("/eskf/odom", 50);
    RCLCPP_INFO(get_logger(), "ESKF node ready.");
  }
private:
  ESKF eskf_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr gnss_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;

  void imu_cb(const sensor_msgs::msg::Imu::SharedPtr& msg) {
    ImuMeasurement z;
    z.t = rclcpp::Time(msg->header.stamp).seconds();
    z.am = {msg->linear_acceleration.x, msg->linear_acceleration.y, msg->linear_acceleration.z};
    z.wm = {msg->angular_velocity.x, msg->angular_velocity.y, msg->angular_velocity.z};
    eskf_.propagate(z);
    publish_odom(msg->header.stamp);
  }

  void gnss_cb(const geometry_msgs::msg::PoseStamped::SharedPtr& msg) {
    GnssMeasurement z;
    z.t = rclcpp::Time(msg->header.stamp).seconds();
    z.pos_ecef = {msg->pose.position.x, msg->pose.position.y, msg->pose.position.z};
    z.R_pos = Eigen::Matrix3d::Identity() * 0.01;
    z.rtk_fix = true;
    eskf_.update_gnss(z);
  }

  void publish_odom(const builtin_interfaces::msg::Time& stamp) {
    auto s = eskf_.state();
    nav_msgs::msg::Odometry odom;
    odom.header.stamp = stamp;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_link";
    odom.pose.pose.position.x = s.p.x();
    odom.pose.pose.position.y = s.p.y();
    odom.pose.pose.position.z = s.p.z();
    Eigen::Quaterniond q(s.R);
    odom.pose.pose.orientation.x = q.x();
    odom.pose.pose.orientation.y = q.y();
    odom.pose.pose.orientation.z = q.z();
    odom.pose.pose.orientation.w = q.w();
    odom.twist.twist.linear.x = s.v.x();
    odom.twist.twist.linear.y = s.v.y();
    odom.twist.twist.linear.z = s.v.z();
    odom_pub_->publish(odom);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ESKFNode>());
  rclcpp::shutdown();
  return 0;
}
