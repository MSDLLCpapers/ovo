import traceback

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly import express as px

from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.utils.cached_db import get_cached_design, get_cached_pools
from ovo.core.database.descriptors_clustering import CLUSTER_INFO_REFERENCES, CLUSTERING_PRESETS
from ovo.app.components.descriptor_scatterplot import PlotSettings
from ovo import viz
from ovo.app.components.download_component import download_descriptor_table, download_job_designs_component
from ovo import storage, Design
from ovo.core.database.models_clustering import FoldseekClusteringWorkflow, ProteinClusteringWorkflow
from ovo.core.utils.formatting import datetime_from_utc_to_local
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.pages.designs.explorer import design_visualization_fragment
from ovo.app.components.workflow_visualization_components import (
    visualize_align_structure_selection,
)
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table
from ovo.core.database import DescriptorJob

FOLDSEEK_ALIGNMENT_DESCRIPTIONS_MAP = {
    0: "3Di Gotoh-Smith-Waterman (local)",
    1: "TMalign (global)",
    2: "3Di+AA Gotoh-Smith-Waterman (Default)",
}


def set_foldseek_params(workflow: FoldseekClusteringWorkflow, key_suffix: str = "") -> FoldseekClusteringWorkflow:
    cols_prefilter = st.columns(2, vertical_alignment="bottom")
    with cols_prefilter[1]:
        workflow.params.exhaustive_search = st.checkbox(
            "Use exhaustive search (skip prefilter)",
            value=False,
            key=f"protein_clustering_exhaustive_search_checkbox{key_suffix}",
            help="Skips the fast structural prefilter (3Di/AA k‑mer screen) and performs all‑vs‑all alignments. More sensitive and makes clustering more consistent (all pairs are aligned and evaluated), but much slower.",
        )
    with cols_prefilter[0]:
        workflow.params.s = st.number_input(
            "Prefiltering sensitivity for Foldseek (s)",
            value=9.5,
            min_value=1.0,
            max_value=20.0,
            step=0.5,
            key=f"protein_clustering_sensitivity_input{key_suffix}",
            help="Adjust sensitivity to speed trade-off; lower is faster, higher more sensitive (fast: 7.5, default: 9.5). Not used when exhaustive search is enabled.",
            disabled=workflow.params.exhaustive_search,
        )
    workflow.params.alignment_type = st.selectbox(
        "Alignment type for Foldseek",
        options=[0, 1, 2],
        format_func=lambda option: FOLDSEEK_ALIGNMENT_DESCRIPTIONS_MAP.get(option, "Error in selection"),
        index=2,
        key=f"protein_clustering_alignment_type_input{key_suffix}",
        help="Choose the alignment method for Foldseek",
    )
    st.write(
        "Foldseek clustering uses a greedy set‑cover algorithm. Two sequences can be in the same cluster if they both align to the same cluster representative and that alignment passes all following thresholds:"
    )
    cols = st.columns(4, vertical_alignment="bottom")
    with cols[0]:
        workflow.params.e = st.number_input(
            "E-value (e)",
            value=10.0,
            min_value=0.0,
            step=1.0,
            key=f"protein_clustering_e_value_input{key_suffix}",
            help="E-value threshold for Foldseek, controls the sensitivity of the search",
        )
    with cols[1]:
        workflow.params.c = st.number_input(
            "Min. Coverage",
            value=0.0,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key=f"protein_clustering_coverage_threshold_input{key_suffix}",
            help="List matches above this fraction of aligned (covered) residues",
        )
    with cols[2]:
        workflow.params.tmscore_threshold = st.number_input(
            "Min. TM-score",
            value=0.0,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key=f"protein_clustering_tmscore_threshold_input{key_suffix}",
            help="Accept alignments with an alignment TMscore > thr",
        )
    with cols[3]:
        workflow.params.min_seq_id = st.number_input(
            "Min. Sequence identity",
            value=0.0,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            key=f"protein_clustering_min_seq_id_input{key_suffix}",
            help="List matches above this sequence identity (for clustering)",
        )
    return workflow


