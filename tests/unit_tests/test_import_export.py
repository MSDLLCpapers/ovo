import os
import tempfile
import zipfile
import pytest
from dataclasses import dataclass

from ovo import db, storage, DescriptorValue, DescriptorJob, UnknownWorkflow
from ovo.core.database import descriptors_rfdiffusion
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    RFdiffusionParams,
)
from ovo import (
    Project,
    Round,
    Pool,
    Design,
    DesignSpec,
    DesignJob,
    Artifact,
    ArtifactTypes,
    ProjectArtifact,
    Labeling,
    DesignLabeling,
)
from ovo.core.logic.import_export_logic import export_project, import_project


def test_export_import_cycle(example_pdb_path, recwarn):
    """Test that export and import work together correctly"""

    # Create a test project with some data
    test_project = Project(
        id="test_export_import_project",
        name="Test Export Import Project",
        author="test_user",
        public=False,
    )
    db.save(test_project)

    # Create a round
    test_round = Round(id="test_export_import_round", project_id=test_project.id, name="Test Round", author="test_user")
    db.save(test_round)

    input_pdb_path = storage.store_file_path(example_pdb_path, "project/inputs/test.pdb")
    missing_pdb_path = (
        "../foo/bar.pdb"  # This file won't be copied, but we want to make sure it doesn't cause export to fail
    )
    test_design_job = DesignJob(
        id="test_export_import_design_job",
        author="test_user",
        scheduler_key="test",
        job_id="test_id",
        workflow=RFdiffusionScaffoldDesignWorkflow(
            rfdiffusion_params=RFdiffusionParams(input_pdb_paths=[input_pdb_path, missing_pdb_path])
        ),
    )
    db.save(test_design_job)
    assert os.path.exists(os.path.join(storage.storage_root, input_pdb_path))

    # Create a pool
    test_pool = Pool(
        id="teip",
        round_id=test_round.id,
        name="Test Pool",
        author="test_user",
        design_job_id=test_design_job.id,
    )
    db.save(test_pool)

    with open(example_pdb_path) as f:
        test_design = Design.from_pdb_file(
            storage=storage,
            filename="5ELI_A.pdb",
            pdb_str=f.read(),
            chains=["A"],
            project_id=test_project.id,
            pool_id=test_pool.id,
        )
        db.save(test_design)
        assert len(test_design.spec.chains) == 1
        assert os.path.exists(os.path.join(storage.storage_root, test_design.structure_path))

    # Test descriptor value
    test_descriptor_job = DescriptorJob(
        id=DescriptorJob.generate_id(),
        project_id=test_project.id,
        workflow=UnknownWorkflow(data={"name": "Test"}, error="Test error"),
        author="test",
        scheduler_key="test",
        job_id="test",
    )
    db.save(test_descriptor_job)

    test_zip_path = storage.store_file_str("Mock ZIP content", f"project/{test_project.id}/descriptors/test.zip")
    storage_zip_path = f"zip://{test_zip_path}:foo/bar.pdb"
    test_descriptor_value = DescriptorValue(
        design_id=test_design.id,
        descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key,
        descriptor_job_id=test_descriptor_job.id,
        chains="A",
        value=storage_zip_path,
    )
    db.save(test_descriptor_value)

    # Test artifact for import/export testing
    @ArtifactTypes.register()
    @dataclass
    class TestArtifact(Artifact):
        """Test artifact with file storage paths"""

        file_paths: list[str] | None = None

        def get_storage_paths(self) -> list[str]:
            return self.file_paths if self.file_paths else []

    # Create artifact files for testing
    artifact_file_path = storage.store_file_str(
        "Test artifact content", f"project/{test_project.id}/artifacts/test_artifact.txt"
    )

    # Create a project artifact
    test_artifact = ProjectArtifact(
        project_id=test_project.id,
        artifact_type=TestArtifact.artifact_type,
        artifact=TestArtifact(
            file_paths=[artifact_file_path],
        ),
        author="test",
    )
    db.save(test_artifact)
    assert os.path.exists(os.path.join(storage.storage_root, artifact_file_path))

    try:
        # Export the project
        export_zip_path = export_project(test_project.id)

        assert len(recwarn) > 0, "Expected at least one warning"
        warning_messages = [str(w.message) for w in recwarn]
        assert any(missing_pdb_path in msg for msg in warning_messages), (
            f"Expected warning about missing file '{missing_pdb_path}', got: {warning_messages}"
        )

        # Verify the ZIP file was created
        assert os.path.exists(export_zip_path)
        assert zipfile.is_zipfile(export_zip_path)

        # Delete the original data
        db.remove(Pool, test_pool.id)
        db.remove(Round, test_round.id)
        db.remove(Project, test_project.id)
        db.remove(Design, test_design.id)
        db.remove(DesignJob, test_design_job.id)
        db.remove(ProjectArtifact, test_artifact.id)
        db.remove(DescriptorJob, test_descriptor_job.id)
        db.remove(
            DescriptorValue,
            design_id=test_design.id,
            descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key,
        )
        # Remove files
        os.unlink(os.path.join(storage.storage_root, test_design.structure_path))
        os.unlink(os.path.join(storage.storage_root, input_pdb_path))
        os.unlink(os.path.join(storage.storage_root, artifact_file_path))
        os.unlink(os.path.join(storage.storage_root, test_zip_path))

        assert not db.count(Project, id=test_project.id), "Project should be deleted"
        assert not db.count(Design, id=test_design.id), "Design should be deleted"
        assert not db.count(ProjectArtifact, id=test_artifact.id), "Artifact should be deleted"

        # Extract ZIP file
        with tempfile.TemporaryDirectory() as temp_root:
            with zipfile.ZipFile(export_zip_path, "r") as zipf:
                zipf.extractall(temp_root)

            paths = os.listdir(temp_root)
            assert len(paths) == 1, "There should be one top-level directory in the export, got: " + str(paths)
            temp_dir = os.path.join(temp_root, paths[0])

            # Remove zip file
            os.unlink(export_zip_path)

            counts = import_project(temp_dir, count_only=True)
            assert counts.get("project") == 1
            assert counts.get("round") == 1
            assert counts.get("pool") == 1
            assert counts.get("project_artifact") == 1
            assert not db.count(Project, id=test_project.id), "Project should still be deleted"

            # Import the data
            counts = import_project(temp_dir, test_project.id)

        # Verify the data was imported correctly
        imported_project = db.get(Project, test_project.id)
        assert imported_project.name == "Test Export Import Project"
        assert imported_project.author == "test_user"
        assert imported_project.public, "Project should become public upon export"

        imported_round = db.get(Round, test_round.id)
        assert imported_round.name == "Test Round"
        assert imported_round.project_id == test_project.id

        imported_pool = db.get(Pool, test_pool.id)
        assert imported_pool.name == "Test Pool"
        assert imported_pool.round_id == test_round.id

        imported_design = db.get(Design, test_design.id)
        assert len(imported_design.spec.chains) == 1
        assert os.path.exists(os.path.join(storage.storage_root, imported_design.structure_path))

        imported_design_job = db.get(DesignJob, test_design_job.id)
        assert os.path.exists(os.path.join(storage.storage_root, input_pdb_path)), (
            "Path referenced inside Workflow dataclass should also be copied"
        )

        imported_descriptor_job = db.get(DescriptorJob, test_descriptor_job.id)
        assert imported_descriptor_job.project_id == test_project.id
        assert isinstance(imported_descriptor_job.workflow, UnknownWorkflow)
        assert imported_descriptor_job.workflow.data["name"] == "Test"

        imported_descriptor_value = db.get(
            DescriptorValue,
            design_id=test_design.id,
            descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key,
        )
        assert imported_descriptor_value.value == storage_zip_path
        with open(os.path.join(storage.storage_root, test_zip_path)) as f:
            assert f.read() == "Mock ZIP content"

        imported_artifact = db.get(ProjectArtifact, test_artifact.id)
        assert imported_artifact.project_id == test_project.id
        assert isinstance(imported_artifact.artifact, TestArtifact)
        assert imported_artifact.artifact.file_paths == [artifact_file_path]
        assert os.path.exists(os.path.join(storage.storage_root, artifact_file_path)), "Artifact file should be copied"

        # Verify import results
        assert counts["project"] == 1
        assert counts["round"] == 1
        assert counts["pool"] == 1
        assert counts["project_artifact"] == 1

    finally:
        # Clean up export file
        if "export_zip_path" in locals() and os.path.exists(export_zip_path):
            os.unlink(export_zip_path)


