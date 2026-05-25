from typing import Callable

import pandas as pd
import streamlit as st

from ovo import storage, CategoricalResidueDescriptor, ResidueNumberDescriptor, NumericGlobalDescriptor, Descriptor
from ovo import viz
from ovo.app.components.descriptor_table import residue_number_descriptor_detail_table
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.workflow_visualization_components import visualize_design_sequence
from ovo.app.utils.cached_db import get_cached_design, get_cached_pool
from ovo.app.utils.protein_qc_plots import FLAG_ICONS
from ovo.core.database.descriptors_proteinqc import (
    PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS_BY_KEY,
)
from ovo.core.logic.proteinqc_logic import get_flag_color


def on_dismiss_dialog():
    st.query_params.pop("dialog", None)


@st.dialog("Detail", on_dismiss=on_dismiss_dialog)
def detail_descriptor_dialog(descriptor, descriptor_values: pd.Series, design_id: str = None):
    st.markdown(
        """
    <style>
    div[role="dialog"] {
        width: 80vw !important;
        max-width: 1200px !important;
        height: auto;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.write(f"**{descriptor.name}**: {descriptor.description}")

    col1, col2 = st.columns([2, 3.5])

    with col1:
        table_data, format_func = detail_table(descriptor, descriptor_values)
        if table_data is None:
            return

    with col2:
        detail_design(descriptor, descriptor_values, table_data, format_func, design_id=design_id)


def detail_button(descriptor, descriptor_values: pd.Series, design_id: str = None):
    if st.button("Show more", key=f"{descriptor.name}_btn"):
        st.query_params["dialog"] = descriptor.key
    if st.query_params.get("dialog") == descriptor.key:
        detail_descriptor_dialog(descriptor, descriptor_values, design_id=design_id)


def detail_table(descriptor, descriptor_values: pd.Series):
    table_data = pd.DataFrame({"value": descriptor_values})
    table_data.index.name = "Design ID"
    styler = None

    if isinstance(descriptor, CategoricalResidueDescriptor):
        value_counts = descriptor_values.value_counts()
        table_data["category_abundance"] = descriptor_values.map(value_counts)
        caption = f"Design sorted by **{descriptor.name}** category abundance"
        table_data = table_data.sort_values(by=["category_abundance", "value"], ascending=[False, True])
        column_config = {
            "design_id": st.column_config.Column("Design ID"),
            "value": st.column_config.TextColumn(descriptor.name),
            "category_abundance": st.column_config.ProgressColumn(
                "Category #",
                help="Category abundance among the designs",
                format="%d",
                min_value=0,
                max_value=int(table_data["category_abundance"].max()),
                width="small",
            ),
        }

        def format_func(design_id):
            return f"{design_id} | {descriptor.name} = {table_data.value.loc[design_id]}"

    elif isinstance(descriptor, NumericGlobalDescriptor):
        caption = f"Designs sorted by **{descriptor.name}**"
        min_val = descriptor.min_value if descriptor.min_value is not None else float(table_data["value"].min())
        max_val = descriptor.max_value if descriptor.max_value is not None else float(table_data["value"].max())

        # Streamlit shows error if min_val == max_val in ProgressColumn so we adjust slightly
        if min_val == max_val:
            epsilon = 1e-6
            min_val -= epsilon
            max_val += epsilon

        table_data = table_data.sort_values(by="value", ascending=True)
        flags = table_data["value"].apply(get_flag_color, descriptor=descriptor)
        if not flags.isna().all():
            table_data["flag"] = flags
            # style flag column
            colors = {
                "missing": "#eeeeee",  # light grey
                "green": "#edf9ee",  # light green
                "yellow": "#ffffec",  # light yellow
                "orange": "#fff6eb",  # orange
            }
            styler = table_data.style.map(
                lambda value: f"background-color: {colors[value]}",
                subset=["flag"],
            )

        column_config = {
            "design_id": st.column_config.Column("Design ID"),
            "value": st.column_config.ProgressColumn(
                descriptor.name, format="%.2f", min_value=min_val, max_value=max_val, color="#111111"
            ),
            "flag": st.column_config.Column("Flag", width="small"),
        }

        def format_func(design_id):
            return f"{design_id} | {descriptor.name} = {table_data.value.loc[design_id]:.2f}"

    elif isinstance(descriptor, ResidueNumberDescriptor):
        table_data, column_config, caption, format_func = residue_number_descriptor_detail_table(
            descriptor, descriptor_values
        )
    else:
        # TODO: Support other descriptor tiles
        st.info("Detail view for this type of descriptor coming soon")
        return None, None

    st.caption(caption)
    st.dataframe(
        styler if styler is not None else table_data,
        column_config=column_config,
        width="stretch",
    )
    return table_data, format_func


def detail_design(
    descriptor: Descriptor,
    descriptor_values: pd.Series,
    table_data: pd.DataFrame,
    format_func: Callable,
    design_id: str = None,
):
    design_id = st.selectbox(
        "Select design:",
        options=table_data.index,
        key="design_id_select",
        format_func=format_func,
        index=0 if design_id is None or design_id not in table_data.index else table_data.index.get_loc(design_id),
    )

    value = descriptor_values.loc[design_id]
    flag = get_flag_color(value, descriptor)
    if flag:
        icon = FLAG_ICONS.get(flag, "")
        if flag == "missing":
            st.markdown(f":grey-background[{icon} Value missing]")
        else:
            # TODO explain thresholds
            #  and maybe compare to percentile in PDB ({descriptor.name} = 123, higher than 95% of PDB)
            st.markdown(f":{flag}-background[{icon} {flag.title()} flag]")

    # TODO: Allow labeling designs - nested dialogs are currently not supported
    # design_labeling_fragment(design_id)
    visualize_design_sequence(design_id)

    design = get_cached_design(design_id)

    left, right = st.columns([1, 2], vertical_alignment="center")

    with left:
        colors_and_types = {
            ("chain-id", "cartoon"): (
                "Cartoon",
                "",
            ),
            ("hydrophobicity", "molecular-surface"): (
                "Surface | Hydrophobicity",
                "Surface colored by hydrophobicity scale: :green-badge[**green** = hydroPHOBIC] :red-badge[**red** = hydroPHILIC]",
            ),
            ("hydrophobicity", "cartoon+ball-and-stick"): (
                "Side chains | Hydrophobicity",
                "Cartoon and side chains colored by hydrophobicity scale: :green-badge[**green** = hydroPHOBIC] :red-badge[**red** = hydroPHILIC]",
            ),
            ("residue-charge", "molecular-surface"): (
                "Surface | Residue charge",
                "Surface colored by residue charge: :blue-badge[**blue** = positive] :red-badge[**red** = negative]",
            ),
            ("residue-charge", "cartoon+ball-and-stick"): (
                "Side chains | Residue charge",
                "Cartoon and side chains colored by residue charge: :blue-badge[**blue** = positive] :red-badge[**red** = negative]",
            ),
        }
        rep_type_index = 0
        if descriptor.key in PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS_BY_KEY:
            rep_type_index = 1
        color, representation_type = st.selectbox(
            "Representation",
            options=list(colors_and_types.keys()),
            format_func=lambda x: colors_and_types[x][0],
            key=f"colors_and_types_input_{descriptor.key}",
            label_visibility="collapsed",
            index=rep_type_index,
        )

    with right:
        st.write(colors_and_types[(color, representation_type)][1])

    left, right = st.columns([1.5, 1])
    with left:
        viz.molstar(
            viz.StructureVisualization(
                data=storage.read_file_str(design.structure_path),
                representations=[
                    viz.Representation(chain_id, representation_type, color=color)
                    for chain in design.spec.chains
                    for chain_id in chain.chain_ids
                ],
            ),
            key="dialog_structure",
            height="300px",
        )
    with right:
        pool = get_cached_pool(design.pool_id)
        st.caption(f"Download {design.id}")
        download_job_designs_component(design_ids=[design_id], pools=[pool], key="single", single_line=False)
