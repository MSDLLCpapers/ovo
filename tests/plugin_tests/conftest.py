"""Fixtures for plugin tests"""

import os
import subprocess
import sys
from pathlib import Path
import shutil
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_HOME_DIR = os.path.join(REPO_ROOT, "test-results", "plugin_tests")
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


@pytest.fixture
def ovo_venv(tmp_path):
    """Create a fresh venv with local OVO installed for each test

    Returns:
        tuple: (venv_dir, python_path)
    """
    venv_dir = tmp_path / "venv"

    # Create venv with uv
    subprocess.run(["uv", "venv", str(venv_dir)], check=True, capture_output=True)

    # Get python path in venv
    python_path = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    # Install local OVO
    ovo_root = Path(__file__).parent.parent.parent
    subprocess.run(
        ["uv", "pip", "install", "-e", str(ovo_root)],
        env={**os.environ, "VIRTUAL_ENV": str(venv_dir)},
        check=True,
        capture_output=True,
    )

    return venv_dir, python_path