@st.cache_data
def umap_scatterplot_plot_preset(
    df_descriptor_values,
    setting: PlotSettings,
    cluster_legend: dict,
    tool: str,
    key: str = "preset_scatterplot",
):
    """Plot available UMAP scatterplots presets for given designs and their cluster information"""
    if not setting.x or not setting.y:
        st.caption("No data available for this preset.")
        return

    # Get plotting subset of descriptor values
    cluster_info = CLUSTER_INFO_REFERENCES[tool]
    cluster_id, cluster_representative = cluster_info["id"], cluster_info["representative"]
    scatterplot_df = df_descriptor_values[
        [
            setting.x.key,
            setting.y.key,
            cluster_id.key,
            cluster_representative.key,
        ]
    ]

    # Hover template
    hovertemplate = "<b>%{customdata[0]}</b><br>Cluster representative: %{customdata[1]}<br>Cluster ID: %{customdata[2]}<br><extra></extra>"

    data_trace = go.Scatter(
        x=scatterplot_df[setting.x.key],
        y=scatterplot_df[setting.y.key],
        mode="markers",
        marker=dict(
            color=scatterplot_df[cluster_representative.key].map(lambda id: cluster_legend[id]["color"]),
            size=8,
        ),
        customdata=scatterplot_df[[cluster_representative.key, cluster_id.key]].reset_index(
            drop=False, names=["design_id"]
        ),
        showlegend=False,
        hovertemplate=hovertemplate,
    )
    # Create figure without legend (legend is shown horizontally above all plots)
    layout = go.Layout(
        xaxis=dict(title=setting.x.name),
        yaxis=dict(title=setting.y.name),
        height=400,
        showlegend=False,
        font=dict(size=18),
    )

    fig = go.Figure(data=data_trace, layout=layout)
    st.plotly_chart(fig, width="stretch", key=key)


def get_cluster_legend(df_descriptor_values, tool: str) -> dict:
    """Get mapping representative_id -> dict with cluster_id and color for cluster legend"""
    cluster_info = CLUSTER_INFO_REFERENCES[tool]

    # Compute unique tuple combinations of cluster representative and cluster id for color mapping
    unique_clusters = set(
        list(zip(*map(df_descriptor_values.get, [cluster_info[col].key for col in cluster_info.keys()])))
    )
    unique_clusters_sorted = sorted(list(unique_clusters), key=lambda x: x[1])
    color_scale = px.colors.qualitative.Plotly
    return {
        cluster_repr: {
            "color": color_scale[i % len(color_scale)],
            "cluster_id": cluster_id,
        }
        for i, (cluster_repr, cluster_id) in enumerate(unique_clusters_sorted)
    }


def umap_scatterplot_component(df_descriptor_values, tool: str):
    design_ids = df_descriptor_values.index.tolist()

    available_presets = {
        key: value
        for key, value in CLUSTERING_PRESETS.items()
        if value["x"].key in df_descriptor_values.columns and value["y"].key in df_descriptor_values.columns
    }

    if not available_presets:
        st.warning(
            f"No scatter plot data available for the selected designs ({'number of designs needs to be at least 10' if len(design_ids) < 10 else ''})."
        )
        return

    # (repr_id, cluster_id) -> color
    cluster_legend = get_cluster_legend(df_descriptor_values, tool)

    # Display horizontal legend above all plots
    st.markdown("**Cluster structure representatives:**")

    # Create legend items in columns for horizontal layout
    legend_cols = st.columns(min(len(cluster_legend), 4))  # Max items per row
    for idx, (cluster_repr, legend) in enumerate(cluster_legend.items()):
        color = legend["color"]
        cluster_id = legend["cluster_id"]
        col_idx = idx % 4
        with legend_cols[col_idx]:
            st.markdown(
                f'<div style="color: {color}; font-size: 15px; margin-bottom: 5px;">'
                f'<span style="font-weight: 500;">● Cluster {cluster_id}</span> {cluster_repr}'
                f"</div>",
                unsafe_allow_html=True,
            )

    # The number of scatterplots defined by number of available presets
    cols = st.columns(len(available_presets), vertical_alignment="center")

    for idx, (preset_name, preset_config) in enumerate(available_presets.items()):
        with cols[idx]:
            st.markdown(f"#### {preset_name}")
            # Create settings from preset configuration
            settings = PlotSettings(x=preset_config["x"], y=preset_config["y"])
            safe_key = f"umap_preset_{idx}"

            # Legend shown in markdown above plots
            umap_scatterplot_plot_preset(df_descriptor_values, settings, cluster_legend, tool, key=safe_key)


