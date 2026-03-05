from datetime import datetime

from ovo.core.auth import is_running_in_streamlit
from ovo import get_scheduler, db
from ovo.core.database.models import JobMixin


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
            job.job_result = job_result
            job.job_finished_date_utc = scheduler.get_job_stop_time(job.job_id) or datetime.utcnow()
            if job.job_result == False or save_on_success:
                # Save the job if failed or if we want to save successful jobs
                # (job status is not saved in case we want to process the results and save them atomically)
                db.save(job)

        return job_result
    except Exception as e:
        if is_running_in_streamlit():
            # TODO this is not the cleanest way to handle this but probably the most foolproof
            import streamlit as st

            st.error(f"Failed to update job status: {e}")
            return None
        else:
            raise


def format_job_duration(job: JobMixin):
    """Return job duration formatted as 00d:00h:00m."""
    if not job.job_id:
        return None
    if not job.job_started_date_utc:
        return "Not started"
    elif job.job_finished_date_utc:
        delta = job.job_finished_date_utc - job.job_started_date_utc
    else:
        delta = datetime.utcnow() - job.job_started_date_utc
    # format 00d:00h:00m
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(days):02d}d:{int(hours):02d}h:{int(minutes):02d}m"
