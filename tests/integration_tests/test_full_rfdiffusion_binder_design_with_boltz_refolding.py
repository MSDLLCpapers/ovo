from ovo import db, design_logic, storage
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
    RFdiffusionBinderDesignWorkflow,
)
from ovo.core.database import (
    descriptors_refolding,
    descriptors_rfdiffusion,
)
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_binder_default_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/5ELI_A.pdb")],
            contigs=["A74-97/0 20"],
            num_designs=1,
            timesteps=15,  # use 15 diffusion timesteps for faster testing
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=2,
            sampling_temp=0.1,
            run_parameters="--seed 42",
        ),
        refolding_params=RefoldingParams(
            primary_test="boltz2_binder_tt",
        ),
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        # Your initialized workflow settings
        workflow=workflow,
        # Name your pool of designs
        pool_name="5ELI boltz refolding binder test",
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

    # reload design_job to make sure it's up to date with the DB
    design_job = db.DesignJob.get(id=design_job.id)
    assert design_job.workflow.acceptance_thresholds[descriptors_refolding.BOLTZ_PRIMARY_IPDE.key].enabled
    assert design_job.workflow.acceptance_thresholds[descriptors_refolding.BOLTZ_PRIMARY_BINDER_PLDDT.key].enabled
    assert not design_job.warnings

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 2

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]
    assert design_ids[0].endswith("_seq1")
    assert design_ids[1].endswith("_seq2")

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    boltz2_ipde = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_IPDE.key, design_ids)
    assert len(boltz2_ipde.dropna()) == 2
    assert (boltz2_ipde < 30).all()

    boltz2_binder_rmsd = db.select_descriptor_values(
        descriptors_refolding.BOLTZ_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.key, design_ids
    )
    assert len(boltz2_binder_rmsd.dropna()) == 2
    assert (boltz2_binder_rmsd < 30).all()

    boltz2_binder_plddt = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_BINDER_PLDDT.key, design_ids)
    assert len(boltz2_binder_plddt.dropna()) == 2
    assert (boltz2_binder_plddt > 0.05).all()
    assert (boltz2_binder_plddt <= 1).all()

    boltz2_pdb_paths = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(boltz2_pdb_paths.dropna()) == 2

    rosetta_ddg = db.select_descriptor_values(descriptors_rfdiffusion.PYROSETTA_DDG.key, design_ids)
    assert len(rosetta_ddg.dropna()) == 2
    assert not rosetta_ddg.isna().any()
