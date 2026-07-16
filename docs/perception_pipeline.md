# Perception Pipeline

## Architecture

The blade defect perception pipeline is a 4-stage process:

```
RGB image  ──┐
              ├─► _preprocess (resize, normalise, stack) ─► (1,4,224,224) float32
Thermal    ──┘
              │
              ▼
       ModelRunner / MCDropoutRunner
       (ONNX Runtime or mock logits)
              │
              ▼
       InferenceResult
       (defect_class, severity, aleatoric, epistemic)
              │
              ▼
       SeverityTemporalFusion (EMA, α=0.3)
              │
              ▼
       Fused patch state → DEFECT ALERT if sev > threshold
```

## Inference backends

| Backend | When used |
|---|---|
| ONNX Runtime (`CUDAExecutionProvider`) | Model `.onnx` exists + `onnxruntime-gpu` installed |
| ONNX Runtime (`CPUExecutionProvider`) | Model `.onnx` exists + `onnxruntime` installed |
| Mock logits | No model file or no onnxruntime |

## Exporting a model

```bash
# Train (not in scope here), then export:
python3 -m drone_perception.model_export \
    --checkpoint weights/blade_defect_v1.pt \
    --output-dir weights/ \
    --img-size 224 \
    --opset 17
```

Outputs:
- `weights/blade_defect_v1.onnx`  — for ONNX Runtime / TensorRT edge deploy
- `weights/blade_defect_v1_ts.pt` — TorchScript for pure-PyTorch deploy

## MC-Dropout uncertainty

Enable via ROS parameter:
```yaml
use_mc_dropout: true
mc_passes: 10
```
Requires the model to be exported with dropout layers in train mode.
The node will run `mc_passes` forward passes and report the mean logit std as `uncertainty_epistemic`.

## Class definitions

| Index | Label | Severity range |
|---|---|---|
| 0 | no_defect | 0.00 – 0.20 |
| 1 | surface_erosion | 0.20 – 0.40 |
| 2 | crack | 0.40 – 0.60 |
| 3 | delamination | 0.60 – 0.80 |
| 4 | lightning_strike | 0.80 – 1.00 |
