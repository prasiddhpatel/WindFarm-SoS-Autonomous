import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('drone_perception')
        self.sub = self.create_subscription(Image, '/camera/rgb', self.cb, 10)
        self.get_logger().info('Perception node placeholder ready.')

    def cb(self, msg):
        _ = msg


def main():
    rclpy.init()
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
