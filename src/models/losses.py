"""分割损失函数：BCE、Dice、BCE+Dice、Focal。"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """soft Dice 损失，输入为 logits。"""

    def __init__(self, smooth=1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, target):
        probs = torch.sigmoid(logits)
        num = (probs * target).sum(dim=(1, 2, 3))
        den = probs.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3))
        dice = (2 * num + self.smooth) / (den + self.smooth)
        return 1 - dice.mean()


class FocalLoss(nn.Module):
    """二分类 Focal Loss，缓解类别不平衡。"""

    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, target):
        bce = F.binary_cross_entropy_with_logits(logits, target, reduction="none")
        p = torch.sigmoid(logits)
        p_t = p * target + (1 - p) * (1 - target)  # 预测正确的概率
        loss = self.alpha * (1 - p_t) ** self.gamma * bce
        return loss.mean()


class BCEDiceLoss(nn.Module):
    """BCE 与 Dice 的加权组合，二分类分割常用。"""

    def __init__(self, bce_weight=0.5, dice_weight=0.5):
        super().__init__()
        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

    def forward(self, logits, target):
        return (self.bce_weight * self.bce(logits, target)
                + self.dice_weight * self.dice(logits, target))


def get_loss(name):
    name = name.lower()
    if name == "bce":
        return nn.BCEWithLogitsLoss()
    if name == "dice":
        return DiceLoss()
    if name == "focal":
        return FocalLoss()
    if name == "bce_dice":
        return BCEDiceLoss()
    raise ValueError(f"未知损失: {name}，可选: bce / dice / bce_dice / focal")
