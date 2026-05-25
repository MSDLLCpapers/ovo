from cmap import Colormap
from ovo.core.utils.formatting import get_hash_of_bytes
import matplotlib.colors as mc
import colorsys


def get_color_from_str(value: str, colormap_name: str) -> str:
    # Colormaps: https://cmap-docs.readthedocs.io/en/latest/catalog/
    cmap = Colormap(colormap_name)

    hash_str = get_hash_of_bytes(value.encode())

    # get number between 0.0-1.0
    hash_number = (int(hash_str[:5], 16) % 1000) / 1000

    return cmap(hash_number).hex.lower()


def darken_lighten(hex_color, factor: float):
    """
    Darken or lighten a hex color by multiplying its lightness component in HLS space.
    factor < 1 → darker, factor > 1 → lighter
    """
    rgb = mc.to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return mc.to_hex((r, g, b))


def lighten(hex_color, factor=1.3):
    return darken_lighten(hex_color, factor=factor)


def darken(hex_color, factor=1.3):
    return darken_lighten(hex_color, factor=1 / factor)
