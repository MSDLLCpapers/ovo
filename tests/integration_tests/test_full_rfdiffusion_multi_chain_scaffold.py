from ovo import db, design_logic, storage
from ovo.core.database.models_refolding import RefoldingWorkflow
from ovo.core.database.models_clustering import FoldseekClusteringWorkflow, FoldseekParams
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
    RFdiffusionScaffoldDesignWorkflow,
)
from ovo.core.database import (
    descriptors_refolding,
    descriptors_rfdiffusion,
    descriptors_clustering,
)
from ovo.core.logic import descriptor_logic
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_scaffold_multichain_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            contigs=["A111-114/10/A117-119/0 A110-113/5/A118-120"],
            num_designs=1,
            timesteps=10,
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=2,
            sampling_temp=0.1,
            run_parameters="--seed 42",
        ),
        refolding_params=RefoldingParams(
            primary_test="af2_model_1_ptm_ft_3rec",
        ),
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        # Your initialized workflow settings
        workflow=workflow,
        # Name your pool of designs
        pool_name="5ELI multi-chain hairpin scaffold test",
        pool_description="",
        # see schedulers for available scheduler keys
        scheduler_key=TEST_SCHEDULER_KEY,
        # Project and Round where the Pool will be created
        round_id=project_round.id,
    )

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    print(jobs)
    assert len(jobs) == 1

    # wait for job to complete and process results
    pool = design_logic.process_results(design_job)

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 2

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]

    design = designs[0]
    assert len(design.spec.chains) == 2
    assert design.spec.chains[0].chain_ids == ["A"]
    assert design.spec.chains[0].contig == "A111-114/10-10/A117-119/0"
    assert design.spec.chains[1].chain_ids == ["B"]
    assert design.spec.chains[1].contig == "A110-113/5-5/A118-120"

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    af2_plddt = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_PLDDT.key, design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    # TODO add alphafold interface metrics - they are computed by colabdesign,
    #  but we don't save them to the JSONL in that script (see METRICS in af2_initial_guess_scaffold_eval.py)
    #  and we don't have corresponding Descriptor objects in OVO for the scaffold refolding tests
    # af2_ipae = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_IPAE.key, design_ids)
    # assert len(af2_ipae.dropna()) == 2
    # assert (af2_ipae < 30).all()
