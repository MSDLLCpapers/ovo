from unittest.mock import ANY

import pytest

from ovo.core.utils.resources import RESOURCES_DIR
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
        mpnn_run_parameters='--omit_AA "CX" --temperature 0.01 ',
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
