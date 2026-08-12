import io
import traceback

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly import express as px

from ovo import storage, Design
from ovo import viz
from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.components.descriptor_scatterplot import PlotSettings
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.workflow_visualization_components import (
    visualize_align_structure_selection,
)
from ovo.app.pages.designs.explorer import design_visualization_fragment
from ovo.app.utils.cached_db import (
    get_cached_design,
    get_cached_pools,
    get_cached_descriptor_values,
    get_cached_designs,
    get_cached_num_cyclic,
)
from ovo.core.database import DescriptorJob
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.database.descriptors_clustering import (
    CLUSTER_INFO_REFERENCES,
    CLUSTERING_PRESETS,
    INTERFACE_HIERARCHICAL_REPR_CLUSTER,
    INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID,
)
from ovo.core.database.descriptors_rfdiffusion import PYDSSP_STRING
from ovo.core.database.models_clustering import (
    BaseHierarchicalClusteringWorkflow,
    FoldseekClusteringWorkflow,
    InterfaceResiduesHierarchicalClusteringWorkflow,
    ProteinClusteringWorkflow,
    SecondaryStructureHierarchicalClusteringWorkflow,
    RMSDHierarchicalClusteringWorkflow,
)
from ovo.core.database.models_clustering import FOLDSEEK_KMER_PREFILTER_MIN_LENGTH
from ovo.core.logic.descriptor_logic import (
    get_interface_residues_by_design_table,
    get_wide_descriptor_table,
)
from ovo.core.utils.colors import hex_to_rgba
from ovo.core.utils.formatting import datetime_from_utc_to_local

FOLDSEEK_ALIGNMENT_DESCRIPTIONS_MAP = {
    0: "3Di Gotoh-Smith-Waterman (local)",
    1: "TMalign (global)",
    2: "3Di+AA Gotoh-Smith-Waterman (Default)",
}

FOLDSEEK_PREFILTER_DESCRIPTION_MAP = {
    0: "kmer/ungapped (Foldseek default)",
    1: "ungapped (default for short sequences)",
    2: "nofilter",
    3: "ungapped&gapped",
}


def has_short_sequences_for_chains(
    design_ids: list[str],
    chains: list[str],
    min_length: int = FOLDSEEK_KMER_PREFILTER_MIN_LENGTH,
) -> bool:
    """
    Check if any designs have sequences shorter than min_length for the specified chains.
    Sequences shorter than FOLDSEEK_KMER_PREFILTER_MIN_LENGTH residues fail in Foldseek easy-search with prefilter_mode 0.

    Returns:
        True if any sequence is shorter than min_length, False otherwise
    """
    designs = get_cached_designs(design_ids)

    for design in designs:
        if not design.spec:
            continue
        for chain_id in chains:
            chain = design.spec.get_chain(chain_id)
            if chain and chain.sequence and len(chain.sequence) < min_length:
                return True

    return False


