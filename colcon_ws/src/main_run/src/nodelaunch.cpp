#include <cstdlib>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/empty.hpp"

using std::placeholders::_1;

class NodeLaunch : public rclcpp::Node {
public:
  NodeLaunch() : Node("nodelaunch") {
    sub_ = this->create_subscription<std_msgs::msg::Empty>(
        "/launch", 1, std::bind(&NodeLaunch::launch_callback, this, _1));

    timer_ = this->create_wall_timer(std::chrono::milliseconds(100),
                                     std::bind(&NodeLaunch::launchloop, this));
  }

private:
  void launch_callback(const std_msgs::msg::Empty::SharedPtr /*msg*/) {
    recdata_ = true;
  }

  void launchloop() {
    if (recdata_) {
      recdata_ = false;
      RCLCPP_INFO(this->get_logger(), "Launch trigger received.");

      // TODO: In ROS2, node lifecycle or component containers are preferred.
      // Replace with ROS 2 launch system call if required.
      // std::system("ros2 launch feetech_controls
      // feetech_control_interface.launch.py");
    }
  }

  rclcpp::Subscription<std_msgs::msg::Empty>::SharedPtr sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  bool recdata_ = false;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NodeLaunch>());
  rclcpp::shutdown();
  return 0;
}
