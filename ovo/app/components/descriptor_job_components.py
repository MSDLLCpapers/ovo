from datetime import datetime
import streamlit as st
from ovo import db, get_scheduler
from ovo.app.components.custom_elements import refresh_button
from ovo.app.components.job_components import job_status_fragment
from ovo.core.database.models import DescriptorJob, WorkflowTypes
from ovo.core.logic.descriptor_logic import update_and_process_descriptors
from ovo.app.utils.cached_db import get_cached_descriptor_jobs_for_design_ids


def refresh_descriptors(design_ids: list[str] | set[str], workflow_names: list[str] | str = None):
    """Update and process all descriptor jobs results and display a Refresh button and log output if any errors occurred."""

    if workflow_names:
        if isinstance(workflow_names, str):
            workflow_names = [workflow_names]
        expanded_workflow_names = list(workflow_names)
        for workflow_name in list(workflow_names):
            # Include all subclasses of the given workflow names
            for subclass_name in WorkflowTypes.get_subclass_names(workflow_name):
                if subclass_name not in expanded_workflow_names:
                    expanded_workflow_names.append(subclass_name)
        workflow_names = expanded_workflow_names

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
            pending_or_failed_jobs = [
                j for j in pending_or_failed_jobs if j.workflow and j.workflow.name in workflow_names
            ]

        pending_jobs = [j for j in pending_or_failed_jobs if j.job_result is None]

        processed_jobs = update_and_process_descriptors(descriptor_jobs=pending_jobs, error_callback=st.error)
        for processed_job in processed_jobs:
            st.success(f"{processed_job.workflow.name} job has finished")
        if processed_jobs:
            get_cached_descriptor_jobs_for_design_ids.clear()

    failed_jobs = [j for j in pending_or_failed_jobs if j.job_result is False]

    if num_pending_jobs := sum(j.job_result is None for j in pending_jobs):
        if num_pending_jobs > 1:
            st.info(f"{num_pending_jobs} descriptor jobs are in progress")
        else:
            st.info("Descriptor job is in progress")

        refresh_button("refresh_descriptors")

        for job in pending_jobs:
            # check again since the job might have been set as finished inside update_and_process_descriptors
            if job.job_result is None:
                job_status_fragment(job)

    if workflow_names:
        successful_jobs = get_cached_descriptor_jobs_for_design_ids(
            design_ids,
            workflow_names=workflow_names,
            project_id=st.session_state.project.id,
            only_exact_design_ids=False,
        )
        if successful_jobs:
            with st.expander(
                (
                    successful_jobs[0].workflow.name
                    if len(successful_jobs) == 1
                    else f"{len(successful_jobs)} descriptor jobs "
                )
                + " completed successfully",
                on_change="rerun",
            ) as expander:
                if expander.open:
                    for i, job in enumerate(successful_jobs):
                        job_status_fragment(job, expand=(i == 0))

        if failed_jobs:
            with st.expander(
                (
                    f"{failed_jobs[0].workflow.name} has failed"
                    if len(failed_jobs) == 1
                    else f"{len(failed_jobs)} descriptor jobs have failed"
                ),
                on_change="rerun",
                icon="⚠️",
            ) as expander:
                if expander.open:
                    for i, job in enumerate(failed_jobs):
                        job_status_fragment(job, expand=(i == 0))


def descriptor_log_fragment(job: DescriptorJob):
    with st.container(height=400):
        scheduler = get_scheduler(job.scheduler_key)
        st.code(scheduler.get_log(job.job_id))
        if st.button(":material/refresh: Refresh", key=f"refresh_{job.job_id}", type="tertiary"):
            if job.job_result is None and scheduler.get_result(job.job_id) is not None:
                # Workflow just finished, re-run whole page
                st.rerun(scope="app")