def cluster_representatives_tiles(df_descriptor_values, tool: str, job: DescriptorJob, max_representatives: int = 6):
    """Display tiles showing cluster representatives with structure visualization"""
    # Get cluster information from descriptors
    if tool not in CLUSTER_INFO_REFERENCES:
        st.error(f"Unknown clustering tool: {tool}")
        return

    cluster_info = CLUSTER_INFO_REFERENCES[tool]
    cluster_legend = get_cluster_legend(df_descriptor_values, tool)
    repr_descriptor = cluster_info["representative"]
    id_descriptor = cluster_info["id"]

    # Get unique representatives and their cluster info
    representatives = (
        df_descriptor_values[[repr_descriptor.key, id_descriptor.key]]
        .groupby(repr_descriptor.key)
        .agg(cluster_id=(id_descriptor.key, "first"), count=(id_descriptor.key, "count"))
        .sort_values(by="cluster_id")
    )

    if representatives.empty:
        st.info("No cluster representatives found")
        return

    num_representatives = len(representatives)
    if num_representatives > max_representatives:
        representatives = representatives.head(max_representatives)
        st.markdown(f"#### Cluster representatives (Top {max_representatives} clusters)")
    else:
        st.markdown("#### Cluster representatives")

    for col, (repr_design_id, row) in zip(wrapped_columns(len(representatives), 3), representatives.iterrows()):
        with col:
            with st.container(border=True):
                legend = cluster_legend[repr_design_id]
                st.markdown(
                    f'<span style="color: {legend["color"]}; font-size: 20px; font-weight: 500;">'
                    f"● Cluster {row['cluster_id']}"
                    f"</span>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Representative:** {repr_design_id}")
                st.markdown(f"**Size:** {row['count']:,} member{'s' if row['count'] > 1 else ''}")

                design = get_cached_design(repr_design_id)
                if design and design.structure_path:
                    viz.molstar(
                        viz.StructureVisualization(
                            data=storage.read_file_str(design.structure_path),
                            representation=None,
                            representations=[
                                viz.Representation(chain, "cartoon", color="secondary-structure")
                                for chain in job.workflow.chains
                            ],
                        ),
                        key=f"cluster_{repr_design_id}_structure",
                        height="300px",
                    )
                else:
                    st.warning("The structure not available")

    if num_representatives > len(representatives):
        st.warning(
            f"Only the top {max_representatives} cluster representatives are shown out of {num_representatives} total clusters, "
            f"use the dropdown below to inspect all clusters."
        )


