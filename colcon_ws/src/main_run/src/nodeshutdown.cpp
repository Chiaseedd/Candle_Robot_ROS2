#include <cstdlib>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/empty.hpp"

using std::placeholders::_1;
using std::placeholders::_2;

class NodeShutdown : public rclcpp::Node {
public:
  NodeShutdown()
      : Node("nodeshutdown") // Changed from "nodecontroller" to avoid name
                             // conflict
  {
    service_ = this->create_service<std_srvs::srv::Empty>(
        "/shutdown_hardware",
        std::bind(&NodeShutdown::shutdown_callback, this, _1, _2));
  }

private:
  void shutdown_callback(
      const std::shared_ptr<std_srvs::srv::Empty::Request> /*req*/,
      std::shared_ptr<std_srvs::srv::Empty::Response> /*res*/) {
    RCLCPP_INFO(this->get_logger(), "Shutdown hardware service called.");
    // TODO: Migrate to ROS2 lifecycle transitions.
    // system("rosnode kill /ROBOT_hardware_interface_node");
    // system("rosnode kill /controller_spawner");
  }

  rclcpp::Service<std_srvs::srv::Empty>::SharedPtr service_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NodeShutdown>());
  rclcpp::shutdown();
  return 0;
}
