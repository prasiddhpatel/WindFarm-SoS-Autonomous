cmake_minimum_required(VERSION 3.8)
project(drone_coverage)

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
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(sos_interfaces REQUIRED)

# PCL is optional — skip gracefully if not found
find_package(PCL QUIET)
find_package(pcl_conversions QUIET)

include_directories(include)

add_library(coverage_core SHARED
  src/boustrophedon_planner.cpp
  src/minimum_snap_trajectory.cpp
  src/standoff_regulator.cpp)
ament_target_dependencies(coverage_core eigen3_cmake_module)
target_link_libraries(coverage_core Eigen3::Eigen)
target_include_directories(coverage_core PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)

add_executable(coverage_planner_node src/coverage_planner_node.cpp)
ament_target_dependencies(coverage_planner_node
  rclcpp geometry_msgs nav_msgs sensor_msgs
  tf2_ros tf2_eigen sos_interfaces eigen3_cmake_module)
target_link_libraries(coverage_planner_node coverage_core Eigen3::Eigen)

install(TARGETS coverage_core coverage_planner_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME} OPTIONAL)

ament_export_targets(export_coverage_core HAS_LIBRARY_TARGET)
ament_export_dependencies(eigen3_cmake_module Eigen3)
ament_package()
