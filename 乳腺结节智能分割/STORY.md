# STORY.md · 《乳腺结节智能分割》教学课件

## ① 用户意图对齐

- **目标受众**：高校课堂学生（医学 AI / 深度学习课程教学场景），授课人按本课件逐页讲解。
- **核心目标**：讲完后学生能（1）说清目标检测与语义分割两类任务的区别与选型理由；（2）画出 YOLO 三段式框架并写出其损失函数构成；（3）画出 U-Net 编码-解码结构、理解 U-Net++ 与深度监督、写出 BCE+Dice 损失；（4）按任务书独立跑通 BUSI 乳腺结节分割实验。
- **PPT 长度**：21 页（教学节奏，含 4 个章节扉页）。
- **视觉调性**：学术严谨 / 蓝白克制 / 证据驱动 / 图示化教学。
- **内容边界**：必讲——临床任务定义、BUSI 数据集、YOLO 框架与损失（检测基础）、U-Net/U-Net++ 结构与分割损失、本项目真实实验结果（Dice 0.738 vs 0.747）、课内实操任务书。不讲——部署与临床落地、Transformer 类分割模型。所有公式与数据必须真实可溯源（YOLOv8 损失构成、U-Net/U-Net++ 原论文、本项目 outputs 实测数据）。

## ② 页面布局骨架

- **目录章节契约**：目录声明 4 章 → 对应 4 个 section 扉页：01 任务与数据（P3）、02 检测基础：YOLO（P7）、03 分割网络：U-Net（P12）、04 实验与实操（P17）。编号 01–04 连续，标题与目录逐字一致。
- **Hero 页**：P1 封面、P5 BUSI 数据集（780 巨型数字）、P8 YOLO 框架总览、P13 U-Net 结构、P18 实验结果、P21 结束页 —— 6/21 ≈ 28.6%，相邻 Hero 间均有 Supporting 页隔开。
- **rhythm 曲线**：peak: P1,P5,P8,P11,P13,P16,P18,P21；transition: P2,P3,P7,P12,P17；valley: P4,P6,P9,P10,P14,P15,P19,P20（无连续 ≥3 valley）。
- **版式分配（非对称 ≥40%）**：P2 左标题+右内容、P4 左大图+右侧文字、P5 巨型数字+洞察、P6 上大图+下方卡片、P7 巨型数字+洞察、P8 上大图+下方卡片、P9 左标题+右内容、P10 非对称双栏、P11 左标题+右内容、P12 巨型数字+洞察、P13 左大图+右侧文字、P14 上大图+下方卡片、P15 左标题+右内容、P16 非对称双栏、P17 巨型数字+洞察、P19 左大图+右侧文字、P20 左标题+右内容 → 非对称 17/21 = 81%。对称仅 P1（封面全屏视觉）、P18（图表+洞察）、P21（居中金句）——P18/P21 为允许的 2 页对称预算。
- **相邻版式检查**：无相邻重复；P1 全屏视觉与 P21 居中金句不相邻。

## ③ 页面大纲

