cmake_minimum_required(VERSION 3.8)
project(main_run)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(cartographer_ros_msgs REQUIRED)
# find_package(feetech_controls REQUIRED)

# Executables
add_executable(navicontroltopic src/navicontroltopic.cpp)
ament_target_dependencies(navicontroltopic rclcpp std_msgs geometry_msgs action_msgs)

add_executable(nodelaunch src/nodelaunch.cpp)
ament_target_dependencies(nodelaunch rclcpp std_msgs)

add_executable(nodeshutdown src/nodeshutdown.cpp)
ament_target_dependencies(nodeshutdown rclcpp std_srvs)

add_executable(nodecontrols src/nodecontrols.cpp)
ament_target_dependencies(nodecontrols rclcpp std_srvs)

add_executable(get_initialpose src/get_initialpose.cpp)
ament_target_dependencies(get_initialpose rclcpp geometry_msgs cartographer_ros_msgs)

# Install
install(TARGETS
  navicontroltopic
  nodelaunch
  nodeshutdown
  nodecontrols
  get_initialpose
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/obstacle_avoidance.py
  scripts/sphere_wanderer.py
  scripts/mobile_goal_tracker.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch config maps param scripts urdf rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
