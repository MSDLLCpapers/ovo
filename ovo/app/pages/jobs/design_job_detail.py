from datetime import datetime

import pandas as pd
import streamlit as st
from humanize import precisedelta
from streamlit_timeago import time_ago

from ovo import db, get_scheduler, Pool, Design, WorkflowTypes, DesignWorkflow
from ovo.app.components.acceptance_thresholds_components import (
    thresholds_and_histograms_component,
    accept_designs_dialog,
    display_current_thresholds,
    filter_designs_by_thresholds_cached,
)
import streamlit.components.v1 as components
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_scatterplot import (
    descriptor_scatterplot_pool_details_component,
    descriptor_scatterplot_input_component,
)
from ovo.core.database import DesignJob, UnknownWorkflow
from ovo.core.logic.design_logic import process_results
from ovo.core.logic.job_logic import update_job_status
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_pool,
    get_cached_design,
    get_cached_design_job,
    get_cached_design_jobs_table,
)


@st.fragment
def design_job_detail(pool_ids):
    pools = get_cached_pools(pool_ids)
    pools_by_design_job = {pool.design_job_id: pool for pool in pools if pool.design_job_id}

    design_job_ids = [pool.design_job_id for pool in pools if pool.design_job_id]
    if not design_job_ids:
        st.warning("Selected pools are not associated with a design job")
        return

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

    st.subheader("Workflow parameters")
    table = get_cached_design_jobs_table(round_ids=sorted(set(p.round_id for p in pools)), id__in=pool_ids)
    table.index = [pools_by_design_job[j.id].id for j in design_jobs]
    st.dataframe(table)

    num_pools_failed = sum(job.job_result == False for job in design_jobs)
    num_pools_in_progress = sum(job.job_result is None for job in design_jobs)

    if num_pools_in_progress:
        st.button(":material/refresh: Refresh", key="refresh1")
        time_ago(datetime.now(), prefix="Refreshed", key="refreshed1")

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
                workflow_detail_fragment(job, pool, first=i == 0)
            except Exception as e:
                # avoid failing here, error is already printed inside fragment
                st.error(f"Failed reading job details for job {job.job_id}: {e}")

    if len(pools) == num_pools_failed + num_pools_in_progress:
        # Nothing to show yet, exit here
        return

    if num_pools_in_progress:
        st.info(
            f"Not including results of {num_pools_in_progress} ongoing workflow"
            + ("s" if num_pools_in_progress > 1 else "")
        )
        st.button(":material/refresh: Refresh", key="refresh2")
        time_ago(datetime.now(), prefix="Refreshed", key="refreshed2")

    all_design_ids = sorted(db.select_unique_values(Design, "id", pool_id__in=pool_ids))

    refresh_descriptors(
        design_ids=all_design_ids,
    )

    job_results_fragment(
        all_design_ids=all_design_ids,
        pools=pools,
        jobs=design_jobs,
    )


