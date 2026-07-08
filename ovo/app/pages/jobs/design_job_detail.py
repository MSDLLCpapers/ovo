import streamlit as st

from ovo import db, Pool, Design, WorkflowTypes, DesignWorkflow
from ovo.app.components.acceptance_thresholds_components import (
    thresholds_and_histograms_component,
    accept_designs_dialog,
    display_current_thresholds,
    filter_designs_by_thresholds_cached,
)
from ovo.app.components.custom_elements import refresh_button
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_scatterplot import (
    descriptor_scatterplot_component,
    descriptor_scatterplot_input_component,
)
from ovo.app.components.design_labeling import design_labeling_fragment
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.job_components import job_status_fragment
from ovo.app.components.navigation import design_navigation_selector
from ovo.app.components.workflow_visualization_components import show_design
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design_jobs_table,
)
from ovo.core.database import DesignJob
from ovo.core.logic.design_logic import process_results
from ovo.core.logic.job_logic import update_job_status


@st.fragment
def design_job_detail(pool_ids):
    pools = get_cached_pools(pool_ids)
    pools_by_design_job = {pool.design_job_id: pool for pool in pools if pool.design_job_id}

    design_job_ids = [pool.design_job_id for pool in pools if pool.design_job_id]
    if not design_job_ids:
        st.warning("Selected pools are not associated with a design job")
        return

    # TODO can we cache this at least when we know that all pools have been processed?
    design_jobs = db.select(DesignJob, id__in=design_job_ids, order_by="-created_date_utc")

    # Display title
    status_icon = (
        ""
        if all(j.job_result for j in design_jobs)
        else ("⚠️" if any(j.job_result is False for j in design_jobs) else "⏳")
    )
    if len(pools) == 1:
        pool = pools[0]
        st.title(f"{status_icon} {pool.name}")
        if pool.description:
            st.write(pool.description)
    else:
        st.title(f"{status_icon} {len(pools)} pools")
        st.markdown("#### " + ", ".join([pool.name for pool in pools]))

    # Update status for all jobs that are still in progress,
    # and process results for those that have finished but are not yet processed
    for job in design_jobs:
        pool = pools_by_design_job[job.id]
        if job.job_result is None:
            with st.spinner(f'Checking status of "{pool.name}"'):
                job_result = update_job_status(job)
            if job_result is True and not pool.processed:
                with st.spinner("Workflow finished, processing designs. This will take a moment..."):
                    progress_bar = st.progress(0)
                    process_results(job, callback=progress_bar.progress, wait=False)
                    progress_bar.empty()
                if job.job_result:
                    st.success(f"Workflow finished: {pool.name}")

    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
        st.subheader("Workflow parameters")

        with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
            st.write("Show as:")
            show_as_rows = (
                st.segmented_control(
                    "Show as",
                    options=["Columns", "Rows"],
                    key="show_as",
                    default="Columns",
                    label_visibility="collapsed",
                )
                == "Rows"
            )

            if len(pool_ids) > 1:
                st.write("Filter:")
                show_distinct = (
                    st.segmented_control(
                        "Distinct",
                        options=["All parameters", "Distinct parameters"],
                        key="show_distinct",
                        default="All parameters",
                        label_visibility="collapsed",
                    )
                    == "Distinct parameters"
                )
            else:
                show_distinct = False

    table = get_cached_design_jobs_table(round_ids=sorted(set(p.round_id for p in pools)), id__in=pool_ids)
    table.index = [pools_by_design_job[j.id].id for j in design_jobs]

    if show_distinct:
        table = table[table.columns[table.astype(str).nunique() > 1]]

    if show_as_rows:
        st.table(table.T, width="content")
    else:
        st.dataframe(table)

    num_pools_failed = sum(job.job_result == False for job in design_jobs)
    num_pools_in_progress = sum(job.job_result is None for job in design_jobs)

    if num_pools_in_progress:
        refresh_button("refresh_top")

    if "show_all" not in st.session_state:
        st.session_state.show_all = False

    for i, job in enumerate(design_jobs):
        pool = pools_by_design_job[job.id]
        if i == 1 and not st.session_state.show_all:
            with st.container(horizontal=True, vertical_alignment="center"):
                if st.button(":material/unfold_more: Show all jobs", key="show_all_jobs_btn"):
                    st.session_state.show_all = True
                    st.rerun()
                st.write(
                    f"1 more job not shown" if len(design_jobs) == 2 else f"{len(design_jobs) - 1} more jobs not shown"
                )
        if i == 0 or st.session_state.show_all:
            try:
                job_status_fragment(job, pool, expand=i == 0)
            except Exception as e:
                # avoid failing here, error is already printed inside fragment
                st.error(f"Failed reading job details for job {job.job_id}: {e}")

    if len(pools) == num_pools_failed + num_pools_in_progress:
        # No results yet, show workflow summary
        st.subheader("Workflow summary")
        show_workflow_summary(design_jobs)
        return

    if num_pools_in_progress:
        st.info(
            f"Not including results of {num_pools_in_progress} ongoing workflow"
            + ("s" if num_pools_in_progress > 1 else "")
        )
        refresh_button("refresh_bottom")

    all_design_ids = sorted(db.select_unique_values(Design, "id", pool_id__in=pool_ids))

    refresh_descriptors(
        design_ids=all_design_ids,
    )

    job_results_fragment(
        all_design_ids=all_design_ids,
        pools=pools,
        jobs=design_jobs,
    )


