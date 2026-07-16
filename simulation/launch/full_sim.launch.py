"""Full simulation launch: Gazebo + bridge + all ROS 2 nodes."""
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    sim_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(os.path.dirname(__file__), 'sim_bridge.launch.py')
        )
    )

    ros_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                os.path.dirname(__file__),
                '..', '..', 'ros2_ws', 'src',
                'windfarm_bringup', 'launch', 'full_system.launch.py'
            )
        )
    )

    return LaunchDescription([
        sim_bridge,
        TimerAction(period=5.0, actions=[ros_stack]),
    ])
