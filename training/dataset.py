"""BladeDefectDataset: PyTorch dataset for RGB+thermal blade inspection images.

Directory layout expected:
  data_root/
    train/
      no_defect/      rgb/*.jpg  thermal/*.png
      surface_erosion/
      crack/
      delamination/
      lightning_strike/
    val/
    test/

Each class folder contains two sub-folders:
  rgb/      - 3-channel JPEG/PNG
  thermal/  - 1-channel (greyscale) PNG
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from PIL import Image

try:
    import torch
    from torch.utils.data import Dataset
    import torchvision.transforms.functional as TF
    _TORCH = True
except ImportError:
    _TORCH = False
    Dataset = object  # type: ignore

CLASS_NAMES = [
    'no_defect',
    'surface_erosion',
    'crack',
    'delamination',
    'lightning_strike',
]
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_NAMES)}


class BladeDefectDataset(Dataset):
    """Loads paired RGB + thermal images and returns a 4-channel tensor.

    Parameters
    ----------
    root : str | Path
        Split root, e.g. ``data/train``.
    img_size : int
        Square resize target (default 224).
    augment : bool
        Enable random horizontal flip + colour jitter (training only).
    transform : callable, optional
        Custom transform applied after stacking (receives 4-ch tensor).
    """

    def __init__(self,
                 root: str | Path,
                 img_size: int = 224,
                 augment: bool = False,
                 transform: Optional[Callable] = None):
        if not _TORCH:
            raise ImportError('PyTorch is required for BladeDefectDataset')
        self.root      = Path(root)
        self.img_size  = img_size
        self.augment   = augment
        self.transform = transform
        self.samples: list[tuple[Path, Path, int]] = []
        self._scan()

    # ------------------------------------------------------------------
    def _scan(self):
        for cls_name in CLASS_NAMES:
            cls_dir = self.root / cls_name
            rgb_dir = cls_dir / 'rgb'
            th_dir  = cls_dir / 'thermal'
            if not rgb_dir.exists():
                continue
            label = CLASS_TO_IDX[cls_name]
            for rgb_path in sorted(rgb_dir.iterdir()):
                if rgb_path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                    continue
                th_path = th_dir / (rgb_path.stem + '.png')
                if not th_path.exists():
                    th_path = th_dir / (rgb_path.stem + '.jpg')
                self.samples.append((rgb_path, th_path, label))

    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        import torch
        rgb_path, th_path, label = self.samples[idx]

        rgb = Image.open(rgb_path).convert('RGB').resize(
            (self.img_size, self.img_size), Image.BILINEAR)
        if th_path.exists():
            th = Image.open(th_path).convert('L').resize(
                (self.img_size, self.img_size), Image.BILINEAR)
        else:
            th = Image.fromarray(np.zeros((self.img_size, self.img_size), np.uint8))

        rgb_t = TF.to_tensor(rgb)                       # (3,H,W) [0,1]
        th_t  = TF.to_tensor(th)                        # (1,H,W) [0,1]

        # Normalise
        mean = torch.tensor([0.485, 0.456, 0.406, 0.5]).view(4,1,1)
        std  = torch.tensor([0.229, 0.224, 0.225, 0.2]).view(4,1,1)
        x = torch.cat([rgb_t, th_t], dim=0)
        x = (x - mean) / std

        if self.augment:
            if torch.rand(1).item() > 0.5:
                x = TF.hflip(x)
            if torch.rand(1).item() > 0.5:
                x = TF.vflip(x)
            # Colour jitter on RGB channels only
            rgb_jitter = TF.adjust_brightness(x[:3], 0.8 + 0.4 * torch.rand(1).item())
            x = torch.cat([rgb_jitter, x[3:4]], dim=0)

        if self.transform is not None:
            x = self.transform(x)

        return x, label

    # ------------------------------------------------------------------
    @staticmethod
    def collate_fn(batch):
        import torch
        xs, ys = zip(*batch)
        return torch.stack(xs), torch.tensor(ys, dtype=torch.long)


def make_dataloaders(data_root: str | Path,
                    img_size: int = 224,
                    batch_size: int = 32,
                    num_workers: int = 4):
    """Convenience factory returning train, val, test DataLoaders."""
    import torch
    from torch.utils.data import DataLoader
    root = Path(data_root)
    loaders = {}
    for split in ('train', 'val', 'test'):
        split_dir = root / split
        if not split_dir.exists():
            continue
        ds = BladeDefectDataset(
            split_dir,
            img_size=img_size,
            augment=(split == 'train'),
        )
        loaders[split] = DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=(split == 'train'),
            num_workers=num_workers,
            collate_fn=BladeDefectDataset.collate_fn,
            pin_memory=torch.cuda.is_available(),
        )
    return loaders
