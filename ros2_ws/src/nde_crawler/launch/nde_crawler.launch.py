from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nde_crawler',
            executable='crawler_node.py',
            name='crawler_controller',
            output='screen',
            parameters=[{
                'scan_duration_s': 5.0,
                'suction_vacuum_pa': 40000.0,
            }]
        )
    ])
