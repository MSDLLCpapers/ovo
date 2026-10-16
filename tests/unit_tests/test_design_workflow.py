from unittest.mock import ANY

import pytest

from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.database.models import Threshold, Workflow
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
    RFdiffusionBinderDesignWorkflow,
)
from tests.unit_tests.utils.mocking import MockScheduler


def test_rfdiffusion_scaffold_design_workflow_get_params():
    from ovo import local_scheduler

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            num_designs=1,
            contigs=["A111-114/10/A117-119"],
            timesteps=1,
            run_parameters="inference.deterministic=True",
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            sampling_temp=0.01,
        ),
        refolding_params=RefoldingParams(
            primary_test="esmfold",
        ),
    )

    assert isinstance(local_scheduler, MockScheduler), "Expected mock scheduler in test initialized by conftest.py"
    assert workflow.prepare_params(workdir=local_scheduler.workdir) == dict(
        design_type="scaffold",
        rfdiffusion_input_pdb=ANY,
        rfdiffusion_num_designs=1,
        rfdiffusion_contig="A111-114/10/A117-119",
        rfdiffusion_run_parameters=" diffuser.T=1  inference.deterministic=True ",
        backbone_generator="rfdiffusion",
        mpnn_num_sequences=1,
        mpnn_run_parameters="--model_type soluble_mpnn "
        '--checkpoint_soluble_mpnn "model_params/solublempnn_v_48_020.pt" '
        '--omit_AA "CX" --temperature 0.01  ',
        refolding_tests="esmfold",
        batch_size=50,
        refolding_chains="A",
    )


def test_rfdiffusion3_inner_batch_size_param():
    """rfd3_inner_batch_size is forwarded to RFD3 via run_parameters as diffusion_batch_size."""
    from ovo import local_scheduler

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            num_designs=2,
            contigs=["A111-114/10/A117-119"],
            timesteps=1,
            backbone_generator="rfdiffusion3",
            rfd3_inner_batch_size=4,
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            sampling_temp=0.01,
        ),
        refolding_params=RefoldingParams(
            primary_test="esmfold",
        ),
    )
    workflow.validate()

    params = workflow.prepare_params(workdir=local_scheduler.workdir)
    assert "diffusion_batch_size=4" in params["rfdiffusion_run_parameters"]
    # routed through run_parameters, not as a spec_overrides InputSpec field
    assert "diffusion_batch_size" not in params.get("rfdiffusion3_spec_overrides", "")


def test_rfdiffusion3_inner_batch_size_validation():
    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            num_designs=1,
            contigs=["A111-114/10/A117-119"],
            timesteps=1,
            backbone_generator="rfdiffusion3",
            rfd3_inner_batch_size=0,
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            sampling_temp=0.01,
        ),
        refolding_params=RefoldingParams(
            primary_test="esmfold",
        ),
    )
    with pytest.raises(ValueError, match="rfd3_inner_batch_size must be >= 1"):
        workflow.validate()


def test_rfdiffusion_hotspot_validation():
    workflow = RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            contigs=["A74-97/0 20"],
            num_designs=1,
            timesteps=15,
            hotspots="A74,A100",
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=2,
            sampling_temp=0.1,
            run_parameters="--seed 42",
        ),
        refolding_params=RefoldingParams(
            primary_test="af2_model_1_multimer_tt_3rec",
        ),
    )
    with pytest.raises(ValueError, match="Hotspot positions {'A100'} are not included in contig segments"):
        workflow.validate()


def _make_scaffold_workflow(**rfdiffusion_overrides) -> RFdiffusionScaffoldDesignWorkflow:
    defaults = {
        "input_pdb_paths": [RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
        "num_designs": 1,
        "contigs": ["A111-114/10/A117-119"],
        "timesteps": 1,
    }
    return RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(**(defaults | rfdiffusion_overrides)),
        protein_mpnn_params=ProteinMPNNParams(num_sequences=1, sampling_temp=0.01),
        refolding_params=RefoldingParams(primary_test="esmfold"),
    )


def test_rfdiffusion_contig_must_have_generated_region():
    workflow = _make_scaffold_workflow(contigs=["A111-114/A117-119"])
    with pytest.raises(ValueError, match="at least one generated region"):
        workflow.rfdiffusion_params.validate()


def test_rfdiffusion_unindexed_invalid_format():
    workflow = _make_scaffold_workflow(
        backbone_generator="rfdiffusion3",
        rfd3_unindex="A244-247",  # ranges not allowed, must be single residues
    )
    with pytest.raises(ValueError, match="Invalid rfd3_unindex format"):
        workflow.rfdiffusion_params.validate()


