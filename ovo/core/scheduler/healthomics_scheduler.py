import json
import os
import re
import time
from datetime import datetime

import pandas as pd
from mypy_boto3_logs.type_defs import OutputLogEventTypeDef

from ovo.core.auth import get_username
from ovo.core.scheduler.base_scheduler import Scheduler, SchedulerTypes
from ovo.core.aws import AWSSessionManager


@SchedulerTypes.register()
class HealthOmicsScheduler(Scheduler):
    def __init__(
        self,
        name: str,
        workdir: str,
        reference_files_dir: str,
        aws: AWSSessionManager,
        allow_submit: bool = True,
        submission_args: dict = None,
    ):
        """
        Args:
            aws:
            name: Human-readable label for this scheduler
            workdir: Working directory - where to store workflow outputs (S3 URI including s3:// prefix)
            reference_files_dir: UNUSED Directory with model weights and other reference files
            aws: AWSSessionManager
            allow_submit: Whether to allow job submission
            submission_args: Default submission arguments, can be overridden in submit method
        """
        super().__init__(name, workdir, reference_files_dir, allow_submit, submission_args)
        self.aws = aws

    def submit(self, pipeline_name: str, params: dict = None, submission_args: dict = None) -> str:
        """
        Submits a workflow asynchronously and returns the PID.

        :param pipeline_name: Workflow name and revision (ovo.rfdiffusion-end-to-end or github url with @version)
        :param params: Dictionary of parameters to pass to the workflow.
        :param submission_args: Submission arguments for the scheduler, overrides values in self.submission_args
        :return: Scheduler job ID
        """
        assert isinstance(params, dict), f"params should be a dictionary, got: {type(params).__name__}"

        if not self.allow_submit:
            raise RuntimeError("Job submission is disabled")

        submission_args = {**self.submission_args, **(submission_args or {})}
        workflow_name_prefix = submission_args.pop("workflow_name_prefix", "")
        role_arn = submission_args.pop("role_arn", "")

        if re.fullmatch(r"https?://.*", pipeline_name):
            raise NotImplementedError("GitHub URL pipeline names are not supported yet with HealthOmicsScheduler")
        elif "/" in pipeline_name or pipeline_name == "." or pipeline_name.endswith(".nf"):
            raise NotImplementedError("Local path pipeline names are not supported with HealthOmicsScheduler")
        elif "." in pipeline_name:  # custom workflow path (python_module_name.my_workflow)
            module_name, workflow_subpath = pipeline_name.split(".")
        else:
            module_name = "ovo"
            workflow_subpath = pipeline_name

        omics_workflow_name = workflow_name_prefix + module_name + "_" + workflow_subpath
        workflow_id = self.aws.get_latest_workflow_id(workflow_name=omics_workflow_name)

        if submission_args:
            # submission args should be empty at this point
            raise ValueError(f"Unrecognized {type(self).__name__} submission args: {submission_args.keys()}")

        # AWS params
        params = params.copy()
        params["account_id"] = self.aws.get_account_id()
        params["aws_region"] = self.aws.region_name
        params["workflow_bucket"] = self.workdir.replace("s3://", "").split("/")[0]
        params["reference_files_dir"] = "unused"

        username = get_username()

        # Submit the job
        response = self.aws.omics.start_run(
            roleArn=role_arn,
            workflowId=workflow_id,
            workflowType="PRIVATE",
            name=f"OVO {omics_workflow_name} {username}",
            outputUri=f"{self.workdir.rstrip('/')}/{workflow_subpath}/",
            parameters=params,
            storageCapacity=500,
            logLevel="ALL",
            tags={"user": username, "app": "OVO"},
            storageType="STATIC",
        )

        return response["id"]

    def get_status_label(self, job_id: str) -> str:
        """Get human-readable job status label. Should NOT be used to determine job status.

        Can return "Cancelled", "Completed", "Deleted", "Failed", "Pending", "Running", "Starting", "Stopping"
        """
        return self.aws.omics.get_run(id=job_id)["status"].capitalize()

    def get_result(self, job_id: str) -> str | bool | None:
        """Get job result: True if successful, False if failed, None if running."""
        if not isinstance(job_id, str):
            raise ValueError(
                f"Job ID of {type(self).__name__} should be a string, got {job_id} ({type(job_id).__name__}). Make sure to use job_id instead of the DB id."
            )
        status = self.aws.omics.get_run(id=job_id)["status"]
        if status in ["STARTING", "PENDING", "PENDING_REDRIVE", "RUNNING", "STOPPING"]:
            return None
        if status in ["SUCCEEDED", "COMPLETED"]:
            return True
        return False

    def _get_log_events(self, job_id: str, task_id: str = None, preview: bool = False) -> list[OutputLogEventTypeDef]:
        log_group = "/aws/omics/WorkflowLog"
        log_stream = f"run/{job_id}" + (f"/task/{task_id}" if task_id else "")

        timeout_seconds = 60
        start_time = time.time()
        events: list[OutputLogEventTypeDef] = []
        next_token = None
        target_lines = 10 if preview else None
        token_key = "nextBackwardToken" if preview else "nextForwardToken"

        kwargs = {
            "logGroupName": log_group,
            "logStreamName": log_stream,
            "startFromHead": not preview,
            "limit": 1000,
        }

        while True:
            if time.time() - start_time > timeout_seconds:
                events.append(
                    {
                        "timestamp": time.time() * 1000,
                        "message": "[...] Log truncated due to timeout. ",
                        "ingestionTime": time.time() * 1000,
                    }
                )
                return events

            if next_token:
                kwargs["nextToken"] = next_token

            try:
                response = self.aws.logs.get_log_events(**kwargs)
            except self.aws.logs.exceptions.ResourceNotFoundException:
                return None

            page_events = response.get("events", [])

            if preview:
                events = page_events + events  # prepend
                if len(events) >= target_lines:
                    events = events[-target_lines:]
                    break
            else:
                events.extend(page_events)

            new_token = response.get(token_key)
            if not new_token or new_token == next_token:
                break

            next_token = new_token

        return events

    def get_log(self, job_id: str, task_id: str = None, preview: bool = False) -> str | None:
        """Get job execution log

        :param job_id: Scheduler job ID (DesignJob.job_id or DescriptorJob.job_id)
        :param task_id: Task id of individual task (workdir for nextflow, task id for AWS Omics), None for entire job log
        :param preview: Whether to return only the last 10 lines
        :return: Log string or None if not available
        """
        if not isinstance(job_id, str) or not job_id.isnumeric():
            raise ValueError(
                f"Job ID of {type(self).__name__} should be a numeric string like 4498077, "
                f"got {job_id} ({type(job_id).__name__}). Make sure to use job_id instead of the DB id."
            )

        events = self._get_log_events(job_id=job_id, task_id=task_id, preview=preview)

        if not events:
            return None

        messages = []
        for event in events:
            # format [2026-02-14T03:58:33.926+01:00] message
            timestamp = datetime.fromtimestamp(event["timestamp"] // 1000).isoformat()
            message = f"[{timestamp}] {event['message']}"
            if not task_id:
                try:
                    parsed_message = json.loads(event["message"])
                    message = f"[{timestamp}] [{parsed_message['logMessage'].ljust(16)}] {parsed_message['message']}"
                except (json.JSONDecodeError, KeyError, TypeError):
                    # Fall back to the original message if the log message is not valid JSON
                    # or does not have the expected structure.
                    pass
            messages.append(message)

        return "\n".join(messages) + "\n"

    def cancel(self, job_id):
        """Cancel job execution"""
        raise NotImplementedError()

    def get_output_dir(self, job_id: str) -> str:
        """Get job output path"""
        return os.path.join(self.aws.omics.get_run(id=job_id)["runOutputUri"], "pubdir")

    def get_job_start_time(self, job_id: str) -> datetime | None:
        """Get job start time"""
        run = self.aws.omics.get_run(id=job_id)
        if "startTime" in run:
            return run["startTime"].replace(tzinfo=None)
        return None

    def get_job_stop_time(self, job_id: str) -> datetime | None:
        """Get job end time"""
        run = self.aws.omics.get_run(id=job_id)
        if "stopTime" in run:
            return run["stopTime"].replace(tzinfo=None)
        return None

    def get_startup_time_minutes(self):
        """Get startup time of a task (in minutes)"""
        return 10

    def get_tasks(self, job_id: str) -> pd.DataFrame | None:
        """Get job tasks as a DataFrame with columns: task_id, name, status, duration_seconds + custom columns from the scheduler"""
        items = []
        kwargs = dict(
            runId=job_id,
            maxResults=100,
        )
        while True:
            response = self.aws.omics.list_run_tasks(**kwargs)
            items.extend(response["items"])
            if not response.get("nextToken") or response["nextToken"] == kwargs.get("nextToken"):
                break
            kwargs["nextToken"] = response["nextToken"]

        if not items:
            return None

        tasks = pd.DataFrame.from_records(items)
        tasks = tasks.rename(
            columns={
                "taskId": "task_id",
                "startTime": "start_time",
                "stopTime": "stop_time",
                "creationTime": "creation_time",
                "instanceType": "instance_type",
            }
        )
        tasks["duration_seconds"] = tasks.apply(
            lambda row: (row["stop_time"] - row["start_time"]).total_seconds()
            if row["stop_time"] and row["start_time"]
            else None,
            axis=1,
        )
        return tasks
