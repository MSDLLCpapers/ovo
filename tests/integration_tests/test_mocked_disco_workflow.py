from ovo import db, design_logic, storage
from ovo.core.database import models_disco
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY, create_test_project_data
import pytest


@pytest.fixture(scope="session")
def project_data():
    """Create one project, project_round, and pool for the entire test run."""
    return create_test_project_data(prefix="OVO DISCO")


def test_mocked_disco(project_data):
    project, project_round, custom_pool = project_data

    workflow = models_disco.DiscoWorkflow(
        disco_params=models_disco.DiscoParams(
            input_json_path=storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/disco_ADP_100.json"),
            experiment="designable",
            effort="fast",
            num_designs=1,
        )
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        workflow=workflow,
        pool_name="DISCO mocked ADP 100",
        pool_description="Mocked DISCO test with ADP ligand",
        scheduler_key=TEST_SCHEDULER_KEY,
        round_id=project_round.id,
        submission_args=dict(stub=True),
    )

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    assert len(jobs) == 1

    pool = design_logic.process_results(design_job)

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 1

    designs = db.Design.select(pool_id=pool.id)
    design = designs[0]
    assert design.spec.chains[0].chain_ids == ["A"]
    assert len(design.spec.chains[0].sequence) == 100

    design_ids = [d.id for d in designs]

    # DISCO-specific descriptors
    length = db.select_descriptor_values("disco|sequence|length", design_ids)
    assert len(length.dropna()) == 1
    assert float(length.dropna().iloc[0]) == 100

    confidence = db.select_descriptor_values("disco|ligandmpnn|overall_confidence", design_ids)
    assert len(confidence.dropna()) == 1

    ligand_confidence = db.select_descriptor_values("disco|ligandmpnn|ligand_confidence", design_ids)
    assert len(ligand_confidence.dropna()) == 1

    # Boltz refolding descriptors
    boltz_rmsd = db.select_descriptor_values("refolding|boltz_primary|design_rmsd", design_ids)
    assert len(boltz_rmsd.dropna()) == 1
    assert float(boltz_rmsd.dropna().iloc[0]) < 2.0

    boltz_plddt = db.select_descriptor_values("refolding|boltz_primary|complex_plddt", design_ids)
    assert len(boltz_plddt.dropna()) == 1
    assert float(boltz_plddt.dropna().iloc[0]) > 0.7
