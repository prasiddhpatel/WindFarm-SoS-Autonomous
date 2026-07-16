#!/usr/bin/env python3
"""Training script for the 4-channel blade defect classifier.

Usage
-----
  python3 training/train.py \
      --data-root data/ \
      --epochs 50 \
      --batch-size 32 \
      --lr 1e-3 \
      --output-dir weights/

After training, export with:
  python3 -m drone_perception.model_export \
      --checkpoint weights/blade_defect_best.pt \
      --output-dir weights/
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path


def build_model(n_classes: int = 5):
    import torch.nn as nn
    import torchvision.models as models
    import torch
    backbone = models.efficientnet_b0(weights='DEFAULT')
    old = backbone.features[0][0]
    new = nn.Conv2d(4, old.out_channels,
                    kernel_size=old.kernel_size, stride=old.stride,
                    padding=old.padding, bias=False)
    with torch.no_grad():
        new.weight[:, :3] = old.weight
        new.weight[:, 3]  = old.weight.mean(dim=1)
    backbone.features[0][0] = new
    in_feat = backbone.classifier[1].in_features
    backbone.classifier[1] = nn.Linear(in_feat, n_classes)
    return backbone


def train(args):
    import torch
    import torch.nn as nn
    from torch.optim import AdamW
    from torch.optim.lr_scheduler import CosineAnnealingLR
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'ros2_ws' / 'src' / 'drone_perception'))
    from training.dataset import make_dataloaders

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')

    loaders = make_dataloaders(args.data_root, args.img_size, args.batch_size, args.workers)
    if 'train' not in loaders:
        raise FileNotFoundError(f'No train split found in {args.data_root}')

    model = build_model(args.n_classes).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    best_val_acc = 0.0
    history = []

    for epoch in range(1, args.epochs + 1):
        # ── train ──
        model.train()
        t0 = time.time()
        train_loss, train_correct, train_total = 0.0, 0, 0
        for x, y in loaders['train']:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss   = criterion(logits, y)
            loss.backward()
            optimizer.step()
            train_loss    += loss.item() * len(y)
            train_correct += (logits.argmax(1) == y).sum().item()
            train_total   += len(y)
        scheduler.step()

        # ── val ──
        val_acc = 0.0
        if 'val' in loaders:
            model.eval()
            val_correct, val_total = 0, 0
            with torch.no_grad():
                for x, y in loaders['val']:
                    x, y = x.to(device), y.to(device)
                    val_correct += (model(x).argmax(1) == y).sum().item()
                    val_total   += len(y)
            val_acc = val_correct / max(1, val_total)

        epoch_loss = train_loss / max(1, train_total)
        epoch_acc  = train_correct / max(1, train_total)
        elapsed    = time.time() - t0
        history.append({'epoch': epoch, 'loss': epoch_loss,
                        'train_acc': epoch_acc, 'val_acc': val_acc})
        print(f'Epoch {epoch:3d}/{args.epochs} | '
              f'loss={epoch_loss:.4f} train_acc={epoch_acc:.3f} '
              f'val_acc={val_acc:.3f} | {elapsed:.1f}s')

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            torch.save({'epoch': epoch, 'state_dict': model.state_dict(),
                        'val_acc': val_acc},
                       out_dir / 'blade_defect_best.pt')

    torch.save({'epoch': args.epochs, 'state_dict': model.state_dict()},
               out_dir / 'blade_defect_last.pt')
    (out_dir / 'history.json').write_text(json.dumps(history, indent=2))
    print(f'\nTraining complete. Best val_acc={best_val_acc:.3f}')
    print(f'Checkpoint: {out_dir}/blade_defect_best.pt')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-root',   required=True)
    ap.add_argument('--epochs',      type=int,   default=50)
    ap.add_argument('--batch-size',  type=int,   default=32)
    ap.add_argument('--img-size',    type=int,   default=224)
    ap.add_argument('--lr',          type=float, default=1e-3)
    ap.add_argument('--n-classes',   type=int,   default=5)
    ap.add_argument('--workers',     type=int,   default=4)
    ap.add_argument('--output-dir',  default='weights')
    train(ap.parse_args())


if __name__ == '__main__':
    main()
