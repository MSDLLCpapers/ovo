"""Task-based scheduler for running Python functions as workflow tasks."""

import os
import traceback
from abc import abstractmethod
from datetime import datetime, timezone
from uuid import uuid1

from ovo.core.scheduler.base_scheduler import Scheduler, SchedulerTypes, JobNotFound


# Global task registry accessible to all TaskScheduler instances
_GLOBAL_TASK_REGISTRY = {}


def task(func):
    """Decorator to register a function as a task.

    The task name is automatically determined from the function's full module path:
    module.path.function_name

    Usage:
        @task
        def my_task(execdir: str, param1: str, param2: int):
            # Task implementation
            pass

    The task will be registered as "module.path.my_task()"

    Args:
        func: Function to register as a task

    Returns:
        The original function with _task_name attribute added
    """
    # Generate task name from module path + function name
    task_name = f"{func.__module__}.{func.__name__}()"
    _GLOBAL_TASK_REGISTRY[task_name] = func
    func._task_name = task_name
    return func


def get_registered_task(name: str):
    """Get a registered task function by name.

    Args:
        name: Task name to retrieve.

    Returns:
        Task function.

    Raises:
        ValueError: If task is not registered.
    """
    if name not in _GLOBAL_TASK_REGISTRY:
        raise ValueError(f"Task '{name}' not registered. Available: {list(_GLOBAL_TASK_REGISTRY.keys())}")
    return _GLOBAL_TASK_REGISTRY[name]


# Generic workflow task - all TaskScheduler workflows use this
# Task name will be: ovo.core.scheduler.task_scheduler.run_workflow()
@task
def run_workflow(execdir: str, workflow_dict: dict, scheduler_key: str = None):
    """Generic task that runs any workflow's run() method.

    This eliminates the need for per-workflow task functions.

    Task name: ovo.core.scheduler.task_scheduler.run_workflow()

    Args:
        execdir: Execution directory
        workflow_dict: Serialized workflow (from asdict())
        scheduler_key: Optional scheduler key for nested workflow calls
    """
    # Import here to avoid circular dependency
    from ovo.core.database.models import Workflow
    from ovo import get_scheduler

    workflow = Workflow.from_dict(workflow_dict)
    scheduler = get_scheduler(scheduler_key) if scheduler_key else None
    workflow.run(execdir=execdir, scheduler=scheduler)


@SchedulerTypes.register()
class TaskScheduler(Scheduler):
    """Abstract base scheduler for running Python tasks directly.

    TaskScheduler extends Scheduler to run Python functions decorated with @task
    instead of external pipelines like Nextflow.
    """

    def __init__(self, name: str, workdir: str, **kwargs):
        """Initialize TaskScheduler.

        Args:
            name: Human-readable scheduler name
            workdir: Working directory for task execution
            **kwargs: Additional arguments passed to Scheduler
        """
        # TaskScheduler doesn't need reference_files_dir, remove if present in kwargs
        kwargs.pop("reference_files_dir", None)
        super().__init__(name=name, workdir=workdir, reference_files_dir="", **kwargs)

    def submit(self, pipeline_name: str, params: dict = None, submission_args: dict = None) -> str:
        """Submit a task for execution.

        Args:
            pipeline_name: Name of registered task function (task name, not pipeline)
            params: Dictionary with task-specific params
            submission_args: Scheduler-specific args

        Returns:
            job_id: Unique job identifier
        """
        raise NotImplementedError()

    def get_output_dir(self, job_id: str):
        """Get task output directory (the execdir itself).

        Args:
            job_id: Job identifier

        Returns:
            Path to execution directory
        """
        return self._get_exec_dir(job_id)

    def _get_exec_dir(self, job_id: str):
        """Get execution directory for job_id, same pattern as NextflowScheduler.

        Args:
            job_id: Job identifier

        Returns:
            Path to execution directory

        Raises:
            ValueError: If job_id is not a string
        """
        if not isinstance(job_id, str):
            raise ValueError(f"Job ID should be string, got {type(job_id).__name__}")
        return os.path.join(self.workdir, "execdir", job_id)

    def supports_pipeline_name(self, pipeline_name: str) -> bool:
        """Check if pipeline can be run as a task.

        Args:
            pipeline_name: Pipeline name to check (full module path to task function)

        Returns:
            True if pipeline is registered in the task registry
        """
        # Check if this pipeline is registered as a task
        return pipeline_name in _GLOBAL_TASK_REGISTRY


