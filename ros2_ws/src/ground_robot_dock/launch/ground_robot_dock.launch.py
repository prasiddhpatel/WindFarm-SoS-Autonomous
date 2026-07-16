from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ground_robot_dock',
            executable='docking_node.py',
            name='docking_node',
            output='screen',
            parameters=[{
                'dock_tolerance_m': 0.05,
                'charge_target_pct': 90.0,
            }]
        )
    ])
