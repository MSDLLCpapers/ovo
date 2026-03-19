from datetime import datetime
import streamlit as st
from ovo import db, get_scheduler
from ovo.app.components.custom_elements import refresh_button
from ovo.core.database.models import DescriptorJob
from ovo.core.logic.descriptor_logic import update_and_process_descriptors


def refresh_descriptors(design_ids: list[str] | set[str], workflow_names: list[str] = None):
    """Update and process all descriptor jobs results and display a Refresh button and log output if any errors occurred."""

    with st.spinner("Updating descriptor job status..."):
        pending_or_failed_jobs = db.select(
            DescriptorJob,
            project_id=st.session_state.project.id,
            _or=(dict(job_result=None), dict(job_result=False)),
            order_by="-created_date_utc",
        )

        # Only consider jobs with a Workflow that links to one of the design IDs
        pending_or_failed_jobs = [
            j for j in pending_or_failed_jobs if j.workflow and set(design_ids).intersection(j.workflow.design_ids)
        ]

        # Only consider certain workflow classes
        if workflow_names:
            if isinstance(workflow_names, str):
                workflow_names = [workflow_names]
            pending_or_failed_jobs = [
                j for j in pending_or_failed_jobs if j.workflow and j.workflow.name in workflow_names
            ]

        pending_jobs = [j for j in pending_or_failed_jobs if j.job_result is None]

        processed_jobs = update_and_process_descriptors(descriptor_jobs=pending_jobs, error_callback=st.error)
        for processed_job in processed_jobs:
            st.success(f"{processed_job.workflow.name} job has finished")

        failed_jobs = [j for j in pending_or_failed_jobs if j.job_result is False]

        if num_pending_jobs := sum(j.job_result is None for j in pending_jobs):
            if num_pending_jobs > 1:
                st.info(f"{num_pending_jobs} descriptor jobs are in progress")
            else:
                st.info("Descriptor job is in progress")

            refresh_button("refresh_descriptors")

            for job in pending_jobs:
                log_expander = st.expander(
                    f"Log output: {job.workflow.name}", on_change="rerun", key=f"expander_{job.job_id}"
                )
                if log_expander.open:
                    with log_expander:
                        descriptor_log_fragment(job)

        for job in failed_jobs:
            failed_design_ids = sorted(set(design_ids).intersection(job.workflow.design_ids))
            num_failed_designs = len(failed_design_ids)
            design_ids_str = ", ".join(failed_design_ids[:3]) + ("..." if len(failed_design_ids) > 3 else "")
            with st.expander(
                f"{job.workflow.name} failed for {num_failed_designs:,} {'design' if num_failed_designs == 1 else 'designs'}: {design_ids_str}",
                icon="⚠️",
            ):
                if st.button("Show log", key=f"show_log_{job.job_id}_failed"):
                    with st.container(height=400):
                        scheduler = get_scheduler(job.scheduler_key)
                        st.code(scheduler.get_log(job.job_id))


def descriptor_log_fragment(job: DescriptorJob):
    with st.container(height=400):
        scheduler = get_scheduler(job.scheduler_key)
        st.code(scheduler.get_log(job.job_id))
        if st.button(":material/refresh: Refresh", key=f"refresh_{job.job_id}", type="tertiary"):
            if job.job_result is None and scheduler.get_result(job.job_id) is not None:
                # Workflow just finished, re-run whole page
                st.rerun(scope="app")
