cmake_minimum_required(VERSION 3.8)
project(drone_perception)

add_compile_options(-Wall -O2)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(image_transport REQUIRED)
find_package(sos_interfaces REQUIRED)
find_package(OpenCV REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Python node for ONNX-Runtime inference
ament_python_install_package(drone_perception_py)

install(PROGRAMS
  scripts/perception_node.py
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY config launch models DESTINATION share/${PROJECT_NAME})
ament_package()
