import pytest

from ovo.core.scheduler.healthomics_scheduler import HealthOmicsScheduler


class MockOmics:
    def __init__(self, statuses: list[str]):
        # Statuses returned by consecutive get_run calls
        self.statuses = statuses
        self.started_runs = []

    def start_run(self, **kwargs):
        self.started_runs.append(kwargs)
        return {"id": "4498077"}

    def get_run(self, id: str):
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        return {"status": status, "runOutputUri": f"s3://test-bucket/workdir/output/{id}"}


class MockAWS:
    region_name = "us-east-1"

    def __init__(self, statuses: list[str]):
        self.omics = MockOmics(statuses)

    def get_latest_workflow_id(self, workflow_name: str):
        return "1234567"

    def get_account_id(self):
        return "000000000000"


def get_scheduler(statuses: list[str]) -> HealthOmicsScheduler:
    return HealthOmicsScheduler(
        name="Test HealthOmics",
        workdir="s3://test-bucket/workdir",
        reference_files_dir="unused",
        aws=MockAWS(statuses),
    )


def test_healthomics_submit_adds_aws_params():
    """Params should be passed on together with the AWS params of the scheduler"""
    scheduler = get_scheduler(["RUNNING"])

    job_id = scheduler.submit(
        pipeline_name="pyrosetta-interface-metrics",
        params=dict(pdb_dir="s3://test-bucket/workdir/inputs/ab/cdef/", relax=True, binder_chain="A"),
        submission_args=dict(role_arn="test-role"),
    )
    assert job_id == "4498077"

    started_run = scheduler.aws.omics.started_runs[0]
    assert started_run["roleArn"] == "test-role"
    assert started_run["outputUri"] == "s3://test-bucket/workdir/pyrosetta-interface-metrics/"
    params = started_run["parameters"]
    assert params["pdb_dir"] == "s3://test-bucket/workdir/inputs/ab/cdef/"
    assert params["relax"] is True
    assert params["binder_chain"] == "A"
    assert params["account_id"] == "000000000000"
    assert params["aws_region"] == "us-east-1"
    assert params["workflow_bucket"] == "test-bucket"


def test_healthomics_submit_and_wait_success():
    """The submission is always asynchronous, waiting for the run is done using the job ID"""
    scheduler = get_scheduler(["STARTING", "RUNNING", "COMPLETED"])

    job_id = scheduler.submit(pipeline_name="pyrosetta-interface-metrics", params=dict(pdb_dir="s3://in/"))
    assert job_id == "4498077"
    assert scheduler.wait(job_id, interval=0) is True
    assert scheduler.get_output_dir(job_id) == "s3://test-bucket/workdir/output/4498077/pubdir"


def test_healthomics_submit_and_wait_failed():
    """Waiting for a failed run should return False"""
    scheduler = get_scheduler(["RUNNING", "FAILED"])

    job_id = scheduler.submit(pipeline_name="pyrosetta-interface-metrics", params=dict(pdb_dir="s3://in/"))
    assert scheduler.wait(job_id, interval=0) is False


def test_healthomics_submit_unrecognized_submission_args():
    scheduler = get_scheduler(["RUNNING"])
    with pytest.raises(ValueError, match="Unrecognized HealthOmicsScheduler submission args"):
        scheduler.submit(
            pipeline_name="pyrosetta-interface-metrics",
            params=dict(pdb_dir="s3://in/"),
            submission_args=dict(sync=True),
        )
