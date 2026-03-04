from ovo import db, design_logic
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


def test_scaffold_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            contigs=["A111-114/10/A117-119"],
            num_designs=1,
            timesteps=1,  # use 1 diffusion iteration for faster testing
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
        pool_name="5ELI hairpin scaffold test",
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

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    af2_plddt = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_PLDDT.key, design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    design_rmsd = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key, design_ids)
    assert len(design_rmsd.dropna()) == 2
    assert (design_rmsd < 20).all()

    # Refolding
    test = "af2_model_1_ptm_nt_3rec"
    empty = db.select_descriptor_values(f"refolding|{test}|plddt", design_ids)
    assert len(empty.dropna()) == 0, "Refolding descriptors should be empty before refolding is run"
    refolding: RefoldingWorkflow = RefoldingWorkflow(
        chains=["A"],
        design_ids=[design.id for design in designs],
        tests=[test],
        design_type="scaffold",
    )
    refolding.validate()
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=refolding, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    af2_plddt = db.select_descriptor_values(f"refolding|{test}|plddt", design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    design_rmsd = db.select_descriptor_values(f"refolding|{test}|design_backbone_rmsd", design_ids)
    assert len(design_rmsd.dropna()) == 2
    assert (design_rmsd < 15).all()

    # Clustering
    clustering: FoldseekClusteringWorkflow = FoldseekClusteringWorkflow(
        chains=["A"],
        design_ids=[design.id for design in designs],
        params=FoldseekParams(
            exhaustive_search=True,
            e=100,
        )
    )
    clustering.validate()
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=clustering, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    cluster_id = db.select_descriptor_values(descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key, design_ids)
    assert len(cluster_id.dropna()) == 2
