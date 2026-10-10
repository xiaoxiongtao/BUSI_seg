# BUSI 乳腺超声图像分割

基于 [BUSI（Breast Ultrasound Images）数据集](https://www.kaggle.com/datasets/sabahesaraki/breast-ultrasound-images-dataset) 的乳腺病灶语义分割项目，使用 PyTorch 实现了 **U-Net** 和 **U-Net++** 两种模型，包含完整的数据加载、训练、指标统计、评估与可视化流程，并对两种模型的性能进行对比。

## 1. 项目简介

本项目完成以下任务：

- 搭建经典 **U-Net** 与 **U-Net++**（嵌套密集跳跃连接 + 深度监督）分割网络；
- 加载 BUSI 数据集，按类别（benign / malignant / normal）分层划分训练、验证、测试集；
- 训练过程中实时统计并记录多种指标与损失：**Loss、Dice、IoU、Precision、Recall、Specificity、Accuracy**；
- 自动保存最优权重、训练曲线与每轮指标（CSV）；
- 提供 Jupyter Notebook，用于数据探索、模型结构查看、权重加载、结果可视化和性能对比。

## 2. 数据集

**下载地址：** https://www.kaggle.com/datasets/sabahesaraki/breast-ultrasound-images-dataset

BUSI 数据集共包含 780 张乳腺超声图像，分为三类：

| 类别 | 数量 | 是否有病灶 mask |
|------|------|----------------|
| benign（良性） | 437 | 是 |
| malignant（恶性） | 210 | 是 |
| normal（正常） | 133 | 否（无病灶） |

### 数据存放方式

下载并解压后，请将数据集放到项目的 `data/` 目录下，目录结构如下：

```
BUSI_seg/
└── data/
    └── Dataset_BUSI_with_GT/
        ├── benign/
        │   ├── benign (1).png
        │   ├── benign (1)_mask.png
        │   └── ...
        ├── malignant/
        │   ├── malignant (1).png
        │   ├── malignant (1)_mask.png
        │   └── ...
        └── normal/
            ├── normal (1).png
            └── ...
```

> 说明：`normal` 类别图像没有病灶，因此没有 `_mask.png` 文件，代码会自动为其生成全 0 的 mask。如果只想使用有病灶的良性/恶性图像进行训练，可在 `src/config.py` 中将 `include_normal` 设为 `False`。

## 3. 项目结构

```
BUSI_seg/
├── data/                      # 数据集（自行下载后放入）
├── src/
│   ├── config.py              # 超参数配置（数据、模型、训练）
│   ├── dataset.py             # 数据加载、划分与增强
│   ├── metrics.py             # Dice / IoU / Precision / Recall 等指标
│   ├── utils.py               # 随机种子、设备、checkpoint、曲线绘制
│   ├── models/
│   │   ├── blocks.py          # DoubleConv 基础模块
│   │   ├── unet.py            # U-Net
│   │   ├── unetpp.py          # U-Net++
│   │   ├── losses.py          # BCE / Dice / BCE+Dice / Focal 损失
│   │   └── __init__.py        # build_model 工厂函数
│   ├── train.py               # 训练脚本
│   ├── evaluate.py            # 测试集评估脚本
│   └── compare.py             # 一键训练并对比 U-Net 与 U-Net++
├── notebooks/
│   └── visualize.ipynb        # 数据探索 + 模型可视化 + 结果对比 Notebook
├── outputs/                   # 训练结果（权重、指标 CSV、曲线图，自动生成）
├── requirements.txt
└── README.md
```

## 4. 环境安装

建议使用 Python 3.9+，并创建独立虚拟环境：

```bash
# 创建并激活虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

> **GPU 用户**：请先到 https://pytorch.org 根据你的 CUDA 版本安装对应的 `torch` 与 `torchvision`，再安装其余依赖。CPU 也可以训练，只是速度较慢。

## 5. 快速开始

以下命令均需在**项目根目录**（`BUSI_seg/`）下执行。

### 5.1 训练单个模型

```bash
# 训练 U-Net
python -m src.train --model unet --epochs 100

# 训练 U-Net++
python -m src.train --model unetpp --epochs 100
```

训练完成后，在 `outputs/<model>_<时间戳>/` 下会生成：

- `best.pt`：验证集 Dice 最高的模型权重；
- `last.pt`：最后一个 epoch 的权重；
- `metrics.csv`：每个 epoch 的损失与各项指标；
- `training_curves.png`：训练曲线图。

### 5.2 评估模型

```bash
python -m src.evaluate --checkpoint outputs/unet_xxx/best.pt
```

会在测试集上打印 loss 与 Dice、IoU、Precision、Recall、Specificity、Accuracy。

### 5.3 一键对比 U-Net 与 U-Net++

```bash
python -m src.compare --epochs 100
```

该命令会依次训练两个模型，分别在测试集上评估，输出对比表，并在 `outputs/comparison/` 下保存对比柱状图 `comparison.png` 与结果表 `comparison.csv`。

### 5.4 可视化 Notebook

```bash
jupyter notebook notebooks/visualize.ipynb
```

Notebook 内容包含：

1. 数据集概览与样本可视化；
2. 训练/验证/测试集划分；
3. 构建并查看 U-Net / U-Net++ 结构与参数量；
4. 加载训练好的权重并在测试集评估；
5. 预测结果可视化（原图 / 真值 / U-Net / U-Net++ / 叠加图）；
6. 训练曲线与两模型性能对比。

> Notebook 会自动向上查找包含 `src/` 和 `data/` 的项目根目录，因此从项目根目录启动最稳妥。若未训练，Notebook 的权重加载部分会给出提示，先运行 `compare` 或 `train` 即可。

## 6. 模型说明

### 6.1 U-Net

经典编码器-解码器结构：编码器逐层下采样提取特征，解码器通过转置卷积上采样，并通过跳跃连接融合浅层特征，最后用 1×1 卷积输出分割图。

### 6.2 U-Net++

在 U-Net 基础上引入**嵌套密集跳跃连接**，使编码器与解码器之间的语义差距更小；同时支持**深度监督**（对多个浅层输出分别计算损失并平均）。深度监督模式下 `forward` 返回 4 个输出（`X^0,1` 到 `X^0,4`），训练时逐项计算损失取平均，推理时使用最深一层输出作为最终结果。

## 7. 损失与指标说明

**损失函数**（`src/models/losses.py`，通过 `--loss` 选择）：

| 名称 | 说明 |
|------|------|
| `bce_dice`（默认） | BCE 与 Dice 各占 0.5 的加权组合 |
| `bce` | 二分类交叉熵（`BCEWithLogitsLoss`） |
| `dice` | soft Dice 损失 |
| `focal` | Focal Loss，缓解类别不平衡 |

**评估指标**（`src/metrics.py`）：基于像素级混淆矩阵计算

- **Dice**：`2TP / (2TP + FP + FN)`，与病灶重合度；
- **IoU**：`TP / (TP + FP + FN)`，交并比；
- **Precision**：精确率；
- **Recall**：召回率（灵敏度）；
- **Specificity**：特异度；
- **Accuracy**：像素准确率。

## 8. 常用参数说明

训练脚本主要参数（`python -m src.train -h` 查看全部）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--data-root` | `data/Dataset_BUSI_with_GT` | 数据集根目录 |
| `--model` | `unet` | 模型：`unet` 或 `unetpp` |
| `--epochs` | `100` | 训练轮数 |
| `--batch-size` | `8` | 批大小 |
| `--lr` | `1e-3` | 学习率 |
| `--img-size` | `256` | 输入图像尺寸 |
| `--base-channels` | `32` | 第一层通道数 |
| `--loss` | `bce_dice` | 损失函数 |
| `--seed` | `42` | 随机种子 |

其余参数（如 `include_normal`、`deep_supervision`、`val_ratio`、`test_ratio` 等）可在 `src/config.py` 中修改。

## 9. 结果说明

由于乳腺超声病灶占比小、正负样本极不均衡，训练时建议关注 **Dice / IoU**（对目标区域敏感）而非仅看 Accuracy。可尝试调整 `base_channels`、损失函数、学习率或训练轮数来提升效果。

## 10. 参考

- Ronneberger et al., *U-Net: Convolutional Networks for Biomedical Image Segmentation*, 2015.
- Zhou et al., *UNet++: A Nested U-Net Architecture for Medical Image Segmentation*, 2018.
- BUSI 数据集：Al-Dhabyani W, Gomaa M, Khaled H, Fahmy A. *Dataset of breast ultrasound images*. Data in Brief, 2020.


## 11. 作者与版权

- **作者**：肖雄涛
- **版权**：Copyright © 2026 肖雄涛，保留所有权利。
- **用途许可**：本项目（含代码、训练脚本与结果）仅供**学习、教学、科研等非商业用途**使用，**禁止用于任何商业目的**；未经作者书面许可，不得将本项目用于商业用途，或进行销售、再分发、商业部署。