@st.fragment
def inspect_clusters(df_descriptor_values, tool: str, job: DescriptorJob):
    """
    Browse clusters and inspect individual structures within each cluster
    """
    cluster_info = CLUSTER_INFO_REFERENCES[tool]
    repr_descriptor = cluster_info["representative"]
    id_descriptor = cluster_info["id"]

    cluster_data_mapping = (
        df_descriptor_values.reset_index(drop=False, names=["design_id"])
        .groupby([id_descriptor.key, repr_descriptor.key])
        .agg(design_ids=("design_id", list))
        .reset_index()
        .set_index(id_descriptor.key)
        .to_dict(orient="index")
    )

    if not cluster_data_mapping:
        st.info("No cluster data available")
        return

    # Let user select a cluster
    available_clusters = sorted(cluster_data_mapping.keys())
    selected_cluster_id = st.selectbox(
        "Select cluster",
        available_clusters,
        format_func=lambda x: f"Cluster {x} - {cluster_data_mapping[x][repr_descriptor.key]} ({len(cluster_data_mapping[x]['design_ids'])} structures)",
        key="selected_cluster",
    )

    if selected_cluster_id is None:
        return

    cluster = cluster_data_mapping[selected_cluster_id]
    cluster_design_ids = cluster["design_ids"]
    representative = cluster[repr_descriptor.key]

    # Ensure the representative design is shown first in the list of cluster designs, followed by the rest (excluding duplicates)
    cluster_design_ids = [representative] + [
        design_id for design_id in cluster_design_ids if design_id != representative
    ]
    cluster_pool_ids = sorted(set(Design.design_id_to_pool_id(design_id) for design_id in cluster_design_ids))
    cluster_pools = get_cached_pools(cluster_pool_ids)
    df_descriptor_values_cluster = df_descriptor_values.loc[cluster_design_ids]

    col1, col2, col3 = st.columns([1, 1, 3])
    # Show cluster information
    with col1:
        st.metric("Cluster ID", selected_cluster_id)
    with col2:
        st.metric("Cluster size", len(cluster_design_ids))
    with col3:
        st.metric("Representative structure of the cluster", representative)

    # Show sequence of all designs in cluster
    st.markdown("### Sequences in the cluster")
    df_descriptors = get_wide_descriptor_table(
        design_ids=df_descriptor_values_cluster.index.tolist(),
        descriptor_keys=df_descriptor_values_cluster.columns,
        nested=True,
        descriptor_job_id=job.id,
    )
    filter_df_descriptor = df_descriptors[[col for col in df_descriptors.columns if "Sequence" in col]]
    descriptor_table(design_ids=cluster_design_ids, descriptors_df=filter_df_descriptor, descriptors=[])

    # Show structures side by side: representative and designs in cluster aligned
    left_col_struct, right_col_struct = st.columns(2, vertical_alignment="top")
    with left_col_struct:
        st.markdown(f"**Representative: {representative}**")
        repr_design = get_cached_design(representative)
        if repr_design and repr_design.structure_path:
            viz.molstar(
                viz.StructureVisualization(
                    data=storage.read_file_str(repr_design.structure_path),
                    representation=None,
                    representations=[
                        viz.Representation(chain, "cartoon", color="secondary-structure")
                        for chain in job.workflow.chains
                    ],
                ),
                key="cluster_repr_structure",
                height="400px",
            )
        else:
            st.warning("Representative structure not available")

    with right_col_struct:
        st.markdown("**Aligned Cluster Structures**")

        try:
            visualize_align_structure_selection(
                design_ids=cluster_design_ids,
                max_examples=15,
                key=f"cluster_{selected_cluster_id}_aligned",
                chains=job.workflow.chains,
            )
        except Exception as e:
            traceback.print_exc()
            st.error(f"Error visualizing aligned structures: {str(e)}")

    st.subheader(f"Download Cluster {selected_cluster_id}")
    download_job_designs_component(cluster_design_ids, cluster_pools)

    # Inspect individual designs
    st.subheader(f"Designs in Cluster {selected_cluster_id}")

    design_visualization_fragment(cluster_design_ids)


def display_clustering_job_params(job: DescriptorJob):
    """Display clustering job parameters"""

    workflow: ProteinClusteringWorkflow = job.workflow

    with st.expander("🔧 Job Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(datetime_from_utc_to_local(job.created_date_utc).strftime("**Submitted on:** %Y-%m-%d %H:%M"))
            st.write("**Chains:**", ", ".join(workflow.chains))

        params = workflow.params.to_dict()
        for i, (param_name, param_value) in enumerate(params.items()):
            param_description = None
            if isinstance(workflow, FoldseekClusteringWorkflow):
                if param_name == "alignment_type":
                    param_description = FOLDSEEK_ALIGNMENT_DESCRIPTIONS_MAP[param_value]
            col = col1 if i % 2 == 0 else col2
            with col:
                param_str = f"**{param_name.capitalize()}:**  {param_value}"
                if param_description:
                    param_str += f" :grey[({param_description})]"
                st.write(param_str)


def download_descriptors_from_job(df_descriptor_values: pd.DataFrame, job: DescriptorJob):
    """Provide download button for descriptor table from clustering job"""
    design_ids = df_descriptor_values.index.tolist()
    descriptor_keys = df_descriptor_values.columns.tolist()
    workflow_name = job.workflow.name.replace(" ", "_").lower()

    download_descriptor_table(
        filename=f"{workflow_name}_{job.id}_descriptors",
        design_ids=design_ids,
        descriptor_keys=descriptor_keys,
        key="download_clustering_descriptors",
        descriptor_job_id=job.id,
        width="content",
    )


def display_clustering_metrics(df_descriptor_values: pd.DataFrame, job: DescriptorJob):
    """Display clustering summary metrics"""
    tool_key = job.workflow.tool_key
    cluster_info = CLUSTER_INFO_REFERENCES[tool_key]
    num_clusters = df_descriptor_values[cluster_info["id"].key].nunique()
    largest_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().max()
    average_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().mean()
    median_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().median()

    with st.container(horizontal=True):
        st.metric("Number of clusters", num_clusters)
        st.metric("Largest cluster size", largest_cluster_size)
        st.metric("Average cluster size", f"{average_cluster_size:.2f}")
        st.metric("Median cluster size", median_cluster_size)
