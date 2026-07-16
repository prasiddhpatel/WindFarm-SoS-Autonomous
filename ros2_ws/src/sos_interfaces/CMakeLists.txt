cmake_minimum_required(VERSION 3.8)
project(sos_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(action_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BladePatch.msg"
  "msg/DefectHypothesis.msg"
  "msg/TelemetryStatus.msg"
  "action/InspectBlade.action"
  "action/CrawlToTarget.action"
  DEPENDENCIES std_msgs geometry_msgs sensor_msgs action_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