@st.fragment
def job_results_fragment(all_design_ids: list[str], pools: list[Pool], jobs: list[DesignJob]):
    st.subheader("Job results")

    # Get dictionary of saved thresholds (descriptor key -> (min, max) or None)
    saved_thresholds = {}
    inconsistent_threshold_keys = set()
    workflows = [job.workflow for job in jobs]
    for workflow in workflows:
        if not hasattr(workflow, "acceptance_thresholds") or not workflow.acceptance_thresholds:
            continue
        sorted_thresholds = sorted(workflow.acceptance_thresholds.items(), key=lambda x: not x[1].enabled)
        for descriptor_key, thresholds in sorted_thresholds:
            if descriptor_key not in saved_thresholds:
                saved_thresholds[descriptor_key] = thresholds
            elif saved_thresholds[descriptor_key] != thresholds:
                st.warning(
                    f"Looking at multiple workflows with different thresholds for {descriptor_key}, showing the first one"
                )
                inconsistent_threshold_keys.add(descriptor_key)

    # Save selected_thresholds into session state when first opening the page
    pool_ids_str = ",".join(p.id for p in pools)
    if "selected_thresholds" not in st.session_state or st.session_state.selected_thresholds_pool_ids != pool_ids_str:
        st.session_state.selected_thresholds = saved_thresholds
        st.session_state.selected_thresholds_pool_ids = pool_ids_str

    show_mode = st.segmented_control(
        "Show",
        options=["Accepted designs", "All designs", "Workflow summary"],
        key="show_designs",
        default=st.query_params.get("show", "Accepted designs"),
    )

    if show_mode != "Accepted designs":
        # Add show mode to query params (but only when changed, to avoid polluting the URL)
        st.query_params["show"] = show_mode

    if show_mode == "Accepted designs":
        displayed_design_ids = show_accepted_designs_and_thresholds(
            all_design_ids,
            saved_thresholds,
            pools,
            jobs,
            inconsistent_threshold_keys,
        )
    elif show_mode == "All designs":
        displayed_design_ids = show_all_designs(all_design_ids)

    elif show_mode == "Workflow summary":
        show_workflow_summary(jobs)
        return
    else:
        st.error("Select a mode.")
        return

    if not displayed_design_ids:
        st.write("No designs found")
        return

    st.subheader("Download")
    download_job_designs_component(displayed_design_ids, pools)

    st.subheader("Structure visualization")
    workflow_names = set(job.workflow.name for job in jobs if job.workflow)

    visualize_designs_fragment(
        design_ids=displayed_design_ids,
        shared_workflow_name=list(workflow_names)[0] if len(workflow_names) == 1 else None,
    )


