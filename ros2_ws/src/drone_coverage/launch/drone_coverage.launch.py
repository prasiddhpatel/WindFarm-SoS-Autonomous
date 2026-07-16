from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_coverage',
            executable='coverage_planner_node',
            name='coverage_planner_node',
            output='screen'
        )
    ])
