"""Guard what importing OVO as a library pulls in, and how long it takes.

Every one of these costs is paid by every ``ovo`` command and every notebook that imports ovo, so
the modules below have to stay out of the import graph and be imported inside the functions that
need them.
"""

import re
import subprocess
import sys
import textwrap

import pytest

# Modules that must stay importable without the streamlit runtime: the top-level package,
# the CLI entrypoint, the database models and the logic modules used by both the CLI and the app.
LIBRARY_MODULES = [
    "ovo",
    "ovo.cli.main",
    "ovo.core.database",
    "ovo.core.auth",
    "ovo.core.logic.design_logic",
    "ovo.core.logic.job_logic",
    "ovo.core.logic.descriptor_logic",
    "ovo.core.logic.filtering_logic",
    "ovo.core.logic.proteinqc_logic",
]

# Packages that none of the modules above may import, by the reason they are kept out.
# Matched on the root package name, so "mypy_boto3" covers mypy_boto3_s3 and its siblings.
FORBIDDEN_PACKAGES = {
    "streamlit": "the app runtime, which OVO must stay usable as a library without",
    "scipy": "~0.8s, needed by a handful of geometry helpers in ovo.core.utils.pdb only",
    "mypy_boto3": "~0.2s of type stub packages, which are needed for annotations only",
}

# How long importing all of LIBRARY_MODULES may take, including interpreter startup and plugins.
# Generous on purpose: this catches a new eager dependency, not a small regression.
MAX_IMPORT_SECONDS = 5.0

# Imports the given modules in a subprocess - the test suite itself imports streamlit - and reports
# which forbidden package got imported from where, plus how long the imports took.
CHECK_SCRIPT = textwrap.dedent("""
    import builtins
    import importlib
    import sys
    import time
    import traceback

    forbidden = sys.argv[1].split(",")
    modules = sys.argv[2:]
    real_import = builtins.__import__
    culprits = {}

    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".")[0]
        for package in forbidden:
            if root.startswith(package) and package not in culprits and root not in sys.modules:
                culprits[package] = "".join(traceback.format_stack())
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = traced_import
    started = time.perf_counter()
    try:
        for module in modules:
            importlib.import_module(module)
    finally:
        elapsed = time.perf_counter() - started
        builtins.__import__ = real_import

    print("OVO_IMPORT_CHECK_START")
    print("elapsed:", round(elapsed, 2))
    for package in forbidden:
        print(f"imported {package}:", any(m.split(".")[0].startswith(package) for m in sys.modules))
    for package, culprit in culprits.items():
        print(f"--- first import of {package} ---")
        print(culprit)
""")


@pytest.fixture(scope="module")
def import_report() -> str:
    """Import every library module in a fresh interpreter once, and return what it reported."""
    result = subprocess.run(
        [sys.executable, "-c", CHECK_SCRIPT, ",".join(FORBIDDEN_PACKAGES), *LIBRARY_MODULES],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"importing {LIBRARY_MODULES} failed:\n{result.stdout}\n{result.stderr}"
    # Ignore any output plugins print while loading
    _, _, report = result.stdout.partition("OVO_IMPORT_CHECK_START\n")
    assert report, f"check script printed no report:\n{result.stdout}\n{result.stderr}"
    return report


@pytest.mark.parametrize("package", list(FORBIDDEN_PACKAGES))
def test_importing_ovo_does_not_import(package: str, import_report: str):
    """Importing OVO as a library must not pull in the app runtime or a heavy optional dependency."""
    assert f"imported {package}: False" in import_report, (
        f"Importing one of {LIBRARY_MODULES} imported {package} ({FORBIDDEN_PACKAGES[package]}). "
        f"Import it inside the function that needs it instead. Report:\n{import_report}"
    )


def test_importing_ovo_is_not_slow(import_report: str):
    """Importing OVO must stay quick: every ovo command and notebook pays for it."""
    match = re.search(r"^elapsed: ([\d.]+)$", import_report, re.MULTILINE)
    assert match, f"check script reported no timing:\n{import_report}"
    elapsed = float(match.group(1))
    assert elapsed < MAX_IMPORT_SECONDS, (
        f"Importing {LIBRARY_MODULES} took {elapsed:.2f}s, over the {MAX_IMPORT_SECONDS}s budget. "
        f"Run `python -X importtime -c 'import ovo'` to see what was added."
    )
