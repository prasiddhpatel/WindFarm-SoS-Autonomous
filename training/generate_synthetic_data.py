#!/usr/bin/env python3
"""Generate a small synthetic dataset for smoke-testing the training pipeline.

Creates data_root/{train,val,test}/<class>/rgb/*.jpg  and
                                           <class>/thermal/*.png
with procedurally generated images.

Usage:
  python3 training/generate_synthetic_data.py --output-dir data/ --n-per-class 20
"""
from __future__ import annotations
import argparse, random
from pathlib import Path
import numpy as np
from PIL import Image

CLASSES = ['no_defect', 'surface_erosion', 'crack', 'delamination', 'lightning_strike']
SPLITS  = {'train': 0.7, 'val': 0.15, 'test': 0.15}


def make_rgb(cls_idx: int, seed: int, size: int = 224) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.integers(80, 200, size=(size, size, 3), dtype=np.uint8)
    if cls_idx == 2:  # crack — thin dark line
        x0 = rng.integers(0, size)
        for dy in range(size):
            xc = x0 + int(dy * rng.uniform(-0.1, 0.1))
            xc = np.clip(xc, 0, size - 1)
            base[dy, max(0,xc-1):xc+2] = [20, 20, 20]
    elif cls_idx == 3:  # delamination — bright blotch
        cx, cy = rng.integers(50, size-50, size=2)
        for i in range(size):
            for j in range(size):
                if (i-cy)**2 + (j-cx)**2 < 900:
                    base[i,j] = np.clip(base[i,j].astype(int) + 60, 0, 255)
    return base


def make_thermal(cls_idx: int, seed: int, size: int = 224) -> np.ndarray:
    rng = np.random.default_rng(seed + 10000)
    base = rng.integers(100, 160, size=(size, size), dtype=np.uint8)
    if cls_idx >= 2:  # hot spot for damage classes
        cx, cy = rng.integers(40, size-40, size=2)
        for i in range(size):
            for j in range(size):
                d2 = (i-cy)**2 + (j-cx)**2
                if d2 < 1600:
                    base[i,j] = min(255, int(base[i,j]) + 60 - d2//50)
    return base


def generate(output_dir: Path, n_per_class: int, img_size: int):
    samples_per_split = {
        'train': max(1, int(n_per_class * SPLITS['train'])),
        'val':   max(1, int(n_per_class * SPLITS['val'])),
        'test':  max(1, int(n_per_class * SPLITS['test'])),
    }
    idx = 0
    for split, n in samples_per_split.items():
        for cls_i, cls_name in enumerate(CLASSES):
            rgb_dir = output_dir / split / cls_name / 'rgb'
            th_dir  = output_dir / split / cls_name / 'thermal'
            rgb_dir.mkdir(parents=True, exist_ok=True)
            th_dir.mkdir(parents=True,  exist_ok=True)
            for k in range(n):
                seed = idx * 1000 + k
                rgb  = make_rgb(cls_i, seed, img_size)
                th   = make_thermal(cls_i, seed, img_size)
                Image.fromarray(rgb).save(rgb_dir / f'{k:04d}.jpg')
                Image.fromarray(th, mode='L').save(th_dir / f'{k:04d}.png')
            idx += 1
    total = sum(samples_per_split.values()) * len(CLASSES)
    print(f'Generated {total} samples across {len(CLASSES)} classes '
          f'in {output_dir} (splits: train/val/test)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir',    default='data')
    ap.add_argument('--n-per-class',   type=int, default=20)
    ap.add_argument('--img-size',      type=int, default=224)
    args = ap.parse_args()
    generate(Path(args.output_dir), args.n_per_class, args.img_size)


if __name__ == '__main__':
    main()
