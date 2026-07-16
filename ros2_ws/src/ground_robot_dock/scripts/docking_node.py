#!/usr/bin/env python3
"""ground_robot_dock: AprilTag-based docking and charging state machine."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from enum import Enum, auto


class DockState(Enum):
    IDLE = auto()
    SEARCHING = auto()
    APPROACHING = auto()
    DOCKED = auto()
    CHARGING = auto()
    RELEASING = auto()


class DockingNode(Node):
    def __init__(self):
        super().__init__('docking_node')

        self.declare_parameter('dock_tolerance_m', 0.05)
        self.declare_parameter('charge_target_pct', 90.0)

        self._state = DockState.IDLE
        self._battery_pct: float = 0.0

        self._tag_sub = self.create_subscription(
            PoseStamped, '/apriltag/dock_pose', self._tag_cb, 10)
        self._battery_sub = self.create_subscription(
            String, '/uav/battery_pct', self._battery_cb, 10)

        self._cmd_pub = self.create_publisher(String, '/dock/command', 10)
        self._status_pub = self.create_publisher(String, '/dock/status', 10)

        self._timer = self.create_timer(0.5, self._tick)
        self.get_logger().info('Docking node ready.')

    def _tag_cb(self, msg: PoseStamped):
        if self._state == DockState.SEARCHING:
            dist = (msg.pose.position.x**2 + msg.pose.position.y**2) ** 0.5
            tol = self.get_parameter('dock_tolerance_m').value
            if dist < tol:
                self._transition(DockState.DOCKED)
            else:
                self._transition(DockState.APPROACHING)

    def _battery_cb(self, msg: String):
        try:
            self._battery_pct = float(msg.data)
        except ValueError:
            pass

    def _tick(self):
        target_pct = self.get_parameter('charge_target_pct').value
        if self._state == DockState.DOCKED:
            self._transition(DockState.CHARGING)
        elif self._state == DockState.CHARGING and self._battery_pct >= target_pct:
            self._transition(DockState.RELEASING)
        elif self._state == DockState.RELEASING:
            self._transition(DockState.IDLE)

        s = String()
        s.data = self._state.name
        self._status_pub.publish(s)

    def _transition(self, new_state: DockState):
        if new_state != self._state:
            self.get_logger().info(f'Dock state: {self._state.name} → {new_state.name}')
            self._state = new_state


def main(args=None):
    rclpy.init(args=args)
    node = DockingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
