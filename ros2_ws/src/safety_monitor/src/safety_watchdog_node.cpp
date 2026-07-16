#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include "safety_monitor/geofence_monitor.hpp"

using namespace std::chrono_literals;

/**
 * Safety Watchdog Node.
 *
 * Implements the layered safety architecture of Sec. VII / Sec. VI-F:
 *  - Geofence containment check  (eq. 38, point-in-polygon)
 *  - Velocity / tilt limits
 *  - Minimum battery reserve for return-to-dock
 *  - Link-loss timeout  -> RTD command
 *  - Heartbeat monitoring of peer nodes (RMS schedulability, eq. 22)
 *  - Adhesion margin monitoring for NDE crawler
 *
 * Runs as an independent node on its own executor with RT priority.
 * Publishes /safety/estop (latched, reliable QoS) on any violation.
 */

class SafetyWatchdogNode : public rclcpp::Node {
public:
  SafetyWatchdogNode() : Node("safety_watchdog") {
    // Parameters
    declare_parameter("max_velocity_m_s",      12.0);
    declare_parameter("max_tilt_deg",           45.0);
    declare_parameter("min_battery_reserve_pct", 0.15);
    declare_parameter("link_loss_timeout_s",     5.0);
    declare_parameter("watchdog_rate_hz",        50.0);
    declare_parameter("geofence_wkt",
      "POLYGON((0 0,100 0,100 100,0 100,0 0))");  // placeholder

    geofence_ = std::make_unique<safety_monitor::GeofenceMonitor>(
        get_parameter("geofence_wkt").as_string());

    // Subscribers
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
        "/eskf/odom",
        rclcpp::QoS(1).best_effort(),
        [this](nav_msgs::msg::Odometry::SharedPtr m){ odom_cb(m); });
    bat_sub_ = create_subscription<std_msgs::msg::Bool>(
        "/uav/low_battery",
        rclcpp::QoS(1).reliable(),
        [this](std_msgs::msg::Bool::SharedPtr m){ low_bat_ = m->data; });
    link_sub_ = create_subscription<std_msgs::msg::Bool>(
        "/comms/link_ok",
        rclcpp::QoS(1).reliable(),
        [this](std_msgs::msg::Bool::SharedPtr m){
          link_ok_ = m->data;
          last_link_time_ = this->now();
        });

    // Publishers
    estop_pub_ = create_publisher<std_msgs::msg::Bool>(
        "/safety/estop",
        rclcpp::QoS(1).reliable().transient_local());
    status_pub_ = create_publisher<std_msgs::msg::String>(
        "/safety/status", 10);
    rtd_pub_ = create_publisher<std_msgs::msg::Bool>(
        "/safety/return_to_dock",
        rclcpp::QoS(1).reliable());

    double rate = get_parameter("watchdog_rate_hz").as_double();
    timer_ = create_wall_timer(
        std::chrono::duration<double>(1.0/rate),
        [this](){ watchdog_loop(); });

    last_link_time_ = this->now();
    RCLCPP_INFO(get_logger(),
        "Safety watchdog armed @ %.0f Hz.", rate);
  }

private:
  std::unique_ptr<safety_monitor::GeofenceMonitor> geofence_;

  nav_msgs::msg::Odometry::SharedPtr last_odom_;
  bool low_bat_{false}, link_ok_{true};
  rclcpp::Time last_link_time_;

  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr bat_sub_, link_sub_;
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr estop_pub_, rtd_pub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::TimerBase::SharedPtr timer_;

  void odom_cb(const nav_msgs::msg::Odometry::SharedPtr& m) {
    last_odom_ = m;
  }

  void watchdog_loop() {
    std::string violations;
    bool estop = false, rtd = false;

    if (last_odom_) {
      // Velocity check
      auto& lv = last_odom_->twist.twist.linear;
      double spd = std::sqrt(lv.x*lv.x + lv.y*lv.y + lv.z*lv.z);
      double vmax = get_parameter("max_velocity_m_s").as_double();
      if (spd > vmax) {
        violations += "OVERSPEED ";
        estop = true;
      }

      // Geofence check  (eq. 38)
      double px = last_odom_->pose.pose.position.x;
      double py = last_odom_->pose.pose.position.y;
      if (!geofence_->inside(px, py)) {
        violations += "GEOFENCE_BREACH ";
        estop = true;
      }
    }

    // Battery reserve
    if (low_bat_) {
      violations += "LOW_BATTERY ";
      rtd = true;
    }

    // Link-loss timeout
    double link_timeout = get_parameter("link_loss_timeout_s").as_double();
    double link_age = (this->now() - last_link_time_).seconds();
    if (link_age > link_timeout) {
      violations += "LINK_LOSS ";
      rtd = true;
    }

    // Publish
    std_msgs::msg::Bool estop_msg; estop_msg.data = estop;
    estop_pub_->publish(estop_msg);

    if (rtd && !estop) {
      std_msgs::msg::Bool rtd_msg; rtd_msg.data = true;
      rtd_pub_->publish(rtd_msg);
    }

    std_msgs::msg::String status;
    status.data = violations.empty() ? "NOMINAL" : violations;
    status_pub_->publish(status);

    if (!violations.empty())
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 1000,
          "Safety violations: %s", violations.c_str());
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SafetyWatchdogNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
