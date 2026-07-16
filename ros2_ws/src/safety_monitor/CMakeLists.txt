cmake_minimum_required(VERSION 3.8)
project(safety_monitor)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sos_interfaces REQUIRED)

include_directories(include)

add_library(safety_core src/rate_monotonic_scheduler.cpp)

add_executable(safety_watchdog_node src/safety_watchdog_node.cpp)
ament_target_dependencies(safety_watchdog_node rclcpp std_msgs geometry_msgs nav_msgs sos_interfaces)
target_link_libraries(safety_watchdog_node safety_core)

install(TARGETS safety_core safety_watchdog_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include launch DESTINATION share/${PROJECT_NAME})

ament_package()
