from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='drone_control',
            executable='geometric_controller',
            name='geometric_controller',
            output='screen',
            parameters=['config/controller.yaml']
        ),
        Node(
            package='drone_control',
            executable='mixer_node',
            name='mixer_node',
            output='screen'
        )
    ])
