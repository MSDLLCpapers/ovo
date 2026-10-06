from datetime import datetime, timezone
import pandas as pd

from ovo.core.auth import is_running_in_streamlit
from ovo import get_scheduler, db, storage
from ovo.core.database.models import (
    JobMixin,
    JobReportArtifact,
    ProjectArtifact,
    DesignJob,
    DescriptorJob,
    Pool,
    Round,
)
from ovo.core.scheduler import Scheduler


def update_job_status(job: JobMixin, save_on_success: bool = False) -> bool | None:
    """Update job status of JobMixin object (Pool, DescriptorJob, ...) and return the scheduler result.

    Job result is saved, except when save_on_success is False and job succeeded,
    this is used in case we want to process the results downstream and save them atomically.

    Returns scheduler result (None = in progress, True = succeeded, False = Failed)
    """
    try:
        scheduler = get_scheduler(job.scheduler_key)
        job_result: bool | None = scheduler.get_result(job.job_id)

        if job.job_started_date_utc is None and (start_time := scheduler.get_job_start_time(job.job_id)):
            # Save start time if not yet saved
            job.job_started_date_utc = start_time
            db.save(job)

        if job_result is not None:
            # Finished state - Successful or Failed
            # Track if this is the first time we're detecting the failure
            first_time_failed = job.job_result is None and job_result == False

            job.job_result = job_result
            job.job_finished_date_utc = scheduler.get_job_stop_time(job.job_id) or datetime.now(timezone.utc).replace(
                tzinfo=None
            )
            if job.job_result == False or save_on_success:
                # Save the job if failed or if we want to save successful jobs
                # (job status is not saved in case we want to process the results and save them atomically)
                db.save(job)

                # Create and save JobReportArtifact for failed jobs (only on first detection)
                if first_time_failed and isinstance(job, (DesignJob, DescriptorJob)):
                    artifact = create_job_report_artifact(job, scheduler)
                    if artifact:
                        db.save(artifact)

        return job_result
    except Exception as e:
        if is_running_in_streamlit():
            # TODO this is not the cleanest way to handle this but probably the most foolproof
            import streamlit as st

            st.error(f"Failed to update job status: {e}")
            return None
        else:
            raise


def delete_job_artifacts(job: DesignJob | DescriptorJob):
    """Delete all job report artifacts associated with a job."""
    artifact_filter = {"descriptor_job_id": job.id} if isinstance(job, DescriptorJob) else {"design_job_id": job.id}
    db.remove(ProjectArtifact, artifact_type=JobReportArtifact.artifact_type, **artifact_filter)


def format_job_duration(job: JobMixin):
    """Return job duration formatted as 00d:00h:00m."""
    if not job.job_id:
        return None
    if not job.job_started_date_utc:
        return "Not started"
    elif job.job_finished_date_utc:
        delta = job.job_finished_date_utc - job.job_started_date_utc
    else:
        delta = datetime.now(timezone.utc).replace(tzinfo=None) - job.job_started_date_utc
    # format 00d:00h:00m
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(days):02d}d:{int(hours):02d}h:{int(minutes):02d}m"


def create_job_report_artifact(job: DesignJob | DescriptorJob, scheduler: Scheduler) -> ProjectArtifact | None:
    """Create a JobReportArtifact for a finished job.

    This should be called when processing job results to capture logs, tasks, and reports.
    The returned ProjectArtifact should be saved atomically with other processed objects.

    Returns ProjectArtifact containing the JobReportArtifact, or None if project_id cannot be determined.
    """
    project_id, pool_id = _get_project_and_pool_ids_for_job(job)
    if not project_id:
        return None

    # Task table
    task_table = scheduler.get_tasks(job.job_id)
    if task_table is not None:
        total_duration_seconds = task_table["duration_seconds"].sum()
        total_compute_hours = total_duration_seconds / 3600
    else:
        total_compute_hours = None

    # Log preview
    log_preview = scheduler.get_log(job.job_id, preview=True)

    project_path = storage.get_project_path(project_id, pool_id=pool_id)

    # Report path
    report_str = scheduler.get_report(job.job_id)
    if not report_str:
        report_path = None
    else:
        report_path = storage.store_file_str(report_str, storage_rel_path=f"{project_path}/jobs/{job.id}/report.html")

    # Timeline path
    timeline_str = scheduler.get_timeline(job.job_id)
    if not timeline_str:
        timeline_path = None
    else:
        timeline_path = storage.store_file_str(
            timeline_str, storage_rel_path=f"{project_path}/jobs/{job.id}/timeline.html"
        )

    # Workflow DAG path
    workflow_dag_str = scheduler.get_dag(job.job_id)
    if not workflow_dag_str:
        workflow_dag_path = None
    else:
        workflow_dag_path = storage.store_file_str(
            workflow_dag_str, storage_rel_path=f"{project_path}/jobs/{job.id}/dag.dot"
        )

    job_report_artifact = JobReportArtifact(
        job_author=job.author,
        total_compute_hours=total_compute_hours,
        log_preview=log_preview,
        task_table=task_table,
        report_path=report_path,
        timeline_path=timeline_path,
        workflow_dag_path=workflow_dag_path,
    )
    if isinstance(job, DescriptorJob):
        artifact_params = {"descriptor_job_id": job.id}
    else:
        artifact_params = {"design_job_id": job.id}
    project_artifact = ProjectArtifact(
        author=job.author,
        project_id=project_id,
        artifact_type=job_report_artifact.artifact_type,
        **artifact_params,
        artifact=job_report_artifact,
    )
    return project_artifact


def _get_project_and_pool_ids_for_job(job: DesignJob | DescriptorJob) -> tuple[str | None, str | None]:
    """Get project_id and pool_id for a job.

    Returns (project_id, pool_id). pool_id is only set for DesignJobs.
    """
    if isinstance(job, DescriptorJob):
        return job.project_id, None
    elif isinstance(job, DesignJob):
        pool = db.get(Pool, design_job_id=job.id)
        if pool:
            project_round = db.get(Round, id=pool.round_id)
            if project_round:
                return project_round.project_id, pool.id
    return None, None