def test_export_import_with_missing_storage_files():
    """Test export behavior when storage files are missing"""

    # Create a project with a design that references a non-existent file
    project = Project(
        id="test_missing_storage_project", name="Test Missing Storage Project", author="test_user", public=False
    )
    db.save(project)

    round_obj = Round(id="test_missing_storage_round", project_id=project.id, name="Test Round", author="test_user")
    db.save(round_obj)

    pool = Pool(id="tmsp", round_id=round_obj.id, name="Test Pool", author="test_user")
    db.save(pool)

    # Create a design with a non-existent PDB file
    design = Design(
        id=f"ovo_{pool.id}_test_missing_storage_design",
        pool_id=pool.id,
        structure_path="non_existent_file.pdb",  # This file doesn't exist
        spec=DesignSpec(chains=[]),  # Required field with proper structure
    )
    db.save(design)

    # Export should print a warning for missing files
    with pytest.warns(UserWarning, match="Skipping file found outside of storage root: non_existent_file.pdb"):
        export_project(project.id)


def test_import_id_conflicts():
    """Test that import fails when IDs already exist"""

    # Create a test project
    test_project = Project(id="test_conflict_project", name="Test Conflict Project", author="test_user", public=False)
    db.save(test_project)

    # Export the project
    export_zip_path = export_project(test_project.id)

    try:
        # Attempt to import while the project still exists (should fail)
        with pytest.raises(ValueError, match="Project already exists in the database: Test Conflict Project .*"):
            with tempfile.TemporaryDirectory() as temp_root:
                with zipfile.ZipFile(export_zip_path, "r") as zipf:
                    zipf.extractall(temp_root)
                    paths = os.listdir(temp_root)
                    assert len(paths) == 1, "There should be one top-level directory in the export, got: " + str(paths)
                    temp_dir = os.path.join(temp_root, paths[0])
                    import_project(temp_dir, test_project.id)

    finally:
        # Clean up export file
        if os.path.exists(export_zip_path):
            os.unlink(export_zip_path)


