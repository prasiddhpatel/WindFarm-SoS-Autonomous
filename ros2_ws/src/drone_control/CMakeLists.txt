cmake_minimum_required(VERSION 3.8)
project(drone_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -O3 -march=native)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(sos_interfaces REQUIRED)

add_executable(geometric_controller
  src/geometric_controller_node.cpp
  src/se3_controller.cpp
  src/control_allocator.cpp
)
ament_target_dependencies(geometric_controller
  rclcpp geometry_msgs nav_msgs sensor_msgs std_msgs
  tf2 tf2_ros tf2_eigen sos_interfaces
)
target_include_directories(geometric_controller PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${EIGEN3_INCLUDE_DIRS}
)

add_executable(mixer_node
  src/mixer_node.cpp
)
ament_target_dependencies(mixer_node rclcpp std_msgs sensor_msgs)
target_include_directories(mixer_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${EIGEN3_INCLUDE_DIRS}
)

install(TARGETS geometric_controller mixer_node
  DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})

ament_package()
