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
from ovo.core.utils.residue_selection import get_chains_and_contigs
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_binder_default_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/5ELI_A.pdb")],
            contigs=["A74-79/A82-97/0 20"],
            num_designs=1,
            timesteps=15,  # use 15 diffusion timesteps for faster testing
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            fastrelax_cycles=2,
            sampling_temp=0.1,
            run_parameters="-seed 42",
        ),
        refolding_params=RefoldingParams(
            primary_test="af2_model_1_multimer_tt_3rec",
        ),
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        # Your initialized workflow settings
        workflow=workflow,
        # Name your pool of designs
        pool_name="5ELI fastrelax binder test",
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
    assert design_ids[0].endswith("_cycle0")
    assert design_ids[1].endswith("_cycle1")

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    af2_ipae = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_IPAE.key, design_ids)
    assert len(af2_ipae.dropna()) == 2
    assert (af2_ipae < 30).all()

    rosetta_ddg = db.select_descriptor_values(descriptors_rfdiffusion.PYROSETTA_DDG.key, design_ids)
    assert len(rosetta_ddg.dropna()) == 2
    assert not rosetta_ddg.isna().any()

    rosetta_buns = db.select_descriptor_values(descriptors_rfdiffusion.PYROSETTA_BUNS.key, design_ids)
    assert len(rosetta_buns.dropna()) == 2
    assert not rosetta_buns.isna().any()

    rosetta_bunsat = db.select_descriptor_values(descriptors_rfdiffusion.PYROSETTA_BUNS.key, design_ids)
    assert len(rosetta_bunsat.dropna()) == 2
    assert not rosetta_bunsat.isna().any()

    af2_paths = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(af2_paths.dropna()) == 2
    af2_pdb_str = storage.read_file_str(af2_paths.iloc[0])
    af2_pdb_residues = get_chains_and_contigs(af2_pdb_str)
    assert af2_pdb_residues == {"A": "A1-20", "B": "B74-79/B82-97"}, (
        "AF2 predicted structure is not numbered as expected"
    )
