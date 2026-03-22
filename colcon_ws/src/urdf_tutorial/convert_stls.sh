#!/bin/bash
cd /mnt/c/Users/User/Downloads/Candle_TheRobot-main/colcon_ws/src/urdf_tutorial/meshes || exit 1
for file in *.stl; do
  admesh "$file" --write-binary-stl="bin_$file"
  mv "bin_$file" "$file"
done
echo "Conversion complete."
