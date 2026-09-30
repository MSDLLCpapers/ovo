import os
import subprocess

import pytest

from ovo.cli.scheduler_cli import prepare_local_path_params
from tests.unit_tests.conftest import TEST_HOME_DIR


@pytest.fixture
def designs_dir(tmp_path):
    designs_dir = tmp_path / "designs"
    designs_dir.mkdir()
    for i in range(3):
        (designs_dir / f"design{i}.pdb").write_text(f"ATOM {i}\n")
    return designs_dir


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


def test_cli_prepare_local_path_params(tmp_path, designs_dir):
    """Local files and directories should be uploaded to the workdir and replaced by their paths"""
    workdir = str(tmp_path / "workdir")
    native_pdb = tmp_path / "native.pdb"
    native_pdb.write_text("ATOM\n")

    params = prepare_local_path_params(
        dict(pdb_dir=f"{designs_dir}/", native_pdb=str(native_pdb), relax=True, binder_chain="A"),
        workdir=workdir,
    )

    assert params["relax"] is True
    assert params["binder_chain"] == "A"
    # Directory is uploaded as a directory, single file as a file
    assert params["pdb_dir"].startswith(os.path.join(workdir, "inputs")) and params["pdb_dir"].endswith("/")
    assert sorted(os.listdir(params["pdb_dir"])) == ["design0.pdb", "design1.pdb", "design2.pdb"]
    assert params["native_pdb"].endswith("/native.pdb")
    assert os.path.exists(params["native_pdb"])


def test_cli_prepare_local_path_params_reuses_uploaded_directory(tmp_path, designs_dir, capsys):
    """A directory that was already uploaded should not be uploaded again, unless it is incomplete"""
    workdir = str(tmp_path / "workdir")

    params = prepare_local_path_params(dict(pdb_dir=f"{designs_dir}/"), workdir=workdir)
    uploaded_dir = params["pdb_dir"]

    params = prepare_local_path_params(dict(pdb_dir=f"{designs_dir}/"), workdir=workdir)
    assert params["pdb_dir"] == uploaded_dir
    # Join the console output, rich wraps the printed lines
    assert "werealreadyuploaded" in "".join(capsys.readouterr().err.split())

    # An interrupted upload should be completed instead of reused
    os.remove(os.path.join(uploaded_dir, "design1.pdb"))
    params = prepare_local_path_params(dict(pdb_dir=f"{designs_dir}/"), workdir=workdir)
    assert params["pdb_dir"] == uploaded_dir
    assert sorted(os.listdir(uploaded_dir)) == ["design0.pdb", "design1.pdb", "design2.pdb"]


def test_cli_scheduler_coerce_param_types():
    """Numbers and booleans given on the command line should be converted to JSON types"""
    from ovo.core.utils.formatting import coerce_param_types

    params = coerce_param_types(
        dict(
            batch_size="60",
            cutoff="-1.5",
            relax="false",
            cyclic="True",
            flag=True,
            binder_chain="A",
            # Values that only look like numbers should be kept as strings
            version="1.1.1",
            padded_id="007",
            scientific="1e5",
        )
    )

    assert params == dict(
        batch_size=60,
        cutoff=-1.5,
        relax=False,
        cyclic=True,
        flag=True,
        binder_chain="A",
        version="1.1.1",
        padded_id="007",
        scientific="1e5",
    )
