cmake_minimum_required(VERSION 3.8)
project(ground_robot_nav)

add_compile_options(-Wall -O2)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(sos_interfaces REQUIRED)

add_executable(mpc_local_planner_node
  src/mpc_local_planner_node.cpp
  src/skid_steer_mpc.cpp
)
ament_target_dependencies(mpc_local_planner_node
  rclcpp nav_msgs geometry_msgs sensor_msgs
  tf2_ros tf2_eigen sos_interfaces)
target_include_directories(mpc_local_planner_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${EIGEN3_INCLUDE_DIRS})

add_executable(slam_manager_node
  src/slam_manager_node.cpp
)
ament_target_dependencies(slam_manager_node
  rclcpp nav_msgs geometry_msgs sensor_msgs tf2_ros)

install(TARGETS mpc_local_planner_node slam_manager_node
  DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ launch config DESTINATION share/${PROJECT_NAME})
ament_package()