def set_foldseek_params(workflow: FoldseekClusteringWorkflow, key_suffix: str = "") -> FoldseekClusteringWorkflow:
    if get_cached_num_cyclic(workflow.design_ids):
        st.warning(
            "Foldseek is not aware of the macrocyclic bond, so it will treat each peptide as linear. "
            'To make sure that similar peptides with "rotated" starting positions are placed in the same cluster, consider using hierarchical clustering instead.'
        )

    has_short_seqs = has_short_sequences_for_chains(workflow.design_ids, workflow.chains)

    if has_short_seqs and workflow.params.prefilter_mode == 0:
        workflow.params.prefilter_mode = 1
        st.caption(
            f":material/info: **Auto-detected some short sequences (<{FOLDSEEK_KMER_PREFILTER_MIN_LENGTH} residues).** "
            f"Prefilter mode automatically set to ungapped.",
        )

    cols_prefilter = st.columns(3, vertical_alignment="bottom")
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
    with cols_prefilter[2]:
        workflow.params.prefilter_mode = st.selectbox(
            "Prefilter mode for Foldseek easy-search",
            options=[0, 1, 2, 3],
            format_func=lambda option: FOLDSEEK_PREFILTER_DESCRIPTION_MAP.get(option, "Error in selection"),
            index=workflow.params.prefilter_mode,
            key=f"protein_clustering_prefilter_mode_input{key_suffix}",
            help=f"Prefilter mode: 0=kmer/ungapped (default, fastest), 1=ungapped, 2=nofilter, 3=ungapped&gapped. ⚠️ Mode 0 will skip sequences <{FOLDSEEK_KMER_PREFILTER_MIN_LENGTH} residues from easy-search, which can cause Foldseek pipeline to fail. Use mode 1 or 2 for pools with mostly short sequences.",
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


def set_hierarchical_clustering_params(
    workflow: BaseHierarchicalClusteringWorkflow, cyclic: bool = False, key_suffix: str = ""
):
    """Set hierarchical clustering parameters based on workflow type"""

    # Configuration based on similarity method
    config = {
        "sequence": {
            "threshold_range": (0.0, 1.0),
            "threshold_help": "Sequence distance threshold. Lower values = tighter clusters. 0.1-0.2: Very similar sequences (>80% identity), 0.3-0.5: Moderate similarity (50-70% identity), 0.6-0.8: Loosely related sequences",
            "show_cyclic": True,
        },
        "rmsd": {
            "threshold_range": (0.0, None),
            "threshold_help": "CEAlign RMSD distance threshold in Ångströms. Lower values = more structurally similar. 0.5-1.5Å: Very similar structures, 2.0-4.0Å: Moderate structural differences, 5.0+Å: Significant structural differences.",
            "show_cyclic": True,
        },
        "interface_residues": {
            "threshold_range": (0.0, 1.0),
            "threshold_help": "Jaccard distance threshold for interface residues. 0.2: Very tight clusters (≥80% similarity), 0.5: Default, 0.8: Loose clusters (≥20% similarity)",
            "show_cyclic": False,
        },
        "secondary_structure": {
            "threshold_range": (0.0, 1.0),
            "threshold_help": "Secondary structure distance threshold. Lower values = more similar fold patterns. 0.1-0.3: Very similar secondary structures, 0.4-0.6: Moderate structural similarity, 0.7-0.9: Different but related folds",
            "show_cyclic": True,
        },
    }

    method = workflow.params.similarity_method
    cfg = config[method]

    linkage_options = ["single", "complete", "average", "ward"]
    workflow.params.linkage_method = st.selectbox(
        "Linkage method",
        options=linkage_options,
        index=linkage_options.index(workflow.params.linkage_method)
        if workflow.params.linkage_method in linkage_options
        else 0,
        key=f"hierarchical_clustering_linkage_method_input{key_suffix}",
        help="The linkage algorithm to use for hierarchical clustering. Single: minimum distance, complete: maximum distance, average: average distance, ward: minimizes variance within clusters.",
    )
    criterion_options = ["distance", "maxclust"]
    workflow.params.criterion = st.selectbox(
        "Clustering criterion",
        options=criterion_options,
        index=criterion_options.index(workflow.params.criterion)
        if workflow.params.criterion in criterion_options
        else 0,
        key=f"sequence_hierarchical_clustering_criterion_input{key_suffix}",
        help="The criterion to use for cutting the hierarchy into flat clusters. 'distance' merges samples under a given distance threshold, 'maxclust' cuts to achieve (at most) the given number of clusters.",
    )

    # Configure threshold input based on criterion
    if workflow.params.criterion == "distance":
        workflow.params.threshold = st.number_input(
            "Distance threshold",
            value=workflow.params.threshold,
            min_value=cfg["threshold_range"][0],
            max_value=cfg["threshold_range"][1],
            key=f"hierarchical_clustering_threshold_input{key_suffix}",
        )
        st.caption(cfg["threshold_help"])
    elif workflow.params.criterion == "maxclust":
        workflow.params.threshold = st.number_input(
            "Maximum number of clusters",
            value=int(workflow.params.threshold) if workflow.params.threshold >= 1 else 10,
            min_value=1,
            max_value=None,
            step=1,
            key=f"hierarchical_clustering_threshold_input{key_suffix}",
            help="Maximum number of clusters to form. The algorithm will cut the dendrogram to produce exactly this many clusters.",
        )
    else:
        st.error("Unknown clustering criterion selected.")
        raise ValueError("Unknown clustering criterion selected.")

    if cfg["show_cyclic"]:
        workflow.params.cyclic = st.checkbox(
            "Cyclic clustering",
            value=cyclic,
            key=f"sequence_hierarchical_clustering_cyclic_checkbox{key_suffix}",
            help="Whether to treat the sequence as cyclic for clustering (e.g. for cyclic peptides). If enabled, all rotations of the sequence/structure will be considered when calculating distances.",
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
                    if isinstance(job.workflow, InterfaceResiduesHierarchicalClusteringWorkflow):
                        default_representation_type = "cartoon"
                        chain_color = "uniform"
                        color_params = {"value": legend["color"].replace("#", "0x")}
                    else:
                        default_representation_type = None
                        chain_color = "secondary-structure"
                        color_params = None

                    viz.molstar(
                        viz.StructureVisualization(
                            data=storage.read_file_str(design.structure_path),
                            representation_type=default_representation_type,
                            representations=[
                                viz.Representation(
                                    job.workflow.chains,
                                    representation_type="cartoon",
                                    color=chain_color,
                                    color_params=color_params,
                                ),
                            ],
                            auto_zoom_chains=job.workflow.chains,
                        ),
                        key=f"cluster_{repr_design_id}_structure",
                        height="300px",
                    )
                else:
                    st.warning("The structure not available")

    if num_representatives > len(representatives):
        st.warning(
            f"Only the top {max_representatives} cluster representatives are shown out of {num_representatives} total clusters, "
            f"use the Cluster browser tab to inspect all clusters."
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

    color_mapping = get_cluster_color_mapping_from_legend(df_descriptor_values, job.workflow.tool_key)

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
    descriptors = []
    if isinstance(job.workflow, SecondaryStructureHierarchicalClusteringWorkflow):
        descriptors.append(PYDSSP_STRING)
    if isinstance(job.workflow, InterfaceResiduesHierarchicalClusteringWorkflow):
        descriptors.append(ALL_DESCRIPTORS_BY_KEY[job.workflow.input_descriptor_key])

    # Do not use descriptors associated with required descriptor jobs
    descriptors = [d for d in descriptors if not d.required_descriptor_job]
    df_descriptors = get_wide_descriptor_table(
        design_ids=df_descriptor_values_cluster.index.tolist(),
        descriptor_keys=[d.key for d in descriptors] if descriptors else None,
        nested=True,
    )
    descriptor_table(design_ids=cluster_design_ids, descriptors_df=df_descriptors, descriptors=descriptors)

    # Show structures side by side: representative and designs in cluster aligned
    visualize_interface = isinstance(job.workflow, InterfaceResiduesHierarchicalClusteringWorkflow)
    left_col_struct, right_col_struct = st.columns(2, vertical_alignment="top")
    with left_col_struct:
        st.markdown(f"**Representative: {representative}**")
        repr_design = get_cached_design(representative)
        if repr_design and repr_design.structure_path:
            if visualize_interface:
                default_representation_type = "cartoon"
                chain_color = "uniform"
                color_params = {"value": color_mapping[selected_cluster_id].replace("#", "0x")}
            else:
                default_representation_type = None
                chain_color = "secondary-structure"
                color_params = None
            viz.molstar(
                viz.StructureVisualization(
                    data=storage.read_file_str(repr_design.structure_path),
                    representation_type=default_representation_type,
                    representations=[
                        viz.Representation(job.workflow.chains, "cartoon", color=chain_color, color_params=color_params)
                    ],
                    auto_zoom_chains=job.workflow.chains,
                ),
                key="cluster_repr_structure",
                height="400px",
            )
        else:
            st.warning("Representative structure not available")

    with right_col_struct:
        st.markdown("**Aligned Cluster Structures**")

        if visualize_interface:
            descriptor = ALL_DESCRIPTORS_BY_KEY[job.workflow.input_descriptor_key]
            target_residues = df_descriptors[(descriptor.tool, descriptor.name)]
            valid_residue_ids = []
            for residues in target_residues.dropna().values:
                for residue_id in str(residues).split(","):
                    residue_id = residue_id.strip()
                    if not residue_id or residue_id.lower() == "none":
                        continue
                    valid_residue_ids.append(residue_id)
            align_chains = sorted({residue_id[0] for residue_id in valid_residue_ids})
            assert align_chains, "No target interface residues found"
        else:
            align_chains = job.workflow.chains
        try:
            visualize_align_structure_selection(
                design_ids=cluster_design_ids,
                max_examples=15,
                key=f"cluster_{selected_cluster_id}_aligned",
                align_chains=align_chains,
                visualize_chains=job.workflow.chains,
                default_representation_type="cartoon" if visualize_interface else None,
                color="chain-id" if visualize_interface else "secondary-structure",
                auto_zoom_chains=job.workflow.chains,
            )
            if isinstance(job.workflow, RMSDHierarchicalClusteringWorkflow):
                st.info("Displayed alignment and RMSD are produced using superposition, not the original CEAlign.")
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
                    param_description = FOLDSEEK_ALIGNMENT_DESCRIPTIONS_MAP.get(param_value)
                elif param_name == "prefilter_mode":
                    param_description = FOLDSEEK_PREFILTER_DESCRIPTION_MAP.get(param_value)
            col = col1 if i % 2 == 0 else col2
            with col:
                param_str = f"**{param_name.capitalize()}:**  {param_value}"
                if param_description:
                    param_str += f" :grey[({param_description})]"
                st.write(param_str)


def display_clustering_metrics(df_descriptor_values: pd.DataFrame, job: DescriptorJob):
    """Display clustering summary metrics"""
    tool_key = job.workflow.tool_key
    cluster_info = CLUSTER_INFO_REFERENCES[tool_key]
    num_designs = len(df_descriptor_values)
    num_clusters = df_descriptor_values[cluster_info["id"].key].nunique()
    largest_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().max()
    average_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().mean()
    median_cluster_size = df_descriptor_values[cluster_info["id"].key].value_counts().median()

    with st.container(horizontal=True):
        st.metric("Number of designs", num_designs)
        st.metric("Number of clusters", num_clusters)
        st.metric("Largest cluster size", largest_cluster_size)
        st.metric("Average cluster size", f"{average_cluster_size:.2f}")
        st.metric("Median cluster size", median_cluster_size)


def interface_clustering_table(
    df_descriptor_values: pd.DataFrame, workflow: InterfaceResiduesHierarchicalClusteringWorkflow
):
    descriptor_values = get_cached_descriptor_values(workflow.input_descriptor_key, design_ids=workflow.design_ids)
    descriptor_values_by_design_series = pd.Series(descriptor_values, index=workflow.design_ids)
    interface_residues_table = get_interface_residues_by_design_table(descriptor_values_by_design_series)
    df_merged_test = (
        df_descriptor_values[[INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID.key, INTERFACE_HIERARCHICAL_REPR_CLUSTER.key]]
        .merge(interface_residues_table, left_index=True, right_index=True)
        .sort_values(by=INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID.key)
    )

    # Apply cluster-based row coloring using the same colors as in UMAP and cluster tiles
    color_mapping = get_cluster_color_mapping_from_legend(df_descriptor_values, workflow.tool_key)

    # Drop the cluster representative column for display
    df_for_display = df_merged_test.drop(columns=[INTERFACE_HIERARCHICAL_REPR_CLUSTER.key])
    styled_df = style_cluster_rows(df_for_display, INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID.key, color_mapping)
    st.dataframe(
        styled_df,
        column_config={
            INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID.key: st.column_config.NumberColumn("Cluster ID", width="small")
        },
    )


def get_cluster_color_mapping_from_legend(df_descriptor_values, tool_key: str) -> dict:
    """Get mapping cluster_id -> color using existing cluster legend logic"""
    cluster_legend = get_cluster_legend(df_descriptor_values, tool_key)

    # Convert (repr_id, cluster_info) -> cluster_id -> color mapping
    cluster_color_map = {}
    for cluster_repr, legend_info in cluster_legend.items():
        cluster_id = legend_info["cluster_id"]
        color = legend_info["color"]
        cluster_color_map[cluster_id] = color

    return cluster_color_map


def style_cluster_rows(df: pd.DataFrame, cluster_id_col: str, color_mapping: dict):
    """Apply background color styling to rows based on cluster ID"""

    def highlight_cluster(row):
        cluster_id = row[cluster_id_col]
        hex_color = color_mapping.get(cluster_id, "#FFFFFF")  # Default to white if not found
        rgba_color = hex_to_rgba(hex_color, alpha=0.15)
        return [f"background-color: {rgba_color}"] * len(row)

    return df.style.apply(highlight_cluster, axis=1)


def prepare_distance_matrix_for_visualization(
    artifact_file_path: str,
    df_descriptor_values: pd.DataFrame,
    cluster_id_key: str,
    representative_id_key: str,
    max_display_size: int = 500,
) -> tuple[pd.DataFrame, dict]:
    """Load, reorder, and subsample distance matrix for visualization.

    :param artifact_file_path: Storage path to distance matrix CSV.gz file
    :param df_descriptor_values: DataFrame with cluster assignments and representatives
    :param cluster_id_key: Column name for cluster IDs
    :param representative_id_key: Column name for representative IDs
    :param max_display_size: Maximum number of designs to display (subsamples if larger)
    :return: Tuple of (prepared matrix DataFrame, metadata dict)
    """
    # 1. Load matrix from storage
    matrix_bytes = storage.read_file_bytes(artifact_file_path)
    matrix_df = pd.read_csv(io.BytesIO(matrix_bytes), index_col=0, compression="gzip")

    # 2. Get cluster info and sort by cluster ID
    cluster_info = df_descriptor_values[[cluster_id_key, representative_id_key]].copy()
    cluster_info = cluster_info.sort_values(cluster_id_key)

    # 3. Reorder matrix (rows and columns) by cluster
    ordered_ids = cluster_info.index.tolist()
    matrix_ordered = matrix_df.loc[ordered_ids, ordered_ids]

    # 4. Get cluster IDs and representatives in order (for color bars and hover)
    cluster_ids = cluster_info[cluster_id_key].tolist()
    representative_ids = cluster_info[representative_id_key].tolist()

    # 5. Build initial metadata (before potential subsampling)
    original_n_designs = len(matrix_ordered)
    cluster_sizes = cluster_info[cluster_id_key].value_counts().sort_index().to_dict()
    representatives = cluster_info[representative_id_key].unique().tolist()

    # 6. Subsample if too large
    if original_n_designs > max_display_size:
        # Show warning about subsampling
        st.warning(
            f"Matrix too large ({original_n_designs} > {max_display_size}). "
            f"Showing up to {max_display_size} designs (representatives prioritized) to keep the plot responsive."
        )

        # Group designs by cluster
        cluster_to_indices = {}
        for i, (cluster_id, design_id) in enumerate(zip(cluster_ids, ordered_ids)):
            if cluster_id not in cluster_to_indices:
                cluster_to_indices[cluster_id] = []
            cluster_to_indices[cluster_id].append(i)

        # Select designs: all representatives + proportional sampling
        selected_indices = set()

        # First, add all representatives
        for i, (design_id, repr_id) in enumerate(zip(ordered_ids, representative_ids)):
            if design_id == repr_id:
                selected_indices.add(i)

        # Then proportionally sample from each cluster
        remaining_slots = max_display_size - len(selected_indices)
        total_non_repr = original_n_designs - len(selected_indices)

        if remaining_slots > 0 and total_non_repr > 0:
            for cluster_id, indices in cluster_to_indices.items():
                non_repr_indices = [
                    i for i in indices if i not in selected_indices and ordered_ids[i] != representative_ids[i]
                ]

                if non_repr_indices:
                    n_samples = max(1, int(len(non_repr_indices) / total_non_repr * remaining_slots))
                    step = max(1, len(non_repr_indices) // n_samples)
                    sampled = non_repr_indices[::step][:n_samples]
                    selected_indices.update(sampled)

        # Apply subsampling
        selected_indices = sorted(list(selected_indices))[:max_display_size]
        selected_ids = [ordered_ids[i] for i in selected_indices]
        matrix_ordered = matrix_ordered.loc[selected_ids, selected_ids]

        # Update metadata for subsampled matrix
        cluster_ids = [cluster_ids[i] for i in selected_indices]
        representative_ids = [representative_ids[i] for i in selected_indices]
        ordered_ids = selected_ids

    # 7. Calculate cluster boundaries
    boundaries = []
    prev_cluster = None
    for i, cluster_id in enumerate(cluster_ids):
        if prev_cluster is not None and cluster_id != prev_cluster:
            boundaries.append(i)
        prev_cluster = cluster_id

    # 8. Final metadata
    metadata = {
        "cluster_boundaries": boundaries,
        "cluster_ids": cluster_ids,
        "representative_ids": representative_ids,
        "representatives": representatives,
        "cluster_sizes": cluster_sizes,  # Keep original sizes
        "ordered_ids": ordered_ids,
    }

    return matrix_ordered, metadata


def visualize_distance_matrix_heatmap(matrix_df: pd.DataFrame, metadata: dict, cluster_colors: dict) -> go.Figure:
    """Create interactive heatmap with cluster color bars (like sns.clustermap row_colors).

    :param matrix_df: Distance matrix DataFrame (already ordered and subsampled by cluster)
    :param metadata: Dict with cluster_boundaries, representatives, etc.
    :param cluster_colors: Dict mapping cluster_id -> color hex code
    :return: Plotly Figure object
    """

    n_designs = len(matrix_df)

    # Build customdata for hover: [design_id_row, design_id_col, cluster_id_row, cluster_id_col, repr_id_row, repr_id_col]
    cluster_ids = metadata["cluster_ids"]
    representative_ids = metadata["representative_ids"]
    design_ids = matrix_df.index.tolist()

    customdata = [
        [
            [
                design_ids[i],  # row design ID
                design_ids[j],  # col design ID
                cluster_ids[i],  # row cluster ID
                cluster_ids[j],  # col cluster ID
                representative_ids[i],  # row representative ID
                representative_ids[j],  # col representative ID
            ]
            for j in range(n_designs)
        ]
        for i in range(n_designs)
    ]

    # Create main distance matrix heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix_df.values,
            x=matrix_df.columns.tolist(),
            y=matrix_df.index.tolist(),
            colorscale="Greens_r",
            # Keep the colorbar next to the plot, the cluster legend is placed to the right of it
            colorbar=dict(title="Distance", x=1.02, xanchor="left"),
            zmin=0,
            hovertemplate=(
                "<b>%{customdata[0]}</b> (Cluster %{customdata[2]}, Rep: %{customdata[4]})<br>"
                "↔<br>"
                "<b>%{customdata[1]}</b> (Cluster %{customdata[3]}, Rep: %{customdata[5]})<br>"
                "<b>Distance:</b> %{z:.3f}"
                "<extra></extra>"
            ),
            customdata=customdata,
            showscale=True,
        )
    )

    # Add colored rectangles for each cluster (row/column color bars)
    boundaries = [0] + metadata["cluster_boundaries"] + [n_designs]

    for i in range(len(boundaries) - 1):
        start_idx = boundaries[i]
        end_idx = boundaries[i + 1]
        cluster_id = cluster_ids[start_idx]
        color = cluster_colors.get(cluster_id, "#CCCCCC")

        # Left side color bar (row colors)
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="y",
            x0=-0.02,
            x1=0,
            y0=start_idx - 0.5,
            y1=end_idx - 0.5,
            fillcolor=color,
            line=dict(width=0),
            layer="below",
        )

        # Invisible trace just to get a legend entry for this cluster color
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(size=10, symbol="square", color=color),
                name=f"Cluster {cluster_id} ({end_idx - start_idx})",
                showlegend=True,
                hoverinfo="skip",
            )
        )

        # Top color bar (column colors)
        fig.add_shape(
            type="rect",
            xref="x",
            yref="paper",
            x0=start_idx - 0.5,
            x1=end_idx - 0.5,
            y0=1.0,
            y1=1.02,
            fillcolor=color,
            line=dict(width=0),
            layer="below",
        )

    # Layout
    fig.update_layout(
        xaxis=dict(
            title="Design ID",
            showticklabels=n_designs <= 100,
            side="bottom",
            showgrid=False,
        ),
        yaxis=dict(
            title="Design ID",
            showticklabels=n_designs <= 100,
            autorange="reversed",
            showgrid=False,
            # Invisible ticks to push the design IDs left of the cluster color bar
            ticks="outside",
            ticklen=10,
            tickcolor="rgba(0,0,0,0)",
        ),
        height=800,
        # Extra left margin so the y axis design IDs are not truncated,
        # extra right margin to fit the colorbar and the cluster legend side by side
        margin=dict(l=200, r=220),
        # Cluster legend on the right, next to the distance colorbar
        legend=dict(
            title="Clusters (size)",
            x=1.13,
            xanchor="left",
            y=1,
            yanchor="top",
            itemclick=False,
            itemdoubleclick=False,
        ),
    )

    return fig


