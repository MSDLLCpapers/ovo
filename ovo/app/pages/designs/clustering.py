import uuid
import streamlit as st
import pandas as pd

from ovo import Scheduler, db
from ovo.app.components.attachment_components import download_distance_matrix_artifacts
from ovo.app.components.custom_elements import simple_tabs
from ovo.core.database.models import ProjectArtifact, DistanceMatrixArtifact
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.submission_components import chain_ids_input, scheduler_selectbox
from ovo.app.utils.cached_db import (
    get_cached_design_ids,
    get_cached_available_descriptors_per_job,
    get_cached_descriptor_jobs_for_design_ids,
    get_cached_design,
    get_cached_pools,
)
from ovo.core.database.descriptors_rfdiffusion import PYDSSP_STRING
from ovo.core.utils.formatting import datetime_from_utc_to_local
from ovo.core.database.models_clustering import (
    FOLDSEEK_UMAP_PIPELINE,
    SEQUENCE_HIERARCHICAL_UMAP_PIPELINE,
    RMSD_HIERARCHICAL_UMAP_PIPELINE,
    SECONDARY_STRUCTURE_UMAP_PIPELINE,
    INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE,
    CLUSTERING_WORKFLOWS_BY_TOOL_KEY,
    PROTEIN_CLUSTERING_TOOLS_BY_KEY,
    PROTEIN_CLUSTERING_TOOLS,
    InterfaceResiduesHierarchicalClusteringWorkflow,
    ProteinClusteringWorkflow,
    SecondaryStructureHierarchicalClusteringWorkflow,
    ProteinClusteringTool,
)
from ovo.core.database.descriptors_clustering import PROTEIN_CLUSTERING_DESCRIPTORS
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow
from ovo.app.components.clustering_components import (
    display_clustering_job_params,
    set_foldseek_params,
    set_hierarchical_clustering_params,
    umap_scatterplot_component,
    cluster_representatives_tiles,
    inspect_clusters,
    display_clustering_metrics,
    interface_clustering_table,
    distance_matrix_component,
)
from ovo.app.utils.cached_db import get_cached_descriptor_values


def tool_supports_scheduler(tool: ProteinClusteringTool, scheduler: Scheduler) -> bool:
    if "conda" in scheduler.submission_args and scheduler.submission_args["conda"]:
        return tool.supports_conda
    return True


@st.fragment
@st.dialog("Protein clustering submission", width="large")
def submit_clustering_dialog(design_ids: list[str]):
    # Create "empty" element to enable clearing the contents after submitting
    content = st.empty()
    with content.container():
        num_designs = len(design_ids)

        st.write(f"""Submit Protein Clustering for {num_designs:,} {"design" if num_designs == 1 else "designs"}""")

        tool_to_add = st.selectbox(
            "Select tool to add",
            options=PROTEIN_CLUSTERING_TOOLS,
            format_func=lambda x: x.name,
            key="add_clustering_tool_selectbox",
        )

        if st.button("Add selected tool", icon=":material/add:", key="add_tool_btn", type="secondary", width="content"):
            instance_id = str(uuid.uuid4())
            st.session_state.clustering_tool_instances.append(
                {
                    "id": instance_id,
                    "tool": tool_to_add,
                }
            )
            st.rerun(scope="fragment")

        if not st.session_state.clustering_tool_instances:
            st.info("Add at least one tool to continue")
            return

        chains = chain_ids_input(design_ids)
        if not chains:
            return

        workflows = []
        tools_to_remove = []

        st.subheader("Tool Configurations")
        for instance in st.session_state.clustering_tool_instances:
            tool = instance["tool"]
            tool = PROTEIN_CLUSTERING_TOOLS_BY_KEY[tool.tool_key]
            instance_id = instance["id"]

            with st.expander(f"🔧 {tool.name}", expanded=True):
                col1, col2 = st.columns([5, 1])

                with col2:
                    if st.container(horizontal=True, horizontal_alignment="right").button(
                        "",
                        icon=":material/delete:",
                        key=f"remove_tool_{instance_id}",
                        help=f"Remove {tool.name}",
                        type="tertiary",
                    ):
                        tools_to_remove.append(instance_id)

                with col1:
                    workflow_class = CLUSTERING_WORKFLOWS_BY_TOOL_KEY[tool.tool_key]

                    workflow = workflow_class(chains=list(chains), design_ids=design_ids)

                    if tool == FOLDSEEK_UMAP_PIPELINE:
                        # Use instance_id in keys to make them unique
                        set_foldseek_params(workflow, key_suffix=f"_instance_{instance_id}")
                    elif tool in [
                        SEQUENCE_HIERARCHICAL_UMAP_PIPELINE,
                        SECONDARY_STRUCTURE_UMAP_PIPELINE,
                        INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE,
                        RMSD_HIERARCHICAL_UMAP_PIPELINE,
                    ]:
                        # Use first design to infer whether cyclic clustering should be enabled by default
                        design_example = get_cached_design(design_ids[0]) if design_ids else None
                        cyclic = all(design_example.spec.get_chain(chain).cyclic for chain in chains)
                        set_hierarchical_clustering_params(
                            workflow, cyclic=cyclic, key_suffix=f"_instance_{instance_id}"
                        )
                    else:
                        st.error("Tool parameters UI not implemented.")

                    workflows.append(workflow)

        # Remove tools marked for deletion
        if tools_to_remove:
            st.session_state.clustering_tool_instances = [
                inst for inst in st.session_state.clustering_tool_instances if inst["id"] not in tools_to_remove
            ]
            st.rerun(scope="fragment")

        if not workflows:
            return

        # Get unique tools for scheduler check
        unique_tools = list(set(inst["tool"] for inst in st.session_state.clustering_tool_instances))

        scheduler_key = scheduler_selectbox(
            workflows, filter=lambda scheduler: all(tool_supports_scheduler(tool, scheduler) for tool in unique_tools)
        )

        col1, col2 = st.columns([4, 1], vertical_alignment="center")
        with col1:
            st.write(f"Ready to submit {len(workflows)} clustering job{'' if len(workflows) == 1 else 's'}")
        with col2:
            submit_button = st.button("Submit All", key="submit_clustering_multi_btn", type="primary", width="stretch")

    if submit_button:
        content.empty()
        st.write(f"Submitting {len(workflows)} job{'s' if len(workflows) != 1 else ''}... 🚀")
        for workflow in workflows:
            submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
        st.session_state.clustering_tool_instances = []  # Clear after submission
        st.rerun()


