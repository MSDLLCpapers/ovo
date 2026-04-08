from collections import Counter
from typing import List, Dict

import numpy as np
import pandas as pd
import streamlit as st

from ovo import CategoricalResidueDescriptor, ResidueNumberDescriptor, NumericGlobalDescriptor
from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.components.descriptor_dialog import detail_button
from ovo.app.utils.protein_qc_plots import (
    format_threshold_value,
    descriptor_histograms,
    FLAG_ICONS,
)
from ovo.core.database import descriptors_rfdiffusion
from ovo.core.database.descriptors_proteinqc import (
    PROTEINQC_SEQUENCE_DESCRIPTORS,
    PROTEINQC_STRUCTURE_DESCRIPTORS,
    ESMFOLD_DESCRIPTORS,
    AF2_PRIMARY_DESCRIPTORS,
)
from ovo.core.database.models import Descriptor
from ovo.core.logic.proteinqc_logic import get_flag_color
from ovo.core.utils.formatting import truncated_list


@st.fragment()
def descriptor_overview_tiles(
    descriptors_df: pd.DataFrame,
    descriptors_by_key: Dict[str, Descriptor],
    design_id: str = None,
    histogram_source: str = "all",
):
    st.subheader(
        "Sequence-based descriptors",
        help="Overview of top sequence-based descriptors of the designs. The top histograms show distribution of the descriptor in PDB and the bottom histograms show distribution of the designs colored by preset warning and error thresholds.",
    )
    descriptor_tiles(
        descriptors_df, PROTEINQC_SEQUENCE_DESCRIPTORS, design_id=design_id, histogram_source=histogram_source
    )

    st.subheader(
        "Structure-based descriptors",
        help="Overview of top structure-based descriptors of the designs. The top histograms show distribution of the descriptor in PDB and the bottom histograms show distribution of the designs colored by preset warning and error thresholds.",
    )
    descriptor_tiles(
        descriptors_df, PROTEINQC_STRUCTURE_DESCRIPTORS, design_id=design_id, histogram_source=histogram_source
    )

    # AF2 initial guess
    af_descriptors = [descriptor for descriptor in AF2_PRIMARY_DESCRIPTORS if descriptor.key in descriptors_by_key]
    if af_descriptors:
        st.subheader("Refolding test: AlphaFold2 initial guess")
        descriptor_tiles(descriptors_df, af_descriptors, design_id=design_id, histogram_source=histogram_source)

    # ESMFold for scaffold design
    esmfold_descriptors = [descriptor for descriptor in ESMFOLD_DESCRIPTORS if descriptor.key in descriptors_by_key]
    if esmfold_descriptors:
        st.subheader("Refolding test: ESMFold")
        descriptor_tiles(descriptors_df, esmfold_descriptors, design_id=design_id, histogram_source=histogram_source)

    backbone_metrics_descriptors = [
        descriptor for descriptor in descriptors_rfdiffusion.BACKBONE_METRICS if descriptor.key in descriptors_by_key
    ]
    # FIXME: ADJUST HOTSPOT INTERFACE METRICS
    if backbone_metrics_descriptors:
        st.subheader("Backbone metrics")
        descriptor_tiles(
            descriptors_df, backbone_metrics_descriptors, design_id=design_id, histogram_source=histogram_source
        )


def get_residue_presence_df(descriptor: Descriptor, nonnull_descriptor_values, total_designs: int):
    """
    Returns a DataFrame with each unique residue and the percentage of designs in which it is present.
    """
    # Filter out empty or non-string values
    nonnull_values = [v for v in nonnull_descriptor_values if isinstance(v, str) and v.strip()]
    all_residues = []

    # Collect all residues from all designs by splitting on commas
    for v in nonnull_values:
        all_residues.extend([r.strip() for r in v.split(",") if r.strip()])
    if not all_residues:
        return None

    # Count in how many designs each residue is present
    residue_in_designs = Counter()
    for v in nonnull_values:
        residues = {r.strip() for r in v.split(",") if r.strip()}
        for residue in residues:
            residue_in_designs[residue] += 1
    residue_df = pd.DataFrame(
        {
            descriptor.name: list(residue_in_designs.keys()),
            "% of designs": [
                100 * count / total_designs if total_designs else 0 for count in residue_in_designs.values()
            ],
        }
    )
    residue_df = residue_df.sort_values(by="% of designs", ascending=False)
    return residue_df


