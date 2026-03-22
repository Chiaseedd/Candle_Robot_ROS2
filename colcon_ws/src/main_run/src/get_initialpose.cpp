#include <memory>
#include <string>

#include "cartographer_ros_msgs/srv/finish_trajectory.hpp"
#include "cartographer_ros_msgs/srv/start_trajectory.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "rclcpp/rclcpp.hpp"

using std::placeholders::_1;

class GetPoseNode : public rclcpp::Node {
public:
  GetPoseNode() : Node("getpose") {
    sub_ = this->create_subscription<
        geometry_msgs::msg::PoseWithCovarianceStamped>(
        "initialpose", 1000,
        std::bind(&GetPoseNode::poseAMCLCallback, this, _1));

    client_ = this->create_client<cartographer_ros_msgs::srv::StartTrajectory>(
        "start_trajectory");
    client2_ =
        this->create_client<cartographer_ros_msgs::srv::FinishTrajectory>(
            "finish_trajectory");
  }

private:
  void poseAMCLCallback(
      const geometry_msgs::msg::PoseWithCovarianceStamped::SharedPtr msgAMCL) {
    double poseAMCLx = msgAMCL->pose.pose.position.x;
    double poseAMCLy = msgAMCL->pose.pose.position.y;
    double poseAMCLa = msgAMCL->pose.pose.orientation.w;
    double poseAMCLz = msgAMCL->pose.pose.orientation.z;

    RCLCPP_INFO(this->get_logger(), "x: %f, y: %f, w: %f, z: %f", poseAMCLx,
                poseAMCLy, poseAMCLa, poseAMCLz);

    auto req2 = std::make_shared<
        cartographer_ros_msgs::srv::FinishTrajectory::Request>();
    req2->trajectory_id = state_;

    auto req = std::make_shared<
        cartographer_ros_msgs::srv::StartTrajectory::Request>();
    req->use_initial_pose = true;
    
    // Declare parameters if not already declared (best practice is doing it in the constructor, but doing it here as a quick fix)
    if (!this->has_parameter("configuration_directory")) {
        this->declare_parameter<std::string>("configuration_directory", "/opt/ros/humble/share/cartographer_ros/configuration_files");
    }
    if (!this->has_parameter("configuration_basename")) {
        this->declare_parameter<std::string>("configuration_basename", "backpack_2d_localization.lua");
    }

    req->configuration_directory = this->get_parameter("configuration_directory").as_string();
    req->configuration_basename = this->get_parameter("configuration_basename").as_string();
    req->initial_pose.position = msgAMCL->pose.pose.position;
    req->initial_pose.orientation = msgAMCL->pose.pose.orientation;
    req->relative_to_trajectory_id = 0;

    // Call service 2 (finish)
    if (client2_->wait_for_service(std::chrono::seconds(1))) {
      auto result2 = client2_->async_send_request(req2);
      // Let it process in the background
      RCLCPP_INFO(this->get_logger(), "Sent call 1 (finish_trajectory)!!");
    } else {
      RCLCPP_ERROR(this->get_logger(),
                   "Failed to call service finish_trajectory");
    }

    // Call service 1 (start)
    if (client_->wait_for_service(std::chrono::seconds(1))) {
      auto result = client_->async_send_request(req);
      state_++;
      RCLCPP_INFO(this->get_logger(), "Sent call 2 (start_trajectory)!!!");
    } else {
      RCLCPP_ERROR(this->get_logger(),
                   "Failed to call service start_trajectory");
    }
  }

  rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr
      sub_;
  rclcpp::Client<cartographer_ros_msgs::srv::StartTrajectory>::SharedPtr
      client_;
  rclcpp::Client<cartographer_ros_msgs::srv::FinishTrajectory>::SharedPtr
      client2_;

  int state_ = 0;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<GetPoseNode>());
  rclcpp::shutdown();
  return 0;
}
