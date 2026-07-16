from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='nde_crawler', executable='crawler_controller', output='screen')
    ])
