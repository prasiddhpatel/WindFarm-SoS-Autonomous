"""Export a PyTorch blade defect classifier to ONNX and TorchScript.

Usage
-----
  python3 -m drone_perception.model_export \
      --checkpoint weights/blade_defect_v1.pt \
      --output-dir weights/ \
      --img-size 224 \
      --opset 17

The exported artefacts are:
  weights/blade_defect_v1.onnx        (ONNX Runtime / TensorRT)
  weights/blade_defect_v1_ts.pt       (TorchScript)
"""
from __future__ import annotations
import argparse
from pathlib import Path


def _build_model(n_classes: int = 5):
    try:
        import torch
        import torch.nn as nn
        import torchvision.models as models
    except ImportError as e:
        raise ImportError('PyTorch + torchvision required for export') from e

    backbone = models.efficientnet_b0(weights=None)
    old_conv = backbone.features[0][0]
    new_conv = nn.Conv2d(
        4, old_conv.out_channels,
        kernel_size=old_conv.kernel_size,
        stride=old_conv.stride,
        padding=old_conv.padding,
        bias=False,
    )
    import torch
    with torch.no_grad():
        new_conv.weight[:, :3] = old_conv.weight
        new_conv.weight[:, 3]  = old_conv.weight.mean(dim=1)
    backbone.features[0][0] = new_conv
    in_features = backbone.classifier[1].in_features
    backbone.classifier[1] = nn.Linear(in_features, n_classes)
    return backbone


def export_onnx(model, output_path: Path, img_size: int, opset: int):
    import torch
    model.eval()
    dummy = torch.zeros(1, 4, img_size, img_size)
    torch.onnx.export(
        model, dummy, str(output_path),
        input_names=['input'], output_names=['logits'],
        dynamic_axes={'input': {0: 'batch'}, 'logits': {0: 'batch'}},
        opset_version=opset, do_constant_folding=True,
    )
    print(f'ONNX  → {output_path}')


def export_torchscript(model, output_path: Path, img_size: int):
    import torch
    model.eval()
    traced = torch.jit.trace(model, torch.zeros(1, 4, img_size, img_size))
    traced.save(str(output_path))
    print(f'TorchScript → {output_path}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint',      default=None)
    ap.add_argument('--output-dir',      default='weights')
    ap.add_argument('--img-size',        type=int, default=224)
    ap.add_argument('--opset',           type=int, default=17)
    ap.add_argument('--n-classes',       type=int, default=5)
    ap.add_argument('--no-torchscript',  action='store_true')
    args = ap.parse_args()

    try:
        import torch
    except ImportError:
        print('PyTorch not installed — skipping export.')
        return

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model = _build_model(args.n_classes)

    if args.checkpoint:
        import torch
        ckpt = torch.load(args.checkpoint, map_location='cpu')
        model.load_state_dict(ckpt.get('state_dict', ckpt), strict=False)
        print(f'Checkpoint: {args.checkpoint}')
    else:
        print('No checkpoint — exporting random weights.')

    stem = Path(args.checkpoint).stem if args.checkpoint else 'blade_defect_v1'
    export_onnx(model, out / f'{stem}.onnx', args.img_size, args.opset)
    if not args.no_torchscript:
        export_torchscript(model, out / f'{stem}_ts.pt', args.img_size)


if __name__ == '__main__':
    main()
