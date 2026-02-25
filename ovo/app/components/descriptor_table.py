import streamlit as st
import pandas as pd
from typing import List, Collection
from cmap import Colormap

from ovo.core.database.models import Descriptor, NumericGlobalDescriptor, ResidueNumberDescriptor
from ovo.core.logic.proteinqc_logic import get_descriptor_cmap


@st.cache_data(hash_funcs={Descriptor: lambda obj: (obj.key)})
def get_descriptor_column_config(descriptor: Descriptor):
    """
    Create a streamlit column_config for a more readable dataframe (labels, help, formatting,...)
    """
    if not isinstance(descriptor, NumericGlobalDescriptor):
        return st.column_config.TextColumn(
            label=descriptor.name, help=f"**{descriptor.name}**: {descriptor.description}", width="small"
        )
    if descriptor.name == "Sequence length":
        format = "%.0f"
    elif "%" in descriptor.name:
        format = "%.2f %%"
    else:
        format = "%.2f"
    return st.column_config.NumberColumn(
        label=descriptor.name, help=f"**{descriptor.name}**: {descriptor.description}", format=format, width="small"
    )


def get_residue_number_column_config(
    descriptor: Descriptor, unique_values: Collection, cmap_name: str = "seaborn:tab10_light", n_colors: int = 10
):
    if isinstance(descriptor, ResidueNumberDescriptor):
        cmap = Colormap(cmap_name)
        colors = list(color.hex for color in cmap.iter_colors(n_colors))
        return st.column_config.MultiselectColumn(
            label=descriptor.name,
            help=f"**{descriptor.name}**: {descriptor.description}",
            width="small",
            options=unique_values,
            color=colors,
        )
    return None


def make_bg_color_func(descriptor, min_val, max_val):
    cmap = get_descriptor_cmap(descriptor, min_val, max_val)

    def color_func(val):
        if pd.isna(val):
            return ""
        return f"background-color: {cmap(val)}"

    return color_func


@st.fragment()
def descriptor_table(design_ids: List[str], descriptors_df: pd.DataFrame, descriptors: List[Descriptor], **kwargs):
    if not design_ids or descriptors_df.empty:
        st.warning("No results yet")
        return
    # Select only columns for the selected descriptors
    assert descriptors_df.columns.nlevels == 2, "Expected nested=True table with 2 levels (tool name, descriptor name)"
    assert len(set(d.key for d in descriptors)) == len(descriptors), (
        f"Duplicate descriptors found in list: {[d.key for d in descriptors]}"
    )
    sequence_cols = [col for col in descriptors_df.columns if col[0] == "Sequence"]
    descriptor_cols = [(descriptor.tool, descriptor.name) for descriptor in descriptors]
    available_cols = set(descriptors_df.columns)
    selected_df = descriptors_df[sequence_cols + [d for d in descriptor_cols if d in available_cols]]
    styles = {}
    column_config = {}

    # When using positional column indices for column config, 0 refers to the first index column
    col_offset = selected_df.index.nlevels

    for descriptor in descriptors:
        col = (descriptor.tool, descriptor.name)
        if col not in selected_df.columns:
            continue
        col_idx = selected_df.columns.get_loc(col) + col_offset
        if isinstance(descriptor, NumericGlobalDescriptor):
            min_val, max_val = selected_df[col].agg(["min", "max"])
        else:
            min_val, max_val = None, None
        styles[col] = selected_df[col].map(make_bg_color_func(descriptor, min_val, max_val))
        if isinstance(descriptor, ResidueNumberDescriptor):
            unique_values = set(x.strip() for row in descriptors_df[col].dropna() for x in row.split(","))
            column_config[col_idx] = get_residue_number_column_config(descriptor, unique_values)
        else:
            column_config[col_idx] = get_descriptor_column_config(descriptor)

    # Combine styles into a DataFrame
    style_df = pd.DataFrame(styles)
    styled_df = selected_df.style.apply(lambda _: style_df, axis=None)

    st.dataframe(styled_df, column_config=column_config, key="descriptor_table", **kwargs)


def residue_number_descriptor_detail_table(descriptor: Descriptor, descriptor_values: pd.Series):
    """
    Returns (table_data, column_config, caption, format_func) for ResidueNumberDescriptor detail view.
    table_data: DataFrame with designs as rows, unique residues as columns, checkmark if present.
    column_config: dict for st.dataframe
    caption: str
    format_func: function for design_id formatting
    """
    unique_residues = set()
    design_to_residues = {}

    # Build mapping from design to set of residues, and collect all unique residues
    for design_id, val in descriptor_values.items():
        residues = {r.strip() for r in str(val).split(",") if r.strip()}
        design_to_residues[design_id] = residues
        unique_residues.update(residues)
    unique_residues = sorted(unique_residues)
    # Remove "None" if present
    if "None" in unique_residues:
        unique_residues.remove("None")
    bool_data = []

    # For each design, create a boolean row for presence of each residue
    for design_id in descriptor_values.index:
        row = [res in design_to_residues[design_id] for res in unique_residues]
        bool_data.append(row)
    bool_df = pd.DataFrame(bool_data, index=descriptor_values.index, columns=unique_residues)

    # Add column for number of residues present in each design and sort
    bool_df["# residues present"] = bool_df.sum(axis=1)
    bool_df = bool_df.sort_values(by="# residues present", ascending=False)

    caption = f"Designs (rows) vs residues (columns) for **{descriptor.name}**"
    column_config = {}
    column_config["# residues present"] = st.column_config.ProgressColumn(
        "# residues present",
        format="%d",
        min_value=0,
        max_value=len(unique_residues),
        width="small",
        help=f"Number of {descriptor.name} present in the design",
    )
    formatted_strings = {
        design_id: f"{design_id} | #residues={row['# residues present']}" for design_id, row in bool_df.iterrows()
    }
    format_func = lambda design_id: formatted_strings.get(design_id, str(design_id))
    return bool_df, column_config, caption, format_func