def show_accepted_designs_and_thresholds(
    all_design_ids: list[str],
    saved_thresholds: dict,
    pools: list[Pool],
    jobs: list[DesignJob],
    inconsistent_threshold_keys: set[str],
):
    accepted_design_ids = db.select_values(Design, "id", id__in=all_design_ids, accepted=True)

    if st.session_state.selected_thresholds != saved_thresholds:
        st.header("Editing thresholds")
    elif accepted_design_ids:
        st.header(
            f"Showing {len(accepted_design_ids)} accepted {'designs' if len(accepted_design_ids) > 1 else 'design'}"
        )

        st.write(
            f"""
                This section enables adjusting acceptance thresholds and visualizing the accepted designs. 
                Visit the [Designs](./designs?project_id={st.session_state.project.id}) page 
                for in-depth analysis of accepted designs.
                """
        )
    else:
        st.header("No accepted designs")
        st.warning(
            """
            None of the designs met the acceptance thresholds. 
            You may adjust to less strict thresholds below, or try submitting more designs.

            To see all generated designs, select 'All designs' above.
            """
        )

    new_accepted_design_ids, num_accepted_by_descriptor = filter_designs_by_thresholds_cached(
        all_design_ids=all_design_ids,
        thresholds=st.session_state.selected_thresholds,
    )

    if st.session_state.selected_thresholds != saved_thresholds:
        st.write(
            f"Accepted designs based on new thresholds: **{len(new_accepted_design_ids):,} / {len(all_design_ids):,}** ({len(new_accepted_design_ids) / len(all_design_ids):.0%})"
        )
    else:
        st.write(
            f"Accepted designs: **{len(accepted_design_ids):,} / {len(all_design_ids):,}** ({len(accepted_design_ids) / len(all_design_ids):.2%})"
        )

    display_current_thresholds(
        selected_thresholds=st.session_state.selected_thresholds,
        all_design_ids=all_design_ids,
        num_accepted_by_descriptor=num_accepted_by_descriptor,
    )

    if st.session_state.selected_thresholds != saved_thresholds:
        if inconsistent_threshold_keys:
            st.warning(
                f"Selected pools currently use different thresholds for {' & '.join(inconsistent_threshold_keys)}, confirming will override these with the selected threshold value."
            )
        left, mid, _, _ = st.columns(4)
        if left.button("Confirm thresholds", key="confirm_designs_btn", type="primary", width="stretch"):
            accept_designs_dialog(
                pools=pools,
                jobs=jobs,
                all_design_ids=all_design_ids,
                new_accepted_design_ids=new_accepted_design_ids,
                num_accepted_by_descriptor=num_accepted_by_descriptor,
                selected_thresholds=st.session_state.selected_thresholds,
            )
        if mid.button("Discard changes", width="stretch"):
            st.session_state.selected_thresholds = saved_thresholds
            st.rerun()

    st.subheader("Acceptance thresholds")
    if inconsistent_threshold_keys:
        st.warning(
            f"Looking at multiple workflows with different thresholds for {' & '.join(inconsistent_threshold_keys)}, using the first values."
        )
    new_thresholds = thresholds_and_histograms_component(
        selected_thresholds=st.session_state.selected_thresholds,
        saved_thresholds=saved_thresholds,
        all_design_ids=all_design_ids,
    )

    if st.session_state.selected_thresholds != new_thresholds:
        # User just changed one of the thresholds, update them in session state
        st.session_state.selected_thresholds = new_thresholds
        st.rerun()

    if st.session_state.selected_thresholds != saved_thresholds:
        st.header(
            f"{len(new_accepted_design_ids):,} accepted {'design' if len(new_accepted_design_ids) == 1 else 'designs'} based on new thresholds"
        )
        st.warning(
            "Thresholds have been changed, showing preview of accepted designs based on new thresholds. "
            "Please save using the 'Confirm thresholds' button above to apply changes."
        )
        displayed_design_ids = new_accepted_design_ids
    else:
        displayed_design_ids = accepted_design_ids
    return displayed_design_ids


def show_all_designs(all_design_ids: list):
    scatterplot_settings = descriptor_scatterplot_input_component(all_design_ids)
    if not scatterplot_settings:
        return

    displayed_design_ids = descriptor_scatterplot_component(
        settings=scatterplot_settings,
        design_ids=all_design_ids,
        highlight_accepted=True,
        selected_thresholds=st.session_state.selected_thresholds,
    )

    if len(displayed_design_ids) < len(all_design_ids):
        header = f"Showing {len(displayed_design_ids):,} {'design' if len(displayed_design_ids) == 1 else 'designs'} selected in scatterplot"
    else:
        header = (
            f"Showing all {len(displayed_design_ids):,} {'design' if len(displayed_design_ids) == 1 else 'designs'}"
        )
    if len(displayed_design_ids) > 1:
        design_labeling_fragment(displayed_design_ids, key_suffix="jobs_bulk", show_header=True, header=header)
    return displayed_design_ids


@st.fragment
def visualize_designs_fragment(design_ids: list[str], shared_workflow_name: str | None = None):
    if not design_ids:
        st.warning("No designs to show")
        return

    design_id = design_navigation_selector(design_ids, allow_all=True, default_all=False)

    if design_id is None:
        WorkflowType = WorkflowTypes.get(shared_workflow_name) if shared_workflow_name else DesignWorkflow

        try:
            WorkflowType.visualize_multiple_designs_structures(design_ids=design_ids)
        except NotImplementedError:
            st.warning(
                f"Visualization of multiple designs not supported by {shared_workflow_name or 'default workflow'}, "
                "please select a single design using the dropdown above."
            )
            return
    else:
        design_labeling_fragment(design_id, key_suffix=f"job_detail_{design_id}")
        show_design(design_id, shared_workflow_name=shared_workflow_name)


def show_workflow_summary(jobs: list[DesignJob]):
    unique_workflow_names = set(job.workflow.name for job in jobs if job.workflow)
    for workflow_name in unique_workflow_names:
        WorkflowType = WorkflowTypes.get(workflow_name)
        if len(unique_workflow_names) > 1:
            st.write(f"### Workflow: {workflow_name}")

        try:
            WorkflowType.visualize_summary(
                jobs=[job for job in jobs if job.workflow and job.workflow.name == workflow_name]
            )
        except NotImplementedError as e:
            st.error(e)
