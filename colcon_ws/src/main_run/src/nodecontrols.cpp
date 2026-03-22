#include <cstdlib>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/empty.hpp"

using std::placeholders::_1;
using std::placeholders::_2;

class NodeController : public rclcpp::Node {
public:
  NodeController() : Node("nodecontroller") {
    service_ = this->create_service<std_srvs::srv::Empty>(
        "/shutdown",
        std::bind(&NodeController::shutdown_callback, this, _1, _2));
  }

private:
  void shutdown_callback(
      const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
      std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/) {
    RCLCPP_INFO(this->get_logger(), "Shutdown service called.");
    // TODO: In ROS2, node lifecycle management is preferred over killing
    // processes. Replace this system call with proper lifecycle transitions if
    // applicable. system("rosnode kill /controller_spawner");
  }

  rclcpp::Service<std_srvs::srv::Empty>::SharedPtr service_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NodeController>());
  rclcpp::shutdown();
  return 0;
}
