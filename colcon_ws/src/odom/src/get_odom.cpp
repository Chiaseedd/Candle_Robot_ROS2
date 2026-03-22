#include <memory>
#include <string>

#include "dynamixel_workbench_msgs/msg/dynamixel_state_list.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "tf2_ros/transform_broadcaster.h"

using std::placeholders::_1;

class GetOdomNode : public rclcpp::Node {
public:
  GetOdomNode() : Node("get_odom_node") {
    pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 10);
    sub_ = this->create_subscription<
        dynamixel_workbench_msgs::msg::DynamixelStateList>(
        "dynamixel_workbench/dynamixel_state", 100,
        std::bind(&GetOdomNode::chatterCallback, this, _1));
    odom_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

    current_time_ = this->now();
    last_time_ = this->now();

    timer_ = this->create_wall_timer(std::chrono::milliseconds(100),
                                     std::bind(&GetOdomNode::odomupdate, this));
  }

private:
  void chatterCallback(
      const dynamixel_workbench_msgs::msg::DynamixelStateList::SharedPtr vel) {
    if (vel->dynamixel_state.size() < 2)
      return;

    double Leftrpm = vel->dynamixel_state[0].present_velocity;
    if (Leftrpm > 1023)
      Leftrpm = -1 * (Leftrpm - 1023);
    double rightrpm = -vel->dynamixel_state[1].present_velocity;
    if (rightrpm < -1023)
      rightrpm = -1 * (rightrpm + 1023);

    Leftw = Leftrpm * 0.11443 * 0.10471975511;
    Rightw = rightrpm * 0.11443 * 0.10471975511;
  }

  void odomupdate() {
    double v = 0.033 * ((Rightw + Leftw) / 2.0);
    vx_new = v;

    double vth = 0.033 * ((Rightw - Leftw) / 0.310);
    th_new = vth;

    current_time_ = this->now();
    double dt = (current_time_ - last_time_).seconds();

    if (dt > 0.0) {
      if (vx_new > vx_old) {
        accel_x = (vx_new - vx_old) / dt;
      }
      vx_old = vx_new;

      accel_th = (th_new - th_old) / dt;
      th_old = th_new;
    }

    double delta_x = (v * cos(th_)) * dt;
    double delta_y = (v * sin(th_)) * dt;
    double delta_th = vth * dt;

    x_ += delta_x;
    y_ += delta_y;
    th_ += delta_th;

    tf2::Quaternion q;
    q.setRPY(0, 0, th_);

    geometry_msgs::msg::TransformStamped odom_trans;
    odom_trans.header.stamp = current_time_;
    odom_trans.header.frame_id = "odom";
    odom_trans.child_frame_id = "base_link";

    odom_trans.transform.translation.x = x_;
    odom_trans.transform.translation.y = y_;
    odom_trans.transform.translation.z = 0.0;
    odom_trans.transform.rotation.x = q.x();
    odom_trans.transform.rotation.y = q.y();
    odom_trans.transform.rotation.z = q.z();
    odom_trans.transform.rotation.w = q.w();

    odom_broadcaster_->sendTransform(odom_trans);

    nav_msgs::msg::Odometry odom;
    odom.header.stamp = current_time_;
    odom.header.frame_id = "odom";

    odom.pose.pose.position.x = x_;
    odom.pose.pose.position.y = y_;
    odom.pose.pose.position.z = 0.0;
    odom.pose.pose.orientation.x = q.x();
    odom.pose.pose.orientation.y = q.y();
    odom.pose.pose.orientation.z = q.z();
    odom.pose.pose.orientation.w = q.w();

    odom.child_frame_id = "base_link";
    odom.twist.twist.linear.x = v * cos(th_);
    odom.twist.twist.linear.y = v * sin(th_);
    odom.twist.twist.angular.z = vth;

    pub_->publish(odom);
    last_time_ = current_time_;
  }

  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr pub_;
  rclcpp::Subscription<
      dynamixel_workbench_msgs::msg::DynamixelStateList>::SharedPtr sub_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> odom_broadcaster_;
  rclcpp::TimerBase::SharedPtr timer_;

  rclcpp::Time current_time_;
  rclcpp::Time last_time_;

  double x_ = 0.0;
  double y_ = 0.0;
  double th_ = 0.0;

  double accel_x = 0.0;
  double vx_old = 0.0;
  double vx_new = 0.0;
  double accel_th = 0.0;
  double th_old = 0.0;
  double th_new = 0.0;

  double Leftw = 0.0;
  double Rightw = 0.0;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<GetOdomNode>();

  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  executor.spin();

  rclcpp::shutdown();
  return 0;
}
