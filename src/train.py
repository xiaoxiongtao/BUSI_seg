"""U-Net / U-Net++ 训练脚本。

用法（在项目根目录下）:
    python -m src.train --model unet   --epochs 100
    python -m src.train --model unetpp --epochs 100
"""
import argparse
import csv

import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

from src.config import Config
from src.dataset import get_dataloaders
from src.models import build_model
from src.models.losses import get_loss
from src.metrics import MetricsTracker
from src.utils import (
    set_seed, get_device, count_parameters, make_run_dir,
    save_checkpoint, plot_training_curves,
)


def compute_loss(outputs, target, criterion):
    """UNet++ 深度监督输出为 list，逐项求 loss 后取平均。"""
    if isinstance(outputs, (list, tuple)):
        return torch.mean(torch.stack([criterion(o, target) for o in outputs]))
    return criterion(outputs, target)


def get_pred(outputs):
    """取最终预测概率；UNet++ 深度监督时使用最深一层输出。"""
    out = outputs[-1] if isinstance(outputs, (list, tuple)) else outputs
    return torch.sigmoid(out)


def train_one_epoch(model, loader, criterion, optimizer, device, desc="train"):
    model.train()
    tracker = MetricsTracker()
    total_loss, total = 0.0, 0
    for images, masks in tqdm(loader, desc=desc, leave=False):
        images, masks = images.to(device), masks.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = compute_loss(outputs, masks, criterion)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        total += images.size(0)
        tracker.update(get_pred(outputs), masks)

    return total_loss / total, tracker.compute()


@torch.no_grad()
def evaluate_loader(model, loader, criterion, device, desc="val"):
    model.eval()
    tracker = MetricsTracker()
    total_loss, total = 0.0, 0
    for images, masks in tqdm(loader, desc=desc, leave=False):
        images, masks = images.to(device), masks.to(device)
        outputs = model(images)
        loss = compute_loss(outputs, masks, criterion)
        total_loss += loss.item() * images.size(0)
        total += images.size(0)
        tracker.update(get_pred(outputs), masks)

    return total_loss / total, tracker.compute()


def log_epoch(epoch, epochs, train_loss, val_loss, train_m, val_m):
    print(
        f"Epoch {epoch:3d}/{epochs} | "
        f"loss: {train_loss:.4f}/{val_loss:.4f} | "
        f"dice: {train_m['dice']:.4f}/{val_m['dice']:.4f} | "
        f"iou: {train_m['iou']:.4f}/{val_m['iou']:.4f} | "
        f"prec: {train_m['precision']:.4f}/{val_m['precision']:.4f} | "
        f"rec: {train_m['recall']:.4f}/{val_m['recall']:.4f}"
    )


def train_model(config: Config):
    set_seed(config.seed)
    device = get_device()
    print(f"使用设备: {device}")

    loaders, split = get_dataloaders(
        config.data_root,
        img_size=config.img_size,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        val_ratio=config.val_ratio,
        test_ratio=config.test_ratio,
        seed=config.seed,
        include_normal=config.include_normal,
    )
    print(f"样本划分 - train: {len(split['train'])} | "
          f"val: {len(split['val'])} | test: {len(split['test'])}")

    model_args = dict(
        name=config.model,
        in_channels=config.in_channels,
        out_channels=config.num_classes,
        base_channels=config.base_channels,
        deep_supervision=config.deep_supervision,
    )
    model = build_model(**model_args).to(device)
    print(f"模型: {config.model} | 可训练参数量: {count_parameters(model):,}")

    criterion = get_loss(config.loss)
    optimizer = AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=config.epochs)

    run_dir = make_run_dir(config.output_dir, config.model)
    print(f"输出目录: {run_dir}")

    history = []
    best_dice = -1.0
    best_path = run_dir / "best.pt"

    for epoch in range(1, config.epochs + 1):
        train_loss, train_m = train_one_epoch(
            model, loaders["train"], criterion, optimizer, device, desc="train")
        val_loss, val_m = evaluate_loader(
            model, loaders["val"], criterion, device, desc="val")
        scheduler.step()

        row = {"epoch": epoch,
               "train_loss": round(train_loss, 6),
               "val_loss": round(val_loss, 6)}
        for k, v in train_m.items():
            row[f"train_{k}"] = round(v, 6)
        for k, v in val_m.items():
            row[f"val_{k}"] = round(v, 6)
        history.append(row)

        log_epoch(epoch, config.epochs, train_loss, val_loss, train_m, val_m)

        save_checkpoint(model, optimizer, epoch, val_m["dice"], model_args,
                        run_dir / "last.pt")
        if val_m["dice"] > best_dice:
            best_dice = val_m["dice"]
            save_checkpoint(model, optimizer, epoch, val_m["dice"], model_args,
                            best_path)
            print(f"  -> 新的最佳验证 Dice: {best_dice:.4f}，已保存 {best_path.name}")

    csv_path = run_dir / "metrics.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(history[0].keys()))
        writer.writeheader()
        writer.writerows(history)
    plot_training_curves(history, run_dir / "training_curves.png")
    print(f"训练完成。指标已保存至 {csv_path}")

    return history, str(best_path), str(run_dir)


def parse_args():
    c = Config()
    p = argparse.ArgumentParser(description="训练 U-Net / U-Net++ 分割模型")
    p.add_argument("--data-root", default=c.data_root)
    p.add_argument("--model", default=c.model, choices=["unet", "unetpp", "unet++"])
    p.add_argument("--epochs", type=int, default=c.epochs)
    p.add_argument("--batch-size", type=int, default=c.batch_size)
    p.add_argument("--lr", type=float, default=c.lr)
    p.add_argument("--img-size", type=int, default=c.img_size)
    p.add_argument("--base-channels", type=int, default=c.base_channels)
    p.add_argument("--loss", default=c.loss, choices=["bce", "dice", "bce_dice", "focal"])
    p.add_argument("--num-workers", type=int, default=c.num_workers)
    p.add_argument("--seed", type=int, default=c.seed)
    p.add_argument("--output-dir", default=c.output_dir)
    args = p.parse_args()

    cfg = Config()
    for k, v in vars(args).items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    cfg.model = "unetpp" if cfg.model in ("unetpp", "unet++") else "unet"
    return cfg


if __name__ == "__main__":
    train_model(parse_args())
