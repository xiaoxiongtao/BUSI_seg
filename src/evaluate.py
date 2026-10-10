"""在测试集上评估已训练模型。

用法:
    python -m src.evaluate --checkpoint outputs/unet_xxx/best.pt
"""
import argparse

import torch
from tqdm import tqdm

from src.config import Config
from src.dataset import get_dataloaders
from src.models import build_model
from src.models.losses import get_loss
from src.metrics import MetricsTracker
from src.utils import set_seed, get_device, count_parameters


@torch.no_grad()
def evaluate(model, loader, criterion, device, desc="test"):
    model.eval()
    tracker = MetricsTracker()
    total_loss, total = 0.0, 0
    for images, masks in tqdm(loader, desc=desc, leave=False):
        images, masks = images.to(device), masks.to(device)
        outputs = model(images)
        if isinstance(outputs, (list, tuple)):
            out = outputs[-1]
            loss = torch.mean(torch.stack([criterion(o, masks) for o in outputs]))
        else:
            out = outputs
            loss = criterion(outputs, masks)

        total_loss += loss.item() * images.size(0)
        total += images.size(0)
        tracker.update(torch.sigmoid(out), masks)

    return total_loss / total, tracker.compute()


def evaluate_model(config: Config, checkpoint_path):
    set_seed(config.seed)
    device = get_device()

    ckpt = torch.load(checkpoint_path, map_location=device)
    model_args = ckpt.get("model_args", {})
    model = build_model(**model_args).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    print(f"加载模型: {model_args.get('name')} | 参数量: {count_parameters(model):,} | "
          f"来自 {checkpoint_path}")

    loaders, _ = get_dataloaders(
        config.data_root,
        img_size=config.img_size,
        batch_size=config.batch_size,
        num_workers=config.num_workers,
        val_ratio=config.val_ratio,
        test_ratio=config.test_ratio,
        seed=config.seed,
        include_normal=config.include_normal,
    )
    criterion = get_loss(config.loss)
    loss, metrics = evaluate(model, loaders["test"], criterion, device, desc="test")

    print("测试集结果:")
    print(f"  loss       : {loss:.4f}")
    for k, v in metrics.items():
        print(f"  {k:11s}: {v:.4f}")
    return metrics, count_parameters(model)


def parse_args():
    c = Config()
    p = argparse.ArgumentParser(description="评估已训练的分割模型")
    p.add_argument("--data-root", default=c.data_root)
    p.add_argument("--checkpoint", required=True, help="模型权重 .pt 文件路径")
    p.add_argument("--img-size", type=int, default=c.img_size)
    p.add_argument("--batch-size", type=int, default=c.batch_size)
    p.add_argument("--num-workers", type=int, default=c.num_workers)
    p.add_argument("--seed", type=int, default=c.seed)
    p.add_argument("--loss", default=c.loss)
    args = p.parse_args()

    cfg = Config()
    for k, v in vars(args).items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    return cfg, args.checkpoint


if __name__ == "__main__":
    cfg, ckpt = parse_args()
    evaluate_model(cfg, ckpt)
