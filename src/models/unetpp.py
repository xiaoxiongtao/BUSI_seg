"""UNet++（Zhou et al., 2018）：嵌套密集跳跃连接 + 深度监督。"""
import torch
import torch.nn as nn

from .blocks import DoubleConv


class UNetPlusPlus(nn.Module):
    def __init__(self, in_channels=3, out_channels=1, base_channels=32,
                 deep_supervision=True):
        super().__init__()
        self.deep_supervision = deep_supervision
        nb = [base_channels * (2 ** i) for i in range(5)]  # [c, 2c, 4c, 8c, 16c]

        self.pool = nn.MaxPool2d(2)
        self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)

        # 编码器（j=0 列）
        self.conv0_0 = DoubleConv(in_channels, nb[0])
        self.conv1_0 = DoubleConv(nb[0], nb[1])
        self.conv2_0 = DoubleConv(nb[1], nb[2])
        self.conv3_0 = DoubleConv(nb[2], nb[3])
        self.conv4_0 = DoubleConv(nb[3], nb[4])

        # 密集跳跃路径
        self.conv0_1 = DoubleConv(nb[0] + nb[1], nb[0])
        self.conv1_1 = DoubleConv(nb[1] + nb[2], nb[1])
        self.conv2_1 = DoubleConv(nb[2] + nb[3], nb[2])
        self.conv3_1 = DoubleConv(nb[3] + nb[4], nb[3])

        self.conv0_2 = DoubleConv(nb[0] * 2 + nb[1], nb[0])
        self.conv1_2 = DoubleConv(nb[1] * 2 + nb[2], nb[1])
        self.conv2_2 = DoubleConv(nb[2] * 2 + nb[3], nb[2])

        self.conv0_3 = DoubleConv(nb[0] * 3 + nb[1], nb[0])
        self.conv1_3 = DoubleConv(nb[1] * 3 + nb[2], nb[1])

        self.conv0_4 = DoubleConv(nb[0] * 4 + nb[1], nb[0])

        # 输出：深度监督时每个浅层输出也有一个 1x1 卷积
        if self.deep_supervision:
            self.final1 = nn.Conv2d(nb[0], out_channels, kernel_size=1)
            self.final2 = nn.Conv2d(nb[0], out_channels, kernel_size=1)
            self.final3 = nn.Conv2d(nb[0], out_channels, kernel_size=1)
            self.final4 = nn.Conv2d(nb[0], out_channels, kernel_size=1)
        else:
            self.final = nn.Conv2d(nb[0], out_channels, kernel_size=1)

    def forward(self, x):
        x0_0 = self.conv0_0(x)
        x1_0 = self.conv1_0(self.pool(x0_0))
        x2_0 = self.conv2_0(self.pool(x1_0))
        x3_0 = self.conv3_0(self.pool(x2_0))
        x4_0 = self.conv4_0(self.pool(x3_0))

        x0_1 = self.conv0_1(torch.cat([x0_0, self.up(x1_0)], dim=1))
        x1_1 = self.conv1_1(torch.cat([x1_0, self.up(x2_0)], dim=1))
        x2_1 = self.conv2_1(torch.cat([x2_0, self.up(x3_0)], dim=1))
        x3_1 = self.conv3_1(torch.cat([x3_0, self.up(x4_0)], dim=1))

        x0_2 = self.conv0_2(torch.cat([x0_0, x0_1, self.up(x1_1)], dim=1))
        x1_2 = self.conv1_2(torch.cat([x1_0, x1_1, self.up(x2_1)], dim=1))
        x2_2 = self.conv2_2(torch.cat([x2_0, x2_1, self.up(x3_1)], dim=1))

        x0_3 = self.conv0_3(torch.cat([x0_0, x0_1, x0_2, self.up(x1_2)], dim=1))
        x1_3 = self.conv1_3(torch.cat([x1_0, x1_1, x1_2, self.up(x2_2)], dim=1))

        x0_4 = self.conv0_4(torch.cat([x0_0, x0_1, x0_2, x0_3, self.up(x1_3)], dim=1))

        if self.deep_supervision:
            return [self.final1(x0_1), self.final2(x0_2),
                    self.final3(x0_3), self.final4(x0_4)]
        return self.final(x0_4)
