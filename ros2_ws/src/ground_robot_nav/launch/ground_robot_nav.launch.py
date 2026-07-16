from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='ground_robot_nav', executable='mpc_local_planner_node', output='screen'),
        Node(package='ground_robot_nav', executable='slam_manager_node', output='screen')
    ])
