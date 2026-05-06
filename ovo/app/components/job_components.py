import streamlit as st
import streamlit.components.v1 as components
from humanize import precisedelta

from ovo import db, schedulers, Pool
from ovo.core.database import DesignJob, DescriptorJob, UnknownWorkflow


@st.fragment()
def job_status_fragment(job: DesignJob | DescriptorJob, pool: Pool = None, expand=True):
    with st.container(border=True):
        if pool:
            title = f"Pool **{pool.id}** | {pool.name}"
        elif isinstance(job, DescriptorJob):
            num_designs = len(job.workflow.design_ids)
            title = f"{job.workflow.name} | {num_designs} " + ("design" if num_designs == 1 else "designs")
        else:
            raise ValueError("Expected pool when job is not a DescriptorJob")
        if job.scheduler_key not in schedulers:
            st.write(title)
            st.warning(
                f"Scheduler '{job.scheduler_key}' not available in the current config. "
                f"Job status or logs cannot be retrieved for job '{job.job_id}'"
            )
            return
        scheduler = schedulers[job.scheduler_key]
        if job.job_result is None:
            title = f"⏳ {scheduler.get_status_label(job.job_id)} | {title}"
        elif job.job_result == False:
            title = f":red-background[❌ :red[**Failed**] | {title}]"
        else:
            title = f"Done | {title}"

        st.write(title)
        if job.job_result == False:
            with st.popover("Re-submit"):
                if scheduler.supports_resume(job.job_id):
                    # Allow user to re-submit failed jobs if the scheduler supports resuming
                    st.write(
                        "Attempt to resume the workflow from the point of failure (with the same parameters). "
                        "Note that in case the workflow cannot be resumed, it might be re-submitted from the beginning, resulting in duplicate compute cost."
                    )
                    if st.button("Re-submit", key=f"retry_{job.id}", type="primary"):
                        # Resume and update job ID (might be the same or a new one depending on the scheduler)
                        job.job_result = None
                        job.job_finished_date_utc = None
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
                ("1 warning" if len(job.warnings) == 1 else f"{len(job.warnings)} warnings") + f" found for {title}"
            )
            for warning in job.warnings:
                st.warning(warning)

        if job.job_result in (None, False) or expand or st.toggle("Show workflow details", key=f"toggle_{job.id}"):
            options = ["Log preview", "Full log", "Workflow tasks"]
            if not job.job_result is None:
                options += ["Workflow schema", "Execution timeline", "Execution report"]
            tab = st.segmented_control(
                "Tab",
                options=options,
                key=f"tabs_{job.id}",
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
                            key=f"task_summary_{job.id}",
                        )
                        st.write("**All tasks**")
                        selection = st.dataframe(
                            tasks,
                            hide_index=True,
                            on_select="rerun",
                            selection_mode="single-row",
                            key=f"tasks_table_{job.id}",
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
                if log_container.button(":material/refresh: Refresh", key=f"refresh_log_{job.id}", type="tertiary"):
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
