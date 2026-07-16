cmake_minimum_required(VERSION 3.8)
project(sos_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/PatchReport.msg"
  "msg/FleetStatus.msg"
  "msg/DefectObservation.msg"
  "msg/CrawlerStatus.msg"
  "msg/RULEstimate.msg"
  "srv/AllocateTask.srv"
  "srv/TriggerScan.srv"
  "action/InspectBlade.action"
  "action/CrawlToTarget.action"
  DEPENDENCIES std_msgs geometry_msgs builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
