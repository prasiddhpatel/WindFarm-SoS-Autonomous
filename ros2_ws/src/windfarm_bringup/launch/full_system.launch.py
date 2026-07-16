from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def include(pkg, file):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare(pkg), 'launch', file])
        )
    )


def generate_launch_description():
    return LaunchDescription([
        include('drone_estimation', 'drone_estimation.launch.py'),
        include('drone_control', 'drone_control.launch.py'),
        include('drone_coverage', 'drone_coverage.launch.py'),
        include('drone_perception', 'drone_perception.launch.py'),
        include('ground_robot_nav', 'ground_robot_nav.launch.py'),
        include('ground_robot_dock', 'ground_robot_dock.launch.py'),
        include('nde_crawler', 'nde_crawler.launch.py'),
        include('safety_monitor', 'safety_monitor.launch.py'),
    ])
