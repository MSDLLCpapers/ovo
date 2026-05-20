import json
import logging
import os
import uuid
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from ovo.core.scheduler import NextflowScheduler
from ovo.core.utils.param_validation import validate_params
from typing import Any, Dict

from pytest_mock import MockerFixture

from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.formatting import format_duration

logger = logging.getLogger(__name__)


def mock_molstar(return_value: dict = None):
    """
    Mock the Mol* component for a given PDB code.

    Args:
        return_value: return value from molstar component

    Returns:
        contextmanager: A context manager that patches the Mol* component.
    """

    @contextmanager
    def _mock_molstar(mocker: MockerFixture):
        molstar = mocker.patch(
            "ovo.app.components.input_components.molstar_custom_component",
            return_value=json.dumps(return_value or None),
        )
        yield molstar

    return _mock_molstar


class MockJob:
    """Mock Job Class"""

    def __init__(self, job_id, pipeline_name, result, log, output_dir):
        """
        Initialize a MockJob instance.

        Args:
            job_id (str): The job ID.
            pipeline_name (str): The workflow revision.
            result (bool): The job result.
            log (str): The job log content.
            output_dir (str): The job output directory.
        """
        self.job_id = job_id
        self.pipeline_name = pipeline_name
        self.result = result
        self.log = log
        self.output_dir = output_dir
        self.start_time = datetime.now()
        self.stop_time = datetime.now()


class MockScheduler(NextflowScheduler):
    """Mock Scheduler Class"""

    def __init__(self, name: str, workdir: str, submission_args: dict = None, *args, **kwargs):
        """
        Initialize a MockScheduler instance.

        Args:
            name (str): Human-readable label for this scheduler.
            workdir (str): Working directory (local filesystem path or S3 URI).
            submission_args (dict, optional): Default submission arguments,
                can be overridden in submit method. Defaults to None.
        """
        self.jobs = {}
        super().__init__(name, workdir, submission_args)
        self.workdir = workdir
        self.submit = Mock(side_effect=self._real_submit)

    def _real_submit(
        self,
        pipeline_name: str,
        params: dict = None,
        submission_args: dict = None,
        *args,
        **kwargs,
    ) -> str:
        """
        Submit a workflow asynchronously and return the job ID.

        Args:
            pipeline_name (str): Nextflow workflow directory
            params (dict, optional): Dictionary of parameters to pass to the workflow. Defaults to None.
            submission_args (dict, optional): Submission arguments for the scheduler,
                overrides values in self.submission_args. Defaults to None.

        Returns:
            str: Scheduler job ID.
        """

        if params:
            # Validate parameters against workflow schema if available
            schema = self.get_param_schema(pipeline_name)
            if schema:
                validate_params(params, schema)

        job_id = str(uuid.uuid1())
        self.jobs[job_id] = MockJob(
            job_id,
            pipeline_name,
            True,
            "log content",
            os.path.join(self.workdir, pipeline_name),
        )
        return job_id

    def get_status_label(self, job_id: str, created_date_utc: datetime | None = None) -> str:
        """
        Get human-readable job status label.
        Should NOT be used to determine job status.

        Args:
            job_id (str): The job ID.
            created_date_utc (datetime | None, optional): The job creation date in UTC. Defaults to None.

        Returns:
            str: Human-readable job status label.
        """
        job = self.jobs[job_id]
        if job.result is None:
            if created_date_utc:
                duration = format_duration(datetime.now(timezone.utc).replace(tzinfo=None) - created_date_utc)
                return f"Running ({duration})"
            return "Running"
        return "Success" if job.result else "Failed"

    def get_result(self, job_id: str, *args, **kwargs) -> bool | None:
        """
        Get job result: True if successful, False if failed, None if still running.

        Args:
            job_id (str): The job ID.

        Returns:
            bool | None: Job result.
        """
        logger.info(self.jobs[job_id].result)
        return self.jobs[job_id].result

    def get_log(self, job_id: str) -> str | None:
        """
        Get job execution log.

        Args:
            job_id (str): The job ID.

        Returns:
            str | None: Job execution log.
        """
        return self.jobs[job_id].result

    def cancel(self, job_id):
        """
        Cancel job execution.

        Args:
            job_id (str): The job ID.
        """
        self.jobs[job_id].result = False
        self.jobs[job_id].stop_time = datetime.now()

    def get_output_dir(self, job_id: str):
        """
        Get job output path.

        Args:
            job_id (str): The job ID.

        Returns:
            str: Job output path.
        """
        return self.jobs[job_id].output_dir

    def get_job_start_time(self, job_id: str) -> datetime | None:
        """
        Get job start time.

        Args:
            job_id (str): The job ID.

        Returns:
            datetime | None: Job start time.
        """
        logger.info(self.jobs[job_id].start_time)
        return self.jobs[job_id].start_time

    def get_job_stop_time(self, job_id: str) -> datetime | None:
        """
        Get job end time.

        Args:
            job_id (str): The job ID.

        Returns:
            datetime | None: Job end time.
        """
        return self.jobs[job_id].stop_time


