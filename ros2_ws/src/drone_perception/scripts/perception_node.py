#!/usr/bin/env python3
"""drone_perception: multimodal blade defect perception node."""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np
import json

try:
    from cv_bridge import CvBridge
    import cv2
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False


DEFECT_CLASSES = [
    'no_defect',
    'surface_erosion',
    'crack',
    'delamination',
    'lightning_strike',
]


def mock_infer(rgb: np.ndarray, thermal: np.ndarray):
    """Placeholder inference returning a defect hypothesis dict.
    Replace with a real TorchScript / ONNX model call.
    """
    mean_rgb = float(rgb.mean()) / 255.0
    mean_th  = float(thermal.mean()) / 255.0
    severity = float(np.clip(0.4 * mean_rgb + 0.6 * mean_th, 0.0, 1.0))

    defect_class = 0
    if severity > 0.75:
        defect_class = 3
    elif severity > 0.55:
        defect_class = 2
    elif severity > 0.35:
        defect_class = 1

    # Aleatoric uncertainty: proxy from local variance
    aleatoric = float(np.std(rgb.astype(np.float32) / 255.0))
    # Epistemic uncertainty: fixed placeholder (MC-dropout / ensemble not yet wired)
    epistemic = 0.05

    return {
        'defect_class': defect_class,
        'defect_label': DEFECT_CLASSES[defect_class],
        'severity': severity,
        'uncertainty_aleatoric': aleatoric,
        'uncertainty_epistemic': epistemic,
        'confidence': float(1.0 - aleatoric - epistemic),
    }


class SeverityTemporalFusion:
    """Exponential moving average fusion of patch-level severity estimates."""
    def __init__(self, alpha: float = 0.3):
        self._alpha = alpha
        self._state: dict[str, dict] = {}

    def update(self, patch_id: str, observation: dict) -> dict:
        if patch_id not in self._state:
            self._state[patch_id] = dict(observation)
            return dict(observation)
        s = self._state[patch_id]
        s['severity'] = (1 - self._alpha) * s['severity'] + self._alpha * observation['severity']
        s['uncertainty_aleatoric'] = (
            (1 - self._alpha) * s['uncertainty_aleatoric']
            + self._alpha * observation['uncertainty_aleatoric']
        )
        # Aggregate defect class by majority if severity crosses threshold
        if s['severity'] > 0.55:
            s['defect_class'] = max(s['defect_class'], observation['defect_class'])
        return dict(s)

    def all_patches(self) -> dict:
        return dict(self._state)


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('drone_perception')

        self.declare_parameter('fuse_alpha', 0.3)
        self.declare_parameter('severity_threshold', 0.35)
        self.declare_parameter('publish_rate_hz', 2.0)

        alpha = self.get_parameter('fuse_alpha').value
        self._fusion = SeverityTemporalFusion(alpha=alpha)
        self._bridge = CvBridge() if CV_AVAILABLE else None
        self._latest_rgb: np.ndarray | None = None
        self._latest_thermal: np.ndarray | None = None
        self._patch_counter = 0

        self._rgb_sub = self.create_subscription(
            Image, '/camera/rgb', self._rgb_cb, 10)
        self._thermal_sub = self.create_subscription(
            Image, '/camera/thermal', self._thermal_cb, 10)

        rate = self.get_parameter('publish_rate_hz').value
        self._timer = self.create_timer(1.0 / rate, self._process)

        self.get_logger().info('Perception node ready (mock inference mode).')

    def _rgb_cb(self, msg: Image):
        if self._bridge:
            self._latest_rgb = self._bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        else:
            h, w = msg.height, msg.width
            self._latest_rgb = np.frombuffer(msg.data, dtype=np.uint8).reshape(h, w, -1)

    def _thermal_cb(self, msg: Image):
        if self._bridge:
            self._latest_thermal = self._bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
        else:
            h, w = msg.height, msg.width
            self._latest_thermal = np.frombuffer(msg.data, dtype=np.uint8).reshape(h, w, -1)

    def _process(self):
        if self._latest_rgb is None:
            return

        rgb = self._latest_rgb
        thermal = self._latest_thermal if self._latest_thermal is not None else np.zeros_like(rgb)

        obs = mock_infer(rgb, thermal)
        patch_id = f'patch_{self._patch_counter % 6:04d}'
        fused = self._fusion.update(patch_id, obs)

        self.get_logger().debug(
            f'[{patch_id}] cls={fused["defect_class"]} '
            f'sev={fused["severity"]:.3f} '
            f'aleat={fused["uncertainty_aleatoric"]:.3f}'
        )

        threshold = self.get_parameter('severity_threshold').value
        if fused['severity'] > threshold:
            self.get_logger().info(
                f'[ALERT] {patch_id}: defect={fused["defect_label"]} '
                f'severity={fused["severity"]:.3f} '
                f'epistemic={fused["uncertainty_epistemic"]:.3f}'
            )

        self._patch_counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
