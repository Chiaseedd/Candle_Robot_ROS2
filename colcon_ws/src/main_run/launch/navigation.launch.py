import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    main_run_dir = get_package_share_directory('main_run')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    map_yaml_file = os.path.join(main_run_dir, 'maps', 'map.yaml')
    params_file = os.path.join(main_run_dir, 'config', 'nav2_params.yaml')

    # Static transform: map -> odom (identity – robot starts at origin in Gazebo)
    # This replaces the dynamic AMCL-broadcasted transform entirely.
    static_map_odom_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_map_odom_tf_publisher',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )

    # Standalone map_server – publishes the occupancy grid (/map) for the global costmap
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': map_yaml_file,
        }]
    )

    # Lifecycle manager just for map_server (autostart=True activates it immediately)
    map_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server'],
        }]
    )

    # Nav2 navigation stack only (planner + controller + BT – no AMCL/localization)
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': 'true',
        }.items(),
    )

    rviz_config_file = os.path.join(main_run_dir, 'rviz', 'custom_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        # These two start immediately so the map frame + map data are available
        # before Nav2's global costmap tries to read them.
        static_map_odom_tf,
        map_server_node,
        map_lifecycle_manager,
        # Give Gazebo ~10 s to fully spawn the robot before Nav2 activates
        TimerAction(
            period=10.0,
            actions=[navigation_launch, rviz_node]
        ),
    ])
