from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='safety_monitor', executable='safety_watchdog_node', output='screen')
    ])
