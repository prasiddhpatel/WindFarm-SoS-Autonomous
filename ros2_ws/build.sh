#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source /opt/ros/humble/setup.bash

echo "=== [1/4] Building sos_interfaces ==="
colcon build --packages-select sos_interfaces --symlink-install
source "$ROOT/install/setup.bash"

echo "=== [2/4] Building Python packages ==="
colcon build \
  --packages-select drone_perception ground_robot_dock nde_crawler \
  --symlink-install
source "$ROOT/install/setup.bash"

echo "=== [3/4] Building C++ packages ==="
colcon build \
  --packages-select \
    drone_control drone_coverage drone_estimation \
    ground_robot_nav safety_monitor \
  --symlink-install
source "$ROOT/install/setup.bash"

echo "=== [4/4] Building bringup ==="
colcon build --packages-select windfarm_bringup --symlink-install
source "$ROOT/install/setup.bash"

echo "=== Build complete ==="
