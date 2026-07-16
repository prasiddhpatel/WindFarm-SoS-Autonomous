from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_estimation',
            executable='eskf_node',
            name='eskf_node',
            output='screen'
        )
    ])
