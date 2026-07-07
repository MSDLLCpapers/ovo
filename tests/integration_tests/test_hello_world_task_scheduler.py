"""Integration test for TaskScheduler with HelloWorldDesignWorkflow."""

import os
import json
import shutil
from abc import ABC, abstractmethod

import pandas as pd
from dataclasses import dataclass
from typing import Callable

from ovo import db, design_logic, storage, get_scheduler
from ovo.core.database.models import (
    WorkflowTypes,
    DesignWorkflow,
    DescriptorWorkflow,
    WorkflowTask,
    DesignJob,
    DescriptorJob,
    Design,
    DesignSpec,
    DesignChain,
    Base,
    DescriptorValue,
    NumericGlobalDescriptor,
    ProjectArtifact,
    Artifact,
    ArtifactTypes,
)
from ovo.core.logic import descriptor_logic
from ovo.core.scheduler.task_scheduler import task, TaskScheduler, SyncTaskScheduler


# Define descriptors
RESIDUE_COUNT = NumericGlobalDescriptor(
    name="Residue Count",
    description="Total number of residues in the design",
    tool="Residue Counter",
    key="residue_counter|residue_count",
    comparison="does_not_apply",
    min_value=0,
)

MESSAGE_LENGTH = NumericGlobalDescriptor(
    name="Message Length",
    description="Length of the hello world message",
    tool="Hello World",
    key="hello_world|message_length",
    comparison="does_not_apply",
    min_value=0,
)


# Define ExampleArtifact for testing
@ArtifactTypes.register()
@dataclass
class ExampleArtifact(Artifact):
    """Example artifact for testing workflow artifact creation."""

    summary_file: str

    def get_storage_paths(self) -> list[str]:
        """Return paths that need to be stored in permanent storage."""
        return [self.summary_file]


class GreetingsDesignWorkflow(DesignWorkflow, ABC):
    """Simple workflow that creates a hello world PDB file."""

    message: str = "Greetings"

    def process_results(self, job: DesignJob, callback: Callable = None) -> list[Base]:
        """Read files and create Design and DescriptorValue objects."""
        from ovo.core.logic import design_logic

        scheduler = get_scheduler(job.scheduler_key)
        execdir = scheduler.get_output_dir(job.job_id)

        # Get pool and project info
        pool = db.get(db.Pool, design_job_id=job.id)
        project_round = db.get(db.Round, id=pool.round_id)

        # Read metadata
        with open(os.path.join(execdir, "metadata.json"), "r") as f:
            metadata = json.load(f)

        # Read PDBs
        designs = []
        descriptor_values = []
        for filename in metadata["filenames"]:
            design_name = os.path.splitext(filename)[0]

            # Read PDB
            with open(os.path.join(execdir, filename), "r") as f:
                pdb_str = f.read()

            # Generate design ID
            design_id = f"ovo_{pool.id}_{design_name}"

            # Store PDB file in permanent location
            structure_path = storage.store_file_str(
                pdb_str,
                storage_rel_path=os.path.join(
                    storage.get_project_path(project_round.project_id, pool.id), f"{design_id}.pdb"
                ),
            )

            # Create Design
            design = Design(
                id=design_id,
                pool_id=pool.id,
                structure_path=structure_path,
                accepted=True,
                spec=DesignSpec.from_pdb_str(pdb_str, chains=["A"]),
            )
            designs.append(design)

            # Create descriptor value
            descriptor_values.extend(
                [
                    DescriptorValue(
                        design_id=design_id,
                        descriptor_key=MESSAGE_LENGTH.key,
                        descriptor_job_id=job.id,
                        chains="A",
                        value=str(len(metadata["message"])),
                    )
                ]
            )

        # Apply acceptance thresholds
        design_logic.set_designs_accepted(designs, descriptor_values, job)

        return designs + descriptor_values


