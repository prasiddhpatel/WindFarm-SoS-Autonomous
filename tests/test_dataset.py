"""Dataset pipeline tests (no PyTorch required — tests stub when absent)."""
import sys, os, importlib
import numpy as np
import pytest

sys.path.insert(0, '.')


def test_class_names_and_index():
    from training.dataset import CLASS_NAMES, CLASS_TO_IDX
    assert len(CLASS_NAMES) == 5
    assert CLASS_TO_IDX['crack'] == 2
    assert CLASS_TO_IDX['no_defect'] == 0


def test_synthetic_generator(tmp_path):
    from training.generate_synthetic_data import generate
    generate(tmp_path, n_per_class=4, img_size=32)
    rgb_files = list((tmp_path / 'train' / 'crack' / 'rgb').glob('*.jpg'))
    th_files  = list((tmp_path / 'train' / 'crack' / 'thermal').glob('*.png'))
    assert len(rgb_files) >= 1
    assert len(th_files)  >= 1


def test_synthetic_image_shapes(tmp_path):
    from training.generate_synthetic_data import generate
    from PIL import Image
    generate(tmp_path, n_per_class=2, img_size=64)
    img = Image.open(next((tmp_path / 'train' / 'no_defect' / 'rgb').glob('*.jpg')))
    assert img.size == (64, 64)
    assert img.mode == 'RGB'
    th = Image.open(next((tmp_path / 'train' / 'no_defect' / 'thermal').glob('*.png')))
    assert th.size == (64, 64)


def test_dataset_len_and_item(tmp_path):
    torch = pytest.importorskip('torch')
    from training.generate_synthetic_data import generate
    from training.dataset import BladeDefectDataset
    generate(tmp_path, n_per_class=4, img_size=32)
    ds = BladeDefectDataset(tmp_path / 'train', img_size=32, augment=False)
    assert len(ds) > 0
    x, y = ds[0]
    assert x.shape == (4, 32, 32)
    assert 0 <= y < 5


def test_dataset_augment(tmp_path):
    torch = pytest.importorskip('torch')
    from training.generate_synthetic_data import generate
    from training.dataset import BladeDefectDataset
    generate(tmp_path, n_per_class=4, img_size=32)
    ds = BladeDefectDataset(tmp_path / 'train', img_size=32, augment=True)
    x, _ = ds[0]
    assert x.shape[0] == 4
