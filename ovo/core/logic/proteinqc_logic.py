from typing import List, Tuple, Literal

import matplotlib.colors as mcolors
import pandas as pd

from ovo import config
from ovo.core.database import Descriptor, NumericDescriptor
from ovo.core.database.models_proteinqc import ProteinQCTool
from ovo.core.scheduler.base_scheduler import Scheduler


def tool_supports_scheduler(tool: ProteinQCTool, scheduler: Scheduler) -> bool:
    if "profile" in scheduler.submission_args and "conda" in scheduler.submission_args["profile"]:
        return tool.supports_conda
    return True


def get_available_tools(tools: List[ProteinQCTool], scheduler: Scheduler) -> List[ProteinQCTool]:
    """
    Get available tools based on the selected scheduler.
    """
    return [tool for tool in tools if tool_supports_scheduler(tool, scheduler)]


def get_descriptor_plot_setting(descriptor: Descriptor) -> Tuple[List[float], bool, str]:
    """
    Get the thresholds, reverse_colors and color_by settings for the descriptor plot.

    The logic for thresholds is as follows:
    - For descriptors with 'lower_is_better', thresholds are [min_value, warning_value, error_value, max_value].
    - For descriptors with 'higher_is_better', thresholds are [min_value, error_value, warning_value, max_value].
    - If any of these values are not set (i.e., None), thresholds will be None.

    Returns:
        Tuple[List[float], bool, str]: thresholds, reverse_colors, color_by
    """
    reverse_colors = False
    if descriptor.comparison == "lower_is_better":
        thresholds = [descriptor.min_value, descriptor.warning_value, descriptor.error_value, descriptor.max_value]
        if None in thresholds:
            thresholds = None
            color_by = "lower_is_better"
        else:
            reverse_colors = True
            color_by = "thresholds"
    elif descriptor.comparison == "higher_is_better":
        thresholds = [descriptor.min_value, descriptor.error_value, descriptor.warning_value, descriptor.max_value]
        if None in thresholds:
            thresholds = None
            color_by = "higher_is_better"
        else:
            color_by = "thresholds"
    else:
        thresholds = None
        reverse_colors = False
        color_by = None

    if isinstance(descriptor, NumericDescriptor) and descriptor.color_scale:
        color_by = descriptor.color_scale

    return thresholds, reverse_colors, color_by


def get_thresholds_colormap(thresholds: List[float], reverse_colors: bool = False, colors=None):
    """
    Create a matplotlib colormap and normalization object corresponding to the Altair redyellowgreen scheme with 4 points in the domain as specified by the thresholds.

    Args:
        thresholds (List[float]): List of threshold values to define color transitions.
        reverse_colors (bool): If True, reverse the color order.

    Returns:
        Callable[[float], str]: A function that takes a value and returns a hex color string of a color in the colormap.
    """

    # Altair redyellowgreen scheme with 4 points in the domain
    assert len(thresholds) == 4, "Expected 4 thresholds for colormap"
    assert None not in thresholds, "Thresholds must not contain None values"

    if colors is None:
        colors = [
            "#f16e43",
            "#fedd8d",
            "#d7ee8e",
            "#64bc61",
        ]  # https://vega.github.io/vega/docs/schemes/#redyellowgreen

    if reverse_colors:
        colors = colors[::-1]

    # Normalize thresholds to [0, 1] for colormap construction
    t_min, t_max = min(thresholds), max(thresholds)
    normalized_positions = [(t - t_min) / (t_max - t_min) for t in thresholds]

    cmap = mcolors.LinearSegmentedColormap.from_list("threshold_colormap", list(zip(normalized_positions, colors)))

    # Use Normalize to map the values onto the domain
    norm = mcolors.Normalize(vmin=t_min, vmax=t_max)

    return lambda value: mcolors.to_hex(cmap(norm(value)))


def get_plddt_color(thresholds: List[float] = [90, 70, 50], lighter: bool = False):
    """
    Create a color function for pLDDT values based on standard thresholds.

    # > 90, very high confidence, '#0053d6'
    # > 70, high confidence, '#65cbf3'
    # > 50, low confidence, '#ffdb13'
    # < 50, 'Very low confidence', '#ff7d45'
    """

    colors = ["#0053d6", "#65cbf3", "#ffdb13", "#ff7d45"]
    if lighter:
        colors = ["#2a6ed1", "#7fd0f8", "#ffd24d", "#ff8f5e"]
    assert len(colors) == len(thresholds) + 1, "Number of colors must be one more than number of thresholds"

    def color_func(value):
        for t, color in zip(thresholds, colors):
            if value >= t:
                return color
        return colors[-1]

    return color_func


def get_pae_colormap():
    """
    Create a color function for PAE values.
    """
    return get_neutral_colormap(0, 25)


def get_rmsd_colormap():
    """
    Create a color function for RMSD values.
    """
    return get_thresholds_colormap([0, 2, 6, 13], reverse_colors=True)


