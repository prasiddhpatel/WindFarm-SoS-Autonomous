cmake_minimum_required(VERSION 3.8)
project(ground_robot_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(eigen3_cmake_module REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(sos_interfaces REQUIRED)

include_directories(include ${EIGEN3_INCLUDE_DIRS})

add_library(nav_core src/skid_steer_mpc.cpp)
target_link_libraries(nav_core Eigen3::Eigen)

add_executable(mpc_local_planner_node src/mpc_local_planner_node.cpp)
ament_target_dependencies(mpc_local_planner_node rclcpp nav_msgs geometry_msgs sensor_msgs tf2_ros tf2_eigen sos_interfaces)
target_link_libraries(mpc_local_planner_node nav_core Eigen3::Eigen)

add_executable(slam_manager_node src/slam_manager_node.cpp)
ament_target_dependencies(slam_manager_node rclcpp)

install(TARGETS nav_core mpc_local_planner_node slam_manager_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include launch DESTINATION share/${PROJECT_NAME})

ament_package()