def show_flag_counts(descriptor: NumericGlobalDescriptor, values: pd.Series, design_id: str = None):
    """Show a list of design counts by group (missing, green, yellow, orange)."""
    warning_ids = {"missing": [], "green": [], "yellow": [], "orange": []}
    if design_id:
        # only show results for selected design
        values = {design_id: values.get(design_id)}
    for d_id, val in values.items():
        flag = get_flag_color(val, descriptor)
        if not flag:
            continue
        warning_ids[flag].append(d_id)
    for flag, ids in warning_ids.items():
        if not ids:
            continue
        if flag == "missing":
            label = "missing value" if len(ids) == 1 else "missing values"
            color = "grey"
        else:
            label = f"{flag} flag" if len(ids) == 1 else f"{flag} flags"
            color = flag
        icon = FLAG_ICONS.get(flag, "")
        st.markdown(f":{color}-background[{icon} **{len(ids):,}** {label}]", help=truncated_list(ids, 10))


def descriptor_tiles(
    descriptors_df: pd.DataFrame, descriptors: List[Descriptor], design_id: str = None, histogram_source: str = "all"
):
    columns = wrapped_columns(len(descriptors), wrap=3, gap="medium")
    for col, descriptor in zip(columns, descriptors):
        with col:
            with st.container(border=True):
                st.markdown(f"#### {descriptor.name}", help=descriptor.description)
                if (descriptor.tool, descriptor.name) not in descriptors_df.columns:
                    st.warning("Not available")
                    continue
                descriptor_values = descriptors_df[(descriptor.tool, descriptor.name)]
                if isinstance(descriptor, NumericGlobalDescriptor):
                    descriptor_values = pd.to_numeric(descriptor_values, errors="coerce")

                nonnull_descriptor_values = descriptor_values.dropna().tolist()

                if not nonnull_descriptor_values:
                    st.warning("Not available")
                    continue

                if len(descriptor_values) > len(nonnull_descriptor_values):
                    perc_missing = (1 - len(nonnull_descriptor_values) / len(descriptor_values)) * 100
                    st.markdown(
                        f":grey-background[:material/question_mark:] **{perc_missing:.2f}%** values missing",
                    )

                if isinstance(descriptor, CategoricalResidueDescriptor):
                    top_n = 10
                    st.write(f"Top {top_n} most common values")
                    counts_df = pd.Series(nonnull_descriptor_values).value_counts().head(top_n).reset_index()
                    counts_df.columns = [descriptor.name, "Count"]
                    st.dataframe(
                        counts_df,
                        column_config={
                            descriptor.name: st.column_config.Column(descriptor.name),
                            "Count": st.column_config.ProgressColumn(
                                "Count",
                                format="%d",
                                min_value=0,
                                max_value=max(1, int(counts_df["Count"].max())),
                            ),
                        },
                        hide_index=True,
                        width="stretch",
                        height=200,
                    )
                    with st.container(horizontal=True, horizontal_alignment="right"):
                        detail_button(descriptor, descriptor_values, design_id=design_id)

                elif isinstance(descriptor, NumericGlobalDescriptor):
                    if design_id:
                        st.metric(
                            descriptor.name, format_threshold_value(descriptor.name, descriptor_values.loc[design_id])
                        )
                    else:
                        avg_value = np.mean(nonnull_descriptor_values)
                        st.metric(f"Average {descriptor.name}", format_threshold_value(descriptor.name, avg_value))

                    fig = descriptor_histograms(
                        descriptor=descriptor,
                        histogram_source=histogram_source,
                        values=nonnull_descriptor_values,
                        precomputed_histogram_height=25,
                        pool_histogram_height=70,
                        value=descriptor_values.loc[design_id] if design_id else None,
                        value_label=design_id,
                    )

                    st.altair_chart(fig, width="stretch")

                    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
                        with st.container():
                            st.empty()
                            show_flag_counts(descriptor, descriptor_values, design_id=design_id)
                        detail_button(descriptor, descriptor_values, design_id=design_id)

                # Support for ResidueNumberDescriptor
                elif isinstance(descriptor, ResidueNumberDescriptor):
                    residue_df = get_residue_presence_df(descriptor, nonnull_descriptor_values, descriptors_df.shape[0])
                    if residue_df is None or residue_df.empty:
                        st.warning("No residue data available.")
                    else:
                        st.dataframe(
                            residue_df,
                            column_config={
                                descriptor.name: st.column_config.Column(descriptor.name),
                                "% of designs": st.column_config.ProgressColumn(
                                    "% of designs",
                                    format="%.1f%%",
                                    min_value=0,
                                    max_value=100,
                                    help="Percentage of designs in which the residue is present",
                                ),
                            },
                            hide_index=True,
                            width="stretch",
                            height=200,
                        )
                    with st.container(horizontal=True, horizontal_alignment="right"):
                        detail_button(descriptor, descriptor_values, design_id=design_id)
                else:
                    st.info("Visualization for this type of descriptor coming soon")
                    with st.container(horizontal=True, horizontal_alignment="right"):
                        detail_button(descriptor, descriptor_values, design_id=design_id)
