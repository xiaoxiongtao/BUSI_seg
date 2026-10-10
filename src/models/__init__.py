"""模型定义与工厂函数。"""
from .unet import UNet
from .unetpp import UNetPlusPlus


def build_model(name, in_channels=3, out_channels=1, base_channels=32,
                deep_supervision=True):
    """根据名称构建模型。

    Args:
        name: "unet" 或 "unetpp"（也支持 unet++ / unet_plus_plus 等写法）
    """
    name = name.lower().replace("_", "").replace("-", "")
    if name == "unet":
        return UNet(in_channels=in_channels, out_channels=out_channels,
                    base_channels=base_channels)
    if name in ("unetpp", "unet++", "unetplusplus", "nestedunet"):
        return UNetPlusPlus(in_channels=in_channels, out_channels=out_channels,
                            base_channels=base_channels,
                            deep_supervision=deep_supervision)
    raise ValueError(f"未知模型: {name}，可选: unet / unetpp")


__all__ = ["UNet", "UNetPlusPlus", "build_model"]
