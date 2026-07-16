from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='ground_robot_dock', executable='docking_node.py', output='screen')
    ])