| # | title | type | role | rhythm | layout | visual | visual_role | density | anti_pattern | description |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 乳腺结节智能分割 | cover | hero | peak | 全屏视觉+大标题 | L1: cover_ultrasound.jpg 全屏底图 | anchor | 字数约60 / 图1 / 留白约40% | 禁装饰小图；禁花哨渐变 | 封面：中文主标+英文副标+汇报人/时间，真实超声影像做全屏底 |
| 2 | 课程目录 | catalog | supporting | transition | 左标题+右内容 | L3 编号条 | evidence | 字数约120 / 图0 / 留白约25% | 禁四卡片预览 | 四章导航：任务与数据→YOLO 检测基础→U-Net 分割网络→实验与实操 |
| 3 | 01 任务与数据 | section | transition | transition | 巨型数字+洞察 | 大数字 01 | atmosphere | 字数约80 / 图0 / 留白约45% | 禁正文段落铺满 | 章节扉页：从临床问题出发，认识 BUSI 数据集与任务定义 |
| 4 | 临床问题与任务定义 | content | supporting | valley | 左大图+右侧文字 | L1: malignant_pair.jpg 占左55% | evidence | 字数约260 / 图1 / 留白约18% | 禁50:50等分双栏 | 超声筛查中恶性病灶形态不规则；给出"检测框 vs 像素级分割"任务差异与分割的临床价值（切缘评估、体积测量） |
| 5 | BUSI 数据集 | content | hero | peak | 巨型数字+洞察 | 大数字 780 + 分布 Chart | anchor | 字数约220 / 图1 / 留白约20% | 禁把数字塞进等宽卡片 | 780 张超声图三类分布（良437/恶210/正常133），含 GT mask；判断：病灶像素占比极小，准确率会"虚高"，必须看 Dice/IoU |
| 6 | 数据处理流水线 | content | supporting | valley | 上大图+下方卡片 | Diagram(处理流程) | evidence | 字数约240 / 图1 / 留白约15% | 禁等宽卡片横排当流程 | 流程：原始图+mask → 灰度化/256×256 → 翻转/旋转/亮度增强 → 分层划分 70/15/15 → Dataset/DataLoader |
| 7 | 02 检测基础：YOLO | section | transition | transition | 巨型数字+洞察 | 大数字 02 | atmosphere | 字数约80 / 图0 / 留白约45% | 禁提前展开公式 | 章节扉页：YOLO 三段式框架、核心模块与损失函数 |
| 8 | YOLO 网络框架总览 | content | hero | peak | 上大图+下方卡片 | L1: SVG 三段式架构图（Backbone/Neck/Head） | anchor | 字数约260 / 图1 / 留白约15% | 禁装饰小图顶替主视觉 | Backbone(CBS/C2f/SPPF) → Neck(PAN-FPN 多尺度融合) → Head(anchor-free 解耦头)，640×640 输入，三尺度输出 8/16/32 |
| 9 | YOLO 核心模块拆解 | content | supporting | valley | 左标题+右内容 | Diagram(模块结构) | evidence | 字数约280 / 图1 / 留白约15% | 禁纯文字堆砌 | CBS=Conv+BN+SiLU；C2f 梯度流分支；SPPF 三次 MaxPool 串行；Detect 解耦头分类/回归分支 + anchor-free + TAL 标签分配 |
| 10 | YOLO 损失函数 | content | supporting | valley | 非对称双栏 | Math 公式组 65:35 | anchor | 字数约240 / 图0 / 留白约15% | 禁公式与解释同栏混杂 | 总损失=λbox·CIoU+λcls·BCE+λdfl·DFL；CIoU 公式、DFL 思想（离散化框分布）、权重 7.5/0.5/1.5；判断：检测损失只在正样本处回归框 |
| 11 | 检测 vs 分割：为什么医学影像选 U-Net | content | supporting | peak | 左标题+右内容 | Table 对比 | evidence | 字数约260 / 图0 / 留白约15% | 禁空洞口号无依据 | 检测输出框/类别，分割输出像素 mask；超声病灶边界模糊、形态不规则，框无法刻画切缘 → 需要像素级分割；且医学小数据集适合 U-Net |
| 12 | 03 分割网络：U-Net | section | transition | transition | 巨型数字+洞察 | 大数字 03 | atmosphere | 字数约80 / 图0 / 留白约45% | 禁重复检测章内容 | 章节扉页：编码-解码、跳跃连接、嵌套结构与分割损失 |
| 13 | U-Net 网络结构详解 | content | hero | peak | 左大图+右侧文字 | L1: SVG U-Net 结构图占左60% | anchor | 字数约280 / 图1 / 留白约15% | 禁把结构图缩小为角标 | 编码器 4 次下采样(32→64→128→256→512)、DoubleConv、解码器转置卷积上采样、跳跃连接拼接、1×1 卷积输出；2015 原论文，医学分割基石 |
| 14 | U-Net++：嵌套密集连接与深度监督 | content | supporting | valley | 上大图+下方卡片 | L1: SVG 嵌套结构图占上55% | anchor | 字数约260 / 图1 / 留白约15% | 禁与上页版式雷同 | 嵌套密集跳跃连接缩小语义鸿沟；深度监督对 X^0,1..X^0,4 分别算损失取平均，推理用最深输出；参数量 9.16M vs U-Net 7.76M |
| 15 | 分割损失函数：BCE 与 Dice | content | supporting | valley | 左标题+右内容 | Math 公式组 | evidence | 字数约280 / 图0 / 留白约15% | 禁杜撰公式 | BCE 逐像素；soft Dice 对类别不平衡鲁棒；BCE+Dice 各 0.5（本项目默认）；Focal 缓解难样本；判断：只看 BCE 会被背景淹没 |
| 16 | 评价指标：从混淆矩阵到 Dice | content | supporting | peak | 非对称双栏 | 混淆矩阵 Diagram + 指标 Math | anchor | 字数约260 / 图1 / 留白约15% | 禁只给公式不给直觉 | TP/FP/FN/TN → Dice=2TP/(2TP+FP+FN)、IoU、Precision/Recall/Specificity/Accuracy；判断：像素准确率 95% 也可能没分出病灶 |
| 17 | 04 实验与实操 | section | transition | transition | 巨型数字+洞察 | 大数字 04 | atmosphere | 字数约80 / 图0 / 留白约45% | 禁展开新概念 | 章节扉页：真实训练结果对比 + 课内动手任务 |
| 18 | 实验结果：U-Net vs U-Net++ | content | hero | peak | 图表+洞察 | L1: comparison.jpg 主图 + KPI | anchor | 字数约220 / 图1 / 留白约18% | 禁只摆数字不给判断 | 测试集 Dice 0.738 vs 0.747、IoU 0.585 vs 0.596、Precision 0.776 vs 0.789；U-Net++ 全面略优但参数多 18% → 教学小数据集上两者差距有限，结构收益需更大基数验证 |
| 19 | 训练曲线与预测可视化 | content | supporting | valley | 左大图+右侧文字 | L1: curve_unetpp.jpg + sample_triptych.jpg | evidence | 字数约260 / 图2 / 留白约15% | 禁把曲线图压成缩略图 | 100 epoch 收敛平稳、Dice 爬升至 0.77；三联图演示"原图→GT→叠加"评估口径；恶性病例边界不规则分割更难 |
| 20 | 课内实操任务书 | content | supporting | valley | 左标题+右内容 | 编号步骤 + 验收表 | evidence | 字数约300 / 图0 / 留白约12% | 禁任务描述无验收标准 | 任务四步：跑通训练→换损失对比→调 base_channels/lr→分析失败案例；验收标准：指标 CSV + 对比结论 + 150 字分析 |
| 21 | 总结与思考 | ending | hero | peak | 居中金句/巨型数字 | 核心金句条 | anchor | 字数约160 / 图0 / 留白约40% | 禁新知识点涌入 | 一句总结"检测框定位病灶，像素级分割刻画病灶"+三点回顾+课后思考题 |
