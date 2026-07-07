"""Design ranking page - rank designs by various criteria."""

import streamlit as st
import pandas as pd

from ovo import db
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.design_labeling import design_labeling_fragment
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.navigation import design_navigation_selector
from ovo.app.utils.cached_db import (
    get_cached_design_ids,
    get_cached_descriptor_jobs_for_design_ids,
    get_cached_designs,
    get_cached_pools,
)
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.logic import descriptor_logic
from ovo.core.database.models import WorkflowTypes, DescriptorJob, NumericDescriptor
from ovo.core.database.models_ranking import RankingTask, RankingDescriptorWorkflow
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table
from ovo.core.database.descriptors_ranking import RANK
from ovo.app.components.workflow_visualization_components import show_design


@st.fragment
@st.dialog("Ranking submission", width="large")
def submit_ranking_dialog(design_ids: list[str]):
    """Dialog for submitting ranking jobs."""
    from ovo import schedulers

    content = st.empty()

    with content.container():
        if not WorkflowTypes.get_subclass_names(RankingTask):
            st.error("No ranking implementations available")
            return

        # Method selector
        selected_method = st.selectbox(
            "Ranking method",
            placeholder="Select a ranking method",
            options=WorkflowTypes.get_subclass_names(RankingTask),
            help="Select the algorithm to use for ranking designs",
            index=None,
        )

        if not selected_method:
            st.write("Please select a ranking method")
            return

        ranking_class = WorkflowTypes.get(selected_method)
        description = ranking_class.ranking_description
        st.markdown(description)

        # Call from_ui() to get workflow-specific parameters
        st.subheader("Ranking parameters")
        workflows = ranking_class.from_ui(design_ids)

        if not workflows:
            return

        # Validate
        for w in workflows:
            try:
                w.validate()
            except ValueError as e:
                st.error(f"Validation error: {e}")
                return

        # Scheduler selection - filter by pipeline compatibility
        compatible_scheduler_keys = [
            key
            for key, scheduler in schedulers.items()
            if all(scheduler.supports_pipeline_name(workflow.get_pipeline_name()) for workflow in workflows)
        ]

        if not compatible_scheduler_keys:
            st.error("No compatible schedulers found for this workflow type.")
            return

        scheduler_key = st.selectbox(
            "Scheduler",
            options=compatible_scheduler_keys,
            format_func=lambda key: schedulers[key].name,
        )
        preview_disabled = not isinstance(workflows[0], RankingTask)
        if st.button(
            "Preview",
            disabled=preview_disabled,
            help="Ranking method does not enable preview" if preview_disabled else None,
        ):
            ranked_values = workflows[0].rank(workflows[0].select_descriptor_values())
            st.dataframe(ranked_values.sort_values(by="rank"))

        # Submit button
        with st.container(horizontal=True, horizontal_alignment="right"):
            submit_button = st.button(
                f"Rank {len(design_ids)} designs",
                type="primary",
            )

    if submit_button:
        content.empty()
        with st.spinner("Submitting ranking job..."):
            for w in workflows:
                descriptor_logic.submit_descriptor_workflow(
                    workflow=w,
                    scheduler_key=scheduler_key,
                    project_id=st.session_state.project.id,
                )
                st.success(f"Ranking job submitted: {w.name}")
        st.rerun()


@st.fragment
def ranking_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    """Main ranking view fragment."""

    # Get design IDs
    if design_ids is None:
        design_ids = get_cached_design_ids(pool_ids=pool_ids, accepted=True)
        if not design_ids:
            st.write("No accepted designs found in selected pools")
            return

    # Header
    st.header(f"🏆 Ranking | {len(design_ids):,} designs")

    # Submit button
    if st.button("New ranking", type="primary"):
        submit_ranking_dialog(design_ids)

    # Refresh descriptor jobs
    workflow_names = WorkflowTypes.get_subclass_names(RankingDescriptorWorkflow)
    refresh_descriptors(design_ids=design_ids, workflow_names=workflow_names)

    # Get completed ranking jobs
    jobs_for_design_ids = get_cached_descriptor_jobs_for_design_ids(
        design_ids=design_ids,
        workflow_names=workflow_names,
        project_id=st.session_state.project.id,
        only_exact_design_ids=False,
    )

    if not jobs_for_design_ids:
        st.write(
            f"No ranking results yet for any of the {len(design_ids)} selected designs. Submit a ranking job to get started."
        )
        return

    # Build job selector
    jobs_by_id = {job.id: job for job in jobs_for_design_ids}
    job_labels = {}
    for job_id, job in jobs_by_id.items():
        timestamp = job.created_date_utc.strftime("%Y-%m-%d %H:%M")
        label = f"**{job.workflow.ranking_name} - {job.workflow.name}** ({timestamp})"
        # Handle duplicate labels
        if label in job_labels.values():
            label = f"{label} [{job_id[:6]}]"
        job_labels[job_id] = label

    # Job selector
    job_id = st.segmented_control(
        "Select ranking result",
        options=list(jobs_by_id.keys()),
        default=jobs_for_design_ids[0].id if len(jobs_for_design_ids) == 1 else None,
        format_func=job_labels.get,
    )

    if job_id is None:
        st.write(":material/arrow_upward: *Please select a ranking result*")
        return

    # Display selected ranking
    job = jobs_by_id[job_id]
    display_ranking_results(job, selected_design_is=design_ids)