@st.fragment
def clustering_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = get_cached_design_ids(pool_ids=pool_ids, accepted=True)
        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". All generated designs can be explored in the **Jobs** page."
            )
            return
    else:
        if not design_ids:
            # Empty list explicitly passed to design_ids
            st.write("No designs selected")
            return

    st.header(f"🫧 Clustering | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    if st.button(
        "Submit Clustering",
        type="primary",
        key="submit_full_proteinclustering_btn",
    ):
        submit_clustering_dialog(design_ids)

    refresh_descriptors(
        design_ids=design_ids,
        workflow_names=[workflow.name for workflow in CLUSTERING_WORKFLOWS_BY_TOOL_KEY.values()],
    )

    if not design_ids:
        st.warning("No designs found")
        return

    # Get registered workflow names that inherit from ProteinClustering workflow
    clustering_workflow_names = ProteinClusteringWorkflow.get_registered_workflow_names()

    # Get all finished jobs for given design ids and clustering workflows
    jobs_for_design_ids = get_cached_descriptor_jobs_for_design_ids(
        design_ids, workflow_names=clustering_workflow_names, project_id=st.session_state.project.id
    )

    if not jobs_for_design_ids:
        # Check if there are any clustering jobs for some of the designs
        jobs_for_some_designs = get_cached_descriptor_jobs_for_design_ids(
            design_ids,
            workflow_names=clustering_workflow_names,
            project_id=st.session_state.project.id,
            only_exact_design_ids=False,
        )
        if jobs_for_some_designs:
            st.info(
                f"**No clustering results found for the selected combination of {len(design_ids):,} designs.**\n\n"
                "Clustering jobs exist for *some* of the accepted designs, but not all. "
                "Since clustering analysis depends on the complete context of all accepted designs, "
                "results are specific to each unique design set.\n\n"
                "**Possible reasons:**\n"
                "- Previous clustering jobs were run on a different pool/design selection\n"
                "- Your current selection includes designs that were not in the original clustering job\n\n"
                "Submit a new clustering job to analyze all currently accepted designs together."
            )
        else:
            st.write("No clustering results yet for the selected designs")
        return

    # Create a lookup dictionary: job_id -> job object
    jobs_by_id = {job.id: job for job in jobs_for_design_ids}

    # Use job IDs as options instead of job objects
    job_labels = {
        job_id: f"**{job.workflow.name}** ({datetime_from_utc_to_local(job.created_date_utc).strftime('%Y-%m-%d %H:%M')})"
        for job_id, job in jobs_by_id.items()
    }
    if len(set(job_labels.values())) != len(job_labels.values()):
        # If there are duplicate labels, append job ID to differentiate
        job_labels = {job_id: f"{label} {job_id}" for job_id, label in job_labels.items()}
    job_id = st.segmented_control(
        "Select clustering result",
        options=list(jobs_by_id.keys()),
        default=jobs_for_design_ids[0].id if len(jobs_for_design_ids) == 1 else None,
        format_func=job_labels.get,
    )
    if job_id is None:
        st.write(":material/arrow_upward: Please select a clustering result above")
        return

    # Get the job object from the selected ID
    job = jobs_by_id[job_id]

    # Display specification of the job
    st.subheader(f"{job.workflow.name} parameters")
    display_clustering_job_params(job)

    if job.warnings:
        warnings_title = ("1 warning" if len(job.warnings) == 1 else f"{len(job.warnings)} warnings") + f" found"
        with st.expander(warnings_title, icon="⚠️"):
            for warning in job.warnings:
                st.warning(warning)

    # Get descriptors for specific job and designs and inform about possibly incomplete job
    descriptors_by_key = get_cached_available_descriptors_per_job(design_ids, job.id)
    descriptors = [d for d in PROTEIN_CLUSTERING_DESCRIPTORS if d.key in descriptors_by_key]
    if not descriptors:
        st.warning("No clustering descriptors found. Try submitting Protein Clustering.")
        return

    # Get values for descriptors for specific job and designs
    df_descriptor_values = pd.DataFrame(
        {
            descriptor.key: get_cached_descriptor_values(descriptor.key, design_ids, descriptor_job_id=job.id)
            for descriptor in descriptors
        }
    )
    if isinstance(job.workflow, SecondaryStructureHierarchicalClusteringWorkflow):
        df_descriptor_values[PYDSSP_STRING.key] = get_cached_descriptor_values(PYDSSP_STRING.key, design_ids)

    # TODO how to get clustering descriptors in a more reliable way
    cluster_id_descriptors = [d for d in descriptors if "Cluster ID" in d.name]
    if not cluster_id_descriptors:
        st.error("No clustering descriptor found")
        return

    cluster_id_descriptor = cluster_id_descriptors[0]

    pools = get_cached_pools(pool_ids)

    extra_col = download_job_designs_component(
        design_ids,
        pools,
        descriptor_job_id={job.id: [d.key for d in descriptors]},
        group_by=cluster_id_descriptor.key,
        group_by_fmt="cluster_{}",
        key="cluster",
    )

    matrix_artifact: DistanceMatrixArtifact | None = None
    matrix_artifacts = db.select(
        ProjectArtifact,
        descriptor_job_id=job.id,
        artifact_type=DistanceMatrixArtifact.artifact_type,
        order_by=ProjectArtifact.created_date_utc.desc(),
    )
    if matrix_artifacts:
        matrix_artifact: DistanceMatrixArtifact = matrix_artifacts[0].artifact
        with extra_col:
            download_distance_matrix_artifacts(matrix_artifact, job, pools, design_ids)

    # Identify which clustering tool was used and get cluster descriptor for id
    # this is neccessary when other clustering algorithms used and columns descriptors named differently
    tool_key = job.workflow.tool_key

    display_clustering_metrics(df_descriptor_values, job=job)

    tab_name = simple_tabs(
        [
            "Representatives",
            "UMAP plots",
            "Distance matrix" if matrix_artifact else None,
            "Interface residues by cluster"
            if isinstance(job.workflow, InterfaceResiduesHierarchicalClusteringWorkflow)
            else None,
            "Cluster browser",
        ],
        key="cluster_tab",
    )
    if tab_name == "UMAP plots":
        st.markdown("#### UMAP scatterplots")
        st.caption(
            "UMAP projects designs into a low-dimensional space by first constructing a k-nearest neighbor graph from pairwise similarity matrix, followed by optimization of embedding coordinates for visualization."
        )
        umap_scatterplot_component(df_descriptor_values, tool=tool_key)

    elif tab_name == "Distance matrix":
        # Visualize distance matrix if available
        if matrix_artifact and hasattr(job.workflow, "params"):  # Only for hierarchical clustering
            distance_matrix_component(tool_key, matrix_artifact.file_path, df_descriptor_values)

    elif tab_name == "Representatives":
        # Create tiles for cluster representatives
        cluster_representatives_tiles(df_descriptor_values, tool=tool_key, job=job)

    elif tab_name == "Interface residues by cluster":
        st.markdown("#### Interface residues by cluster")
        interface_clustering_table(df_descriptor_values, job.workflow)

    elif tab_name == "Cluster browser":
        st.markdown("#### Cluster browser")
        inspect_clusters(df_descriptor_values, tool=tool_key, job=job)
