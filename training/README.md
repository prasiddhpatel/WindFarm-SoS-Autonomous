# Training Pipeline

## Quick start (synthetic data)

```bash
# 1. Generate synthetic smoke-test dataset
python3 training/generate_synthetic_data.py --output-dir data/ --n-per-class 50

# 2. Train
python3 training/train.py \
    --data-root data/ \
    --epochs 10 \
    --batch-size 16 \
    --output-dir weights/

# 3. Export to ONNX + TorchScript
python3 -m drone_perception.model_export \
    --checkpoint weights/blade_defect_best.pt \
    --output-dir weights/

# 4. Deploy: point perception node at the model
#    ros2 param set /drone_perception model_path weights/blade_defect_v1.onnx
```

## Dataset layout

```
data/
  train/  val/  test/
    no_defect/
      rgb/      0001.jpg ...
      thermal/  0001.png ...
    surface_erosion/
    crack/
    delamination/
    lightning_strike/
```

## Model architecture

EfficientNet-B0 with the first conv patched to accept 4 channels (RGB + thermal).
ImageNet weights are used for the RGB channels; the thermal channel is initialised
from the mean of the RGB weights.

## Class labels

| Index | Label |
|---|---|
| 0 | no_defect |
| 1 | surface_erosion |
| 2 | crack |
| 3 | delamination |
| 4 | lightning_strike |
