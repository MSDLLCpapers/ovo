from ovo import db, design_logic, storage
from ovo.core.database.models import DESIGNED_CHAINS, DescriptorValue
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
from ovo.core.database.models import ProjectArtifact, JobReportArtifact
from ovo.core.logic import descriptor_logic
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_scaffold_end_to_end_logic(project_data):
    project, project_round, custom_pool = project_data

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/5ELI_A.pdb")],
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
    # by default, ESMfold pLDDT threshold should be enabled
    assert design_job.workflow.acceptance_thresholds[descriptors_refolding.ESMFOLD_PLDDT.key].enabled, (
        "ESMFold pLDDT threshold should be enabled by default"
    )

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    print(jobs)
    assert len(jobs) == 1

    # wait for job to complete and process results
    pool = design_logic.process_results(design_job)

    # Check that artifact was created
    artifacts = db.select(ProjectArtifact, design_job_id=design_job.id, artifact_type=JobReportArtifact.artifact_type)
    assert len(artifacts) == 1
    assert artifacts[0].artifact.job_author == design_job.author

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 2

    designs = db.Design.select(pool_id=pool.id)
    design_ids = [d.id for d in designs]

    design_job = db.DesignJob.get(id=design_job.id)
    assert design_job.workflow.acceptance_thresholds[descriptors_refolding.AF2_PRIMARY_PLDDT.key].enabled, (
        "AF2 pLDDT threshold should be enabled for scaffold design workflow"
    )
    assert not design_job.workflow.acceptance_thresholds[descriptors_refolding.ESMFOLD_PLDDT.key].enabled, (
        "ESMFold pLDDT threshold should be disabled when not available after workflow has finished"
    )
    assert not design_job.warnings

    rag = db.select_descriptor_values(descriptors_rfdiffusion.RADIUS_OF_GYRATION.key, design_ids)
    assert len(rag.dropna()) == 2
    assert (rag > 0).all()

    af2_plddt = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_PLDDT.key, design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    design_rmsd = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key, design_ids)
    assert len(design_rmsd.dropna()) == 2
    assert (design_rmsd < 20).all()

    af2_pdbs = db.select_descriptor_values(descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH.key, design_ids)
    assert len(af2_pdbs.dropna()) == 2
    assert af2_pdbs.iloc[0].endswith(".pdb")
    assert "ATOM " in storage.read_file_str(af2_pdbs.iloc[0])

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

    # Check that artifact was created for descriptor job
    artifacts = db.select(
        ProjectArtifact, descriptor_job_id=descriptor_job.id, artifact_type=JobReportArtifact.artifact_type
    )
    assert len(artifacts) == 1

    af2_plddt = db.select_descriptor_values(f"refolding|{test}|plddt", design_ids)
    assert len(af2_plddt.dropna()) == 2
    assert (af2_plddt > 10).all()

    af2_pdb_paths = db.select_descriptor_values(f"refolding|{test}|af2_structure_path", design_ids)
    assert len(af2_pdb_paths.dropna()) == 2

    design_rmsd = db.select_descriptor_values(f"refolding|{test}|design_backbone_rmsd", design_ids)
    assert len(design_rmsd.dropna()) == 2
    assert (design_rmsd < 20).all()

    # Clustering
    clustering: FoldseekClusteringWorkflow = FoldseekClusteringWorkflow(
        chains=["A"],
        design_ids=[design.id for design in designs],
        params=FoldseekParams(
            exhaustive_search=True,
            e=100,
        ),
    )
    clustering.validate()
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=clustering, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    cluster_id = db.select_descriptor_values(
        descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key, design_ids, descriptor_job_id=descriptor_job.id
    )
    assert len(cluster_id.dropna()) == 2

    # Clustering using the designed chain of each design, which should give the same result
    # (all designs have the same designed chain here, see test_mixed_designed_chains_clustering for a mixed case)
    designed_clustering: FoldseekClusteringWorkflow = FoldseekClusteringWorkflow(
        chains=[DESIGNED_CHAINS],
        design_ids=[design.id for design in designs],
        params=FoldseekParams(
            exhaustive_search=True,
            e=100,
        ),
    )
    designed_clustering.validate()
    designed_descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=designed_clustering, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(designed_descriptor_job)

    designed_cluster_id = db.select_descriptor_values(
        descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key, design_ids, descriptor_job_id=designed_descriptor_job.id
    )
    assert designed_cluster_id.to_dict() == cluster_id.to_dict()

    # The resolved chain IDs are stored for each design, not the DESIGNED_CHAINS placeholder
    stored_chains = db.select_values(
        DescriptorValue,
        "chains",
        descriptor_job_id=designed_descriptor_job.id,
        descriptor_key=descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key,
    )
    assert set(stored_chains) == {"A"}


def test_failed_job_creates_artifact(project_data):
    """Test that JobReportArtifact is created even when job fails."""
    project, project_round, _ = project_data

    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/5ELI_A.pdb")],
            contigs=["A200-210/10/A220-230"],  # Invalid: regions outside PDB range
            num_designs=1,
            timesteps=1,
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            sampling_temp=0.1,
        ),
        refolding_params=RefoldingParams(
            primary_test="esmfold",
        ),
    )

    design_job, pool = design_logic.submit_design_workflow(
        workflow=workflow,
        pool_name="Failed Job Test",
        pool_description="Test artifact creation on failure",
        scheduler_key=TEST_SCHEDULER_KEY,
        round_id=project_round.id,
    )

    try:
        design_logic.process_results(design_job)
        assert False, "Job should have failed"
    except ValueError:
        pass

    # Verify artifact was created despite failure
    artifacts = db.select(ProjectArtifact, design_job_id=design_job.id, artifact_type=JobReportArtifact.artifact_type)
    assert len(artifacts) == 1
    assert artifacts[0].project_id == project.id
    assert artifacts[0].artifact.job_author == design_job.author

    # Verify job is marked as failed
    design_job = db.get(db.DesignJob, id=design_job.id)
    assert design_job.job_result is False
