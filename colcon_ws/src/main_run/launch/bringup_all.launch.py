import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    main_run_dir = get_package_share_directory('main_run')
    urdf_tutorial_dir = get_package_share_directory('urdf_tutorial')
    
    # 1. Gazebo Simulation with Robot
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(urdf_tutorial_dir, 'launch', 'gazebo.launch.py')
        )
    )

    # The green sphere is already spawned natively inside gazebo.launch.py

    # 3. Navigation 2 Data Stack
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(main_run_dir, 'launch', 'navigation.launch.py')
        )
    )

    # 4. (Removed autonomous tracker scripts)

    return LaunchDescription([
        # GPU acceleration for Gazebo on WSL (prevents software-renderer freeze)
        SetEnvironmentVariable('MESA_D3D12_DEFAULT_ADAPTER_NAME', 'NVIDIA'),
        SetEnvironmentVariable('MESA_GL_VERSION_OVERRIDE', '3.3'),
        # Fix RViz2 GLSL shader compilation failure on WSL Mesa drivers
        SetEnvironmentVariable('OGRE_RTT_MODE', 'Copy'),
        SetEnvironmentVariable('MESA_GLSL_VERSION_OVERRIDE', '130'),
        # Ensure Gazebo finds meshes
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.join(urdf_tutorial_dir, 'models')),
        
        gazebo_launch,
        TimerAction(period=15.0, actions=[nav2_launch]),
    ])
