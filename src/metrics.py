"""分割任务常用指标：Dice、IoU、Precision、Recall、Specificity、Accuracy。"""
import torch

EPS = 1e-7


def confusion_counts(pred: torch.Tensor, target: torch.Tensor):
    """输入二值张量 (0/1)，返回 TP / TN / FP / FN。"""
    pred = pred.bool()
    target = target.bool()
    tp = (pred & target).sum().float()
    tn = ((~pred) & (~target)).sum().float()
    fp = (pred & (~target)).sum().float()
    fn = ((~pred) & target).sum().float()
    return tp, tn, fp, fn


def dice(tp, fp, fn):
    return (2 * tp + EPS) / (2 * tp + fp + fn + EPS)


def iou(tp, fp, fn):
    return (tp + EPS) / (tp + fp + fn + EPS)


def precision(tp, fp):
    return (tp + EPS) / (tp + fp + EPS)


def recall(tp, fn):
    return (tp + EPS) / (tp + fn + EPS)


def specificity(tn, fp):
    return (tn + EPS) / (tn + fp + EPS)


def accuracy(tp, tn, fp, fn):
    return (tp + tn) / (tp + tn + fp + fn + EPS)


class MetricsTracker:
    """跨 batch 累积混淆矩阵，最终一次性计算所有指标。"""

    def __init__(self):
        self.reset()

    def reset(self):
        self.tp = 0.0
        self.tn = 0.0
        self.fp = 0.0
        self.fn = 0.0

    def update(self, pred_probs: torch.Tensor, target: torch.Tensor):
        """pred_probs 为预测概率（0~1），内部按 0.5 阈值二值化。"""
        pred = (pred_probs > 0.5).float()
        tp, tn, fp, fn = confusion_counts(pred, target)
        self.tp += tp.item()
        self.tn += tn.item()
        self.fp += fp.item()
        self.fn += fn.item()

    def compute(self):
        tp, tn, fp, fn = self.tp, self.tn, self.fp, self.fn
        return {
            "dice": float(dice(tp, fp, fn)),
            "iou": float(iou(tp, fp, fn)),
            "precision": float(precision(tp, fp)),
            "recall": float(recall(tp, fn)),
            "specificity": float(specificity(tn, fp)),
            "accuracy": float(accuracy(tp, tn, fp, fn)),
        }
