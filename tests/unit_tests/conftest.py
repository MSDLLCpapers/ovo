import os
import shutil
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_HOME_DIR = os.path.join(REPO_ROOT, "test-results", "unit_tests")
os.environ["USER"] = "test_user"
os.environ["OVO_HOME"] = ""

# Remove test-results directory if it exists
if os.path.exists(TEST_HOME_DIR):
    shutil.rmtree(TEST_HOME_DIR)

# Initialize OVO config.yml in test-results directory
subprocess.run(["ovo", "init", "home", TEST_HOME_DIR, "-y", "--no-env"])
assert os.path.exists(os.path.join(TEST_HOME_DIR, "config.yml")), "OVO init home failed"
os.environ["OVO_HOME"] = TEST_HOME_DIR
os.environ["NO_VERIFY_SSL"] = "1"

import pytest
from pytest_mock import MockerFixture
from streamlit.testing.v1 import AppTest
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.mocking import MockClient, MockScheduler, MockSession, mock_create_client
from ovo import schedulers, default_scheduler
from ovo.core.scheduler import NextflowScheduler


@pytest.fixture
def test_wrapper(request: pytest.FixtureRequest) -> AppTest:
    """
    Pytest fixture to wrap tests with additional logging and error handling.

    Args:
        request (pytest.FixtureRequest): The pytest fixture request object.

    Yields:
        AppTest: The AppTest instance created from the test file.
    """
    at = AppTest.from_file(os.path.join(REPO_ROOT, "ovo/run_app.py"))
    at.switch_page(request.param)
    at.run(timeout=10)
    try:
        yield at
    except Exception as e:
        print("An error occurred during test.")
        print(at)
        asserts.assert_no_error_on_exception(at, f"{type(e).__name__}: {e}")
        raise e


@pytest.fixture(autouse=True)
def mock_scheduler(monkeypatch: pytest.MonkeyPatch) -> MockScheduler:
    """
    Pytest fixture to mock the scheduler configuration.

    Args:
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
    """
    import ovo

    mocked_scheduler = MockScheduler(name="Mocked scheduler", workdir=os.path.join(TEST_HOME_DIR, "workdir"))
    # mock all schedulers with the single mocked scheduler
    for scheduler_key in schedulers:
        schedulers[scheduler_key] = mocked_scheduler
    ovo.local_scheduler = mocked_scheduler
    return mocked_scheduler


@pytest.fixture
def nextflow_scheduler() -> NextflowScheduler:
    return default_scheduler


@pytest.fixture(scope="function", autouse=True)
def auto_mocks(mocker: MockerFixture) -> None:
    """
    Pytest fixture to mock AWS connections and other functions.

    Args:
        mocker (MockerFixture): The pytest mocker fixture.
    """
    mocker.patch("boto3.client", MockClient)
    mocker.patch("botocore.client.ClientCreator.create_client", mock_create_client)
    mocker.patch("mypy_boto3_s3.client.S3Client", MockClient)
    mocker.patch("boto3.session.Session", MockSession)


@pytest.fixture()
def ovo_resources_path():
    return os.path.join(os.path.dirname(__file__), "..", "..", "ovo", "resources")


@pytest.fixture()
def example_pdb_path(ovo_resources_path):
    return os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb")
