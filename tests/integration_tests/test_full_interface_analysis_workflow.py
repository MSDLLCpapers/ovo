import pytest

from ovo import db
from ovo.core.database import Design
from ovo.core.database.descriptors_rfdiffusion import (
    FASTRELAX_STRUCTURE_PATH,
    BIOTITE_INTERFACE_TARGET_RESIDUES_AA,
    BIOTITE_INTERFACE_BINDER_RESIDUES_AA,
    PYROSETTA_INTERFACE_TARGET_RESIDUES_AA,
    PYROSETTA_INTERFACE_BINDER_RESIDUES_AA,
)
from ovo.core.database.models import DescriptorValue
from ovo.core.database.models_interface_analysis import (
    BiotiteInterfaceAnalysisWorkflow,
    PyRosettaInterfaceAnalysisWorkflow,
)
from ovo.core.logic import descriptor_logic
from ovo.core.utils.tests import TEST_SCHEDULER_KEY, create_test_project_data


@pytest.fixture(scope="module")
def interface_project_data():
    return create_test_project_data(test_input_filename="examples/inputs/ovo_buv_0789_cycle02_trimmed.pdb")


@pytest.fixture(scope="module")
def single_chain_project_data():
    return create_test_project_data(test_input_filename="examples/inputs/5ELI_A.pdb")


def test_biotite_interface_analysis(interface_project_data):
    project, project_round, custom_pool = interface_project_data

    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    workflow = BiotiteInterfaceAnalysisWorkflow(
        chains=["A"],
        target_chains=["B"],
        design_ids=design_ids,
    )
    workflow.validate()

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=workflow, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    values = descriptor_logic.get_wide_descriptor_table(design_ids=design_ids)
    print(values.to_dict(orient="records"))
    first_value = values.iloc[0]

    assert first_value["N hydrogen bonds (biotite)"] >= 0
    assert first_value["N salt bridges (biotite)"] >= 0

    sc_target = db.select(
        DescriptorValue, design_id__in=design_ids, descriptor_key=BIOTITE_INTERFACE_TARGET_RESIDUES_AA.key
    )
    sc_binder = db.select(
        DescriptorValue, design_id__in=design_ids, descriptor_key=BIOTITE_INTERFACE_BINDER_RESIDUES_AA.key
    )
    assert sc_target and sc_binder
    all_target_residues = set(r for v in sc_target for r in (v.value.split(",") if v.value else []))
    all_binder_residues = set(r for v in sc_binder for r in (v.value.split(",") if v.value else []))
    assert "B64" in all_target_residues, f"PHE64 expected on target interface, got: {all_target_residues}"
    assert "A15" in all_binder_residues, f"PHE15 expected on binder interface, got: {all_binder_residues}"
    assert "B63" not in all_target_residues, f"LEU63 expected off target interface, got: {all_target_residues}"
    assert "A9" not in all_binder_residues, f"GLU9 expected off binder interface, got: {all_binder_residues}"


def test_pyrosetta_interface_analysis(interface_project_data):
    project, project_round, custom_pool = interface_project_data

    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    workflow = PyRosettaInterfaceAnalysisWorkflow(
        chains=["A"],
        target_chains=["B"],
        design_ids=design_ids,
        relax=False,
    )
    workflow.validate()

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=workflow, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    values = descriptor_logic.get_wide_descriptor_table(design_ids=design_ids)
    print(values.to_dict(orient="records"))
    first_value = values.iloc[0]

    assert first_value["Rosetta ddG"] < 0
    assert 0 <= first_value["Interface Shape Complementarity"] <= 1

    sc_target = db.select(
        DescriptorValue, design_id__in=design_ids, descriptor_key=PYROSETTA_INTERFACE_TARGET_RESIDUES_AA.key
    )
    sc_binder = db.select(
        DescriptorValue, design_id__in=design_ids, descriptor_key=PYROSETTA_INTERFACE_BINDER_RESIDUES_AA.key
    )
    assert sc_target and sc_binder
    all_target_residues = set(r for v in sc_target for r in (v.value.split(",") if v.value else []))
    all_binder_residues = set(r for v in sc_binder for r in (v.value.split(",") if v.value else []))
    assert "B64" in all_target_residues, f"PHE64 expected on target interface, got: {all_target_residues}"
    assert "A15" in all_binder_residues, f"PHE15 expected on binder interface, got: {all_binder_residues}"
    assert "B63" not in all_target_residues, f"LEU63 expected off target interface, got: {all_target_residues}"
    assert "A9" not in all_binder_residues, f"GLU9 expected off binder interface, got: {all_binder_residues}"


def test_pyrosetta_interface_analysis_with_relax(interface_project_data):
    project, project_round, custom_pool = interface_project_data

    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    workflow = PyRosettaInterfaceAnalysisWorkflow(
        chains=["A"],
        target_chains=["B"],
        design_ids=design_ids,
        relax=True,
    )
    workflow.validate()

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=workflow, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    relaxed_pdbs = db.select(
        DescriptorValue,
        design_id__in=design_ids,
        descriptor_key=FASTRELAX_STRUCTURE_PATH.key,
    )
    assert len(relaxed_pdbs) == len(design_ids)
    assert all(v.value and v.value.endswith(".pdb") for v in relaxed_pdbs)


def test_biotite_interface_analysis_fails_on_single_chain(single_chain_project_data):
    """Biotite interface analysis should fail when there is only one chain (no interface to analyze)."""
    project, project_round, custom_pool = single_chain_project_data

    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    workflow = BiotiteInterfaceAnalysisWorkflow(
        chains=["A"],
        target_chains=["B"],
        design_ids=design_ids,
    )
    workflow.validate()

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=workflow, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    with pytest.raises(ValueError, match="failed"):
        descriptor_logic.process_results(descriptor_job)
