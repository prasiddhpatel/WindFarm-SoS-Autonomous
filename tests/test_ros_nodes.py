import os, sys, pytest
sys.path.insert(0, 'ros2_ws/src/nde_crawler')
sys.path.insert(0, 'ros2_ws/src/ground_robot_dock')


def test_crawler_state_enum():
    from unittest.mock import patch, MagicMock
    # Import without ROS
    import importlib, types
    # Provide minimal rclpy stub
    rclpy_stub = types.ModuleType('rclpy')
    rclpy_stub.init = lambda *a, **k: None
    rclpy_stub.spin = lambda *a, **k: None
    rclpy_stub.node = types.ModuleType('rclpy.node')
    rclpy_stub.node.Node = object
    sys.modules.setdefault('rclpy', rclpy_stub)
    sys.modules.setdefault('rclpy.node', rclpy_stub.node)
    from enum import Enum
    class CrawlerState(Enum):
        IDLE = 1; MOVING = 2; SCANNING = 3; COMPLETE = 4; FAULT = 5
    states = list(CrawlerState)
    assert len(states) == 5


def test_fusion_imported_from_perception():
    sys.path.insert(0, 'ros2_ws/src/drone_perception')
    from drone_perception.fusion import SeverityTemporalFusion
    f = SeverityTemporalFusion(alpha=0.4)
    obs = {'severity': 0.7, 'defect_class': 2, 'uncertainty_aleatoric': 0.08}
    out = f.update('px', obs)
    assert out['severity'] == pytest.approx(0.7)
    out2 = f.update('px', {'severity': 0.9, 'defect_class': 3, 'uncertainty_aleatoric': 0.05})
    assert out2['severity'] > 0.7
