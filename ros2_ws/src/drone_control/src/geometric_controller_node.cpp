#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include "drone_control/se3_controller.hpp"
#include "drone_control/control_allocator.hpp"
#include <tf2_eigen/tf2_eigen.hpp>

using namespace drone_control;
using namespace std::chrono_literals;

class GeometricControllerNode : public rclcpp::Node {
public:
  GeometricControllerNode() : Node("geometric_controller") {
    // Parameters
    declare_parameter("mass_kg", 3.5);
    declare_parameter("ixx", 0.082); declare_parameter("iyy", 0.082);
    declare_parameter("izz", 0.149);
    declare_parameter("arm_length_m", 0.275);
    declare_parameter("kf", 8.54858e-6); declare_parameter("km", 1.6e-7);
    declare_parameter("omega_min_rad_s", 100.0);
    declare_parameter("omega_max_rad_s", 1200.0);
    declare_parameter("control_rate_hz", 200.0);

    double m   = get_parameter("mass_kg").as_double();
    double ixx = get_parameter("ixx").as_double();
    double iyy = get_parameter("iyy").as_double();
    double izz = get_parameter("izz").as_double();
    Eigen::Matrix3d J = Eigen::Vector3d(ixx,iyy,izz).asDiagonal();

    controller_ = std::make_unique<SE3Controller>(m, J);
    allocator_  = std::make_unique<ControlAllocator>(
        get_parameter("kf").as_double(),
        get_parameter("km").as_double(),
        get_parameter("arm_length_m").as_double(),
        get_parameter("omega_min_rad_s").as_double(),
        get_parameter("omega_max_rad_s").as_double());

    // Subscribers
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
        "/eskf/odom", rclcpp::SensorDataQoS(),
        [this](nav_msgs::msg::Odometry::SharedPtr msg){ odom_cb(msg); });
    ref_sub_ = create_subscription<nav_msgs::msg::Odometry>(
        "/drone/reference", 10,
        [this](nav_msgs::msg::Odometry::SharedPtr msg){ ref_cb(msg); });

    // Publishers
    cmd_pub_ = create_publisher<std_msgs::msg::Float64MultiArray>(
        "/cmd/motor_speeds", rclcpp::QoS(1).best_effort());
    wrench_pub_ = create_publisher<geometry_msgs::msg::WrenchStamped>(
        "/cmd/wrench", 10);

    double rate = get_parameter("control_rate_hz").as_double();
    timer_ = create_wall_timer(
        std::chrono::duration<double>(1.0/rate),
        [this](){ control_loop(); });

    RCLCPP_INFO(get_logger(), "SE(3) geometric controller ready @ %.0f Hz", rate);
  }

private:
  std::unique_ptr<SE3Controller>    controller_;
  std::unique_ptr<ControlAllocator> allocator_;

  SE3Controller::State     state_{};
  SE3Controller::Reference ref_{};
  bool state_valid_{false}, ref_valid_{false};

  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_, ref_sub_;
  rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr cmd_pub_;
  rclcpp::Publisher<geometry_msgs::msg::WrenchStamped>::SharedPtr wrench_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Time last_t_;

  void odom_cb(const nav_msgs::msg::Odometry::SharedPtr& msg) {
    state_.p = {msg->pose.pose.position.x,
                msg->pose.pose.position.y,
                msg->pose.pose.position.z};
    state_.v = {msg->twist.twist.linear.x,
                msg->twist.twist.linear.y,
                msg->twist.twist.linear.z};
    Eigen::Quaterniond q;
    tf2::fromMsg(msg->pose.pose.orientation, q);
    state_.R = q.toRotationMatrix();
    state_.omega = {msg->twist.twist.angular.x,
                    msg->twist.twist.angular.y,
                    msg->twist.twist.angular.z};
    state_valid_ = true;
  }

  void ref_cb(const nav_msgs::msg::Odometry::SharedPtr& msg) {
    ref_.pd = {msg->pose.pose.position.x,
               msg->pose.pose.position.y,
               msg->pose.pose.position.z};
    ref_.vd = {msg->twist.twist.linear.x,
               msg->twist.twist.linear.y,
               msg->twist.twist.linear.z};
    Eigen::Quaterniond q;
    tf2::fromMsg(msg->pose.pose.orientation, q);
    auto euler = q.toRotationMatrix().eulerAngles(2,1,0);
    ref_.yaw_d = euler(0);
    ref_valid_ = true;
  }

  void control_loop() {
    if (!state_valid_ || !ref_valid_) return;
    auto now = this->now();
    double dt = (last_t_.nanoseconds() == 0) ? 0.005
                : (now - last_t_).seconds();
    last_t_ = now;
    dt = std::clamp(dt, 0.001, 0.05);

    auto out = controller_->compute(state_, ref_, dt);
    auto alloc = allocator_->allocate(out.thrust, out.torque);

    std_msgs::msg::Float64MultiArray cmd;
    cmd.data = {alloc.omega[0], alloc.omega[1],
                alloc.omega[2], alloc.omega[3]};
    cmd_pub_->publish(cmd);

    geometry_msgs::msg::WrenchStamped w;
    w.header.stamp = now;
    w.wrench.force.z  = out.thrust;
    w.wrench.torque.x = out.torque.x();
    w.wrench.torque.y = out.torque.y();
    w.wrench.torque.z = out.torque.z();
    wrench_pub_->publish(w);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GeometricControllerNode>());
  rclcpp::shutdown();
  return 0;
}
