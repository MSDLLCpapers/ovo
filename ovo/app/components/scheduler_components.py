import time
from typing import Callable

import streamlit as st

from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.formatting import truncate_middle


def wait_with_statusbar(
    scheduler: Scheduler,
    job_id: str,
    label="Workflow in progress...",
    interval_seconds=1.0,
    timeout_seconds=60 * 60,
) -> bool:
    if scheduler.get_result(job_id):
        # Do not render the component at all if the job has already finished
        return True

    log_element = None
    watching_since = time.time()
    with st.status("") as statusbar:
        log_container = st.container(height=300, key=f"job_log_{job_id}")
        if st.button("Abort", key=f"abort_{job_id}"):
            statusbar.update(state="error", label="Job cancelled", expanded=False)
            scheduler.cancel(job_id)
            return False
        # Wait in sleep loop
        while True:
            result = scheduler.get_result(job_id)

            tasks = scheduler.get_tasks(job_id)
            log_text = None
            running_label = label
            if tasks is not None:
                # job in progress, try using log of last task
                last_task = tasks.iloc[-1]
                log_text = scheduler.get_log(job_id, task_id=last_task["task_id"])
                if log_text:
                    last_line = truncate_middle(log_text.rstrip().splitlines()[-1], 80)
                    running_label = f"{label} | {last_task['name']} | {last_line}"
                else:
                    running_label = f"{label} | {last_task['name']}"

            if log_text is None:
                # fallback to main log if task-specific log is not available
                log_text = scheduler.get_log(job_id)

            if log_text:
                if result is None:
                    log_text = log_text.rstrip() + "\n\n...auto-refreshing logs..."
                if log_element is None:
                    with log_container:
                        log_element = st.code(log_text)
                else:
                    log_element.code(log_text)

            if result is not None:
                if result:
                    statusbar.update(state="complete", label="Job finished")
                else:
                    statusbar.update(state="error", label="Job failed", expanded=True)
                return result

            queue_size = scheduler.queue_size(job_id=job_id) if hasattr(scheduler, "queue_size") else None
            if queue_size is None:
                # Job is running or queue is not used
                statusbar.update(state="running", label=running_label)
            else:
                if queue_size == 0:
                    # Job is next to run
                    behind_label = ", starting soon"
                else:
                    # Job is waiting in front of others
                    behind_label = f" behind {queue_size} {'job' if queue_size == 1 else 'jobs'}"
                statusbar.update(state="running", label=f"Waiting in queue{behind_label}...")

            if time.time() - watching_since > timeout_seconds:
                scheduler.cancel(job_id)
                raise TimeoutError(f"Waiting timed out after {timeout_seconds} seconds, cancelling job {job_id}")

            time.sleep(interval_seconds)
