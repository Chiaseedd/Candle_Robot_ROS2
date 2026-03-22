import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_urdf_tutorial = get_package_share_directory('urdf_tutorial')

    # Enable Gazebo to find ROS packages at `package://` and `model://` URIs
    gazebo_model_path = os.path.join(get_package_share_directory('urdf_tutorial'), '..')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        gazebo_model_path += os.pathsep + os.environ['GAZEBO_MODEL_PATH']
    set_model_path = SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path)

    # Disable Gazebo from trying to download models from the internet, which causes long startup hangs
    disable_online_models = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')

    urdf_file = os.path.join(pkg_urdf_tutorial, 'urdf', 'feetech_tray.urdf.xacro')
    robot_description = {'robot_description': Command(['xacro ', urdf_file])}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')]),
        launch_arguments={
            'world': os.path.join(pkg_urdf_tutorial, 'world', 'apartment.world'),
            'extra_gazebo_args': '--verbose'
        }.items(),
    )

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')]),
        launch_arguments={'extra_gazebo_args': '--verbose'}.items(),
    )

    x_pose = LaunchConfiguration('x', default='0.0')
    y_pose = LaunchConfiguration('y', default='0.0')
    z_pose = LaunchConfiguration('z', default='0.1')
    yaw_pose = LaunchConfiguration('yaw', default='0.0')

    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'feetech',
                                   '-x', x_pose,
                                   '-y', y_pose,
                                   '-z', z_pose,
                                   '-Y', yaw_pose],
                        output='screen')

    spawn_sphere = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-file', os.path.join(get_package_share_directory('main_run'), 'urdf', 'green_sphere.urdf'),
                                   '-entity', 'green_sphere',
                                   '-x', '2.0',
                                   '-y', '0.0',
                                   '-z', '0.2'],
                        output='screen')

    spawn_delay = TimerAction(
        period=5.0,
        actions=[spawn_entity, spawn_sphere]
    )

    return LaunchDescription([
        set_model_path,
        gazebo_server,
        gazebo_client,
        node_robot_state_publisher,
        spawn_delay,
    ])
