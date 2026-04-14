from ovo import db, design_logic
from ovo.core.database import (
    descriptors_refolding,
    descriptors_rfdiffusion,
)
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
    RFdiffusionScaffoldDesignWorkflow,
)
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_scaffold_boltz_end_to_end_logic(project_data):
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
            primary_test="boltz2_scaffold_nt",
        ),
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        # Your initialized workflow settings
        workflow=workflow,
        # Name your pool of designs
        pool_name="5ELI hairpin scaffold test with boltz refolding",
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

    design_job = db.DesignJob.get(id=design_job.id)
    assert design_job.workflow.acceptance_thresholds[
        descriptors_refolding.BOLTZ_PRIMARY_NATIVE_MOTIF_RMSD.key
    ].enabled, "Boltz motif RMSD threshold should be enabled for scaffold design workflow"
    assert design_job.workflow.acceptance_thresholds[descriptors_refolding.BOLTZ_PRIMARY_PLDDT.key].enabled, (
        "Boltz pLDDT threshold should be enabled for scaffold design workflow"
    )
    assert not design_job.workflow.acceptance_thresholds[descriptors_refolding.AF2_PRIMARY_PLDDT.key].enabled, (
        "AF2 pLDDT threshold should be disabled for scaffold design workflow"
    )
    assert not design_job.workflow.acceptance_thresholds[descriptors_refolding.ESMFOLD_PLDDT.key].enabled, (
        "ESMFold pLDDT threshold should be disabled when not available after workflow has finished"
    )
    assert not design_job.warnings

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    boltz2_pde = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_PDE.key, design_ids)
    assert len(boltz2_pde.dropna()) == 2
    assert (boltz2_pde < 30).all()

    boltz2_design_rmsd = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_DESIGN_RMSD.key, design_ids)
    assert len(boltz2_design_rmsd.dropna()) == 2
    assert (boltz2_design_rmsd < 30).all()

    boltz2_motif_rmsd = db.select_descriptor_values(
        descriptors_refolding.BOLTZ_PRIMARY_NATIVE_MOTIF_RMSD.key, design_ids
    )
    assert len(boltz2_motif_rmsd.dropna()) == 2
    assert (boltz2_motif_rmsd < 30).all()

    boltz2_plddt = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_PLDDT.key, design_ids)
    assert len(boltz2_plddt.dropna()) == 2
    assert (boltz2_plddt > 0.05).all()
    assert (boltz2_plddt <= 1).all()

    boltz2_pdb_paths = db.select_descriptor_values(descriptors_refolding.BOLTZ_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(boltz2_pdb_paths.dropna()) == 2