def encode(class_to_encode: Any) -> bytes:
    """
    Encode a dataclass to a JSON UTF-8 byte string.

    Args:
        class_to_encode (Any): The dataclass to encode.

    Returns:
        bytes: The encoded JSON byte string.
    """
    return json.dumps(asdict(class_to_encode)).encode("utf-8")


class MockS3Object:
    """Mock S3 Object Class"""

    def __init__(self, content: bytes) -> None:
        """
        Initialize a MockS3Object instance.

        Args:
            content (bytes): The content of the S3 object.
        """
        self.content = content

    def read(self) -> bytes:
        """
        Read the content of the S3 object.

        Returns:
            bytes: The content of the S3 object.
        """
        return self.content


class MockClient:
    """Mock AWS S3 Client"""

    def __init__(self, service_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a MockClient instance.

        Args:
            service_name (str): The name of the AWS service.
        """
        self.service_name = service_name
        self.storage: Dict[str, Any] = {}

    def assume_role(self, *args: Any, **kwargs: Any) -> Dict[str, Dict[str, Any]]:
        """
        Mock the assume_role method.

        Returns:
            Dict[str, Dict[str, Any]]: Mocked credentials.
        """
        return {
            "Credentials": {
                "AccessKeyId": "fake_access_key",
                "SecretAccessKey": "fake_secret_key",
                "SessionToken": "fake_session_token",
                "Expiration": datetime.now() + timedelta(hours=5),
            }
        }

    def get_object(self, Bucket: Any, Key: str, *args: Any, **kwargs: Any) -> Dict[str, MockS3Object]:
        """
        Mock the get_object method.

        Args:
            Bucket (Any): The S3 bucket object (not used here).
            Key (str): Path to the object in AWS S3.

        Returns:
            Dict[str, MockS3Object]: Mocked S3 object.
        """
        if Key in self.storage:
            return {"Body": MockS3Object(encode(self.storage[Key]))}

    def put_object(self, Body: Any, Bucket: Any, Key: str, *args: Any, **kwargs: Any) -> None:
        """
        Mock the put_object method, storing the object in self.storage.

        Args:
            Body (Any): The object body to store.
            Bucket (Any): The S3 bucket object (not used here).
            Key (str): Path to the object in AWS S3.
        """
        self.storage[Key] = Body

    def list_objects_v2(self, Bucket: Any, Prefix: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        List all objects in the specified S3 directory.

        Args:
            Bucket (Any): The S3 bucket object (not used here).
            Prefix (str): Path to the directory in AWS S3.

        Returns:
            Dict[str, Any]: Mocked directory contents.
        """
        return {}

    def head_object(self, *args: Any, **kwargs: Any) -> Dict[str, int]:
        """
        Mock the head_object method.

        Returns:
            Dict[str, int]: Mocked content length.
        """
        return {"ContentLength": 12345}


class MockSession:
    """Mock boto3.session.Session class"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a MockSession instance.
        """
        self.clients: Dict[str, MockClient] = {}

    def client(self, service: str, *args: Any, **kwargs: Any) -> MockClient:
        """
        Return a mocked client for the specified service.

        Args:
            service (str): The name of the AWS service.

        Returns:
            MockClient: The mocked client instance.
        """
        if service not in self.clients:
            self.clients[service] = MockClient(service)
        return self.clients[service]


def mock_create_client(instance: Any, service_name: str, *args: Any, **kwargs: Any) -> MockClient:
    """
    Create a mocked client instance.

    Args:
        instance (Any): The mocked instance.
        service_name (str): The name of the AWS service.

    Returns:
        MockClient: The mocked client instance.
    """
    return MockClient(service_name)
