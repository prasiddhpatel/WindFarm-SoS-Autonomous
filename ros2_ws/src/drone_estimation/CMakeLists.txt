cmake_minimum_required(VERSION 3.8)
project(drone_estimation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(eigen3_cmake_module REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(sos_interfaces REQUIRED)

include_directories(include ${EIGEN3_INCLUDE_DIRS})

add_library(eskf_lib src/eskf.cpp)
target_link_libraries(eskf_lib Eigen3::Eigen)

add_executable(eskf_node src/eskf_node.cpp)
ament_target_dependencies(eskf_node rclcpp sensor_msgs nav_msgs geometry_msgs tf2_ros tf2_eigen sos_interfaces)
target_link_libraries(eskf_node eskf_lib Eigen3::Eigen)

install(TARGETS eskf_lib eskf_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include launch DESTINATION share/${PROJECT_NAME})

ament_package()
