#include <rclcpp/rclcpp.hpp>
#include <sos_interfaces/action/crawl_to_target.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

class CrawlerController : public rclcpp::Node {
public:
  using CrawlToTarget = sos_interfaces::action::CrawlToTarget;
  explicit CrawlerController() : Node("crawler_controller") {
    RCLCPP_INFO(get_logger(), "Crawler controller ready.");
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<CrawlerController>());
  rclcpp::shutdown();
  return 0;
}