def get_higher_is_better_colormap(min_val, max_val):
    colors = ["#ffffff", "#d7ee8e"]  # white → light green
    cmap = mcolors.LinearSegmentedColormap.from_list("neutral_accent", colors)

    def color_func(value):
        if pd.isna(value):
            return ""
        # Normalize value to [0, 1] based on min/max
        normed = (value - min_val) / (max_val - min_val) if max_val != min_val else 0.0
        return mcolors.to_hex(cmap(normed))

    return color_func


def get_lower_is_better_colormap(min_val, max_val):
    colors = ["#d7ee8e", "#ffffff"]  # light green -> white
    cmap = mcolors.LinearSegmentedColormap.from_list("neutral_accent", colors)

    def color_func(value):
        if pd.isna(value):
            return ""
        # Normalize value to [0, 1] based on min/max
        normed = (value - min_val) / (max_val - min_val) if max_val != min_val else 1.0
        return mcolors.to_hex(cmap(normed))

    return color_func


def get_neutral_colormap(min_val, max_val):
    colors = ["#ffffff", "#b0b0b0"]  # white -> light gray
    cmap = mcolors.LinearSegmentedColormap.from_list("neutral_accent", colors)

    def color_func(value):
        if pd.isna(value):
            return ""
        # Normalize value to [0, 1] based on min/max
        normed = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        return mcolors.to_hex(cmap(normed))

    return color_func


def get_descriptor_cmap(descriptor: Descriptor, min_val: float, max_val: float):
    """
    Return a color mapping function for the given descriptor.

    Colormap logic:
    - For special descriptors (e.g., pLDDT, PAE), apply custom color schemes.
    - If all thresholds (min_value, warning_value, error_value, max_value) are set, use them for color transitions based on the comparison type.
    - If thresholds are not fully set but a comparison is defined, use a 2-color scale (more green is better) based on comparison type and min/max values in the data.
    - If thresholds are not fully set and no comparison is defined, use a neutral colormap (higher values are darker grey), determined by min/max values in the data.

    Args:
        descriptor (Descriptor): The descriptor for which to create the colormap.
        min_val (float): Minimum value among the selected designs.
        max_val (float): Maximum value among the selected designs.
    """
    if not isinstance(descriptor, NumericDescriptor):
        return lambda val: "#ffffff"

    thresholds, reverse_colors, color_by = get_descriptor_plot_setting(descriptor)

    if descriptor.min_value is not None and descriptor.max_value is not None:
        # When both min_value and max_value are explicitly set in the descriptor, use them instead of data min/max
        min_val, max_val = descriptor.min_value, descriptor.max_value

    return get_cmap(
        color_by=color_by,
        min_val=min_val,
        max_val=max_val,
        thresholds=thresholds,
        reverse_colors=reverse_colors,
    )


def get_cmap(color_by, min_val: float, max_val: float, thresholds: list[float] = None, reverse_colors: bool = False):
    if pd.isna(min_val) or pd.isna(max_val):
        return lambda val: "#ffffff"

    if color_by == "plddt":
        cmap = get_plddt_color(lighter=True)
    elif color_by == "pae":
        cmap = get_pae_colormap()
    elif color_by == "rmsd":
        cmap = get_rmsd_colormap()
    elif color_by == "thresholds" and thresholds is not None:
        cmap = get_thresholds_colormap(thresholds, reverse_colors=reverse_colors)
    elif color_by == "higher_is_better":
        cmap = get_higher_is_better_colormap(min_val, max_val)
    elif color_by == "lower_is_better":
        cmap = get_lower_is_better_colormap(min_val, max_val)
    else:
        cmap = get_neutral_colormap(min_val, max_val)

    return cmap


def get_flag_color(value: float, descriptor: Descriptor) -> Literal["green", "yellow", "orange", "missing", None]:
    if not isinstance(descriptor, NumericDescriptor):
        return None
    if not descriptor.warning_value or not descriptor.error_value:
        return None
    if pd.isna(value):
        return "missing"
    try:
        value = float(value)
    except ValueError:
        return None
    if descriptor.comparison == "higher_is_better":
        if value > descriptor.warning_value:
            return "green"
        elif value > descriptor.error_value:
            return "yellow"
        else:
            return "orange"
    elif descriptor.comparison == "lower_is_better":
        if value < descriptor.warning_value:
            return "green"
        elif value < descriptor.error_value:
            return "yellow"
        else:
            return "orange"
    else:
        return None


def get_descriptor_comment(descriptor: Descriptor) -> str:
    if not isinstance(descriptor, NumericDescriptor):
        return descriptor.description

    thresholds, _, color_by = get_descriptor_plot_setting(descriptor)

    description = descriptor.description

    if color_by == "plddt":
        description += f"\n(pLDDT color scheme: > 90 very high confidence, > 70 high confidence, > 50 low confidence, < 50 very low confidence)"
    elif color_by == "pae":
        description += f"\n(PAE color scheme: lower values are better, higher values indicate less confidence)"
    elif thresholds is not None and color_by == "thresholds":
        description += f"\n(Minimum value: {descriptor.min_value}, Maximum value: {descriptor.max_value},  Warning value: {descriptor.warning_value}, Error value: {descriptor.error_value})"

    return description
