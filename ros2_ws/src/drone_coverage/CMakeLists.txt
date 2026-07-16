cmake_minimum_required(VERSION 3.8)
project(drone_coverage)

add_compile_options(-Wall -O2)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(sos_interfaces REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(PCL REQUIRED)

add_executable(coverage_planner_node
  src/coverage_planner_node.cpp
  src/boustrophedon_planner.cpp
  src/standoff_regulator.cpp
  src/minimum_snap_trajectory.cpp
)
ament_target_dependencies(coverage_planner_node
  rclcpp rclcpp_action geometry_msgs nav_msgs sensor_msgs
  tf2_ros tf2_eigen sos_interfaces pcl_conversions)
target_include_directories(coverage_planner_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${EIGEN3_INCLUDE_DIRS} ${PCL_INCLUDE_DIRS})
target_link_libraries(coverage_planner_node ${PCL_LIBRARIES})

install(TARGETS coverage_planner_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ launch config DESTINATION share/${PROJECT_NAME})
ament_package()
