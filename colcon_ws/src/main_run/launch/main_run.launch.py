import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    rplidar_config = os.path.join(
        get_package_share_directory('main_run'),
        'config',
        'rplidar.yaml'
    )

    rplidar_launch = Node(
        package='rplidar_ros',
        executable='rplidar_node',
        name='rplidar_node',
        parameters=[rplidar_config],
        output='screen'
    )
    
    odom_node = Node(
        package='odom',
        executable='get_odom',
        name='odom',
        output='screen'
    )
    
    # In ROS 2, dynamixel_workbench_controllers has not been officially ported by ROBOTIS.
    # We must comment this out, the user will need to use a ros2_control dynamixel plugin instead.
    # dynamixel_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('dynamixel_workbench_controllers'), 'launch', 'dynamixel_controllers.launch.py')])
    # )
    
    laser_filter_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('laser_filters'), 'examples', 'box_filter_example.launch.py')])
    )

    return LaunchDescription([
        rplidar_launch,
        odom_node,
        # dynamixel_launch,
        laser_filter_launch
    ])
