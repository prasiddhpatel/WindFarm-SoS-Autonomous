cmake_minimum_required(VERSION 3.8)
project(safety_monitor)

add_compile_options(-Wall -O2)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sos_interfaces REQUIRED)

add_executable(safety_watchdog_node
  src/safety_watchdog_node.cpp
  src/geofence_monitor.cpp
  src/rate_monotonic_scheduler.cpp
)
ament_target_dependencies(safety_watchdog_node
  rclcpp std_msgs geometry_msgs nav_msgs sos_interfaces)
target_include_directories(safety_watchdog_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

install(TARGETS safety_watchdog_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ launch config DESTINATION share/${PROJECT_NAME})
ament_package()
