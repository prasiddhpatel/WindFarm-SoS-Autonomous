from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_perception',
            executable='perception_node.py',
            name='drone_perception',
            output='screen'
        )
    ])
