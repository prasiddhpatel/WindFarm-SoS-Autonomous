#!/usr/bin/env python3
"""drone_perception: multimodal blade defect perception node.

Inference backend priority:
  1. ONNX Runtime  (model path set via ROS param 'model_path')
  2. Mock logits   (fallback when model not found or onnxruntime absent)

MC-Dropout epistemic uncertainty estimation is enabled via
  'use_mc_dropout: true'  +  'mc_passes: 10'
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np

try:
    from cv_bridge import CvBridge
    _CV_BRIDGE = True
except ImportError:
    _CV_BRIDGE = False

from drone_perception.model_runner import ModelRunner, MCDropoutRunner
from drone_perception.fusion import SeverityTemporalFusion


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('drone_perception')

        self.declare_parameter('model_path',         'weights/blade_defect_v1.onnx')
        self.declare_parameter('use_mc_dropout',     False)
        self.declare_parameter('mc_passes',          10)
        self.declare_parameter('fuse_alpha',         0.3)
        self.declare_parameter('severity_threshold', 0.35)
        self.declare_parameter('publish_rate_hz',    2.0)

        model_path    = self.get_parameter('model_path').value
        use_mc        = self.get_parameter('use_mc_dropout').value
        mc_passes     = self.get_parameter('mc_passes').value
        fuse_alpha    = self.get_parameter('fuse_alpha').value

        RunnerClass = MCDropoutRunner if use_mc else ModelRunner
        if use_mc:
            self._runner = MCDropoutRunner(model_path, n_passes=mc_passes)
        else:
            self._runner = ModelRunner(model_path)

        self._fusion  = SeverityTemporalFusion(alpha=fuse_alpha)
        self._bridge  = CvBridge() if _CV_BRIDGE else None
        self._latest_rgb:     np.ndarray | None = None
        self._latest_thermal: np.ndarray | None = None
        self._patch_counter = 0

        self._rgb_sub     = self.create_subscription(Image, '/camera/rgb',     self._rgb_cb,     10)
        self._thermal_sub = self.create_subscription(Image, '/camera/thermal', self._thermal_cb, 10)

        rate = self.get_parameter('publish_rate_hz').value
        self._timer = self.create_timer(1.0 / rate, self._process)
        self.get_logger().info(
            f'Perception node ready | model={model_path} | mc_dropout={use_mc}'
        )

    # ── image callbacks ─────────────────────────────────────────────────────
    def _rgb_cb(self, msg: Image):
        if self._bridge:
            self._latest_rgb = self._bridge.imgmsg_to_cv2(msg, 'rgb8')
        else:
            self._latest_rgb = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, -1)

    def _thermal_cb(self, msg: Image):
        if self._bridge:
            self._latest_thermal = self._bridge.imgmsg_to_cv2(msg, 'mono8')
        else:
            self._latest_thermal = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width)

    # ── inference + fusion tick ─────────────────────────────────────────────
    def _process(self):
        if self._latest_rgb is None:
            return

        rgb     = self._latest_rgb
        thermal = self._latest_thermal if self._latest_thermal is not None \
                  else np.zeros(rgb.shape[:2], dtype=np.uint8)

        result = self._runner.infer(rgb, thermal)
        patch_id = f'patch_{self._patch_counter % 6:04d}'
        fused  = self._fusion.update(patch_id, result.to_dict())

        self.get_logger().debug(
            f'[{patch_id}] cls={fused["defect_class"]}({fused["defect_label"]}) '
            f'sev={fused["severity"]:.3f} '
            f'aleat={fused["uncertainty_aleatoric"]:.3f} '
            f'epist={fused["uncertainty_epistemic"]:.3f}'
        )

        threshold = self.get_parameter('severity_threshold').value
        if fused['severity'] > threshold:
            self.get_logger().info(
                f'[DEFECT ALERT] {patch_id}: {fused["defect_label"]} '
                f'sev={fused["severity"]:.3f} '
                f'epist={fused["uncertainty_epistemic"]:.3f}'
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
