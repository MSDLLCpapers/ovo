"""Fixtures for plugin tests"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


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