@SchedulerTypes.register()
class SyncTaskScheduler(TaskScheduler):
    """Synchronous task scheduler that runs tasks directly in the current process.

    This scheduler executes tasks immediately and blocks until completion.
    Since execution is synchronous, by the time submit() returns, the job is done.
    Job state is determined by the existence of the execdir.

    Suitable for testing and short-running tasks. Can be used across processes
    since it doesn't maintain in-memory state.
    """

    def __init__(self, name: str = "Sync Task Scheduler", workdir: str = None, **kwargs):
        """Initialize SyncTaskScheduler.

        Args:
            name: Human-readable scheduler name
            workdir: Working directory (required)
            **kwargs: Additional arguments

        Raises:
            ValueError: If workdir is None
        """
        if workdir is None:
            raise ValueError("workdir is required for SyncTaskScheduler and cannot be None")
        super().__init__(name=name, workdir=workdir, **kwargs)

    def submit(self, pipeline_name: str, params: dict = None, submission_args: dict = None) -> str:
        """Submit a task for execution.

        Args:
            pipeline_name: Name of registered task function (task name, not pipeline)
            params: Dictionary with task-specific params
            submission_args: Scheduler-specific args

        Returns:
            job_id: Unique job identifier
        """
        task_func = get_registered_task(pipeline_name)

        # Generate job_id like Nextflow (uuid1 is increasing by time)
        job_id = str(uuid1())
        execdir = self._get_exec_dir(job_id)
        os.makedirs(self.workdir, exist_ok=True)
        os.makedirs(execdir, exist_ok=False)

        params = params or {}

        try:
            # Call task with execdir as first arg
            task_func(execdir=execdir, **params)
        except Exception as e:
            # Write error to execdir for later retrieval
            error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            error_file = os.path.join(execdir, "error.log")
            with open(error_file, "w") as f:
                f.write(error_msg)
            # Don't re-raise - job_id should still be returned
            # Job will be marked as failed via get_result()

        return job_id

    def get_result(self, job_id: str) -> bool | None:
        """Get job result by checking execdir existence.

        Since tasks execute synchronously, if the execdir exists, the job is done.
        Success is determined by the absence of error.log file.

        Args:
            job_id: Job identifier

        Returns:
            True if successful, False if failed, None if execdir doesn't exist
        """
        execdir = self._get_exec_dir(job_id)

        if not os.path.exists(execdir):
            return None

        # Check if error.log exists
        error_file = os.path.join(execdir, "error.log")
        if os.path.exists(error_file):
            return False  # Failed
        else:
            return True  # Success

    def get_status_label(self, job_id: str) -> str:
        """Get human-readable status.

        Args:
            job_id: Job identifier

        Returns:
            Status string: "Done" or "Failed"
        """
        result = self.get_result(job_id)
        return "Done" if result else "Failed"

    def get_log(self, job_id: str, task_id: str = None, preview: bool = False) -> str | None:
        """Get job log (error message if failed).

        Args:
            job_id: Job identifier
            task_id: Ignored for sync scheduler
            preview: Ignored for sync scheduler

        Returns:
            Error message if failed, None otherwise
        """
        execdir = self._get_exec_dir(job_id)
        error_file = os.path.join(execdir, "error.log")

        if os.path.exists(error_file):
            with open(error_file, "r") as f:
                return f.read()

        return None

    def get_job_start_time(self, job_id: str) -> datetime | None:
        """Get job start time.

        Not implemented for SyncTaskScheduler since jobs complete immediately.

        Args:
            job_id: Job identifier

        Returns:
            None
        """
        return None

    def get_job_stop_time(self, job_id: str) -> datetime | None:
        """Get job end time.

        Not implemented for SyncTaskScheduler since jobs complete immediately.

        Args:
            job_id: Job identifier

        Returns:
            None
        """
        return None

    def cancel(self, job_id: str):
        """Cannot cancel synchronous tasks.

        Args:
            job_id: Job identifier

        Raises:
            NotImplementedError: Always, as sync tasks can't be cancelled
        """
        raise NotImplementedError("Cannot cancel synchronous tasks")

    def get_pipeline_names(self) -> list[str]:
        """Return list of registered task names.

        Returns:
            List of available task names
        """
        return list(_GLOBAL_TASK_REGISTRY.keys())

    def get_failed_message(self, job_id: str):
        """Get failure message for failed job.

        Args:
            job_id: Job identifier

        Returns:
            Error message from error.log or default message
        """
        log = self.get_log(job_id)
        return log or f"Job {job_id} has failed."
