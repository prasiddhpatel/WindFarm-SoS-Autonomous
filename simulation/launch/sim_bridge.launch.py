"""Launch the Gazebo Harmonic simulation and ROS 2 bridge.

Requires:
  ros-humble-ros-gz-bridge
  gz-harmonic (or gz-garden)
"""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, ExecuteProcess, TimerAction
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    world_file = os.path.join(
        os.path.dirname(__file__), '..', 'worlds', 'windfarm.sdf'
    )

    gz_sim = ExecuteProcess(
        cmd=[
            'gz', 'sim', '-r',
            world_file,
            '--headless-rendering',
        ],
        output='screen',
        name='gz_sim',
    )

    # ROS ↔ Gazebo topic bridges
    bridge_params = [
        # UAV IMU
        '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
        # UAV odometry (ground truth from Gazebo)
        '/uav/ground_truth/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        # UGV odometry
        '/ugv/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        # UGV cmd_vel
        '/ugv/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        # RGB camera
        '/camera/rgb@sensor_msgs/msg/Image[gz.msgs.Image',
        # Thermal camera (simulated as 2nd image topic)
        '/camera/thermal@sensor_msgs/msg/Image[gz.msgs.Image',
        # Clock
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
    ]

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=bridge_params,
        output='screen',
    )

    return LaunchDescription([
        gz_sim,
        TimerAction(period=3.0, actions=[ros_gz_bridge]),
    ])
