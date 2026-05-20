import subprocess
from tests.unit_tests.conftest import TEST_HOME_DIR


def test_cli_scheduler_run_params():
    p = subprocess.run(
        ["ovo", "scheduler", "run", "rfdiffusion-end-to-end", "/tmp/foo", "--foo", "bar"],
        capture_output=True,
        text=True,
    )
    err = p.stderr.strip()
    print("Output:\n=====", err)
    print("=======")
    assert TEST_HOME_DIR in "".join(err.split()), "Test should use TEST_HOME_DIR as OVO home dir"
    assert "--rfdiffusion_input_pdb: " in err, "Test should print help params"
    assert "Input parameters are invalid: 'design_type' is a required property" in err, (
        "Test should print missing params"
    )
