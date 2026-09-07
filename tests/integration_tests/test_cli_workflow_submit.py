import re

from typer.testing import CliRunner

from ovo import db
from ovo.core.database.models import DesignJob, Pool
from ovo.core.database import descriptors_refolding, descriptors_rfdiffusion
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY
from ovo.cli.workflow_cli import app

runner = CliRunner()

EXAMPLE_CONFIG = str(RESOURCES_DIR / "examples/inputs/5ELI_A_hairpin_scaffold.yaml")


def test_cli_workflow_names():
    """Test listing available workflow type names."""
    result = runner.invoke(app, ["names"])
    assert result.exit_code == 0, f"CLI names failed: {result.output}"
    assert "RFdiffusion scaffold design" in result.output


def test_cli_workflow_template():
    """Test generating a YAML config template."""
    result = runner.invoke(app, ["template", "--name", "RFdiffusion scaffold design"])
    assert result.exit_code == 0, f"CLI template failed: {result.output}"
    assert "submissions:" in result.output
    assert "name: RFdiffusion scaffold design" in result.output


def test_cli_workflow_submit(project_data):
    project, project_round, custom_pool = project_data

    result = runner.invoke(
        app,
        [
            "submit",
            EXAMPLE_CONFIG,
            "--project",
            project.name,
            "--round",
            project_round.name,
            "--scheduler",
            TEST_SCHEDULER_KEY,
            "--yes",
        ],
    )
    assert result.exit_code == 0, f"CLI submit failed: {result.output}"
    assert "submitted successfully" in result.output

    # Extract job ID (UUID) from output
    uuid_match = re.search(
        r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", result.output, re.MULTILINE
    )
    job_id = uuid_match.group(1) if uuid_match else None

    assert job_id is not None, f"Could not find job ID in output: {result.output}"

    # Verify job was created in DB
    design_job = db.get(DesignJob, id=job_id)
    assert design_job is not None
    assert design_job.workflow.name == "RFdiffusion scaffold design"

    pool = db.get(Pool, design_job_id=design_job.id)
    assert pool is not None
    assert pool.name == "CLI hairpin scaffold test"

    # Process results via CLI
    process_result = runner.invoke(app, ["process", job_id])
    assert process_result.exit_code == 0, f"CLI process failed: {process_result.output}"
    assert "processed" in process_result.output

    pool = db.get(Pool, design_job_id=design_job.id)
    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 2

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]

    # Verify RFdiffusion descriptors
    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    # Verify refolding descriptors
    af2_plddt = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_PLDDT.key, design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    # Test status command — should show processed after CLI process
    status_result = runner.invoke(app, ["status", job_id])
    assert status_result.exit_code == 0
    assert "Done" in status_result.output

    # Test log command
    log_result = runner.invoke(app, ["log", job_id])
    assert log_result.exit_code == 0

    # Test tasks command
    tasks_result = runner.invoke(app, ["tasks", job_id])
    assert tasks_result.exit_code == 0, f"CLI tasks failed: {tasks_result.output}"

    # Test list command with project/round filter
    list_result = runner.invoke(app, ["list", "--project", project.name, "--round", project_round.name, "--no-update"])
    assert list_result.exit_code == 0, f"CLI list failed: {list_result.output}"
    assert "CLI hairpin scaffold test" in list_result.output

    # Test list command with pool filter
    list_pool_result = runner.invoke(app, ["list", "--pool", "CLI hairpin scaffold test", "--no-update"])
    assert list_pool_result.exit_code == 0, f"CLI list --pool failed: {list_pool_result.output}"
    assert job_id in list_pool_result.output
