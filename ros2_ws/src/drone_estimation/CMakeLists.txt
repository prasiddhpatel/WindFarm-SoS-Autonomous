cmake_minimum_required(VERSION 3.8)
project(drone_estimation)

add_compile_options(-Wall -O3)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(sos_interfaces REQUIRED)

add_executable(eskf_node
  src/eskf_node.cpp
  src/eskf.cpp
)
ament_target_dependencies(eskf_node
  rclcpp sensor_msgs nav_msgs geometry_msgs
  tf2_ros tf2_eigen sos_interfaces)
target_include_directories(eskf_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${EIGEN3_INCLUDE_DIRS})

install(TARGETS eskf_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})
ament_package()