def test_rfdiffusion_unindexed_overlap_with_contig_rejected():
    workflow = _make_scaffold_workflow(
        contigs=["A111-114/10/A117-119"],
        backbone_generator="rfdiffusion3",
        rfd3_unindex="A112,A200",  # A112 lies inside A111-114
    )
    with pytest.raises(ValueError, match=r"Unindexed residues \['A112'\]"):
        workflow.rfdiffusion_params.validate()


def test_rfdiffusion_unindexed_valid():
    workflow = _make_scaffold_workflow(
        contigs=["A111-114/10/A117-119"],
        backbone_generator="rfdiffusion3",
        rfd3_unindex="A200,A244",
    )
    workflow.rfdiffusion_params.validate()


def _make_partial_diffusion_workflow(input_pdb_paths: list[str], contigs: list[str]):
    return RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=input_pdb_paths,
            contigs=contigs,
            partial_diffusion=True,
            timesteps=20,
            num_designs=1,
        ),
        protein_mpnn_params=ProteinMPNNParams(num_sequences=1, sampling_temp=0.01),
        refolding_params=RefoldingParams(primary_test="esmfold"),
    )


def test_split_contig_recognizes_the_binder_in_either_order():
    """The binder is the generated part of the contig, whichever side of the chain break it is on."""
    de_novo = RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(contigs=["A123-456/0 20-40"], partial_diffusion=False)
    )
    assert de_novo.split_contig() == ("20-40", "A123-456")

    partial = _make_partial_diffusion_workflow(["one.pdb"], ["5-5/A6-20/0 B20-130"])
    assert partial.split_contig() == ("5-5/A6-20", "B20-130")


def test_partial_diffusion_selection_can_be_emptied_and_set_again():
    """Deselecting every residue keeps the whole binder fixed, which is still read back as chain A."""
    workflow = _make_partial_diffusion_workflow(["one.pdb"], ["12-12/0 B20-130"])
    assert workflow.get_selected_segments(contig_index=0, partial_diffusion=True) == ["A1-12"]

    workflow.set_selected_segments([], contig_index=0, partial_diffusion=True)
    assert workflow.rfdiffusion_params.contigs == ["A1-12/0 B20-130"]
    assert workflow.split_contig() == ("A1-12", "B20-130")
    assert workflow.get_selected_segments(contig_index=0, partial_diffusion=True) == []

    workflow.set_selected_segments(["A3-7"], contig_index=0, partial_diffusion=True)
    assert workflow.get_selected_segments(contig_index=0, partial_diffusion=True) == ["A3-7"]


def test_drop_skipped_inputs_leaves_out_the_inputs_without_a_selection():
    """An input with nothing to redesign is left out of the submission, without changing the workflow."""
    workflow = _make_partial_diffusion_workflow(
        ["one.pdb", "two.pdb", "three.pdb"],
        ["12-12/0 B20-130", "A1-15/0 B20-130", "5-5/A6-20/0 B20-130"],
    )
    assert workflow.get_skipped_contig_indexes() == [1]

    submitted = workflow.drop_skipped_inputs()
    assert submitted.rfdiffusion_params.input_pdb_paths == ["one.pdb", "three.pdb"]
    assert submitted.rfdiffusion_params.contigs == ["12-12/0 B20-130", "5-5/A6-20/0 B20-130"]
    assert len(workflow.rfdiffusion_params.contigs) == 3, "The workflow of the page keeps every input"
    assert submitted.drop_skipped_inputs() is submitted, "Nothing to skip, so no copy is made"


def test_drop_skipped_inputs_keeps_a_shared_input():
    """A workflow with several contigs for a single input keeps that input, see get_input_pdb_path."""
    workflow = _make_partial_diffusion_workflow(["one.pdb"], ["12-12/0 B20-130", "A1-15/0 B20-130"])

    submitted = workflow.drop_skipped_inputs()
    assert submitted.rfdiffusion_params.input_pdb_paths == ["one.pdb"]
    assert submitted.rfdiffusion_params.contigs == ["12-12/0 B20-130"]


def test_from_dict_leaves_the_given_dict_alone():
    """Loading a workflow does not turn the thresholds of the dict it was given into objects."""
    data = {
        "name": RFdiffusionBinderDesignWorkflow.name,
        "design_ids": ["ovo_abc_001"],
        "acceptance_thresholds": {"af2|primary_ipae": {"min_value": None, "max_value": 10.0, "enabled": True}},
    }

    workflow = Workflow.from_dict(data)

    assert workflow.acceptance_thresholds == {"af2|primary_ipae": Threshold(max_value=10.0)}
    assert data["acceptance_thresholds"] == {
        "af2|primary_ipae": {"min_value": None, "max_value": 10.0, "enabled": True}
    }, "The dict given to from_dict should be left as it was"
