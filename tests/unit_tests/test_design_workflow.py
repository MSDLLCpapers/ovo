from unittest.mock import ANY

from ovo.core.logic import design_logic
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
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
        mpnn_num_sequences=1,
        mpnn_run_parameters='--omit_AA "CX" --temperature 0.01',
        refolding_tests="esmfold",
        batch_size=50,
    )
