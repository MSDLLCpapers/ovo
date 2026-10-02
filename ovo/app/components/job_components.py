import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from humanize import precisedelta

from ovo import db, schedulers, storage, Pool
from ovo.core.database import DesignJob, DescriptorJob, UnknownWorkflow, ProjectArtifact, JobReportArtifact
from ovo.core.logic.job_logic import delete_job_artifacts


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

        # Try getting the job report artifact
        if isinstance(job, DesignJob):
            report_params = {"design_job_id": job.id}
        else:
            report_params = {"descriptor_job_id": job.id}
        report_artifacts = db.select(
            ProjectArtifact,
            **report_params,
            artifact_type=JobReportArtifact.artifact_type,
            order_by=ProjectArtifact.created_date_utc.desc(),
        )
        if report_artifacts:
            job_report_artifact: JobReportArtifact = report_artifacts[0].artifact
        else:
            job_report_artifact = None

        # Get scheduler only if available (will be used as fallback when artifact is missing)
        scheduler = schedulers.get(job.scheduler_key) if job.scheduler_key in schedulers else None
        scheduler_available = scheduler is not None

        # Build title with status
        if job.job_result is None:
            # Job is in progress
            if scheduler_available:
                status_label = scheduler.get_status_label(job.job_id)
                title = f"⏳ {status_label} | {title}"
            else:
                title = f"⏳ In Progress | {title}"
        elif job.job_result == False:
            title = f":red-background[❌ :red[**Failed**] | {title}]"
        else:
            title = f"Done | {title}"

        st.write(title)

        # Warn if scheduler is not available (after showing the title)
        if not scheduler_available and not job_report_artifact:
            st.warning(
                f"Scheduler '{job.scheduler_key}' not available in the current config and no job report artifact found. "
                f"Job status or logs cannot be retrieved for job '{job.job_id}'"
            )
            return
        if job.job_result == False and scheduler_available:
            with st.popover("Re-submit"):
                if scheduler.supports_resume(job.job_id):
                    # Allow user to re-submit failed jobs if the scheduler supports resuming
                    st.write(
                        "Attempt to resume the workflow from the point of failure (with the same parameters). "
                        "Note that in case the workflow cannot be resumed, it might be re-submitted from the beginning, resulting in duplicate compute cost."
                    )
                    if st.button("Re-submit", key=f"retry_{job.id}", type="primary"):
                        job.job_result = None
                        job.job_finished_date_utc = None
                        job.job_id = scheduler.resume(job.job_id)
                        delete_job_artifacts(job)
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
            # Determine available tabs based on job state and data availability
            options = ["Log preview", "Full log", "Workflow tasks"]
            if job.job_result is not None:
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
                    if job_report_artifact and job_report_artifact.log_preview:
                        log = job_report_artifact.log_preview
                    elif scheduler_available:
                        log = scheduler.get_log(job.job_id, preview=True) or "No log output available"
                    else:
                        log = "No log output available (scheduler not available)"
                    st.code(log)
                if job.job_result == False:
                    st.write('Job failed. See more detailed log output in "Full log" or "Workflow tasks" tab above.')
            elif tab == "Full log":
                # Show full log in a scrollable container with fixed height
                with st.spinner("Getting job log output..."):
                    log_container = st.container(height=400)
                    if scheduler_available:
                        log_container.code(scheduler.get_log(job.job_id) or "No log output available")
                    else:
                        log_container.code("No log output available (scheduler not available)")
            elif tab == "Workflow tasks":
                # Get tasks from artifact or scheduler
                tasks = None
                if job_report_artifact and job_report_artifact.task_table is not None:
                    tasks = job_report_artifact.task_table
                elif scheduler_available:
                    tasks = scheduler.get_tasks(job.job_id)

                if tasks is not None:
                    if not tasks.empty:
                        st.write("**Summary**")
                        name_without_suffix = tasks["name"].apply(lambda s: s.split()[0])
                        summary = (
                            tasks.groupby(name_without_suffix, sort=False)["status"]
                            .value_counts()
                            .unstack(fill_value=0)
                        )
                        # Do not show durations in seconds for long workflows
                        total_duration = tasks["duration_seconds"].sum()
                        delta_kwargs = {"minimum_unit": "minutes"} if total_duration >= 3600 else {}

                        summary["avg_duration"] = (
                            tasks.groupby(name_without_suffix)["duration_seconds"]
                            .mean()
                            .apply(precisedelta, **delta_kwargs)
                        )
                        summary["total_duration"] = (
                            tasks.groupby(name_without_suffix)["duration_seconds"]
                            .sum()
                            .apply(precisedelta, **delta_kwargs)
                        )
                        task_durations = tasks.groupby(name_without_suffix)["duration_seconds"].sum()
                        if total_duration > 0:
                            summary["% of total"] = task_durations / total_duration * 100
                        else:
                            summary["% of total"] = 0
                        # Add total row to summary
                        total_row_data = {
                            "name": "Total",
                            "avg_duration": "",
                            "total_duration": precisedelta(total_duration, **delta_kwargs),
                            "% of total": "-",
                        }
                        # Add empty columns for status counts
                        for col in summary.columns:
                            if col not in ["avg_duration", "total_duration", "% of total"]:
                                total_row_data[col] = ""
                        summary_with_total = pd.concat(
                            [summary.reset_index(), pd.DataFrame([total_row_data])], ignore_index=True
                        )
                        # Apply white-to-grey gradient styling
                        num_task_rows = len(summary_with_total) - 1  # Exclude the total row
                        styled = summary_with_total.style.background_gradient(
                            subset=pd.IndexSlice[: num_task_rows - 1, "% of total"],  # Skip the total row (last)
                            cmap="Greys",
                            vmin=0,
                            vmax=100,
                        ).format({"% of total": lambda x: x if isinstance(x, str) else f"{x:.1f}%"})
                        st.dataframe(
                            styled,
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
                            if not scheduler_available:
                                st.write("Scheduler not available. Task logs cannot be retrieved.")
                            else:
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
                if job_report_artifact and job_report_artifact.workflow_dag_path:
                    dag = storage.read_file_str(job_report_artifact.workflow_dag_path)
                elif scheduler_available:
                    dag = scheduler.get_dag(job.job_id)
                else:
                    dag = None
                if dag:
                    st.graphviz_chart(dag)
                else:
                    st.write("Workflow schema not available.")
            elif tab == "Execution timeline":
                if job_report_artifact and job_report_artifact.timeline_path:
                    timeline_html = storage.read_file_str(job_report_artifact.timeline_path)
                elif scheduler_available:
                    timeline_html = scheduler.get_timeline(job.job_id)
                else:
                    timeline_html = None
                if timeline_html:
                    components.html(timeline_html, height=600, scrolling=True)
                else:
                    st.write("Execution timeline not available.")
                    if not scheduler_available:
                        st.write("Scheduler not available.")
            elif tab == "Execution report":
                if job_report_artifact and job_report_artifact.report_path:
                    report_html = storage.read_file_str(job_report_artifact.report_path)
                elif scheduler_available:
                    report_html = scheduler.get_report(job.job_id)
                else:
                    report_html = None
                if report_html:
                    # hide navigation bar in report
                    report_html = report_html.replace(
                        "</head>",
                        "<style>\n#nf-report-navbar { display: none }\nbody { padding-top: 0 }\n</style>\n</head>",
                    )
                    components.html(report_html, height=650, scrolling=True)
                else:
                    st.write("Execution report not available.")
