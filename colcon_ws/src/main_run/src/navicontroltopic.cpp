#include <memory>
#include <string>

#include "action_msgs/msg/goal_status_array.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/bool.hpp"
// TODO: Replace these with actual ROS2 equivalents if available
// #include "feetech_controls/msg/headcontrols.hpp"

using std::placeholders::_1;

// Placeholder structure since custom msg may need porting
struct HeadControls {
  double headjointvalues1;
  double headjointvalues2;
  int arucoid;
  int type;
};

class NavicontrolTopicNode : public rclcpp::Node {
public:
  NavicontrolTopicNode() : Node("navicontroltopic") {
    // sub_ = this->create_subscription<feetech_controls::msg::Headcontrols>(
    //   "/aruco/getid", 1, std::bind(&NavicontrolTopicNode::getidcallback,
    //   this, _1));

    // Subscribe to Nav2 action status instead of move_base/result
    sub2_ = this->create_subscription<action_msgs::msg::GoalStatusArray>(
        "/navigate_to_pose/_action/status", 1,
        std::bind(&NavicontrolTopicNode::repubarucocheck, this, _1));

    sub3_ = this->create_subscription<std_msgs::msg::Bool>(
        "/setrepubaruco", 1,
        std::bind(&NavicontrolTopicNode::setrecheckaruco, this, _1));

    // pub_ =
    // this->create_publisher<feetech_controls::msg::Headcontrols>("/aruco/getid",
    // 10);
    pub2_ = this->create_publisher<std_msgs::msg::Bool>("/navicond", 10);
  }

private:
  void setrecheckaruco(const std_msgs::msg::Bool::SharedPtr msg) {
    condreplan_ = msg->data;
  }

  // void getidcallback(const feetech_controls::msg::Headcontrols::SharedPtr
  // msg)
  // {
  //   arucofind_.headjointvalues1 = msg->headjointvalues1;
  //   arucofind_.headjointvalues2 = msg->headjointvalues2;
  //   arucofind_.arucoid = msg->arucoid;
  //   arucofind_.type = msg->type;
  // }

  void repubarucocheck(const action_msgs::msg::GoalStatusArray::SharedPtr msg) {
    if (msg->status_list.empty())
      return;

    // 4 is SUCCEEDED in action_msgs::msg::GoalStatus
    int status = msg->status_list.back().status;

    std_msgs::msg::Bool pub2con;

    if (!condreplan_) {
      if (status == 4) {
        pub2con.data = true;
        pub2_->publish(pub2con);
      } else {
        pub2con.data = false;
        pub2_->publish(pub2con);
      }
    } else {
      if (status == 4) {
        // pub_->publish(arucofind_);
        condreplan_ = false;
      } else {
        pub2con.data = false;
        pub2_->publish(pub2con);
      }
    }
  }

  // rclcpp::Subscription<feetech_controls::msg::Headcontrols>::SharedPtr sub_;
  rclcpp::Subscription<action_msgs::msg::GoalStatusArray>::SharedPtr sub2_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub3_;

  // rclcpp::Publisher<feetech_controls::msg::Headcontrols>::SharedPtr pub_;
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr pub2_;

  bool condreplan_ = false;
  HeadControls arucofind_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<NavicontrolTopicNode>());
  rclcpp::shutdown();
  return 0;
}
