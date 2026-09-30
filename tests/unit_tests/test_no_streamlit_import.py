import subprocess
import sys
import textwrap

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

# Script that imports the given modules and reports where streamlit gets imported from, if anywhere.
# Run in a subprocess because the unit test suite itself imports streamlit.
CHECK_SCRIPT = textwrap.dedent("""
    import builtins
    import importlib
    import sys
    import traceback

    modules = sys.argv[1:]
    real_import = builtins.__import__
    culprits = []

    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.split(".")[0] == "streamlit" and "streamlit" not in sys.modules and not culprits:
            culprits.append("".join(traceback.format_stack()))
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = traced_import
    try:
        for module in modules:
            importlib.import_module(module)
            if "streamlit" in sys.modules:
                # Once streamlit is loaded, later modules can no longer be checked
                break
    finally:
        builtins.__import__ = real_import
        last_module = module

    print("OVO_IMPORT_CHECK_START")
    print("last module imported:", last_module)
    print("streamlit imported:", "streamlit" in sys.modules)
    for culprit in culprits:
        print(culprit)
""")


def test_importing_ovo_does_not_import_streamlit():
    """OVO must stay usable as a library, without pulling in the streamlit runtime.

    Modules under ovo.app (and anything else importing streamlit) must therefore only be
    imported lazily, inside the functions that need them.
    """
    result = subprocess.run(
        [sys.executable, "-c", CHECK_SCRIPT, *LIBRARY_MODULES],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"importing {LIBRARY_MODULES} failed:\n{result.stdout}\n{result.stderr}"
    # Ignore any output plugins print while loading
    _, _, report = result.stdout.partition("OVO_IMPORT_CHECK_START\n")
    assert "streamlit imported: False" in report, (
        f"Importing one of {LIBRARY_MODULES} imported streamlit, first imported from:\n{report}"
    )
