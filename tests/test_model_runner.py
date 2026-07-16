import sys, os, pytest
import numpy as np
sys.path.insert(0, 'ros2_ws/src/drone_perception')

from drone_perception.model_runner import (
    ModelRunner, MCDropoutRunner, InferenceResult,
    _softmax, _preprocess, DEFECT_LABELS, N_CLASSES,
)

# ── softmax ──────────────────────────────────────────────────────────────────
def test_softmax_sums_to_one():
    x = np.array([1.0, 2.0, 0.5, -1.0, 3.0])
    p = _softmax(x)
    assert pytest.approx(p.sum(), abs=1e-6) == 1.0

def test_softmax_argmax_preserved():
    x = np.array([0.1, 0.2, 5.0, 0.0, 0.05])
    assert _softmax(x).argmax() == 2

# ── InferenceResult ───────────────────────────────────────────────────────────
def test_inference_result_no_defect():
    logits = np.array([5.0, 0.0, 0.0, 0.0, 0.0])
    r = InferenceResult(logits)
    assert r.defect_class == 0
    assert r.defect_label == 'no_defect'
    assert r.severity < 0.2
    assert 0.0 <= r.confidence <= 1.0

def test_inference_result_crack():
    logits = np.array([-2.0, -1.0, 4.0, -1.0, -2.0])
    r = InferenceResult(logits)
    assert r.defect_class == 2
    assert r.defect_label == 'crack'

def test_inference_result_severity_range():
    for _ in range(20):
        logits = np.random.randn(N_CLASSES).astype(np.float32)
        r = InferenceResult(logits)
        assert 0.0 <= r.severity <= 1.0
        assert 0.0 <= r.uncertainty_aleatoric

def test_inference_result_to_dict_keys():
    r = InferenceResult(np.zeros(N_CLASSES))
    d = r.to_dict()
    for k in ('defect_class','defect_label','confidence','severity',
              'uncertainty_aleatoric','uncertainty_epistemic','class_probs'):
        assert k in d

# ── ModelRunner (mock path) ───────────────────────────────────────────────────
def test_model_runner_mock_no_defect():
    runner = ModelRunner('nonexistent_model.onnx')
    rgb     = np.zeros((64, 64, 3), dtype=np.uint8)
    thermal = np.zeros((64, 64),    dtype=np.uint8)
    r = runner.infer(rgb, thermal)
    assert r.defect_class == 0
    assert r.severity < 0.3

def test_model_runner_mock_high_severity():
    runner = ModelRunner('nonexistent_model.onnx')
    rgb     = np.full((64, 64, 3), 230, dtype=np.uint8)
    thermal = np.full((64, 64),    230, dtype=np.uint8)
    r = runner.infer(rgb, thermal)
    assert r.defect_class >= 2
    assert r.severity > 0.5

# ── MCDropoutRunner (mock) ────────────────────────────────────────────────────
def test_mc_dropout_runner_returns_epistemic():
    runner = MCDropoutRunner('nonexistent_model.onnx', n_passes=5)
    rgb     = np.ones((64, 64, 3), dtype=np.uint8) * 100
    thermal = np.ones((64, 64),    dtype=np.uint8) * 100
    r = runner.infer(rgb, thermal)
    assert r.uncertainty_epistemic == pytest.approx(0.05)

# ── fusion integration ────────────────────────────────────────────────────────
def test_runner_fusion_integration():
    from drone_perception.fusion import SeverityTemporalFusion
    runner = ModelRunner('nonexistent_model.onnx')
    fusion = SeverityTemporalFusion(alpha=0.4)
    rgb     = np.full((64, 64, 3), 180, dtype=np.uint8)
    thermal = np.full((64, 64),    200, dtype=np.uint8)
    for _ in range(5):
        result = runner.infer(rgb, thermal)
        fused  = fusion.update('p0', result.to_dict())
    assert 0.0 <= fused['severity'] <= 1.0
    assert fused['defect_class'] in range(N_CLASSES)
