"""集中管理数据、模型、训练相关的超参数。"""
from dataclasses import dataclass


@dataclass
class Config:
    # ---------- 数据 ----------
    data_root: str = "data/Dataset_BUSI_with_GT"  # BUSI 数据集根目录（解压后）
    img_size: int = 256                           # 输入图像尺寸（正方形）
    include_normal: bool = True                   # 是否将 normal（无病灶）图像纳入训练
    val_ratio: float = 0.15                       # 验证集比例
    test_ratio: float = 0.15                      # 测试集比例
    num_workers: int = 0                          # Windows 上建议设为 0

    # ---------- 模型 ----------
    model: str = "unet"           # "unet" 或 "unetpp"
    in_channels: int = 3
    num_classes: int = 1          # 二分类分割（病灶 / 背景）
    base_channels: int = 32       # 第一层通道数，越大模型越大
    deep_supervision: bool = True  # 仅对 UNet++ 生效

    # ---------- 训练 ----------
    epochs: int = 100
    batch_size: int = 8
    lr: float = 1e-3
    weight_decay: float = 1e-4
    loss: str = "bce_dice"        # bce_dice / dice / bce / focal
    seed: int = 42

    # ---------- 输出 ----------
    output_dir: str = "outputs"
