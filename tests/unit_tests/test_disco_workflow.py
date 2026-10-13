import pytest

from ovo.core.database.models_disco import DiscoWorkflow, DiscoParams
from ovo.core.logic.design_logic_disco import build_disco_input_json


def _single_job(workflow: DiscoWorkflow) -> dict:
    json_list = build_disco_input_json(workflow)
    assert isinstance(json_list, list) and len(json_list) == 1
    return json_list[0]


def test_build_input_json_ccd():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand="CCD_ATP", sequence_length=100))
    job = _single_job(workflow)
    assert job["name"] == "length_100_ATP"
    assert job["sequences"][0]["proteinChain"]["sequence"] == "-" * 100
    assert job["sequences"][1]["ligand"]["ligand"] == "CCD_ATP"


def test_build_input_json_smiles():
    smiles = "CC(=O)Oc1ccccc1C(=O)O"
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand=smiles, sequence_length=150))
    job = _single_job(workflow)
    assert job["name"] == "length_150_smiles"
    assert len(job["sequences"][0]["proteinChain"]["sequence"]) == 150
    assert job["sequences"][1]["ligand"]["ligand"] == smiles


def test_build_input_json_file_override():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand="FILE_/some/storage/heme_b.sdf", sequence_length=200))
    # Simulate the staged basename reference used at submit time
    job = build_disco_input_json(workflow, ligand_value="FILE_heme_b.sdf")[0]
    assert job["name"] == "length_200_heme_b"
    assert job["sequences"][1]["ligand"]["ligand"] == "FILE_heme_b.sdf"


def test_build_input_json_no_ligand():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand=None, sequence_length=70, input_json_path="x.json"))
    job = _single_job(workflow)
    assert job["name"] == "length_70"
    # No ligand entity when no ligand provided
    assert len(job["sequences"]) == 1
    assert job["sequences"][0]["proteinChain"]["sequence"] == "-" * 70


def test_validate_accepts_no_ligand_unconditional():
    # No ligand is valid: this is unconditional generation
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand=None, input_json_path=None, sequence_length=100))
    workflow.validate()


def test_validate_rejects_bad_sequence_length():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand=None, input_json_path=None, sequence_length=0))
    with pytest.raises(ValueError, match="sequence_length must be at least 1"):
        workflow.validate()


def test_validate_rejects_bad_experiment():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand="CCD_ATP", experiment="nonsense"))
    with pytest.raises(ValueError, match="experiment must be"):
        workflow.validate()


def test_validate_accepts_ligand_only():
    workflow = DiscoWorkflow(disco_params=DiscoParams(ligand="CCD_ATP", sequence_length=100))
    # Should not raise
    workflow.validate()


def test_validate_accepts_custom_json():
    custom = '[{"sequences": [{"proteinChain": {"sequence": "----", "count": 1}}], "name": "rna_job"}]'
    # custom JSON is valid even with no ligand and an invalid sequence_length (the JSON takes precedence)
    workflow = DiscoWorkflow(disco_params=DiscoParams(custom_input_json=custom, sequence_length=0))
    workflow.validate()


def test_validate_rejects_invalid_custom_json():
    workflow = DiscoWorkflow(disco_params=DiscoParams(custom_input_json="{not valid"))
    with pytest.raises(ValueError, match="not valid JSON"):
        workflow.validate()


def test_validate_rejects_non_list_custom_json():
    workflow = DiscoWorkflow(disco_params=DiscoParams(custom_input_json='{"sequences": []}'))
    with pytest.raises(ValueError, match="non-empty list"):
        workflow.validate()
