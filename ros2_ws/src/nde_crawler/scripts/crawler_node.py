#!/usr/bin/env python3
"""nde_crawler: crawl-to-target action server and UT scan executor."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from geometry_msgs.msg import PoseStamped
from enum import Enum, auto


class CrawlerState(Enum):
    IDLE = auto()
    MOVING = auto()
    SCANNING = auto()
    COMPLETE = auto()
    FAULT = auto()


class CrawlerNode(Node):
    """Crawler controller node: subscribes to target pose, executes mock UT scan."""

    def __init__(self):
        super().__init__('crawler_controller')

        self.declare_parameter('scan_duration_s', 5.0)
        self.declare_parameter('suction_vacuum_pa', 40000.0)

        self._state = CrawlerState.IDLE
        self._scan_elapsed = 0.0

        self._target_sub = self.create_subscription(
            PoseStamped, '/crawler/target_pose', self._target_cb, 10)
        self._state_pub = self.create_publisher(String, '/crawler/state', 10)
        self._ut_result_pub = self.create_publisher(Float32, '/crawler/ut_depth_m', 10)

        self._timer = self.create_timer(0.1, self._tick)
        self.get_logger().info('Crawler controller node ready.')

    def _target_cb(self, msg: PoseStamped):
        if self._state == CrawlerState.IDLE:
            self.get_logger().info(
                f'New target: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})'
            )
            self._transition(CrawlerState.MOVING)
            self._scan_elapsed = 0.0

    def _tick(self):
        dt = 0.1
        if self._state == CrawlerState.MOVING:
            # Placeholder: immediately arrive at target
            self._transition(CrawlerState.SCANNING)

        elif self._state == CrawlerState.SCANNING:
            scan_dur = self.get_parameter('scan_duration_s').value
            self._scan_elapsed += dt
            if self._scan_elapsed >= scan_dur:
                # Publish mock UT depth result
                msg = Float32()
                msg.data = 0.003  # 3 mm crack depth placeholder
                self._ut_result_pub.publish(msg)
                self.get_logger().info(
                    f'UT scan complete: depth={msg.data*1000:.1f} mm'
                )
                self._transition(CrawlerState.COMPLETE)

        elif self._state == CrawlerState.COMPLETE:
            self._transition(CrawlerState.IDLE)

        s = String()
        s.data = self._state.name
        self._state_pub.publish(s)

    def _transition(self, new: CrawlerState):
        if new != self._state:
            self.get_logger().info(f'Crawler: {self._state.name} → {new.name}')
            self._state = new


def main(args=None):
    rclpy.init(args=args)
    node = CrawlerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