def test_export_import_labels_skip_existing(example_pdb_path):
    """Test that labels are exported and imported correctly, skipping existing labels with same attributes"""

    # Create a test project with designs and labels
    test_project = Project(
        id="test_label_export_import_project",
        name="Test Label Export Import Project",
        author="test_user",
        public=False,
    )
    db.save(test_project)

    test_round = Round(
        id="test_label_export_import_round", project_id=test_project.id, name="Test Round", author="test_user"
    )
    db.save(test_round)

    test_pool = Pool(id="tlei", round_id=test_round.id, name="Test Pool", author="test_user")
    db.save(test_pool)

    # Create designs
    with open(example_pdb_path) as f:
        pdb_content = f.read()
        test_design_1 = Design.from_pdb_file(
            storage=storage,
            filename="design1.pdb",
            pdb_str=pdb_content,
            chains=["A"],
            project_id=test_project.id,
            pool_id=test_pool.id,
        )
        test_design_2 = Design.from_pdb_file(
            storage=storage,
            filename="design2.pdb",
            pdb_str=pdb_content,
            chains=["A"],
            project_id=test_project.id,
            pool_id=test_pool.id,
        )
        db.save_all([test_design_1, test_design_2])

    # Create labels for the project
    label_good = Labeling(id="import_good_id_test", label="Good", explanation="Good design", author="test_user")
    label_interesting = Labeling(
        id="import_interesting_id_test", label="Interesting", explanation="Interesting design", author="test_user"
    )
    db.save_all([label_good, label_interesting])

    # Create design-label associations
    design_labeling_1 = DesignLabeling(design_id=test_design_1.id, labeling_id=label_good.id)
    design_labeling_2 = DesignLabeling(design_id=test_design_2.id, labeling_id=label_good.id)
    design_labeling_3 = DesignLabeling(design_id=test_design_2.id, labeling_id=label_interesting.id)
    db.save_all([design_labeling_1, design_labeling_2, design_labeling_3])

    try:
        # Export the project
        export_zip_path = export_project(test_project.id)
        assert os.path.exists(export_zip_path)

        # Delete the project data but keep label_good to test that it gets skipped on import
        db.remove(DesignLabeling, design_id=test_design_1.id, labeling_id=label_good.id)
        db.remove(DesignLabeling, design_id=test_design_2.id, labeling_id=label_good.id)
        db.remove(DesignLabeling, design_id=test_design_2.id, labeling_id=label_interesting.id)
        # Keep label_good in database to test skipping behavior
        db.remove(Labeling, label_interesting.id)
        db.remove(Design, test_design_1.id)
        db.remove(Design, test_design_2.id)
        db.remove(Pool, test_pool.id)
        db.remove(Round, test_round.id)
        db.remove(Project, test_project.id)

        # Extract and import
        with tempfile.TemporaryDirectory() as temp_root:
            with zipfile.ZipFile(export_zip_path, "r") as zipf:
                zipf.extractall(temp_root)
            paths = os.listdir(temp_root)
            temp_dir = os.path.join(temp_root, paths[0])

            # Count entities before import
            counts = import_project(temp_dir, count_only=True)
            assert counts.get("design") == 2
            assert counts.get("labeling") == 2  # Good and Interesting
            assert counts.get("design_labeling") == 3

            # Import the data
            counts = import_project(temp_dir, test_project.id)

        # Verify imported data
        imported_design_1 = db.get(Design, test_design_1.id)
        imported_design_2 = db.get(Design, test_design_2.id)
        assert imported_design_1 is not None
        assert imported_design_2 is not None

        # Verify labels exist (Good was skipped, Interesting was imported)
        all_labelings = db.select(Labeling)
        labeling_by_name = {labeling.label: labeling for labeling in all_labelings}

        assert "Good" in labeling_by_name, "Good label should exist (was already in DB, skipped during import)"
        assert "Interesting" in labeling_by_name, "Interesting label should exist (was imported)"

        # Verify labels kept their original IDs
        good_label = labeling_by_name["Good"]
        assert good_label.id == "import_good_id_test", "Good label should keep its original ID"
        interesting_label = labeling_by_name["Interesting"]
        assert interesting_label.id == "import_interesting_id_test", "Interesting label should keep its original ID"

        # Verify design-label associations
        design1_labelings = db.select(DesignLabeling, design_id=test_design_1.id)
        assert len(design1_labelings) == 1
        assert design1_labelings[0].labeling_id == label_good.id

        design2_labelings = db.select(DesignLabeling, design_id=test_design_2.id)
        assert len(design2_labelings) == 2
        design2_labeling_ids = {dl.labeling_id for dl in design2_labelings}
        assert label_good.id in design2_labeling_ids
        assert label_interesting.id in design2_labeling_ids

        # Verify counts
        assert counts["design"] == 2
        assert counts["labeling"] == 1, "Only 1 label should be imported (Good was skipped because it already exists)"
        assert counts["design_labeling"] == 3

    finally:
        # Clean up
        if "export_zip_path" in locals() and os.path.exists(export_zip_path):
            os.unlink(export_zip_path)
        # Clean up the label_good that we kept in the database
        if db.count(Labeling, id=label_good.id):
            db.remove(Labeling, label_good.id)
