from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    gz_models_path = os.path.expanduser('~/ros2_ws/../simulation/models')
    world_path = os.path.expanduser('~/ros2_ws/../simulation/worlds/windfarm_field.sdf')

    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', gz_models_path),

        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_path],
            output='screen'
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/uav_a_01/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
                '/uav_a_01/gnss@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat',
                '/uav_a_01/cmd_motor_speed@std_msgs/msg/Float64MultiArray]gz.msgs.Actuators',
            ],
            output='screen'
        ),
    ])
