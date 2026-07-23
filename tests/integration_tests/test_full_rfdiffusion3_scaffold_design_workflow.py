from ovo import db, design_logic, storage
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionParams,
    ProteinMPNNParams,
    RefoldingParams,
    RFdiffusionScaffoldDesignWorkflow,
)
from ovo.core.database import (
    descriptors_refolding,
    descriptors_rfdiffusion,
)
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY, create_test_project_data
import pytest


def test_scaffold_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"],
            contigs=["5-10/A118/5-10"],
            contigmap_length="10-15",
            num_designs=2,
            backbone_generator="rfdiffusion3",
            timesteps=70,  # reduced from 200 for faster testing
            rfd3_select_fixed_atoms='{"A111": "CA,C,N", "A118": "BKBN", "A119": "CA,C,N"}',
            rfd3_unindex="A111,A119",
            rfd3_inner_batch_size=2,
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
        workflow=workflow,
        pool_name="5ELI hairpin scaffold test (RFdiffusion3)",
        pool_description="",
        scheduler_key=TEST_SCHEDULER_KEY,
        round_id=project_round.id,
    )
    print(f"{design_job.id=}")
    print(f"{pool.id=}")

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    print(jobs)
    assert len(jobs) == 1

    pool = design_logic.process_results(design_job)

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 8

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]

    # Backbone structure exists
    # check that inner_batch_size = 2, so total backbones = 2*2 = 4.
    # There is a descriptorValue for each sequence design so in total 2*2*2=8 objects, with 4 unique values
    backbone_pdbs = db.select_descriptor_values(
        descriptors_rfdiffusion.RFDIFFUSION3_ALL_ATOM_STRUCTURE_PATH.key, design_ids
    )
    assert len(backbone_pdbs.dropna()) == 8
    assert len(backbone_pdbs.dropna().unique()) == 4
    assert backbone_pdbs.iloc[0].endswith(".pdb")
    assert "ATOM " in storage.read_file_str(backbone_pdbs.iloc[0])

    # gzip compressed cif artifact exists (raw RFD3 output)
    all_atom_cif_gz_path = db.select_descriptor_values(
        descriptors_rfdiffusion.RFDIFFUSION3_ALL_ATOM_STRUCTURE_PATH_COMPRESSED_CIF.key, design_ids
    )
    assert len(all_atom_cif_gz_path.dropna()) == 8
    assert len(all_atom_cif_gz_path.dropna().unique()) == 4
    assert all_atom_cif_gz_path.iloc[0].endswith(".cif.gz")

    # TRB descriptor is absent for RFD3 (no .trb file produced)
    trb_paths = db.select_descriptor_values(descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key, design_ids)
    assert len(trb_paths.dropna()) == 0

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 8
    assert (rag > 0).all()

    af2_plddt = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_PLDDT.key, design_ids)
    assert len(af2_plddt.dropna()) == 8
    assert (af2_plddt > 10).all()

    design_rmsd = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key, design_ids)
    assert len(design_rmsd.dropna()) == 8
    assert (design_rmsd < 20).all()

    af2_pdbs = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(af2_pdbs.dropna()) == 8
    assert af2_pdbs.iloc[0].endswith(".pdb")
    assert "ATOM " in storage.read_file_str(af2_pdbs.iloc[0])
