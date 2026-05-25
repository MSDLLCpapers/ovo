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


def test_binder_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionBinderDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            contigs=["A74-79/A82-97/0 20"],
            hotspots="A78,A79",
            num_designs=1,
            backbone_generator="rfdiffusion3",
            timesteps=10,  # reduced from 200 for faster testing
            rfd3_select_hotspots='{"A78": "CA,CB", "A79": "CA,CB"}',
            rfd3_is_non_loopy=True,
            rfd3_spec_overrides='{"plddt_enhanced": true, "is_non_loopy": false}',
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
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        workflow=workflow,
        pool_name="5ELI binder test (RFdiffusion3)",
        pool_description="",
        scheduler_key=TEST_SCHEDULER_KEY,
        round_id=project_round.id,
    )

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    print(jobs)
    assert len(jobs) == 1

    pool = design_logic.process_results(design_job)

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 2

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]
    assert design_ids[0].endswith("_seq1")
    assert design_ids[1].endswith("_seq2")

    # Backbone structure exists
    backbone_pdbs = db.select_descriptor_values(descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key, design_ids)
    assert len(backbone_pdbs.dropna()) == 2
    assert backbone_pdbs.iloc[0].endswith(".pdb")
    assert "ATOM " in storage.read_file_str(backbone_pdbs.iloc[0])

    # TRB descriptor is absent for RFD3 (no .trb file produced)
    trb_paths = db.select_descriptor_values(descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key, design_ids)
    assert len(trb_paths.dropna()) == 0

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    af2_ipae = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_IPAE.key, design_ids)
    assert len(af2_ipae.dropna()) == 2
    assert (af2_ipae < 30).all()

    af2_pdbs = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(af2_pdbs.dropna()) == 2
    assert af2_pdbs.iloc[0].endswith(".pdb")
    af2_pdb_str = storage.read_file_str(af2_pdbs.iloc[0])
    assert "ATOM " in af2_pdb_str
    af2_pdb_residues = get_chains_and_contigs(af2_pdb_str)
    assert "A" in af2_pdb_residues, "Expected binder chain A in refolded structure"
    assert "B" in af2_pdb_residues, "Expected target chain B in refolded structure"
