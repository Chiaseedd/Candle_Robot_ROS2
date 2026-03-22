import time
from ament_index_python.packages import get_package_share_directory

t0 = time.time()
print("Starting...")
path = get_package_share_directory('gazebo_ros')
print(f"Path: {path}")
print(f"Time: {time.time() - t0}")
