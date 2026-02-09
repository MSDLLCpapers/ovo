import os
import pytest
from ovo.core.utils.tests import create_test_project_data


@pytest.fixture(scope="session", autouse=True)
def check_unit_test_mode():
    if os.environ.get("OVO_UNIT_TEST") == "1":
        raise RuntimeError("Please run unit tests and workflow tests separately.")


@pytest.fixture(scope="session")
def project_data():
    """Create one project, project_round, and pool for the entire test run."""
    return create_test_project_data()