class GreetingsTask(WorkflowTask, GreetingsDesignWorkflow, ABC):
    def run(self, execdir: str, scheduler: TaskScheduler) -> None:
        filenames = self.create_files(execdir)
        # Save metadata for process_results
        metadata = {"message": self.message, "filenames": filenames}
        with open(os.path.join(execdir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    @abstractmethod
    def create_files(self, execdir: str) -> list[str]:
        """Create files needed for the workflow. To be implemented by subclasses."""
        raise NotImplementedError()


@WorkflowTypes.register("Hello World")
@dataclass
class HelloWorldTask(GreetingsTask):
    """Simple workflow that creates a hello world PDB file."""

    message: str = "Hello World"

    def create_files(self, execdir: str) -> list[str]:
        """Create a simple hello world PDB file."""
        # Create a minimal PDB with single amino acid
        pdb_content = f"""REMARK   1 {self.message}
ATOM      1  N   ALA A   1       0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  ALA A   1       1.458   0.000   0.000  1.00  0.00           C
ATOM      3  C   ALA A   1       2.009   1.420   0.000  1.00  0.00           C
ATOM      4  O   ALA A   1       1.251   2.396   0.000  1.00  0.00           O
ATOM      5  CB  ALA A   1       1.989  -0.729  -1.232  1.00  0.00           C
END
"""

        # Save PDB to execdir
        filename = "hello_world.pdb"
        with open(os.path.join(execdir, filename), "w") as f:
            f.write(pdb_content)

        return [filename]


class ResidueCountingDescriptorWorkflow(DescriptorWorkflow, ABC):
    """Descriptor workflow that counts residues in designs."""

    def process_results(self, job: DescriptorJob, callback: Callable = None) -> list[Base]:
        """Read files and create DescriptorValue and ProjectArtifact objects."""
        from ovo.core.auth import get_username

        scheduler = get_scheduler(job.scheduler_key)
        execdir = scheduler.get_output_dir(job.job_id)

        # Read results CSV
        df = pd.read_csv(os.path.join(execdir, "residue_counts.csv"))

        # Create DescriptorValue objects
        descriptor_values = []
        chains_str = ",".join(self.chains)

        for _, row in df.iterrows():
            descriptor_value = DescriptorValue(
                design_id=row["design_id"],
                descriptor_key=RESIDUE_COUNT.key,
                descriptor_job_id=job.id,
                chains=chains_str,
                value=str(int(row["count"])),
            )
            descriptor_values.append(descriptor_value)

        # Store artifact file to permanent storage
        summary_path = os.path.join(execdir, "residue_summary.txt")

        stored_summary = storage.store_file_path(
            source_abs_path=summary_path,
            storage_rel_path=os.path.join(
                storage.get_project_path(job.project_id, "artifacts"), f"residue_summary_{job.id}.txt"
            ),
        )

        # Create ProjectArtifact
        artifact = ProjectArtifact(
            project_id=job.project_id,
            artifact_type=ExampleArtifact.artifact_type,
            descriptor_job_id=job.id,
            design_job_id=None,
            author=get_username(),
            artifact=ExampleArtifact(
                summary_file=stored_summary,
            ),
        )

        return descriptor_values + [artifact]


class ResidueCountingTask(WorkflowTask, ResidueCountingDescriptorWorkflow, ABC):
    """Descriptor workflow that counts residues in designs."""

    def run(self, execdir: str, scheduler: TaskScheduler) -> None:
        """Count residues in each design and save results to files."""
        designs = db.select(Design, id__in=self.design_ids)
        lengths_by_design = self.compute_lengths(designs)

        # Save results to CSV
        df = pd.DataFrame({"count": lengths_by_design})
        df.index.name = "design_id"
        df.to_csv(os.path.join(execdir, "residue_counts.csv"), index=True)

        # Create artifact file
        with open(os.path.join(execdir, "residue_summary.txt"), "w") as f:
            f.write(f"Residue counting completed for {len(df)} designs\n")
            f.write(f"Chains analyzed: {','.join(self.chains)}\n")
            for design_id, count in lengths_by_design.items():
                f.write(f"  {design_id}: {count} residues\n")

    @abstractmethod
    def compute_lengths(self, designs: list[Design]) -> dict[str, int]:
        """Compute residue counts for each design. To be implemented by subclasses."""
        raise NotImplementedError()


@WorkflowTypes.register("BioPython Residue Counting")
@dataclass
class BioPythonResidueCountingTask(ResidueCountingTask):
    """Descriptor workflow that counts residues in designs."""

    def compute_lengths(self, designs: list[Design]) -> dict[str, int]:
        from Bio import PDB
        import io

        # Load designs and count residues
        results = {}

        for design in designs:
            pdb_str = storage.read_file_str(design.structure_path)

            # Count residues by parsing PDB
            parser = PDB.PDBParser(QUIET=True)
            structure = parser.get_structure("design", io.StringIO(pdb_str))

            # Count residues in specified chains
            residue_count = 0
            for chain_id in self.chains:
                try:
                    chain = structure[0][chain_id]
                    # Count only standard residues (not waters, heteroatoms)
                    residue_count += sum(1 for res in chain if res.id[0] == " ")
                except KeyError:
                    # Chain not found
                    pass

            results[design.id] = residue_count

        return results


def test_residue_counting_descriptor_workflow(project_data):
    """Test ResidueCountingDescriptorWorkflow with TaskScheduler."""
    from ovo import schedulers
    import tempfile

    project, project_round, custom_pool = project_data

    # Create and register a SyncTaskScheduler for this test
    test_workdir = tempfile.mkdtemp(prefix="ovo_test_descriptor_scheduler_")
    test_scheduler = SyncTaskScheduler(
        name="Test Descriptor Scheduler",
        workdir=test_workdir,
        allow_submit=True,
    )
    schedulers["test_descriptor_scheduler"] = test_scheduler

    try:
        # First create a pool with designs using HelloWorld workflow
        workflow_names = WorkflowTypes.get_subclass_names(GreetingsDesignWorkflow)
        assert workflow_names == ["Hello World"]
        MyGreetingWorkflow = WorkflowTypes.get(workflow_names[0])
        workflow = MyGreetingWorkflow(message="Test design for descriptor")
        workflow.validate()
        workflow.get_table_row()

        design_job, pool = design_logic.submit_design_workflow(
            workflow=workflow,
            pool_name="Descriptor Test Pool",
            pool_description="Pool for testing descriptor workflow",
            scheduler_key="test_descriptor_scheduler",
            round_id=project_round.id,
        )

        # Verify job was created
        jobs = design_logic.get_design_jobs_table(id=pool.id)
        assert len(jobs) == 1

        # Process results
        pool = design_logic.process_results(design_job)

        # Get design IDs
        designs = db.Design.select(pool_id=pool.id)
        design_ids = [d.id for d in designs]
        assert len(design_ids) == 1

        # Verify HelloWorld design was created correctly
        design = designs[0]
        assert design.id == f"ovo_{pool.id}_hello_world"
        assert design.accepted == True
        assert design.structure_path is not None

        # Verify design spec
        assert len(design.spec.chains) == 1
        assert design.spec.chains[0].chain_ids == ["A"]
        assert design.spec.chains[0].type == "protein"
        assert design.spec.chains[0].sequence == "A"

        # Verify PDB file exists and contains message
        pdb_str = storage.read_file_str(design.structure_path)
        assert "Test design for descriptor" in pdb_str
        assert "ATOM" in pdb_str
        assert "ALA A" in pdb_str

        # Verify descriptor value was also created by HelloWorld (using MESSAGE_LENGTH)
        message_length_values = db.DescriptorValue.select(descriptor_key=MESSAGE_LENGTH.key, design_id=design.id)
        assert len(message_length_values) == 1
        assert message_length_values[0].value == str(len("Test design for descriptor"))
        assert message_length_values[0].chains == "A"
        assert message_length_values[0].descriptor_job_id == design_job.id

        # Now run descriptor workflow on these designs
        counting_workflows = WorkflowTypes.get_subclass_names(ResidueCountingDescriptorWorkflow)
        MyCountingWorkflow = WorkflowTypes.get(counting_workflows[0])
        descriptor_workflow = MyCountingWorkflow(
            chains=["A"],
            design_ids=design_ids,
        )
        descriptor_workflow.validate()

        # Submit descriptor workflow
        descriptor_job = descriptor_logic.submit_descriptor_workflow(
            workflow=descriptor_workflow,
            scheduler_key="test_descriptor_scheduler",
            project_id=project.id,
        )

        # Process descriptor results
        descriptor_logic.process_results(descriptor_job)

        # Verify descriptor values were created
        residue_counts = db.select_descriptor_values(RESIDUE_COUNT.key, design_ids)
        assert len(residue_counts) == 1
        assert residue_counts.iloc[0] == 1  # HelloWorld has 1 residue (ALA)

        # Verify the descriptor value in database
        descriptor_values = db.DescriptorValue.select(descriptor_key=RESIDUE_COUNT.key, design_id=design_ids[0])
        assert len(descriptor_values) == 1
        assert descriptor_values[0].value == "1"
        assert descriptor_values[0].chains == "A"

        # Verify artifact was created
        artifacts = db.ProjectArtifact.select(descriptor_job_id=descriptor_job.id)
        assert len(artifacts) == 1, f"Expected 1 artifact, found {len(artifacts)}"
        artifact = artifacts[0]
        assert artifact.project_id == project.id
        assert artifact.descriptor_job_id == descriptor_job.id
        assert artifact.design_job_id is None
        assert isinstance(artifact.artifact, ExampleArtifact)

        # Verify artifact file was stored in permanent storage
        assert artifact.artifact.summary_file.startswith("project/")

        # Verify we can read the file from storage
        summary_content = storage.read_file_str(artifact.artifact.summary_file)
        assert "Residue counting completed for 1 designs" in summary_content
        assert "Chains analyzed: A" in summary_content
        assert design_ids[0] in summary_content
        assert "1 residues" in summary_content

    finally:
        # Clean up: remove test scheduler from registry
        if "test_descriptor_scheduler" in schedulers:
            del schedulers["test_descriptor_scheduler"]
        # Clean up: remove temporary directory
        if os.path.exists(test_workdir):
            shutil.rmtree(test_workdir)


def test_sync_task_scheduler_error_handling():
    """Test that SyncTaskScheduler handles errors correctly without in-memory state."""
    import tempfile

    # Create a task that always fails
    @task
    def failing_task(execdir: str):
        raise ValueError("This task always fails!")

    # Create scheduler
    workdir = tempfile.mkdtemp(prefix="ovo_test_error_")
    scheduler = SyncTaskScheduler(name="Error Test Scheduler", workdir=workdir)

    try:
        # Submit failing task (use full module path)
        task_name = f"{__name__}.failing_task"
        job_id = scheduler.submit(task_name, params={})

        # Job should exist but be marked as failed
        result = scheduler.get_result(job_id)
        assert result == False, "Job should be marked as failed"

        # Should have error log
        log = scheduler.get_log(job_id)
        assert log is not None, "Should have error log"
        assert "ValueError" in log, "Error log should contain exception type"
        assert "This task always fails!" in log, "Error log should contain error message"

        # Status should be Failed
        status = scheduler.get_status_label(job_id)
        assert status == "Failed", f"Status should be 'Failed', got '{status}'"

        # Failed message should contain error
        failed_msg = scheduler.get_failed_message(job_id)
        assert "ValueError" in failed_msg, "Failed message should contain error"
    finally:
        # Clean up: remove temporary directory
        if os.path.exists(workdir):
            shutil.rmtree(workdir)
