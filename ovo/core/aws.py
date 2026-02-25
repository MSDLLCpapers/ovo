from datetime import datetime
from time import time
import boto3
from botocore.exceptions import ClientError
from mypy_boto3_logs import CloudWatchLogsClient

from mypy_boto3_s3.client import S3Client
from mypy_boto3_omics import OmicsClient


class AWSSessionManager:
    def __init__(self, assume_role: str = None, region_name="us-east-1"):
        self.assume_role = assume_role
        self.region_name = region_name
        self._AWS_CLIENTS = {}
        self._AWS_CLIENTS_EXPIRATION = {}

    @property
    def s3(self) -> S3Client:
        return self.get_client("s3")

    @property
    def omics(self) -> OmicsClient:
        return self.get_client("omics")

    @property
    def logs(self) -> CloudWatchLogsClient:
        return self.get_client("logs")

    def get_client(self, service, refresh_minutes_before_expiration=30):
        expired = (
            service in self._AWS_CLIENTS_EXPIRATION
            and self._AWS_CLIENTS_EXPIRATION[service].timestamp() - time() < 60 * refresh_minutes_before_expiration
        )
        if service not in self._AWS_CLIENTS or expired:
            session, expiration_datetime = self._create_session()
            self._AWS_CLIENTS[service] = session.client(service)
            if expiration_datetime is not None:
                self._AWS_CLIENTS_EXPIRATION[service] = expiration_datetime
        return self._AWS_CLIENTS[service]

    def _create_session(self) -> tuple[boto3.Session, datetime | None]:
        sts_client = boto3.client("sts")

        if self.assume_role is not None:
            assumed_role_object = sts_client.assume_role(RoleArn=self.assume_role, RoleSessionName="OVO")

            # The response contains temporary credentials to the assumed role.
            credentials = assumed_role_object["Credentials"]

            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=self.region_name,
            )
            expiration_datetime = credentials["Expiration"]
        else:
            session = boto3.Session()
            expiration_datetime = None

        return session, expiration_datetime

    def get_account_id(self):
        # Use the STS client to get account information
        sts_client = self.get_client("sts")
        response = sts_client.get_caller_identity()
        return response["Account"]

    def get_latest_workflow_id(self, workflow_name: str):
        limit = 100
        items = self.omics.list_workflows(type="PRIVATE", name=workflow_name, maxResults=limit)["items"]
        if len(items) >= limit:
            # We could add pagination to solve this, at least make sure we raise an error for now
            raise ValueError(f"Too many workflows with name '{workflow_name}' found in AWS (>{limit})")
        if not items:
            raise ValueError(f"HealthOmics workflow with name '{workflow_name}' was not found in AWS")
        latest_workflow = sorted(items, key=lambda x: x["creationTime"], reverse=True)[0]
        return latest_workflow["id"]

    def s3_file_exists(self, s3_uri: str):
        assert s3_uri.startswith("s3://"), f"Invalid S3 URI: {s3_uri}"
        bucket, key = s3_uri[5:].split("/", maxsplit=1)
        try:
            self.s3.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            # Check if the error is "Not Found"
            if e.response["Error"]["Code"] in ("NoSuchKey", "404", 404):
                return False
            else:
                print("S3 ERROR", e, e.response)
                raise e

    def get_s3_bytes(self, s3_uri: str):
        assert s3_uri.startswith("s3://"), f"Invalid S3 URI: {s3_uri}"
        bucket, key = s3_uri[5:].split("/", maxsplit=1)
        response = self.s3.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
