"""Utility functions for plugin testing"""

import os
import subprocess
from pathlib import Path

import pytest


def install_plugin(plugin_dir: Path, venv_dir: Path):
    """Install plugin into existing venv"""
    subprocess.run(
        ["uv", "pip", "install", "-e", str(plugin_dir)],
        env={**os.environ, "VIRTUAL_ENV": str(venv_dir)},
        check=True,
        capture_output=True,
    )


def run_ovo_init_plugin(working_dir: Path, inputs: list[str]) -> Path:
    """Run 'ovo init plugin' and return plugin directory"""
    result = subprocess.run(
        ["ovo", "init", "plugin"],
        cwd=str(working_dir),
        input="\n".join(inputs) + "\n",
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        pytest.fail(f"ovo init plugin failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

    # Extract module name (first input)
    return working_dir / inputs[0]


def verify_plugin_registration(python_path: Path, test_code: str):
    """Run verification code in isolated venv and fail test if it doesn't pass"""
    result = subprocess.run([str(python_path), "-c", test_code], capture_output=True, text=True)

    if result.returncode != 0:
        pytest.fail(f"Plugin registration verification failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
