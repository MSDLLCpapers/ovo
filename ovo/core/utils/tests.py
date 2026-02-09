import datetime
import os
import shutil

from ovo import schedulers, NextflowScheduler, config
from ovo.core.utils.resources import RESOURCES_DIR

# Scheduler key to use for tests, must be set in environment
TEST_SCHEDULER_KEY = os.getenv("OVO_TEST_SCHEDULER", config.default_scheduler)
# Test output results will be symlinked to this directory
TEST_OUTPUT_DIR = os.getenv("OVO_TEST_OUTPUT_DIR", os.path.join(config.dir, "workdir", "test-results"))
# Name of testing project in the DB
TEST_PROJECT_NAME = "OVO Tests"


def get_test_scheduler() -> NextflowScheduler:
    if TEST_SCHEDULER_KEY not in schedulers:
        raise ValueError(
            f"Expected OVO_TEST_SCHEDULER to be one of {list(schedulers.keys())}, but got '{TEST_SCHEDULER_KEY}'"
        )
    return schedulers[TEST_SCHEDULER_KEY]


def prepare_test_output_dir(script_path: str) -> str:
    """Create test directory like test-results/workflows/rfdiffusion-end-to-end/test_scaffold_hairpin

    Removes existing directory if it exists.
    """
    path = script_path.removesuffix(".py")
    if "pipelines/" in path:
        path = path.split("pipelines/", 1)[-1]
        path = path.replace("/tests/", "/")
    else:
        path = os.path.basename(path)
    if test_name := os.getenv("PYTEST_CURRENT_TEST"):
        # append test function name to path
        test_name = test_name.split("::")[-1].split()[0]
        path = os.path.join(path, test_name)
    output_dir = os.path.join(TEST_OUTPUT_DIR, path)
    shutil.rmtree(output_dir, ignore_errors=True)
    return output_dir


def assert_similar_sequence(a: str, b: str, min_identity: float):
    """Assert that two sequences are similar enough."""
    if len(a) != len(b):
        raise AssertionError(f"Sequences have different lengths: {len(a)} != {len(b)}, {a} vs {b}")
    assert isinstance(min_identity, float) and 0 <= min_identity <= 1
    matches = sum(1 for x, y in zip(a, b) if x == y)
    identity = matches / len(a)
    if identity < min_identity:
        diff = f"{a}\n{b}\n" + "".join("^" if x != y else " " for x, y in zip(a, b))
        raise AssertionError(f"Sequences are not similar enough: {identity:.2f} < {min_identity:.2f}:\n{diff}")


def create_test_project_data(prefix="OVO"):
    from ovo import db, storage, Design, Pool

    round_name = prefix + " " + datetime.datetime.now().strftime("%a %d %b %Y")

    if not db.Project.count(name=TEST_PROJECT_NAME):
        project = db.Project(name=TEST_PROJECT_NAME, author="test", public=True)
        db.save(project)
    else:
        project = db.Project.get(name=TEST_PROJECT_NAME)

    if db.Round.count(name=round_name, project_id=project.id):
        # Clear round if exists
        project_round = db.Round.get(name=round_name, project_id=project.id)
        pools = db.Pool.select(round_id=project_round.id)
        designs = db.Design.select(pool_id__in=[p.id for p in pools])
        db.DescriptorValue.remove(design_id__in=[d.id for d in designs])
        db.Design.remove(pool_id__in=[p.id for p in pools])
        db.DesignJob.remove(id__in=[p.design_job_id for p in pools if p.design_job_id])
        db.Pool.remove(round_id=project_round.id)
        db.Round.remove(id=project_round.id)
        # note that db.DescriptorJob is not cleared because it's associated to project

    project_round = db.Round(
        name=round_name,
        project_id=project.id,
        author="test",
    )
    db.save(project_round)

    # Create a pool
    pool = Pool(
        id=Pool.generate_id(),
        round_id=project_round.id,
        name="Custom Upload",
        author="test",
    )
    db.save(pool)

    # Create a test design
    test_design = Design.from_pdb_file(
        storage=storage,
        filename="5ELI_A.pdb",
        pdb_str=(RESOURCES_DIR / "examples/inputs/5ELI_A.pdb").read_text(),
        chains=["A"],
        project_id=project.id,
        pool_id=pool.id,
    )
    db.save(test_design)
    assert len(test_design.spec.chains) == 1
    assert os.path.exists(os.path.join(storage.storage_root, test_design.structure_path))

    return project, project_round, pool
