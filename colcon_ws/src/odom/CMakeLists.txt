cmake_minimum_required(VERSION 3.8)
project(odom)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2 REQUIRED)
find_package(dynamixel_workbench_msgs REQUIRED)

add_executable(odom_c src/odom_c.cpp)
ament_target_dependencies(odom_c
  rclcpp
  nav_msgs
  geometry_msgs
  tf2_ros
  tf2
  dynamixel_workbench_msgs
)

add_executable(get_odom src/get_odom.cpp)
ament_target_dependencies(get_odom
  rclcpp
  nav_msgs
  geometry_msgs
  tf2_ros
  tf2
  dynamixel_workbench_msgs
)

install(TARGETS
  odom_c
  get_odom
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