@st.fragment()
def workflow_detail_fragment(job: DesignJob, pool: Pool, first=False):
    scheduler = get_scheduler(job.scheduler_key)
    with st.container(border=True):
        # noinspection PyUnreachableCode
        title_suffix = f"Pool **{pool.id}** | {pool.name}"
        if job.job_result is None:
            title = f"⏳ {scheduler.get_status_label(job.job_id)} | {title_suffix}"
        elif job.job_result == False:
            title = f":red-background[❌ :red[**Failed**] | {title_suffix}]"
        else:
            title = f"Done | {title_suffix}"

        st.write(title)
        if job.job_result == False:
            with st.popover("Re-submit"):
                if scheduler.supports_resume(job.job_id):
                    # Allow user to re-submit failed jobs if the scheduler supports resuming
                    st.write(
                        "Attempt to resume the workflow from the point of failure (with the same parameters). "
                        "Note that in case the workflow cannot be resumed, it might be re-submitted from the beginning, resulting in duplicate compute cost."
                    )
                    if st.button("Re-submit", key=f"retry_{pool.id}", type="primary"):
                        # Resume and update job ID (might be the same or a new one depending on the scheduler)
                        job.job_result = None
                        job.job_id = scheduler.resume(job.job_id)
                        db.save(job)
                        st.rerun()
                else:
                    st.write(f"{scheduler.__class__.__name__} currently does not support resuming failed jobs.")

        if job.workflow and job.workflow.is_instance(UnknownWorkflow):
            st.warning(f"Workflow failed to load: {job.workflow.error}")
            with st.expander("Raw data"):
                st.json(job.workflow.data)

        if job.warnings:
            st.write(
                ("1 warning" if len(job.warnings) == 1 else f"{len(job.warnings)} warnings")
                + f" found for pool {pool.name}:"
            )
            for warning in job.warnings:
                st.warning(warning)

        if job.job_result in (None, False) or first or st.toggle("Show workflow details", key=f"toggle_{pool.id}"):
            options = ["Log preview", "Full log", "Workflow tasks"]
            if not job.job_result is None:
                options += ["Workflow schema", "Execution timeline", "Execution report"]
            tab = st.segmented_control(
                "Tab",
                options=options,
                key=f"tabs_{pool.id}",
                label_visibility="collapsed",
                default="Log preview",
            )
            log_container = st
            if tab == "Log preview":
                with st.spinner("Getting job log output..."):
                    st.code(scheduler.get_log(job.job_id, preview=True) or "No log output available")
            elif tab == "Full log":
                # Show full log in a scrollable container with fixed height
                with st.spinner("Getting job log output..."):
                    log_container = st.container(height=400)
                    log_container.code(scheduler.get_log(job.job_id) or "No log output available")
            elif tab == "Workflow tasks":
                if (tasks := scheduler.get_tasks(job.job_id)) is not None:
                    if not tasks.empty:
                        st.write("**Summary**")
                        name_without_suffix = tasks["name"].apply(lambda s: s.split()[0])
                        summary = (
                            tasks.groupby(name_without_suffix, sort=False)["status"]
                            .value_counts()
                            .unstack(fill_value=0)
                        )
                        summary["avg_duration"] = (
                            tasks.groupby(name_without_suffix)["duration_seconds"].mean().apply(precisedelta)
                        )
                        summary["total_duration"] = (
                            tasks.groupby(name_without_suffix)["duration_seconds"].sum().apply(precisedelta)
                        )
                        st.dataframe(
                            summary.reset_index(),
                            hide_index=True,
                            width="content",
                            key=f"task_summary_{pool.id}",
                        )
                        st.write("**All tasks**")
                        selection = st.dataframe(
                            tasks,
                            hide_index=True,
                            on_select="rerun",
                            selection_mode="single-row",
                            key=f"tasks_table_{pool.id}",
                        )
                        if selection["selection"]["rows"]:
                            selected_task_row = tasks.iloc[selection["selection"]["rows"][0]]
                            st.write(f"**Task log** | {selected_task_row.status} | {selected_task_row['name']}")
                            with st.spinner("Getting task log output..."):
                                task_log = scheduler.get_log(job.job_id, selected_task_row.task_id)
                                log_container = st.container(height=400)
                                log_container.code(task_log or "No log output available")
                        else:
                            st.write("Select a task above to show its log output.")
                    else:
                        st.write("No tasks yet.")
                else:
                    st.write("Workflow task information not available.")

            if job.job_result is None:
                if log_container.button(":material/refresh: Refresh", key=f"refresh_log_{pool.id}", type="tertiary"):
                    if job.job_result is None and scheduler.get_result(job.job_id) is not None:
                        # Workflow just finished, re-run whole page
                        st.rerun(scope="app")
                # Job still in progress, return here
                return

            elif tab == "Workflow schema":
                if dag := scheduler.get_dag(job.job_id):
                    st.graphviz_chart(dag)
                else:
                    st.write("Workflow schema not available.")
            elif tab == "Execution timeline":
                if timeline_html := scheduler.get_timeline(job.job_id):
                    components.html(timeline_html, height=600, scrolling=True)
                else:
                    st.write("Execution timeline not available.")
            elif tab == "Execution report":
                if report_html := scheduler.get_report(job.job_id):
                    # hide navigation bar in report
                    report_html = report_html.replace(
                        "</head>",
                        "<style>\n#nf-report-navbar { display: none }\nbody { padding-top: 0 }\n</style>\n</head>",
                    )
                    components.html(report_html, height=650, scrolling=True)
                else:
                    st.write("Execution report not available.")


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
        for descriptor_key, thresholds in workflow.acceptance_thresholds.items():
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
        options=["Accepted designs", "All designs"],
        key="show_designs",
        default=st.query_params.get("show", "Accepted designs"),
    )

    if show_mode == "Accepted designs":
        accepted_design_ids = db.select_values(Design, "id", id__in=all_design_ids, accepted=True)

        if st.session_state.selected_thresholds != saved_thresholds:
            st.header("Editing thresholds")
        elif accepted_design_ids:
            st.header(
                f"Showing {len(accepted_design_ids)} accepted {'designs' if len(accepted_design_ids) > 1 else 'design'}"
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

    elif show_mode == "All designs":
        st.query_params["show"] = show_mode
        scatterplot_settings = descriptor_scatterplot_input_component(all_design_ids)
        if not scatterplot_settings:
            return

        selected_design_ids, selection_label = descriptor_scatterplot_pool_details_component(
            settings=scatterplot_settings,
            design_ids=all_design_ids,
            highlight_accepted=True,
            selected_thresholds=st.session_state.selected_thresholds,
        )

        if selection_label:
            st.info(f"Selected region: {selection_label}")
            displayed_design_ids = selected_design_ids
            st.header(
                f"Showing {len(displayed_design_ids):,} {'design' if len(displayed_design_ids) == 1 else 'designs'} selected in scatterplot"
            )
        else:
            st.caption(
                ":material/info: Select a region in the scatterplot to display designs that fall within the selected range."
            )
            displayed_design_ids = all_design_ids
            st.header(f"Showing all {len(displayed_design_ids):,} designs")

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


@st.fragment
def visualize_designs_fragment(design_ids: list[str], shared_workflow_name: str | None = None):
    if not design_ids:
        st.warning("No designs to show")
        return
    elif len(design_ids) == 1:
        design_id = design_ids[0]
    else:
        indexes = {v: i for i, v in enumerate(design_ids, start=1)}
        design_id = st.selectbox(
            "Select design",
            options=[None] + design_ids,
            format_func=lambda v: "Preview all designs" if v is None else f"{indexes[v]} | {v}",
            index=1,
        )

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
        st.subheader(design_id)

        design = get_cached_design(design_id)
        pool = get_cached_pool(design.pool_id)
        if not shared_workflow_name and pool.design_job_id:
            design_job = get_cached_design_job(pool.design_job_id)
            shared_workflow_name = design_job.workflow.name if design_job and design_job.workflow else None

        WorkflowType = WorkflowTypes.get(shared_workflow_name) if shared_workflow_name else DesignWorkflow

        try:
            WorkflowType.visualize_single_design_structures(design_id)
        except Exception as e:
            st.error(f"Error visualizing structure: {e}")

        st.write("### Sequence")

        WorkflowType.visualize_single_design_sequences(design_id)

        st.write(f"### Download {design_id}")

        download_job_designs_component(design_ids=[design_id], pools=[pool], key="single")