def display_ranking_results(job: DescriptorJob, selected_design_is: list[str]):
    """Display ranking results for a job."""

    workflow: RankingDescriptorWorkflow = job.workflow
    available_design_ids = set(workflow.design_ids)
    overlap_design_ids = [design_id for design_id in selected_design_is if design_id in available_design_ids]

    # Job info
    workflow.visualize_summary(job)

    if len(available_design_ids) != len(overlap_design_ids):
        num_label = f"{len(overlap_design_ids)}/{len(available_design_ids)}"
    else:
        num_label = f"{len(overlap_design_ids)}"
    st.subheader(f"{num_label} Ranked {'design' if len(overlap_design_ids) == 1 else 'designs'}")
    if len(overlap_design_ids) < len(selected_design_is):
        st.warning(
            f"Only {len(overlap_design_ids)} of the {len(selected_design_is)} selected designs are included in this ranking result. "
            f"The remaining {len(selected_design_is) - len(overlap_design_ids)} designs will not be displayed."
        )
    if len(selected_design_is) < len(available_design_ids):
        st.write(
            f":material/info: This ranking result includes {len(available_design_ids)} designs in total, "
            f"but only {len(selected_design_is):,} were selected for display."
        )

    # Get design data
    designs = get_cached_designs(overlap_design_ids)
    designs_by_id = {d.id: d for d in designs}

    # Select descriptors to display
    descriptors = [RANK] + [ALL_DESCRIPTORS_BY_KEY[key] for key in workflow.descriptor_keys]
    rank_column_name = (RANK.tool, RANK.name)

    # Get descriptor used for ranking
    descriptor_job_id = {
        job.id: [RANK.key],
        None: workflow.descriptor_keys,  # hack to put the important descriptor columns at the beginning
    }
    descriptors_df = get_wide_descriptor_table(
        design_ids=overlap_design_ids,
        descriptor_keys=[d.key for d in descriptors],
        descriptor_job_id=descriptor_job_id,
        nested=True,
    )
    descriptors_df = descriptors_df.sort_values(by=rank_column_name, ascending=True)
    ranked_design_ids = descriptors_df.index.tolist()

    descriptor_table(ranked_design_ids, descriptors_df, descriptors)

    pools = get_cached_pools(sorted(set(db.Design.design_id_to_pool_id(design_id) for design_id in ranked_design_ids)))
    download_job_designs_component(
        ranked_design_ids,
        pools,
        descriptor_job_id=descriptor_job_id,
        group_by=RANK.key,
        group_by_fmt="rank_{}",
        group_by_flatten=True,
    )

    # Design selector for detailed view
    st.subheader("Ranked designs")
    selected_design_id = design_navigation_selector(
        ranked_design_ids,
        fmt=lambda design_id: format_design_label(descriptors_df.loc[design_id], workflow.descriptor_keys),
        key=f"ranking_selector_{job.id}",
    )

    if selected_design_id:
        design = designs_by_id[selected_design_id]
        rank = descriptors_df[rank_column_name][selected_design_id]

        design_labeling_fragment(design.id, header=f"#{rank}: {design.id}")

        st.write("Ranking metrics:")
        workflow.show_design_header(design)

        show_design(design.id)


def format_design_label(descriptor_row: pd.Series, descriptor_keys: list[str]) -> str:
    """Format design label for display in ranking table."""
    values = []
    # get inde
    descriptor_values = {(tool, key): value for (tool, key), value in descriptor_row.items()}
    for key in descriptor_keys:
        descriptor = ALL_DESCRIPTORS_BY_KEY[key]
        value = descriptor_values.get((descriptor.tool, descriptor.name))
        if pd.isna(value):
            value_fmt = "N/A"
        elif isinstance(descriptor, NumericDescriptor):
            value_fmt = descriptor.format(value)
        else:
            value_fmt = value
        values.append(f"{descriptor.name}: {value_fmt}")
    return " | ".join(values)
