"""通用工具：随机种子、设备、参数量统计、checkpoint 存取、训练曲线绘制。"""
import math
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

import matplotlib


def _in_notebook() -> bool:
    """判断是否运行在 Jupyter/IPython 中。"""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except Exception:
        return False


# 无显示环境（脚本 / 服务器后台训练）用 Agg 后端；Notebook 中保持 inline 以正常出图。
if not _in_notebook():
    matplotlib.use("Agg")

import matplotlib.pyplot as plt


def set_seed(seed: int = 42):
    """固定随机种子，保证结果可复现。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def count_parameters(model: nn.Module) -> int:
    """统计可训练参数量。"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def make_run_dir(output_dir: str, model: str) -> Path:
    """为一次训练创建带时间戳的输出目录。"""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = Path(output_dir) / f"{model}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_checkpoint(model, optimizer, epoch, best_metric, model_args, path):
    """保存模型权重与训练状态。model_args 记录模型结构，方便评估时重建。"""
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "best_metric": best_metric,
            "model_args": model_args,
        },
        path,
    )


def load_checkpoint(path, model, device, optimizer=None):
    """加载 checkpoint 到模型，可选地恢复优化器。"""
    ckpt = torch.load(path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    if optimizer is not None and "optimizer_state_dict" in ckpt:
        optimizer.load_state_dict(ckpt["optimizer_state_dict"])
    return ckpt


def plot_training_curves(history, save_path):
    """根据 history（每个 epoch 一个 dict）绘制 loss 与各项指标的曲线。"""
    metric_keys = ["dice", "iou", "precision", "recall", "specificity", "accuracy"]
    epochs = [h["epoch"] for h in history]

    n_panels = len(metric_keys) + 1  # +1 给 loss
    cols = 3
    rows = math.ceil(n_panels / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = np.array(axes).reshape(-1)

    # Loss 曲线
    axes[0].plot(epochs, [h["train_loss"] for h in history], label="Train")
    axes[0].plot(epochs, [h["val_loss"] for h in history], label="Val")
    axes[0].set_title("Loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 各项指标曲线
    for i, key in enumerate(metric_keys, start=1):
        ax = axes[i]
        if f"train_{key}" in history[0]:
            ax.plot(epochs, [h[f"train_{key}"] for h in history], label="Train")
            ax.plot(epochs, [h[f"val_{key}"] for h in history], label="Val")
        ax.set_title(key.upper())
        ax.legend()
        ax.grid(True, alpha=0.3)

    # 隐藏多余的子图
    for j in range(n_panels, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Training Curves")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