@st.fragment
def distance_matrix_component(
    tool_key: str,
    artifact_file_path: str,
    df_descriptor_values: pd.DataFrame,
):
    """Display interactive distance matrix visualization with clusters highlighted.

    :param tool_key: Clustering tool key
    :param artifact_file_path: Storage path to distance matrix artifact
    :param df_descriptor_values: DataFrame with clustering results
    """
    # Get cluster info using the same logic as other components
    if tool_key not in CLUSTER_INFO_REFERENCES:
        st.error(f"Unknown clustering tool: {tool_key}")
        return

    cluster_info = CLUSTER_INFO_REFERENCES[tool_key]
    repr_descriptor = cluster_info["representative"]
    repr_key = repr_descriptor.key
    id_descriptor = cluster_info["id"]
    id_key = id_descriptor.key

    with st.spinner("Loading and processing distance matrix..."):
        # Prepare data
        matrix_df, metadata = prepare_distance_matrix_for_visualization(
            artifact_file_path,
            df_descriptor_values,
            id_key,
            repr_key,
        )

        # Get cluster colors using the existing color scheme
        cluster_color_mapping = get_cluster_color_mapping_from_legend(df_descriptor_values, tool_key)

        # Create and display visualization
        fig = visualize_distance_matrix_heatmap(matrix_df, metadata, cluster_color_mapping)

        st.plotly_chart(fig, use_container_width=True)
