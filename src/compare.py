"""依次训练并对比 U-Net 与 U-Net++ 的性能。

用法:
    python -m src.compare --epochs 100
    会依次训练两个模型，在测试集上评估，并输出对比表 + 对比柱状图。
"""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.config import Config
from src.train import train_model
from src.evaluate import evaluate_model


METRIC_KEYS = ["dice", "iou", "precision", "recall", "specificity", "accuracy"]


def plot_comparison(results, save_path):
    models = list(results.keys())
    x = np.arange(len(models))
    width = 0.12
    colors = plt.cm.viridis(np.linspace(0, 1, len(METRIC_KEYS)))

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, m in enumerate(METRIC_KEYS):
        vals = [results[mod]["test"][m] for mod in models]
        ax.bar(x + i * width, vals, width, label=m, color=colors[i])

    ax.set_xticks(x + width * (len(METRIC_KEYS) - 1) / 2)
    ax.set_xticklabels([m.upper() for m in models])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("U-Net vs U-Net++ (test set)")
    ax.legend(ncol=len(METRIC_KEYS))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def main():
    cfg = parse_args()

    results = {}
    for name in ["unet", "unetpp"]:
        cfg.model = name
        print(f"\n{'=' * 60}\n训练 {name}\n{'=' * 60}")
        history, best_path, run_dir = train_model(cfg)
        print(f"\n{'=' * 60}\n评估 {name}（测试集）\n{'=' * 60}")
        test_metrics, n_params = evaluate_model(cfg, best_path)
        results[name] = {
            "test": test_metrics,
            "params": n_params,
            "best_val_dice": max(h["val_dice"] for h in history),
            "run_dir": run_dir,
        }

    # 打印对比表
    print("\n" + "=" * 60)
    print("性能对比（测试集）")
    print("=" * 60)
    header = f"{'model':<10}{'params':>12}"
    for m in METRIC_KEYS:
        header += f"{m:>12}"
    print(header)
    for name, r in results.items():
        line = f"{name:<10}{r['params']:>12,}"
        for m in METRIC_KEYS:
            line += f"{r['test'][m]:>12.4f}"
        print(line)

    # 保存对比结果
    save_dir = Path(cfg.output_dir) / "comparison"
    save_dir.mkdir(parents=True, exist_ok=True)
    plot_comparison(results, save_dir / "comparison.png")

    csv_path = save_dir / "comparison.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric"] + list(results.keys()))
        for m in METRIC_KEYS:
            w.writerow([m] + [results[mod]["test"][m] for mod in results])
        w.writerow(["params"] + [results[mod]["params"] for mod in results])
        w.writerow(["best_val_dice"] + [results[mod]["best_val_dice"] for mod in results])
        w.writerow(["run_dir"] + [results[mod]["run_dir"] for mod in results])

    print(f"\n对比结果已保存至 {save_dir}")


def parse_args():
    c = Config()
    p = argparse.ArgumentParser(description="训练并对比 U-Net 与 U-Net++")
    p.add_argument("--data-root", default=c.data_root)
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
    return cfg


if __name__ == "__main__":
    main()
