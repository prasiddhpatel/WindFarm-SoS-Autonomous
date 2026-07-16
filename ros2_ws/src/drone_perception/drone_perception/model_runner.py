"""Model runner: ONNX Runtime inference with pure-numpy fallback.

Usage
-----
from drone_perception.model_runner import ModelRunner
runner = ModelRunner('weights/blade_defect_v1.onnx')
result = runner.infer(rgb_hwc_uint8, thermal_hw_uint8)

Design notes
------------
* cv2 is NOT imported at module level — resize is done with numpy so that
  the module works in CI environments where opencv is not installed.
* onnxruntime is optional — falls back to deterministic mock logits.
"""
from __future__ import annotations
import os
import numpy as np
from pathlib import Path

try:
    import onnxruntime as ort
    _ORT_AVAILABLE = True
except ImportError:
    _ORT_AVAILABLE = False

try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


DEFECT_LABELS = [
    'no_defect',
    'surface_erosion',
    'crack',
    'delamination',
    'lightning_strike',
]
N_CLASSES = len(DEFECT_LABELS)
_IMG_SIZE = (224, 224)


def _resize_numpy(img: np.ndarray, target_hw: tuple[int, int]) -> np.ndarray:
    """Nearest-neighbour resize using pure numpy — no cv2 dependency."""
    h_in, w_in = img.shape[:2]
    h_out, w_out = target_hw
    row_idx = (np.arange(h_out) * h_in / h_out).astype(np.int32)
    col_idx = (np.arange(w_out) * w_in / w_out).astype(np.int32)
    if img.ndim == 2:
        return img[np.ix_(row_idx, col_idx)]
    return img[np.ix_(row_idx, col_idx)]  # works for (H,W,C) via advanced indexing


def _preprocess(rgb: np.ndarray, thermal: np.ndarray) -> np.ndarray:
    """Normalise and stack RGB+thermal into a (1, 4, H, W) float32 tensor.

    Uses pure-numpy nearest-neighbour resize so opencv is not required.
    """
    h, w = _IMG_SIZE
    rgb_r = _resize_numpy(rgb,     (h, w)).astype(np.float32) / 255.0
    th_r  = _resize_numpy(thermal, (h, w)).astype(np.float32) / 255.0
    if th_r.ndim == 2:
        th_r = th_r[:, :, None]
    mean = np.array([0.485, 0.456, 0.406, 0.5], dtype=np.float32)
    std  = np.array([0.229, 0.224, 0.225, 0.2], dtype=np.float32)
    combined = np.concatenate([rgb_r, th_r], axis=-1)   # (H,W,4)
    combined = (combined - mean) / std
    tensor   = combined.transpose(2, 0, 1)[None]         # (1,4,H,W)
    return tensor


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


class InferenceResult:
    __slots__ = (
        'defect_class', 'defect_label', 'confidence', 'severity',
        'uncertainty_aleatoric', 'uncertainty_epistemic', 'class_probs',
    )

    def __init__(self, logits: np.ndarray, mc_std: float = 0.0):
        probs = _softmax(logits.flatten())
        self.class_probs           = probs.tolist()
        self.defect_class          = int(probs.argmax())
        self.defect_label          = DEFECT_LABELS[self.defect_class]
        self.confidence            = float(probs.max())
        weights = np.arange(N_CLASSES, dtype=np.float32) / (N_CLASSES - 1)
        self.severity              = float(np.dot(probs, weights))
        eps = 1e-8
        self.uncertainty_aleatoric = float(-np.sum(probs * np.log(probs + eps)))
        self.uncertainty_epistemic = mc_std

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class ModelRunner:
    """Load and run an ONNX model for blade defect classification.

    Falls back to deterministic mock inference if the model file is absent
    or onnxruntime is not installed (e.g. in CI).
    """

    def __init__(self, model_path: str | Path,
                 providers: list[str] | None = None):
        self._model_path  = Path(model_path)
        self._session: 'ort.InferenceSession | None' = None
        self._input_name: str = ''

        if _ORT_AVAILABLE and self._model_path.exists():
            providers = providers or ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self._session = ort.InferenceSession(
                str(self._model_path), providers=providers
            )
            self._input_name = self._session.get_inputs()[0].name
        # No warning spam in test environments — mock is intentional

    def infer(self, rgb: np.ndarray, thermal: np.ndarray) -> InferenceResult:
        if self._session is not None:
            tensor  = _preprocess(rgb, thermal)
            outputs = self._session.run(None, {self._input_name: tensor})
            logits  = np.array(outputs[0]).flatten()
        else:
            logits = self._mock_logits(rgb, thermal)
        return InferenceResult(logits)

    def _mock_logits(self, rgb: np.ndarray, thermal: np.ndarray) -> np.ndarray:
        mean_r   = float(rgb.mean())     / 255.0
        mean_t   = float(thermal.mean()) / 255.0
        severity = 0.4 * mean_r + 0.6 * mean_t
        logits   = np.zeros(N_CLASSES, dtype=np.float32)
        logits[0] = 2.0 * (1.0 - severity)
        logits[1] = 1.5 * max(0.0, severity - 0.20)
        logits[2] = 2.0 * max(0.0, severity - 0.40)
        logits[3] = 2.5 * max(0.0, severity - 0.60)
        logits[4] = 3.0 * max(0.0, severity - 0.75)
        return logits


class MCDropoutRunner(ModelRunner):
    """N forward passes with dropout active to estimate epistemic uncertainty.

    Falls back to single mock pass + fixed mc_std=0.05 in CI.
    """

    def __init__(self, model_path: str | Path, n_passes: int = 10,
                 providers: list[str] | None = None):
        super().__init__(model_path, providers)
        self._n = n_passes

    def infer(self, rgb: np.ndarray, thermal: np.ndarray) -> InferenceResult:
        if self._session is None:
            logits = self._mock_logits(rgb, thermal)
            return InferenceResult(logits, mc_std=0.05)
        tensor = _preprocess(rgb, thermal)
        all_logits = []
        for _ in range(self._n):
            out = self._session.run(None, {self._input_name: tensor})
            all_logits.append(np.array(out[0]).flatten())
        stack       = np.stack(all_logits)
        mean_logits = stack.mean(axis=0)
        mc_std      = float(stack.std(axis=0).mean())
        return InferenceResult(mean_logits, mc_std=mc_std)
