# -*- coding: utf-8 -*-
"""《乳腺结节智能分割》教学课件生成脚本（备用通道，python-pptx 直出）。
布局规范与 STORY.md / 学术风设计原则一致：1280x720 画布、蓝白学术风。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

BASE = os.path.dirname(os.path.abspath(__file__))
FDIR = os.path.join(BASE, 'assets', 'formulas')
os.makedirs(FDIR, exist_ok=True)

EMU_PX = 9525
def u(px): return Emu(int(round(px * EMU_PX)))

DEEP = RGBColor(0x0E, 0x3F, 0x8C)
BLUE = RGBColor(0x1E, 0x4F, 0xA8)
BLUE2 = RGBColor(0x2A, 0x5C, 0xB0)
MID = RGBColor(0x3D, 0x7B, 0xD9)
MID2 = RGBColor(0x6C, 0x97, 0xD8)
LIGHT = RGBColor(0xE8, 0xEF, 0xF8)
LIGHT2 = RGBColor(0xF0, 0xF5, 0xFC)
BG = RGBColor(0xF7, 0xF9, 0xFC)
TEXT = RGBColor(0x1A, 0x22, 0x30)
SUB = RGBColor(0x4A, 0x55, 0x68)
GRAY = RGBColor(0x8B, 0x97, 0xA8)
LINE = RGBColor(0xD6, 0xDC, 0xE5)
RED = RGBColor(0xD9, 0x53, 0x4F)
YELLOW = RGBColor(0xFF, 0xC1, 0x07)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CDEEP = RGBColor(0xDC, 0xE6, 0xF5)
FONT = '微软雅黑'

prs = Presentation()
prs.slide_width = u(1280)
prs.slide_height = u(720)
BLANK = prs.slide_layouts[6]


def set_run(run, text, size, color, bold, italic=False, font=FONT):
    run.text = text
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.name = font
    f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        e = rPr.find(qn(tag))
        if e is None:
            e = rPr.makeelement(qn(tag), {})
            rPr.append(e)
        e.set('typeface', font)


def add_text(slide, x, y, w, h, content, size=18, color=TEXT, bold=False,
             align='l', anchor='t', lh=1.25, font=FONT, italic=False):
    tb = slide.shapes.add_textbox(u(x), u(y), u(w), u(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    amap = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}
    paras = content if isinstance(content, list) else [content]
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = amap[align]
        para.line_spacing = lh
        runs = p if isinstance(p, list) else [(p, {})]
        for txt, st in runs:
            r = para.add_run()
            set_run(r, txt, st.get('size', size), st.get('color', color),
                    st.get('bold', bold), st.get('italic', italic), st.get('font', font))
    return tb


def add_rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, radius=None, alpha=None):
    shp_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius is not None else MSO_SHAPE.RECTANGLE
    sp = slide.shapes.add_shape(shp_type, u(x), u(y), u(w), u(h))
    if radius is not None and radius is not False:
        try:
            sp.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
        if alpha is not None:
            sF = sp.fill._xPr.find(qn('a:solidFill'))
            clr = sF.find(qn('a:srgbClr'))
            a = clr.makeelement(qn('a:alpha'), {'val': str(int(alpha * 1000))})
            clr.append(a)
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    sp.text_frame.paragraphs[0].text = ''
    return sp


def add_line(slide, x1, y1, x2, y2, color=MID, w=1.5, dash=None):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, u(x1), u(y1), u(x2), u(y2))
    ln.line.color.rgb = color
    ln.line.width = Pt(w)
    if dash:
        lnEl = ln.line._get_or_add_ln()
        d = lnEl.makeelement(qn('a:prstDash'), {'val': dash})
        lnEl.append(d)
    ln.shadow.inherit = False
    return ln


def add_arrow_r(slide, x, y, w=24, h=16, color=MID):
    sp = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, u(x), u(y), u(w), u(h))
    sp.adjustments[0] = 0.55
    sp.adjustments[1] = 0.55
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def add_arrow_d(slide, x, y, h=18, w=14, color=MID):
    sp = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, u(x), u(y), u(w), u(h))
    sp.adjustments[0] = 0.55
    sp.adjustments[1] = 0.55
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def add_arrow_diag(slide, x1, y1, x2, y2, w=14, color=MID):
    """斜向箭头：细线 + 末端小三角（简化为线 + 中点圆头）"""
    add_line(slide, x1, y1, x2, y2, color=color, w=2)
    return None


_f_count = [0]
def add_formula(slide, x, y, latex, w_px, color='#1A2230', fontsize=20):
    _f_count[0] += 1
    path = os.path.join(FDIR, 'f%02d.png' % _f_count[0])
    tex = latex if latex.strip().startswith('$') else '$%s$' % latex
    fig = plt.figure(figsize=(6, 1.5))
    t = fig.text(0.02, 0.5, tex, fontsize=fontsize, color=color, va='center')
    fig.canvas.draw()
    bbox = t.get_window_extent(fig.canvas.get_renderer())
    iw = max(bbox.width / fig.dpi, 0.4)
    ih = max(bbox.height / fig.dpi, 0.25)
    plt.close(fig)
    fig = plt.figure(figsize=(iw + 0.08, ih + 0.08))
    fig.text(0.5, 0.5, tex, fontsize=fontsize, color=color, va='center', ha='center')
    fig.savefig(path, dpi=300, transparent=True, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    im = Image.open(path)
    h_px = w_px * im.height / im.width
    slide.shapes.add_picture(path, u(x), u(y), u(w_px), u(h_px))
    return h_px


def page_frame(slide, num, title, chapter):
    add_rect(slide, 0, 0, 1280, 8, fill=BLUE)
    add_text(slide, 40, 26, 900, 60, title, size=30, color=DEEP, bold=True)
    add_rect(slide, 1020, 34, 220, 36, fill=LIGHT, radius=0.5)
    add_text(slide, 1020, 40, 220, 26, chapter, size=15, color=BLUE, align='c')
    add_rect(slide, 40, 92, 1200, 2, fill=LINE)
    add_rect(slide, 0, 670, 1280, 50, fill=BG)
    add_rect(slide, 0, 670, 1280, 1, fill=RGBColor(0xE5, 0xE7, 0xEB))
    add_text(slide, 40, 686, 500, 22, '乳腺结节智能分割 · 教学课件', size=12, color=GRAY)
    add_text(slide, 1100, 686, 140, 22, '%02d / 21' % num, size=13, color=BLUE, align='r')


def card(slide, x, y, w, h, fill=BG, border=True, line_color=None):
    return add_rect(slide, x, y, w, h, fill=fill,
                    line=(line_color or (LINE if border else None)), lw=1.0, radius=0.06)


def section_page(num, part_en, title, desc, tags, pageno=None):
    s = prs.slides.add_slide(BLANK)
    add_rect(s, 0, 0, 1280, 720, fill=BG)
    add_rect(s, 0, 0, 1280, 8, fill=BLUE)
    add_text(s, 66, 30, 500, 340, '%02d' % num, size=250, color=CDEEP, bold=True)
    add_rect(s, 524, 216, 10, 44, fill=YELLOW)
    add_text(s, 552, 218, 660, 34, part_en, size=19, color=MID, bold=True)
    add_text(s, 552, 258, 680, 70, title, size=42, color=DEEP, bold=True)
    add_text(s, 552, 336, 660, 130, desc, size=20, color=SUB, lh=1.5)
    x = 552
    for t in tags:
        w = 34 + 15 * len(t)
        add_rect(s, x, 486, w, 42, fill=LIGHT, radius=0.5)
        add_text(s, x, 495, w, 26, t, size=16, color=BLUE, align='c')
        x += w + 12
    add_rect(s, 0, 670, 1280, 50, fill=WHITE)
    add_rect(s, 0, 670, 1280, 1, fill=RGBColor(0xE5, 0xE7, 0xEB))
    add_text(s, 40, 686, 500, 22, '乳腺结节智能分割 · 教学课件', size=12, color=GRAY)
    add_text(s, 1100, 686, 140, 22, '%02d / 21' % (pageno or (num + 2)), size=13, color=BLUE, align='r')
    return s


# ============================================================ P1 封面
s = prs.slides.add_slide(BLANK)
s.shapes.add_picture(os.path.join(BASE, 'assets', 'cover_ultrasound.jpg'), 0, 0, u(1280), u(720))
add_rect(s, 0, 0, 1280, 720, fill=RGBColor(0x0A, 0x28, 0x5F), alpha=62)
add_rect(s, 0, 0, 1280, 8, fill=BLUE)
add_rect(s, 96, 96, 330, 40, fill=WHITE, alpha=14, radius=0.5, line=RGBColor(0xFF, 0xFF, 0xFF), lw=0.75)
add_text(s, 96, 104, 330, 26, '深度学习与医学影像 · 课程教学课件', size=15, color=WHITE, align='c')
add_text(s, 96, 168, 1100, 110, '乳腺结节智能分割', size=72, color=WHITE, bold=True)
add_text(s, 96, 292, 1100, 36, 'Intelligent Segmentation of Breast Lesions in Ultrasound Images',
         size=22, color=LIGHT, italic=True, font='Georgia')
add_rect(s, 96, 344, 110, 4, fill=YELLOW)
add_text(s, 96, 372, 1050, 100,
         'U-Net 与 U-Net++ 的网络结构讲解',
         size=23, color=WHITE)
add_text(s, 96, 412, 1050, 40, '与两个网络在 BUSI 数据集上的性能对比', size=23, color=WHITE)
add_rect(s, 0, 656, 1280, 64, fill=RGBColor(0x0A, 0x28, 0x5F), alpha=72)
add_text(s, 96, 676, 400, 26, '主讲：肖雄涛', size=17, color=WHITE)
add_text(s, 500, 676, 690, 26, '基于 BUSI 乳腺超声数据集（780 例） · 2026 年 10 月',
         size=16, color=LIGHT, align='r')

# ============================================================ P2 目录
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 340, 720, fill=DEEP)
add_rect(s, 0, 0, 1280, 8, fill=BLUE)
add_text(s, 44, 150, 252, 80, '目录', size=56, color=WHITE, bold=True)
add_text(s, 44, 236, 252, 30, 'CONTENTS', size=19, color=RGBColor(0x9F, 0xB6, 0xDE))
add_rect(s, 44, 278, 56, 4, fill=YELLOW)
add_text(s, 44, 310, 250, 120,
         ['四个章节，一条主线：', '同一个任务，两个网络'], size=16, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.6)
add_text(s, 44, 660, 252, 24, '乳腺结节智能分割 · 教学课件', size=12, color=RGBColor(0x9F, 0xB6, 0xDE))
catalog = [
    ('01', '任务与数据：从临床问题到 BUSI 数据集', '为什么必须是像素级分割 · 780 例数据与预处理流水线'),
    ('02', '分割网络：U-Net 与 U-Net++ 结构详解', '编解码通用范式与五大模块 · U-Net 跳跃连接 · U-Net++ 嵌套密集连接与深度监督 · 两网络结构对比'),
    ('03', '损失函数与评价指标', 'BCE + Dice 为什么更适配不平衡数据 · 混淆矩阵、Dice 与 IoU'),
    ('04', '实验与实操：真实结果对比与课内任务', '公平实验设置 · U-Net vs U-Net++ 实测 Dice 0.738 / 0.747 · 分组动手任务书'),
]
yy = 108
for i, (no, t1, t2) in enumerate(catalog):
    card(s, 400, yy, 820, 118, fill=(LIGHT2 if i == 2 else BG))
    add_rect(s, 426, yy + 27, 64, 64, fill=(DEEP if i == 2 else BLUE), radius=0.15)
    add_text(s, 426, yy + 42, 64, 34, no, size=24, color=WHITE, bold=True, align='c')
    add_text(s, 514, yy + 24, 680, 34, t1, size=23, color=TEXT, bold=True)
    add_text(s, 514, yy + 64, 680, 28, t2, size=15, color=SUB)
    yy += 142
add_rect(s, 340, 670, 940, 50, fill=WHITE)
add_rect(s, 340, 670, 940, 1, fill=RGBColor(0xE5, 0xE7, 0xEB))
add_text(s, 1140, 686, 120, 22, '02 / 21', size=13, color=BLUE, align='r')

# ============================================================ P3 章节1
section_page(1, 'PART 01 · TASK & DATA', '任务与数据',
             '从乳腺超声筛查的临床痛点出发，明确像素级分割的任务定义与临床价值，'
             '并认识本项目使用的 BUSI 数据集与其预处理流水线。',
             ['临床问题', '任务定义', 'BUSI 数据集', '数据增强'])

# ============================================================ P4 临床问题
s = prs.slides.add_slide(BLANK)
page_frame(s, 4, '临床问题与任务定义：为什么需要像素级分割', '01 任务与数据')
card(s, 40, 110, 660, 370)
s.shapes.add_picture(os.path.join(BASE, 'assets', 'malignant_pair.jpg'), u(56), u(126), u(628), u(307))
add_text(s, 56, 442, 300, 24, 'malignant (5) 原图：边界模糊、形态不规则', size=14, color=SUB)
add_text(s, 366, 442, 318, 24, '医师标注 GT mask（红色叠加）', size=14, color=RED, align='r')
add_rect(s, 40, 496, 660, 152, fill=LIGHT, radius=0.08)
add_text(s, 64, 516, 612, 116, [
    [('同一张图，医师给出的是', {}), ('逐像素的病灶轮廓', {'bold': True}),
     ('，而不是一个矩形框——边界模糊、毛刺状的恶性病灶，矩形框无法刻画其真实形态。', {})],
], size=17, color=DEEP, lh=1.5)
blocks = [
    ('1', '临床痛点', '乳腺超声是筛查一线手段，但良恶性结节的灰度表现重叠，人工勾画轮廓耗时且观察者间差异大。'),
    ('2', '任务定义', '语义分割 = 对每个像素做二分类（病灶 / 背景），输出与原图等大小的概率图，阈值化后得到 mask。'),
    ('3', '临床价值', '精确轮廓支撑病灶体积测量、形态学特征（毛刺、纵横比）量化与 BI-RADS 分级辅助。'),
]
yy = 110
for no, t, d in blocks:
    card(s, 724, yy, 516, 148)
    add_rect(s, 744, yy + 22, 36, 36, fill=BLUE, radius=0.2)
    add_text(s, 744, yy + 28, 36, 24, no, size=16, color=WHITE, bold=True, align='c')
    add_text(s, 794, yy + 26, 420, 30, t, size=20, color=DEEP, bold=True)
    add_text(s, 744, yy + 68, 476, 72, d, size=15, color=SUB, lh=1.45)
    yy += 162
add_rect(s, 724, 592, 516, 66, fill=DEEP, radius=0.08)
add_text(s, 744, 600, 478, 56, '本课主线：同一个任务、同一份数据与同一套训练设置，'
                               '只换网络结构——看 U-Net 与 U-Net++ 究竟差在哪。',
         size=13.5, color=WHITE, bold=True, lh=1.35)

# ============================================================ P5 BUSI 数据集
s = prs.slides.add_slide(BLANK)
page_frame(s, 5, 'BUSI 数据集：780 例乳腺超声与像素级标注', '01 任务与数据')
add_text(s, 40, 112, 470, 110, '780', size=92, color=BLUE, bold=True)
add_text(s, 40, 238, 470, 34, '张乳腺超声图像（含医师标注 mask）', size=19, color=SUB)
stats = [('437', '良性 benign', DEEP), ('210', '恶性 malignant', RED), ('133', '正常 normal', SUB)]
xx = 40
for v, t, c in stats:
    add_rect(s, xx, 296, 146, 84, fill=LIGHT2, radius=0.1, line=LINE, lw=0.75)
    add_text(s, xx, 306, 146, 40, v, size=30, color=c, bold=True, align='c')
    add_text(s, xx, 348, 146, 24, t, size=14, color=SUB, align='c')
    xx += 162
add_rect(s, 40, 396, 470, 178, fill=LIGHT, radius=0.08)
add_text(s, 64, 414, 424, 150, [
    [('数据来源：Al-Dhabyani et al., ', {}), ('Data in Brief', {'italic': True}), (', 2020。', {})],
    '良 / 恶图像均带 _mask.png 像素级真值；normal 无病灶，训练中自动生成全 0 mask。',
], size=15, color=DEEP, lh=1.45)
card(s, 540, 110, 700, 408)
cd = CategoryChartData()
cd.categories = ['良性 benign', '恶性 malignant', '正常 normal']
cd.add_series('样本数', (437, 210, 133))
gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, u(560), u(124), u(660), u(380), cd)
ch = gf.chart
ch.has_title = True
ch.chart_title.text_frame.text = 'BUSI 三类样本分布（共 780 张）'
for r in ch.chart_title.text_frame.paragraphs[0].runs:
    set_run(r, r.text, 16, TEXT, True)
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(13)
plot = ch.plots[0]
plot.has_data_labels = True
plot.data_labels.show_value = True
plot.data_labels.font.size = Pt(13)
plot.data_labels.font.bold = True
plot.data_labels.font.color.rgb = WHITE
pts = list(plot.series[0].points)
for p, c in zip(pts, [BLUE, RED, GRAY]):
    p.format.fill.solid()
    p.format.fill.fore_color.rgb = c
add_rect(s, 540, 534, 700, 124, fill=DEEP, radius=0.08)
add_text(s, 564, 550, 652, 96, [
    [('关键判断：病灶像素通常只占整图的极小部分，像素准确率会"虚高"到 95% 以上——'
      '因此本项目全程以 ', {}), ('Dice / IoU', {'color': YELLOW, 'bold': True}),
     (' 作为模型选择与对比的核心指标。', {})],
], size=16, color=WHITE, bold=False, lh=1.5)

# ============================================================ P6 数据流水线
s = prs.slides.add_slide(BLANK)
page_frame(s, 6, '数据处理流水线：从原始图像到 DataLoader', '01 任务与数据')
card(s, 40, 112, 1200, 230)
steps = [('图像 + mask', '原图与 _mask.png 成对读取', BLUE, WHITE),
         ('预处理', '统一缩放 256×256 归一化', MID, WHITE),
         ('数据增强', '水平翻转 / 旋转 / 亮度扰动', MID, WHITE),
         ('分层划分', '按类别 70% / 15% / 15%', BLUE, WHITE),
         ('DataLoader', 'batch = 8 随机打乱', DEEP, WHITE)]
xx = 60
for i, (t, d, c, tc) in enumerate(steps):
    add_rect(s, xx, 158, 186, 108, fill=c, radius=0.1)
    add_text(s, xx, 178, 186, 30, t, size=17, color=tc, bold=True, align='c')
    add_text(s, xx + 6, 212, 174, 46, d, size=12, color=RGBColor(0xDC, 0xE6, 0xF5), align='c', lh=1.3)
    if i < 4:
        add_arrow_r(s, xx + 194, 200, 24, 22)
    xx += 226
pipes = [
    ('为什么统一 256×256？',
     'BUSI 原图尺寸不一，编码-解码结构要求固定输入。分辨率取 256 在保留病灶纹理与显存开销之间取得平衡，'
     'mask 同步最近邻插值以保持 0/1 标签。', '配置项：config.img_size = 256'),
    ('为什么必须分层划分？',
     '三类样本比例约 437 : 210 : 133，若随机打乱，测试集可能良恶性分布失衡。'
     '按类别分层抽样保证每个子集分布一致，指标才可比、可复现（seed = 42）。', '训练 / 验证 / 测试 = 70 / 15 / 15'),
]
xx = 40
for t, d, tag in pipes:
    card(s, xx, 366, 590, 292)
    add_text(s, xx + 24, 388, 542, 34, t, size=21, color=DEEP, bold=True)
    add_text(s, xx + 24, 430, 542, 150, d, size=16, color=SUB, lh=1.55)
    add_rect(s, xx + 24, 596, 320, 40, fill=LIGHT, radius=0.2)
    add_text(s, xx + 24, 606, 320, 24, tag, size=14, color=BLUE, align='c')
    xx += 610

# ============================================================ P7 章节2
section_page(2, 'PART 02 · SEGMENTATION NETWORK', '分割网络的结构与对比',
             '医学图像分割的基石是如何工作的：编码-解码结构为什么能同时保住"看得懂"的语义与"画得准"的细节，'
             '以及 U-Net++ 在 U-Net 之上做了哪些针对性改良。',
             ['通用范式', '核心模块', 'U-Net 结构', 'U-Net++ 结构', '两网络对比'], pageno=7)

# ============================================================ P8 通用范式
s = prs.slides.add_slide(BLANK)
page_frame(s, 8, '分割网络的通用范式：编码器 → 瓶颈 → 解码器', '02 分割网络')
card(s, 40, 104, 1200, 330)
add_text(s, 40, 116, 1200, 22,
         '方块高度 = 特征图空间分辨率（越高越细）；方块颜色 = 语义抽象程度（越深越抽象）',
         size=12.5, color=SUB, align='c')
CY = 252
_res = [('256\u00b2', 196), ('128\u00b2', 164), ('64\u00b2', 132), ('32\u00b2', 100)]
enc_x = [200, 296, 392, 488]
for i, (lbl, hh) in enumerate(_res):
    add_rect(s, enc_x[i], CY - hh / 2, 78, hh, fill=[BLUE, BLUE2, MID, MID2][i], radius=0.08)
    add_text(s, enc_x[i], CY - 14, 78, 28, ['32', '64', '128', '256'][i] + 'ch',
             size=12.5, color=WHITE, bold=True, align='c')
    add_text(s, enc_x[i] - 6, 348, 90, 20, lbl, size=11, color=SUB, align='c')
add_rect(s, 584, CY - 34, 78, 68, fill=DEEP, radius=0.08)
add_text(s, 584, CY - 14, 78, 28, '512ch', size=12.5, color=WHITE, bold=True, align='c')
add_text(s, 578, 348, 90, 20, '16\u00b2', size=11, color=SUB, align='c')
dec_x = [680, 776, 872, 968]
for i, (lbl, hh) in enumerate(_res):
    fill = [MID2, MID, BLUE2, BLUE][i]
    add_rect(s, dec_x[i], CY - hh / 2, 78, hh, fill=fill, radius=0.08)
    add_text(s, dec_x[i], CY - 14, 78, 28, ['256', '128', '64', '32'][i] + 'ch',
             size=12.5, color=WHITE, bold=True, align='c')
    add_text(s, dec_x[i] - 6, 348, 90, 20, lbl, size=11, color=SUB, align='c')
add_rect(s, 70, 155, 110, 194, fill=WHITE, line=MID, lw=1.5, radius=0.06)
add_text(s, 70, 234, 110, 40, ['超声图像', '3 通道'], size=13, color=DEEP, bold=True, align='c', lh=1.4)
add_rect(s, 1066, 155, 110, 194, fill=WHITE, line=YELLOW, lw=2.5, radius=0.06)
add_text(s, 1066, 234, 110, 40, ['概率图', '1 通道'], size=13, color=DEEP, bold=True, align='c', lh=1.4)
for x1, x2 in [(239, 1007), (335, 911), (431, 815), (527, 719)]:
    add_line(s, x1, 141, x2, 141, color=RED, w=2.0, dash='dash')
add_text(s, 200, 378, 960, 22, '红色虚线 = 跳跃连接：把编码器同分辨率的浅层细节旁路送到解码器',
         size=12, color=RED, align='c')
cols = [('A', '编码器：为什么要压缩？', '卷积 + 池化逐级下采样，通道翻倍、分辨率减半——用空间精度换语义抽象，'
                                        '让每个像素位置的感受野覆盖足够的上下文来判断"这里是不是病灶"。', BG),
        ('B', '解码器：为什么要还原？', '上采样逐级恢复到输入分辨率，通道对称减半，最后 1×1 卷积 + Sigmoid '
                                        '得到逐像素概率图——把"看懂了什么"翻译回"哪几个像素属于病灶"。', BG),
        ('C', '为什么必须有跳跃连接？', '池化下采样不可逆，深层特征有语义却丢了边界。跳跃连接（concat 而非相加）'
                                       '把丢失的细节抄近道送回解码器，这是 U 形结构的核心。', LIGHT2)]
xx = 40
for no, t, d, f in cols:
    card(s, xx, 452, 386, 206, fill=f)
    add_rect(s, xx + 20, 470, 34, 34, fill=(DEEP if no == 'C' else BLUE), radius=0.2)
    add_text(s, xx + 20, 476, 34, 24, no, size=15, color=WHITE, bold=True, align='c')
    add_text(s, xx + 66, 474, 300, 30, t, size=18, color=DEEP, bold=True)
    add_text(s, xx + 20, 516, 346, 130, d, size=14, color=SUB, lh=1.5)
    xx += 407

# ============================================================ P9 分割核心模块
s = prs.slides.add_slide(BLANK)
page_frame(s, 9, '分割网络核心模块拆解', '02 分割网络')
add_rect(s, 0, 92, 330, 578, fill=DEEP)
add_text(s, 40, 140, 250, 30, '02 分割网络', size=17, color=RGBColor(0x9F, 0xB6, 0xDE))
add_text(s, 40, 182, 260, 44, '核心模块拆解', size=27, color=WHITE, bold=True)
add_rect(s, 40, 282, 56, 4, fill=YELLOW)
add_text(s, 40, 300, 250, 110,
         '五个积木，构成了本项目的两个网络。理解了它们，U-Net 与 U-Net++ 的结构差异就只剩"怎么连"。',
         size=15, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.6)
add_rect(s, 40, 470, 250, 150, fill=BLUE2, radius=0.1)
add_text(s, 58, 486, 214, 120,
         '提示：这些模块在两个网络中完全相同——本页内容可在两个网络之间直接迁移。',
         size=13.5, color=WHITE, lh=1.5)
mods = [
    ('DoubleConv', 'Conv 3×3 + BN + ReLU 各两次',
     'U-Net 的最小编码单元：两次 3×3 卷积把感受野叠到 5×5，BN 稳定训练，ReLU 引入非线性；每一级的通道数在这里确定（32→64→128→256→512）。', BG, BLUE),
    ('MaxPool', '2×2 最大池化下采样',
     '分辨率减半、通道不变：计算量下降并获得平移不变性，代价是不可逆的细节丢失——这项损失由跳跃连接补偿。', BG, BLUE),
    ('Up-Conv', '转置卷积上采样',
     '2×2 转置卷积把特征图分辨率翻倍（也可用双线性插值），其后紧跟 DoubleConv 平滑上采样带来的棋盘状伪影。', BG, BLUE),
    ('Skip', '跳跃连接 concat',
     '把编码器同分辨率输出在通道维拼接（通道数翻倍）而非相加——保留完整浅层细节，让解码器按需取用。', BG, BLUE),
    ('1×1 Conv', '逐像素二分类器 + Sigmoid',
     '用 1×1 卷积把 32 通道特征压成 1 通道 logits，Sigmoid 后得到每个像素属于病灶的概率，0.5 阈值二值化为 mask。', LIGHT2, DEEP),
]
yy = 104
for name, t, d, f, c in mods:
    card(s, 376, yy, 864, 106, fill=f, border=(f == BG), line_color=(None if f != BG else LINE))
    add_rect(s, 396, yy + 14, 128, 78, fill=c, radius=0.12)
    add_text(s, 396, yy + 40, 128, 28, name, size=15, color=WHITE, bold=True, align='c')
    add_text(s, 542, yy + 10, 674, 28, t, size=18, color=DEEP, bold=True)
    add_text(s, 542, yy + 44, 674, 56, d, size=13.5, color=SUB, lh=1.42)
    yy += 112

# ============================================================ P10 U-Net 结构
s = prs.slides.add_slide(BLANK)
page_frame(s, 10, 'U-Net 结构详解：编码-解码与跳跃连接', '02 分割网络')
card(s, 40, 104, 700, 554)


def unet_node(sl, x, y, t1, t2, color, sub_color=WHITE):
    add_rect(sl, x, y, 170, 64, fill=color, radius=0.12)
    add_text(sl, x, y + 7, 170, 22, t1, size=11.5, color=WHITE, bold=True, align='c')
    add_text(sl, x, y + 38, 170, 18, t2, size=10, color=RGBColor(0xD5, 0xE1, 0xF5), align='c')


unet_node(s, 40, 120, '输入 256×256×3', 'Conv 3×3 ×2 → 32ch', BLUE)
add_arrow_d(s, 118, 186, 16)
add_text(s, 140, 186, 120, 20, 'MaxPool 2×2', size=11, color=SUB)
unet_node(s, 40, 212, 'Conv ×2 → 64ch', '128×128', BLUE2)
add_arrow_d(s, 118, 278, 16)
unet_node(s, 40, 300, 'Conv ×2 → 128ch', '64×64', MID)
add_arrow_d(s, 118, 366, 16)
unet_node(s, 40, 388, 'Conv ×2 → 256ch', '32×32', MID2)
add_arrow_diag(s, 210, 440, 265, 496)
unet_node(s, 265, 492, '瓶颈层 → 512ch', '16×16 语义最抽象', DEEP)
add_arrow_diag(s, 435, 496, 490, 440)
unet_node(s, 490, 388, '上采样+Conv → 256ch', '转置卷积 2×', MID2)
add_arrow_d(s, 568, 366, 16)
unet_node(s, 490, 300, '上采样+Conv → 128ch', '64×64', MID)
add_arrow_d(s, 568, 278, 16)
unet_node(s, 490, 212, '上采样+Conv → 64ch', '128×128', BLUE2)
add_arrow_d(s, 568, 186, 16)
unet_node(s, 490, 120, '1×1 Conv → 1ch', 'Sigmoid 概率图 256×256', BLUE)
for i, yy in enumerate([152, 244, 336, 420]):
    add_line(s, 212, yy, 488, yy, color=RED, w=2.5, dash='dash')
add_text(s, 214, 124, 272, 20, 'Skip Connection：concat(浅层细节)', size=11, color=RED, bold=True)
add_text(s, 60, 570, 660, 60,
         '结构来源：Ronneberger et al., MICCAI 2015（本项目 base_channels=32，7.76M 参数）；'
         '红色虚线为跳跃连接，浅层细节被"抄近道"送入解码器。',
         size=12.5, color=SUB, lh=1.5, align='c')
infos = [
    ('① 编码器：看懂图像', '每级 DoubleConv（Conv+BN+ReLU ×2）后 MaxPool 下采样，通道 32→512 逐级翻倍，空间细节换语义抽象。', BG, False),
    ('② 解码器：画回原尺寸', '转置卷积逐级上采样恢复分辨率，通道对称减半，最后 1×1 卷积 + Sigmoid 输出逐像素概率图。', BG, False),
    ('③ 跳跃连接：本结构的灵魂', '把编码器同分辨率的浅层特征 concat 进解码器——丢失的边缘细节被"抄近道"送回，分割边界因此更准。', LIGHT2, True),
]
yy = 104
for t, d, f, hl in infos:
    card(s, 764, yy, 476, 150, fill=f, line_color=(BLUE if hl else None))
    add_text(s, 788, yy + 14, 430, 28, t, size=18, color=(BLUE if hl else DEEP), bold=True)
    add_text(s, 788, yy + 48, 430, 96, d, size=14, color=(DEEP if hl else SUB), lh=1.45)
    yy += 162
add_rect(s, 764, 604, 476, 54, fill=LIGHT, radius=0.1)
add_text(s, 788, 616, 430, 34, '为什么适合医学影像？结构对称、参数可调，数百例小数据集即可收敛——BUSI 780 例够用。',
         size=13, color=DEEP, lh=1.4)

# ============================================================ P11 U-Net++
s = prs.slides.add_slide(BLANK)
page_frame(s, 11, 'U-Net++：嵌套密集跳跃连接与深度监督', '02 分割网络')
card(s, 40, 104, 1200, 300)
nodes = [('X\u2080\u2080', '编码器 32ch', 30, BLUE), ('X\u2080\u2081', '浅解码 · 输出1', 300, MID),
         ('X\u2080\u2082', '中解码 · 输出2', 570, MID2), ('X\u2080\u2083', '深解码 · 输出3', 840, BLUE2),
         ('X\u2080\u2084', '最深 · 推理输出', 1040, DEEP)]
for lbl, sub, x, c in nodes:
    add_rect(s, x, 170, 120, 58, fill=c, radius=0.12)
    add_text(s, x, 178, 120, 24, lbl, size=15, color=WHITE, bold=True, align='c')
    add_text(s, x, 204, 120, 18, sub, size=10, color=RGBColor(0xDC, 0xE6, 0xF5), align='c')
low = [('X\u2081\u2080', 30), ('X\u2081\u2081', 300), ('X\u2082\u2080', 570)]
for lbl, x in low:
    add_rect(s, x, 248, 120, 50, fill=MID2, radius=0.12)
    add_text(s, x, 259, 120, 24, lbl, size=15, color=WHITE, bold=True, align='c')
for x1, x2 in [(150, 300), (420, 570), (690, 840), (960, 1040)]:
    add_arrow_r(s, x1, 188, x2 - x1, 22, color=MID)
for x1, x2 in [(150, 300), (420, 570)]:
    add_arrow_r(s, x1, 262, x2 - x1, 18, color=MID)
add_line(s, 90, 166, 360, 128, color=RED, w=2.5, dash='dash')
add_line(s, 360, 166, 630, 128, color=RED, w=2.5, dash='dash')
add_line(s, 630, 166, 900, 128, color=RED, w=2.5, dash='dash')
add_line(s, 900, 166, 1100, 128, color=RED, w=2.5, dash='dash')
add_text(s, 80, 96, 1040, 22, '红色虚线：嵌套密集跳跃连接（同层拼接）——特征在编码与解码之间"逐级过渡"而非一步跨越',
         size=13, color=RED, bold=True)
add_text(s, 60, 322, 1160, 24, '实线箭头：上采样流；每个 X\u2080\u2c7c 都可接分割头（深度监督），推理时只用最深层 X\u2080\u2084。',
         size=12.5, color=SUB)
card(s, 40, 424, 520, 234)
add_text(s, 64, 444, 472, 32, '嵌套密集连接解决什么问题？', size=20, color=DEEP, bold=True)
add_text(s, 64, 484, 472, 160, [
    [('U-Net 的跳跃连接直接把', {}), ('深层语义', {'bold': True}), ('与', {}), ('浅层细节', {'bold': True}),
     ('拼接，两者之间存在语义鸿沟。U-Net++ 在编码-解码之间插入一系列嵌套的中间节点，'
      '让特征"逐级过渡"，语义差距更平滑（Zhou et al., DLMIA 2018）。', {})],
], size=15, color=SUB, lh=1.55)
card(s, 584, 424, 400, 234, fill=LIGHT2, line_color=BLUE)
add_text(s, 608, 444, 352, 32, '深度监督（本项目已开启）', size=20, color=BLUE, bold=True)
add_text(s, 608, 484, 352, 160, [
    [('训练时对四个浅层输出', {}), ('分别计算损失取平均', {'bold': True}),
     ('，为浅层提供直接梯度；推理时只用最深层，精度不降、参数不增。', {})],
], size=15, color=DEEP, lh=1.55)
add_rect(s, 1008, 424, 232, 234, fill=DEEP, radius=0.08)
add_text(s, 1032, 444, 190, 32, '代价与收益', size=19, color=WHITE, bold=True)
add_text(s, 1032, 490, 106, 36, '9.16M', size=22, color=YELLOW, bold=True)
add_text(s, 1032, 528, 106, 20, 'U-Net++ 参数', size=12, color=RGBColor(0xC9, 0xD7, 0xEE))
add_text(s, 1142, 490, 98, 36, '7.76M', size=22, color=WHITE, bold=True)
add_text(s, 1142, 528, 98, 20, 'U-Net 参数', size=12, color=RGBColor(0xC9, 0xD7, 0xEE))
add_text(s, 1032, 566, 190, 80, '参数多 18%，换取更平滑的特征过渡（实测对比见第 18 页）',
         size=13, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.45)

# ============================================================ P12 U-Net vs U-Net++
s = prs.slides.add_slide(BLANK)
page_frame(s, 12, 'U-Net vs U-Net++：结构差异一览', '02 分割网络')
add_rect(s, 0, 92, 330, 578, fill=DEEP)
add_text(s, 40, 140, 250, 30, '02 分割网络', size=17, color=RGBColor(0x9F, 0xB6, 0xDE))
add_text(s, 40, 178, 285, 80, 'U-Net vs U-Net++', size=22, color=WHITE, bold=True)
add_text(s, 40, 262, 250, 40, '两处改动：连接变密、监督变多', size=15, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.4)
add_rect(s, 40, 318, 56, 4, fill=YELLOW)
add_rect(s, 40, 350, 250, 140, fill=BLUE2, radius=0.1)
add_text(s, 58, 366, 214, 110,
         '记住两句话：连接变密（同层互连），监督变多（浅层也管）。',
         size=14, color=WHITE, lh=1.55)
add_text(s, 40, 506, 250, 150, '骨架、卷积单元、损失函数、训练配置全部相同——'
                              '这正是"一个变量"的受控对比实验。',
         size=13.5, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.6)
tbl_shape = s.shapes.add_table(7, 3, u(376), u(112), u(864), u(400))
tbl = tbl_shape.table
tbl.columns[0].width = u(170)
tbl.columns[1].width = u(347)
tbl.columns[2].width = u(347)
rows = [
    ('对比维度', 'U-Net（2015）', 'U-Net++（2018）'),
    ('跳跃连接', '同级单层直连，共 4 条', '嵌套密集连接，每个节点汇聚同层前驱'),
    ('监督方式', '仅最深层单点监督', '深度监督：4 个输出层各自算损失取平均'),
    ('参数量', '7.76M（7,763,041）', '9.16M（9,159,780，+18%）'),
    ('实测 Dice', '0.7382', '0.7468'),
    ('推理开销', '单路前向，最快', '额外密集拼接，显存与耗时略增（推理只用最深层）'),
    ('适用场景', '基线首选、显存受限、快速迭代', '追求更高精度且可接受额外成本'),
]
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.margin_left = cell.margin_right = Pt(6)
        cell.margin_top = cell.margin_bottom = Pt(3)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        if r == 0:
            cell.fill.fore_color.rgb = DEEP if c == 2 else BLUE
        else:
            cell.fill.fore_color.rgb = WHITE if r % 2 else BG
        tf = cell.text_frame
        tf.word_wrap = True
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER if r == 0 else PP_ALIGN.LEFT
        run = para.add_run()
        hl = (r == 4 and c == 2)
        set_run(run, val, 13.5, WHITE if r == 0 else (RED if hl else TEXT), r == 0 or c == 0 or hl)
add_rect(s, 376, 532, 864, 126, fill=LIGHT, radius=0.08)
add_text(s, 400, 548, 816, 96, [
    [('小结：', {'bold': True}),
     ('U-Net++ 没有改变 U-Net 的骨架，只是把"一步跨越的跳跃连接"改写成"逐级过渡的密集连接"，'
      '并给浅层加上直接监督。实测 Dice 0.738 → 0.747（+0.9 个点），代价是参数 +18%——'
      '典型的"用结构复杂度换精度"，是否值得取决于部署条件（见第 18 页）。', {})],
], size=15, color=DEEP, lh=1.45)

# ============================================================ P13 章节3
section_page(3, 'PART 03 · LOSS & METRICS', '损失函数与评价指标',
             '病灶像素往往不到整张图的 5%：什么样的损失才能在极度不平衡中"盯住"病灶，'
             '又该用哪些指标衡量"画得像不像"——为什么 Accuracy 在分割任务里不可信。',
             ['BCE 与 Dice', '类别不平衡', '混淆矩阵', 'Dice / IoU'], pageno=13)

# ============================================================ P15 分割损失
s = prs.slides.add_slide(BLANK)
page_frame(s, 14, '分割损失函数：BCE 与 Dice 的组合', '03 损失与指标')
add_rect(s, 0, 92, 330, 578, fill=DEEP)
add_text(s, 40, 140, 250, 30, '03 损失与指标', size=17, color=RGBColor(0x9F, 0xB6, 0xDE))
add_text(s, 40, 178, 250, 150, '分割损失函数：BCE 与 Dice 的组合', size=30, color=WHITE, bold=True, lh=1.3)
add_rect(s, 40, 358, 56, 4, fill=YELLOW)
add_text(s, 40, 380, 250, 140, '选择依据：病灶像素占比极小，逐像素损失会被背景"淹没"，必须引入对前景区域敏感的 Dice 项。',
         size=15, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.6)
add_rect(s, 40, 540, 250, 110, fill=BLUE2, radius=0.1)
add_text(s, 58, 560, 214, 76, '本项目默认：L = 0.5·L_BCE + 0.5·L_Dice，可经 --loss 参数切换。',
         size=13.5, color=WHITE, lh=1.45)
seg_losses = [
    ('BCE', '逐像素二分类交叉熵', BG, BLUE, False,
     r'L_{BCE}=-\frac{1}{N}\sum_{i=1}^{N}\left[y_i\log\hat{p}_i+(1-y_i)\log(1-\hat{p}_i)\right]',
     '优化稳定、梯度平滑；但背景像素占 95%+ 时，损失被易分背景主导，病灶区域学不充分。'),
    ('Dice', 'soft Dice（可微）', BG, BLUE, False,
     r'L_{Dice}=1-\frac{2\sum_i p_i g_i}{\sum_i p_i+\sum_i g_i}',
     '直接优化"预测与真值的重合度"，只关心前景区域规模，天然对类别不平衡鲁棒——代价是梯度不如 BCE 稳定。'),
    ('BCE+Dice', '两者取长补短 · 默认', LIGHT2, DEEP, True,
     r'L=\lambda_1 L_{BCE}+\lambda_2 L_{Dice},\ \lambda_1=\lambda_2=0.5',
     'BCE 提供逐像素的稳定梯度，Dice 提供区域级的重合度导向——医学分割最常用的组合之一。'),
    ('Focal', 'γ 为聚焦参数（常取 2）', BG, MID, False,
     r'L_{FL}=-(1-\hat{p}_t)^{\gamma}\log(\hat{p}_t)',
     '在 BCE 上乘调制因子，把权重集中到难分样本（如边界模糊的恶性病灶边缘）。'),
]
yy = 112
for name, tag, f, c, hl in [(x[0], x[1], x[2], x[3], x[4]) for x in seg_losses]:
    pass
fwidths = {'BCE': 380, 'Dice': 330, 'BCE+Dice': 380, 'Focal': 300}
for name, tag, f, c, hl, la, d in seg_losses:
    card(s, 376, yy, 864, 130, fill=f, line_color=(BLUE if hl else None))
    add_rect(s, 396, yy + 20, 130, 90, fill=c, radius=0.12)
    add_text(s, 396, yy + 52, 130, 28, name, size=16, color=WHITE, bold=True, align='c')
    add_formula(s, 548, yy + 20, la, fwidths[name], fontsize=14)
    add_text(s, 934, yy + 16, 286, 106, tag + '。' + d, size=13, color=(DEEP if hl else SUB), lh=1.42)
    yy += 142

# ============================================================ P16 指标
s = prs.slides.add_slide(BLANK)
page_frame(s, 15, '评价指标：从混淆矩阵到 Dice 系数', '03 损失与指标')
card(s, 40, 110, 430, 400)
mx = [('TP', '正确找病灶', BLUE, 140, 140), ('FP', '误报', RED, 236, 140),
      ('FN', '漏诊', MID, 140, 236), ('TN', '正确背景', GRAY, 236, 236)]
for lbl, sub, c, x, y in mx:
    add_rect(s, x, y, 84, 84, fill=c, radius=0.1)
    add_text(s, x, y + 18, 84, 30, lbl, size=19, color=WHITE, bold=True, align='c')
    add_text(s, x, y + 50, 84, 20, sub, size=11, color=RGBColor(0xE5, 0xEA, 0xF2), align='c')
add_text(s, 110, 116, 140, 20, '预测=病灶', size=12.5, color=SUB, align='c')
add_text(s, 226, 116, 140, 20, '预测=背景', size=12.5, color=SUB, align='c')
add_text(s, 52, 174, 80, 20, '真值=病灶', size=12, color=SUB)
add_text(s, 52, 270, 80, 20, '真值=背景', size=12, color=SUB)
add_text(s, 60, 430, 390, 48, '像素级混淆矩阵：一切指标由此计算（本项目 src/metrics.py）',
         size=13.5, color=SUB, align='c', lh=1.4)
add_rect(s, 40, 528, 430, 130, fill=LIGHT, radius=0.08)
add_text(s, 64, 546, 382, 98, [
    [('反直觉的一点：', {'bold': True}),
     ('一张 256×256 图，病灶仅占 3% 时——模型全输出"背景"，Accuracy 也有 97%，但它什么都没做对。', {})],
], size=15, color=DEEP, lh=1.55)
mets = [
    ('Dice（核心）', r'Dice=\frac{2TP}{2TP+FP+FN}', '与真值的重合度，选最优权重按它', True),
    ('IoU（交并比）', r'IoU=\frac{TP}{TP+FP+FN}', '交集 / 并集，比 Dice 更严格', False),
    ('Precision 精确率', r'P=\frac{TP}{TP+FP}', '报出来的病灶有多少是真的（误报代价）', False),
    ('Recall 召回率', r'R=\frac{TP}{TP+FN}', '真实病灶找到了多少（漏诊代价）', False),
    ('Specificity 特异度', r'Sp=\frac{TN}{TN+FP}', '背景被正确保留的比例', False),
    ('Accuracy 准确率', r'Acc=\frac{TP+TN}{TP+TN+FP+FN}', '全体像素正确率，仅作参考', False),
]
yy = 110
for t, la, d, hl in mets:
    card(s, 494, yy, 746, 66, fill=(DEEP if hl else BG), line_color=(None if hl else LINE))
    add_text(s, 516, yy + 20, 190, 28, t, size=16, color=(YELLOW if hl else DEEP), bold=True)
    add_formula(s, 720, yy + 10, la, 220, color=('#FFFFFF' if hl else '#1A2230'), fontsize=13)
    add_text(s, 964, yy, 260, 66, d, size=12.5, color=(RGBColor(0xC9, 0xD7, 0xEE) if hl else SUB), anchor='m')
    yy += 74
add_rect(s, 494, 558, 746, 100, fill=LIGHT, radius=0.08)
add_text(s, 518, 576, 700, 70, [
    [('临床视角：筛查场景更怕', {}), ('漏诊', {'bold': True}), ('（看 Recall），定量分析更怕', {}),
     ('误报', {'bold': True}), ('（看 Precision）——Dice 是两者的综合体现。', {})],
], size=15, color=DEEP, lh=1.5)

# ============================================================ P17 章节4
section_page(4, 'PART 04 · RESULTS & HANDS-ON', '实验与实操',
             '用真实训练结果检验结构改造是否值得：先看实验设置是否公平，再看 U-Net 与 U-Net++ '
             '在测试集上的全面对比，最后是每组同学都要完成的动手任务。',
             ['实验设置', '结果对比', '训练曲线', '预测可视化', '任务书'], pageno=16)

# ============================================================ P17 实验设置
s = prs.slides.add_slide(BLANK)
page_frame(s, 17, '实验设置：如何做一次公平的网络对比', '04 实验与实操')
card(s, 40, 112, 760, 524)
rows_cfg = [
    ('配置项', '本项目取值（两个网络完全相同）'),
    ('数据集', 'BUSI 乳腺超声 780 例（良性 437 / 恶性 210 / 正常 133），良恶性带医师逐像素标注'),
    ('数据划分', '按类别分层抽样 70% 训练 / 15% 验证 / 15% 测试，seed = 42，随机种子固定'),
    ('图像预处理', '统一 Resize 到 256×256，按 mean=std=0.5 归一化到 [-1, 1]；mask 最近邻插值后 0.5 阈值二值化'),
    ('数据增强', '随机水平翻转、随机垂直翻转、随机 90° 倍数旋转（k∈{0,1,2,3}），图像与 mask 同步变换'),
    ('网络容量', 'base_channels = 32（通道按级翻倍至 512），U-Net 7.76M / U-Net++ 9.16M 参数'),
    ('损失函数', 'BCE + Dice 各占 0.5；U-Net++ 额外开启深度监督（四个输出层各算损失取平均）'),
    ('优化与训练', 'AdamW，lr = 1e-3，weight_decay = 1e-4，CosineAnnealingLR；100 epoch，batch = 8'),
    ('评测口径', '取验证集 Dice 最优权重；测试集上按 0.5 阈值二值化，统一计算 Dice/IoU/Precision/Recall 等指标'),
]
tbl_shape = s.shapes.add_table(len(rows_cfg), 2, u(64), u(132), u(712), u(484))
tbl = tbl_shape.table
tbl.columns[0].width = u(150)
tbl.columns[1].width = u(562)
for r, row in enumerate(rows_cfg):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.margin_left = cell.margin_right = Pt(6)
        cell.margin_top = cell.margin_bottom = Pt(2)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        if r == 0:
            cell.fill.fore_color.rgb = BLUE if c == 0 else DEEP
        else:
            cell.fill.fore_color.rgb = WHITE if r % 2 else BG
        tf = cell.text_frame
        tf.word_wrap = True
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER if (r == 0 or c == 0) else PP_ALIGN.LEFT
        run = para.add_run()
        set_run(run, val, 12, WHITE if r == 0 else (DEEP if c == 0 else TEXT), r == 0 or c == 0)
card(s, 824, 112, 416, 150, fill=LIGHT2, line_color=BLUE)
add_text(s, 848, 130, 368, 30, '原则一 · 同样的输入', size=19, color=BLUE, bold=True)
add_text(s, 848, 168, 368, 76, '同一份数据、同一种划分方式与同一个随机种子，'
                               '同一套预处理与增强——保证两个网络"看到"的分布完全一致。',
         size=14, color=DEEP, lh=1.5)
card(s, 824, 274, 416, 150)
add_text(s, 848, 292, 368, 30, '原则二 · 同样的训练', size=19, color=DEEP, bold=True)
add_text(s, 848, 330, 368, 76, '优化器、学习率及其调度、epoch 数、batch 大小、损失函数完全相同，'
                               '都取验证集 Dice 最优的那一份权重参与测试。',
         size=14, color=SUB, lh=1.5)
card(s, 824, 436, 416, 150)
add_text(s, 848, 454, 368, 30, '原则三 · 同样的评测口径', size=19, color=DEEP, bold=True)
add_text(s, 848, 492, 368, 76, '同一测试集、同一 0.5 二值化阈值、同一套 MetricMeter 实现，'
                               '指标不因评判方式不同而产生偏差。',
         size=14, color=SUB, lh=1.5)
add_rect(s, 824, 604, 416, 32, fill=DEEP, radius=0.08)
add_text(s, 824, 610, 416, 24, '唯一变量：网络结构（U-Net ↔ U-Net++）',
         size=13.5, color=WHITE, bold=True, align='c')

# ============================================================ P18 实验结果
s = prs.slides.add_slide(BLANK)
page_frame(s, 18, '实验结果：两种网络究竟差多少？', '04 实验与实操')
card(s, 40, 104, 760, 554)
s.shapes.add_picture(os.path.join(BASE, 'assets', 'comparison.jpg'), u(60), u(120), u(720), u(432))
add_text(s, 60, 568, 720, 76,
         'BUSI 测试集（按类别分层 70/15/15 划分，seed=42）。两模型均训练 100 epoch，batch=8，lr=1e-3，'
         '损失 BCE+Dice，按验证集 Dice 保存最优权重（outputs/comparison/）。',
         size=13.5, color=SUB, lh=1.5)
add_rect(s, 824, 104, 196, 96, fill=DEEP, radius=0.08)
add_text(s, 824, 114, 196, 44, '0.747', size=34, color=WHITE, bold=True, align='c')
add_text(s, 824, 160, 196, 24, 'U-Net++ Dice', size=13, color=RGBColor(0xC9, 0xD7, 0xEE), align='c')
add_rect(s, 1044, 104, 196, 96, fill=BLUE, radius=0.08)
add_text(s, 1044, 114, 196, 44, '0.738', size=34, color=WHITE, bold=True, align='c')
add_text(s, 1044, 160, 196, 24, 'U-Net Dice', size=13, color=RGBColor(0xC9, 0xD7, 0xEE), align='c')
tbl_shape = s.shapes.add_table(6, 3, u(824), u(216), u(416), u(216))
tbl = tbl_shape.table
tbl.columns[0].width = u(140)
tbl.columns[1].width = u(138)
tbl.columns[2].width = u(138)
trows = [
    ('指标', 'U-Net', 'U-Net++'),
    ('IoU', '0.585', '0.596'),
    ('Precision', '0.776', '0.789'),
    ('Recall', '0.704', '0.709'),
    ('参数量', '7.76M', '9.16M'),
    ('验证集 Dice', '0.770', '0.781'),
]
for r, row in enumerate(trows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLUE if r == 0 else (WHITE if r % 2 else BG)
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        run = para.add_run()
        hl = (r == 4 and c == 2)
        set_run(run, val, 13, WHITE if r == 0 else (RED if hl else TEXT), r == 0 or c == 0 or hl)
card(s, 824, 448, 416, 210)
add_text(s, 848, 466, 368, 30, '怎么解读这组数字？', size=19, color=DEEP, bold=True)
add_text(s, 848, 500, 368, 150, [
    [('U-Net++ 六项指标全部略优（验证集 Dice 0.781 vs 0.770），密集连接与深度监督有效；'
      '但提升约 1 个点、参数多 18%——', {}),
     ('教学级小数据集上结构收益有限，公平比较须控制训练配置一致。', {'bold': True})],
], size=13.5, color=SUB, lh=1.5)

# ============================================================ P19 曲线与可视化
s = prs.slides.add_slide(BLANK)
page_frame(s, 19, '训练过程与预测效果可视化', '04 实验与实操')
card(s, 40, 104, 560, 554)
s.shapes.add_picture(os.path.join(BASE, 'assets', 'curve_unetpp.jpg'), u(66), u(120), u(508), u(406))
add_text(s, 56, 536, 528, 110,
         'U-Net++（深度监督）100 epoch 训练曲线：Loss 收敛平稳，Dice 爬升至约 0.78，'
         '验证曲线与训练曲线基本贴合（outputs/unetpp_20261010_204944/）。',
         size=13, color=SUB, lh=1.5, align='c')
card(s, 624, 104, 616, 240)
s.shapes.add_picture(os.path.join(BASE, 'assets', 'sample_triptych.jpg'), u(644), u(118), u(576), u(178))
add_text(s, 644, 306, 180, 22, '① 输入原图', size=13, color=SUB)
add_text(s, 850, 306, 200, 22, '② 医师 GT mask', size=13, color=SUB, align='c')
add_text(s, 1030, 306, 190, 22, '③ 预测与 GT 叠加', size=13, color=RED, align='r')
card(s, 624, 356, 616, 190)
add_text(s, 648, 372, 568, 30, '从曲线里读出三件事', size=19, color=DEEP, bold=True)
add_text(s, 648, 406, 568, 134, [
    '① 前期验证曲线剧烈震荡——小数据集 + 类别不平衡的典型现象，后期趋于平稳；',
    '② 训练 / 验证曲线基本贴合，无过拟合剪刀差，100 epoch 轮数合适；',
    '③ Specificity 恒近 1.0 而 Recall 起伏大——瓶颈在"漏诊"而非"误报"。',
], size=13.5, color=SUB, lh=1.45)
add_rect(s, 624, 558, 616, 100, fill=LIGHT, radius=0.08)
add_text(s, 648, 576, 568, 70, [
    [('观察任务（课堂互动）：', {'bold': True}),
     ('恶性病例边界呈毛刺状、与腺体重叠，叠加图中预测轮廓在这些区域偏差最大——请思考：'
      '更强的边界损失？更高分辨率？还是更多数据？哪个最有针对性？', {})],
], size=14, color=DEEP, lh=1.5)

# ============================================================ P20 任务书
s = prs.slides.add_slide(BLANK)
page_frame(s, 20, '课内实操任务书', '04 实验与实操')
add_rect(s, 0, 92, 330, 578, fill=DEEP)
add_text(s, 40, 140, 250, 30, '04 实验与实操', size=17, color=RGBColor(0x9F, 0xB6, 0xDE))
add_text(s, 40, 182, 260, 44, '课内实操任务书', size=27, color=WHITE, bold=True)
add_rect(s, 40, 296, 56, 4, fill=YELLOW)
add_text(s, 40, 322, 250, 140, '2 人一组，约 60 分钟。所有命令在项目根目录 BUSI_seg/ 下执行，结果自动保存到 outputs/ 目录。',
         size=15, color=RGBColor(0xC9, 0xD7, 0xEE), lh=1.6)
add_rect(s, 40, 480, 250, 130, fill=BLUE2, radius=0.1)
add_text(s, 58, 498, 214, 96, '环境：Python 3.9+，pip install -r requirements.txt（CPU 可跑，GPU 更快）',
         size=14, color=WHITE, lh=1.5)
tasks = [
    ('1', '复现基线对比（20 分钟）',
     'python -m src.train --model unet --epochs 30    /    --model unetpp --epochs 30',
     '两个网络共用同一份划分与同一套超参；记录各自 val Dice、参数量与耗时。', False),
    ('2', '结构消融：深度监督的贡献（15 分钟）',
     '把 src/config.py 的 deep_supervision 改为 False 后重跑 unetpp 并对比',
     '观察开关前后的 val Dice 与收敛速度，回答：提升更多来自密集连接，还是来自深度监督？', False),
    ('3', '损失与容量对照（15 分钟）',
     '--loss bce / dice / focal（各一次）   --base-channels 16 vs 64（选一组）',
     '在 U-Net 上做单点对照，验证"BCE+Dice 最稳"这一默认选择在 BUSI 上是否成立。', False),
    ('4', '失败案例与分析（10 分钟）',
     'python -m src.evaluate --checkpoint outputs/<你的目录>/best.pt',
     '找出两个网络 Dice 都低的 2 张图，判断根因：边界模糊？病灶过小？还是标注本身就有争议？', True),
]
yy = 108
for no, t, cmd, d, hl in tasks:
    card(s, 376, yy, 864, 122, fill=(LIGHT2 if hl else BG), line_color=(BLUE if hl else None))
    add_rect(s, 396, yy + 18, 46, 46, fill=(DEEP if hl else BLUE), radius=0.2)
    add_text(s, 396, yy + 28, 46, 28, no, size=19, color=WHITE, bold=True, align='c')
    add_text(s, 458, yy + 12, 500, 28, t, size=18, color=DEEP, bold=True)
    add_rect(s, 458, yy + 44, 758, 34, fill=DEEP, radius=0.15)
    add_text(s, 474, yy + 51, 740, 24, cmd, size=13.5, color=RGBColor(0xC9, 0xD7, 0xEE))
    add_text(s, 458, yy + 84, 758, 32, d, size=13, color=(DEEP if hl else SUB), lh=1.35)
    yy += 134
add_rect(s, 376, 620, 864, 44, fill=LIGHT, radius=0.3)
add_text(s, 392, 626, 836, 34,
         '验收：① 对比记录表（U-Net / U-Net++ 的 Dice、IoU、Recall、参数量、耗时）② 一句明确结论（推荐哪个网络 + 理由）'
         '③ 150 字失败案例分析。评分：对比完整性 40% + 结论有据 40% + 分析 20%。',
         size=11.5, color=DEEP, lh=1.25)

# ============================================================ P21 结束页
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 1280, 300, fill=DEEP)
add_rect(s, 0, 0, 1280, 8, fill=BLUE)
add_text(s, 80, 96, 1120, 30, 'SUMMARY · 课程总结', size=18, color=RGBColor(0x9F, 0xB6, 0xDE), align='c')
add_text(s, 80, 140, 1120, 120, '同一个任务，两个网络：结构决定性能', size=44, color=WHITE, bold=True, align='c')
sums = [
    ('01', 'U-Net：四十年未变的 U 形骨架', '编码-解码 + 跳跃连接；7.76M 参数，至今仍是医学分割最可靠的基线。'),
    ('02', 'U-Net++：连得更密、盯得更紧', '嵌套密集连接 + 深度监督；9.16M 参数（+18%）。'),
    ('03', '实验：结构收益要配成本看', 'Dice 0.738 → 0.747（+0.9 个点）：提升真实但有限，取决于部署条件。'),
]
xx = 80
for no, t, d in sums:
    card(s, xx, 340, 357, 200)
    add_text(s, xx + 24, 352, 100, 44, no, size=28, color=BLUE, bold=True)
    add_text(s, xx + 24, 398, 309, 66, t, size=16.5, color=DEEP, bold=True, lh=1.3)
    add_text(s, xx + 24, 466, 309, 66, d, size=13, color=SUB, lh=1.42)
    xx += 381
add_text(s, 80, 580, 900, 70, [
    [('课后思考：', {'bold': True}),
     ('① 若把 U-Net++ 的中间输出全部用于 ensemble，推理成本会怎样变化？是否值得？'
      '  ② 深度监督为什么对小数据集更友好？  ③ 若你的数据集扩大到 10 倍，本课的结论会反转吗？', {})],
], size=15, color=DEEP, lh=1.6)
add_text(s, 1000, 588, 200, 40, '谢谢！', size=24, color=DEEP, bold=True, align='r')
add_rect(s, 0, 670, 1280, 50, fill=WHITE)
add_rect(s, 0, 670, 1280, 1, fill=RGBColor(0xE5, 0xE7, 0xEB))
add_text(s, 40, 686, 500, 22, '乳腺结节智能分割 · 教学课件 · 肖雄涛', size=12, color=GRAY)
add_text(s, 1100, 686, 140, 22, '21 / 21', size=13, color=BLUE, align='r')

out = os.path.join(BASE, '乳腺结节智能分割.pptx')
prs.save(out)
print('saved:', out, 'slides:', len(prs.slides._sldIdLst))
