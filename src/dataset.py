"""BUSI 数据集加载、训练/验证/测试划分与数据增强。

BUSI 数据集目录结构（解压后）:
    Dataset_BUSI_with_GT/
        benign/      benign (1).png, benign (1)_mask.png, ...
        malignant/   malignant (1).png, malignant (1)_mask.png, ...
        normal/      normal (1).png, ...   # normal 无病灶，没有 mask
"""
import random
from pathlib import Path

from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import functional as F
from torchvision.transforms import InterpolationMode
from sklearn.model_selection import train_test_split


CLASSES = ["benign", "malignant", "normal"]
MEAN = [0.5, 0.5, 0.5]
STD = [0.5, 0.5, 0.5]


def collect_samples(data_root, include_normal=True):
    """扫描数据集目录，返回样本列表（图像路径 + mask 路径 + 类别）。"""
    data_root = Path(data_root)
    if not data_root.exists():
        raise FileNotFoundError(
            f"数据集目录不存在: {data_root}\n"
            "请将 BUSI 数据集解压为 data/Dataset_BUSI_with_GT，"
            "使其包含 benign / malignant / normal 三个子目录。"
        )

    samples = []
    for cls in CLASSES:
        if cls == "normal" and not include_normal:
            continue
        cls_dir = data_root / cls
        if not cls_dir.is_dir():
            continue
        for img_path in sorted(cls_dir.glob("*.png")):
            if "_mask" in img_path.name:
                continue
            mask_path = img_path.with_name(img_path.stem + "_mask.png")
            samples.append(
                {
                    "image": str(img_path),
                    "mask": str(mask_path) if mask_path.exists() else None,
                    "class": cls,
                }
            )

    if not samples:
        raise RuntimeError(f"在 {data_root} 中没有找到任何图像，请检查目录结构。")
    return samples


class BUSIDataset(Dataset):
    """返回 (image[C,H,W], mask[1,H,W])，mask 为 0/1。"""

    def __init__(self, samples, img_size=256, augment=False):
        self.samples = samples
        self.img_size = img_size
        self.augment = augment

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        image = Image.open(s["image"]).convert("RGB")
        if s["mask"]:
            mask = Image.open(s["mask"]).convert("L")
        else:
            mask = Image.new("L", image.size, 0)  # normal 图像 mask 全 0

        size = (self.img_size, self.img_size)
        image = F.resize(image, size, interpolation=InterpolationMode.BILINEAR)
        mask = F.resize(mask, size, interpolation=InterpolationMode.NEAREST)

        if self.augment:
            if random.random() < 0.5:
                image = F.hflip(image)
                mask = F.hflip(mask)
            if random.random() < 0.5:
                image = F.vflip(image)
                mask = F.vflip(mask)
            k = random.randint(0, 3)  # 0/90/180/270 度旋转，避免插值破坏 mask
            if k:
                image = F.rotate(image, 90 * k, interpolation=InterpolationMode.BILINEAR)
                mask = F.rotate(mask, 90 * k, interpolation=InterpolationMode.NEAREST)

        image = F.to_tensor(image)
        mask = F.to_tensor(mask)
        image = F.normalize(image, mean=MEAN, std=STD)
        mask = (mask > 0.5).float()
        return image, mask


def split_samples(samples, val_ratio=0.15, test_ratio=0.15, seed=42):
    """按类别分层划分 train/val/test。"""
    labels = [s["class"] for s in samples]
    train_val, test = train_test_split(
        samples, test_size=test_ratio, random_state=seed, stratify=labels
    )
    tv_labels = [s["class"] for s in train_val]
    val_frac = val_ratio / (1 - test_ratio)
    train, val = train_test_split(
        train_val, test_size=val_frac, random_state=seed, stratify=tv_labels
    )
    return train, val, test


def get_dataloaders(
    data_root,
    img_size=256,
    batch_size=8,
    num_workers=0,
    val_ratio=0.15,
    test_ratio=0.15,
    seed=42,
    include_normal=True,
):
    """构建 train/val/test 三个 DataLoader，同时返回划分后的样本字典。"""
    samples = collect_samples(data_root, include_normal=include_normal)
    train, val, test = split_samples(samples, val_ratio, test_ratio, seed)

    train_ds = BUSIDataset(train, img_size=img_size, augment=True)
    val_ds = BUSIDataset(val, img_size=img_size, augment=False)
    test_ds = BUSIDataset(test, img_size=img_size, augment=False)

    loaders = {
        "train": DataLoader(
            train_ds, batch_size=batch_size, shuffle=True,
            num_workers=num_workers, pin_memory=True, drop_last=True,
        ),
        "val": DataLoader(
            val_ds, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=True,
        ),
        "test": DataLoader(
            test_ds, batch_size=batch_size, shuffle=False,
            num_workers=num_workers, pin_memory=True,
        ),
    }
    return loaders, {"train": train, "val": val, "test": test}
