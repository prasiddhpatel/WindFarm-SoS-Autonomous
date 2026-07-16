cmake_minimum_required(VERSION 3.8)
project(drone_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(eigen3_cmake_module REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(sos_interfaces REQUIRED)

include_directories(include)

# Control allocator library
add_library(control_allocator SHARED
  src/control_allocator.cpp)
ament_target_dependencies(control_allocator eigen3_cmake_module)
target_link_libraries(control_allocator Eigen3::Eigen)
target_include_directories(control_allocator PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

# Geometric controller node
add_executable(geometric_controller
  src/geometric_controller_node.cpp)
ament_target_dependencies(geometric_controller
  rclcpp rclcpp_action geometry_msgs nav_msgs
  sensor_msgs std_msgs tf2 tf2_ros tf2_eigen
  sos_interfaces eigen3_cmake_module)
target_link_libraries(geometric_controller control_allocator Eigen3::Eigen)

# Mixer node
add_executable(mixer_node src/mixer_node.cpp)
ament_target_dependencies(mixer_node rclcpp std_msgs)

install(TARGETS control_allocator geometric_controller mixer_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
  OPTIONAL)

ament_export_targets(export_control_allocator HAS_LIBRARY_TARGET)
ament_export_dependencies(eigen3_cmake_module Eigen3)
ament_package()
