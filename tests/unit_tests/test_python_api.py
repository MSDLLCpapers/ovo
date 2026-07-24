import pytest
from jsonschema import ValidationError

from ovo import db
from ovo.core.database import Project, Design
from ovo.core.scheduler import Scheduler


def test_create_project():
    """Test creating a project."""
    project = db.Project(name="Unique Test Project Name", author="test_user", public=False)
    db.save(project)
    assert db.Project.get(name="Unique Test Project Name").id == project.id
    assert db.Project.count(name="Unique Test Project Name") == 1
    assert db.Project.select(name="Unique Test Project Name")[0].id == project.id
    assert db.count(Project) == db.Project.count()
    assert db.count(Design) == db.Design.count()


def test_schedule_valid_params(mock_scheduler: Scheduler):
    job_id = mock_scheduler.submit(
        "rfdiffusion-backbone",
        params=dict(
            num_designs=1,
            contig="A30-40/10/A50-60",
            input_pdb="tests/resources/examples/inputs/5ELI_A.pdb",
            run_parameters="diffuser.T=1",
        ),
    )
    assert mock_scheduler.get_output_dir(job_id) is not None


def test_schedule_invalid_params(nextflow_scheduler):
    with pytest.raises(ValidationError):
        nextflow_scheduler.submit(
            "rfdiffusion-backbone",
            params=dict(
                num_designs=1,
                # contig="A30-40/10/A50-60",
                input_pdb="tests/resources/examples/inputs/5ELI_A.pdb",
                run_parameters="diffuser.T=1",
            ),
        )
    with pytest.raises(ValidationError):
        nextflow_scheduler.submit(
            "rfdiffusion-backbone",
            params=dict(
                num_designs=1,
                contig="A30-40/10/A50-60",
                input_pdb="tests/resources/examples/inputs/5ELI_A.pdb",
                run_parameters="diffuser.T=1",
                INVALID_PARAM="SOME_VALUE",
            ),
        )

    try:
        nextflow_scheduler.submit(
            "rfdiffusion-backbone",
            params=dict(
                num_designs="INVALID",
                contig="A30-40/10/A50-60",
                input_pdb="tests/resources/examples/inputs/5ELI_A.pdb",
                run_parameters="diffuser.T=1",
            ),
        )
        assert False, "Expected ValidationError"
    except ValidationError as e:
        assert e.message == "'INVALID' is not of type 'integer'"
        assert ".".join(e.path) == "num_designs"


def test_design_id():
    design = Design(id="ovo_foo_123", pool_id="foo")
    with pytest.raises(ValueError):
        design = Design(id="foo", pool_id="bar")
