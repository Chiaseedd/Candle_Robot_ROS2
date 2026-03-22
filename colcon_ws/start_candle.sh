#!/bin/bash
# Candle Robot - Complete Bringup Script
# This uses Windows Terminal (wt.exe) to seamlessly open 4 configured WSL tabs.
# It automatically sets up the environment to force Gazebo and RViz entirely onto your NVIDIA 4060.

# Base setup for every tab (Forcing the RTX 4060)
SETUP_CMD="source /opt/ros/humble/setup.bash && source install/setup.bash && export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA"

echo "Launching the Candle Robot Environment in Windows Terminal..."
echo "Please wait while the tabs load up sequentially..."

# Note: Terminal 1 uses GL=3.3 per instructions, but Terminal 2 uses GL=4.1 to prevent RViz Map crashes
wt.exe -w 0 nt --title "Gazebo" wsl -- bash -c "killall -9 gzserver gzclient rviz2 2>/dev/null; $SETUP_CMD && export MESA_GL_VERSION_OVERRIDE=3.3 && echo 'Starting Gazebo...' && ros2 launch urdf_tutorial gazebo.launch.py; exec bash" \
    \; nt --title "Navigation" wsl -- bash -c "$SETUP_CMD && export MESA_GL_VERSION_OVERRIDE=4.1 && echo 'Waiting 15s for Gazebo to load...' && sleep 15 && clear && ros2 launch main_run navigation.launch.py; exec bash" \
    \; nt --title "SphereWanderer" wsl -- bash -c "$SETUP_CMD && echo 'Waiting 20s for Navigation to load...' && sleep 20 && clear && echo 'Press s to toggle stop/resume, Ctrl-C to quit' && ros2 run main_run sphere_wanderer.py; exec bash" \
    \; nt --title "RobotTracker" wsl -- bash -c "$SETUP_CMD && echo 'Waiting 20s for Navigation to load...' && sleep 20 && clear && echo 'Press h to toggle return home' && ros2 run main_run mobile_goal_tracker.py; exec bash"

echo "Done! Look at your new Windows Terminal window."
