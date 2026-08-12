from typing import List, Callable

from ovo.core.database import DescriptorJob
from ovo.core.database.descriptors_rfdiffusion import PYROSETTA_INTERFACE_TARGET_RESIDUES_AA, PYDSSP_STRING
from ovo.core.database.models import DescriptorWorkflow, WorkflowParams, WorkflowTypes, Design, ResidueNumberDescriptor
from dataclasses import dataclass, field

# Minimum sequence length for Foldseek k-mer prefilter mode (prefilter_mode=0)
# Sequences shorter than this will be skipped in easy-search with default prefilter
FOLDSEEK_KMER_PREFILTER_MIN_LENGTH = 14


@dataclass
class ProteinClusteringWorkflow(DescriptorWorkflow):
    """
    Class that provides abstraction for protein clustering workflows and defines necessary variables for all
    clustering methods.
    """

    # Number of neighbors for UMAP dimensionality reduction
    n_neighbors: List[int] = field(default_factory=lambda: [10, 30, 100])
    tool_key: str | None = None
    params: WorkflowParams = field(default_factory=WorkflowParams)

    @classmethod
    def get_registered_workflow_names(cls) -> list[str]:
        """Get all registered workflow names that are ProteinClusteringWorkflow subclasses"""
        from ovo.core.database.models import WorkflowTypes

        names = []
        for workflow_name, workflow_class in WorkflowTypes._registry.items():
            # Check if this registered workflow is a subclass of ProteinClusteringWorkflow
            try:
                if issubclass(workflow_class, cls):
                    names.append(workflow_name)
            except TypeError:
                # Not a class, skip
                continue
        return names

    def validate(self):
        super().validate()
        if self.tool_key is None:
            raise ValueError("ProteinClusteringWorkflow requires a ProteinClusteringTool to be specified.")
        if self.tool_key not in PROTEIN_CLUSTERING_TOOLS_BY_KEY.keys():
            raise ValueError(
                f"Invalid Protein Clustering tool '{self.tool}', available tools: {', '.join(PROTEIN_CLUSTERING_TOOLS_BY_KEY.keys())}"
            )


@dataclass(frozen=True)
class ProteinClusteringTool:
    name: str = None
    tool_key: str = None
    supports_conda: bool = False


FOLDSEEK_UMAP_PIPELINE = ProteinClusteringTool(
    name="Foldseek with UMAP",
    tool_key="foldseek_clustering",
    supports_conda=True,
)

SEQUENCE_HIERARCHICAL_UMAP_PIPELINE = ProteinClusteringTool(
    name="Sequence identity with hierarchical clustering and UMAP",
    tool_key="sequence_hierarchical_clustering",
    supports_conda=True,
)

RMSD_HIERARCHICAL_UMAP_PIPELINE = ProteinClusteringTool(
    name="CEAlign RMSD similarity with hierarchical clustering and UMAP",
    tool_key="rmsd_hierarchical_clustering",
    supports_conda=True,
)

SECONDARY_STRUCTURE_UMAP_PIPELINE = ProteinClusteringTool(
    name="Secondary structure similarity with hierarchical clustering and UMAP",
    tool_key="secondary_structure_hierarchical_clustering",
    supports_conda=True,
)

INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE = ProteinClusteringTool(
    name="Interface residues Jaccard similarity with hierarchical clustering and UMAP",
    tool_key="interface_residues_hierarchical_clustering",
    supports_conda=True,
)


@dataclass
class FoldseekParams(WorkflowParams):
    e: float = 10.0
    alignment_type: int = 2
    c: float = 0.0
    tmscore_threshold: float = 0.0
    exhaustive_search: bool = False
    embedding_metric: str = "qtmscore"
    min_seq_id: float = 0.0
    s: float = 9.5
    prefilter_mode: int = 0


@dataclass
class HierarchicalClusteringParams(WorkflowParams):
    similarity_method: str  # sequence, secondary_structure, interface_residues, rmsd
    linkage_method: str = "average"  # single, complete, average, ward
    threshold: float = None
    criterion: str = "distance"  # distance or maxclust
    cyclic: bool = False


@WorkflowTypes.register("Foldseek Clustering workflow")
@dataclass
class FoldseekClusteringWorkflow(ProteinClusteringWorkflow):
    tool_key: str = FOLDSEEK_UMAP_PIPELINE.tool_key
    designs_target: List[Design] = field(default_factory=list)
    params: FoldseekParams = field(default_factory=FoldseekParams, metadata=dict(tool_name="Foldseek Clustering"))

    def get_pipeline_name(self) -> str:
        return "ovo.protein-clustering"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.descriptor_logic import prepare_foldseek_clustering_workflow_params

        return prepare_foldseek_clustering_workflow_params(self, workdir=workdir)

    def process_results(self, job: DescriptorJob, callback: Callable = None):
        from ovo import get_scheduler
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values
        import re
        from sqlalchemy.orm.attributes import flag_modified

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse
            filenames={"protein_clustering|foldseek_clustering": "final_clustering"},
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )

        # Extract warnings from job logs (check both main log and task logs)
        scheduler = get_scheduler(job.scheduler_key)

        # Check main job log
        warning_regex = r"\[Warning\]\s+(.+?)(?=\n|$)"
        log = scheduler.get_log(job.job_id)
        if log:
            warning_lines = re.findall(warning_regex, log, re.IGNORECASE)
            for warning in warning_lines:
                if warning not in job.warnings:
                    job.warnings.append(warning)

        # Check individual task logs
        tasks = scheduler.get_tasks(job.job_id)
        if tasks is not None and not tasks.empty:
            for _, task in tasks.iterrows():
                task_log = scheduler.get_log(job.job_id, task_id=task["task_id"])
                if task_log:
                    warning_lines = re.findall(warning_regex, task_log, re.IGNORECASE)
                    for warning in warning_lines:
                        warning_with_task = f"{task['name']}: {warning}"
                        if warning_with_task not in job.warnings:
                            job.warnings.append(warning_with_task)

        # Mark warnings as modified so SQLAlchemy persists changes
        if job.warnings:
            flag_modified(job, "warnings")

        return descriptor_values + [job]

    def validate(self):
        super().validate()
        if len(self.chains) > 1:
            raise NotImplementedError("Currently only single chain clustering is supported.")


@dataclass
class BaseHierarchicalClusteringWorkflow(ProteinClusteringWorkflow):
    designs_target: List[Design] = field(default_factory=list)
    params: HierarchicalClusteringParams = field(default_factory=HierarchicalClusteringParams)
    requires_structures: bool = False  # Whether this workflow requires structure files
    max_distance_matrix_designs: int = 5000  # Maximum number of designs to save distance matrix for

    def get_pipeline_name(self) -> str:
        return "ovo.protein-clustering"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.descriptor_logic import prepare_hierarchical_clustering_workflow_params

        return prepare_hierarchical_clustering_workflow_params(self, workdir=workdir)

    def process_results(self, job: DescriptorJob, callback: Callable = None):
        from ovo import db, storage, get_scheduler
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values
        from ovo.core.database.models import ProjectArtifact, DistanceMatrixArtifact
        import os

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse
            filenames={f"protein_clustering|{self.tool_key}": "final_clustering"},
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )

        # Save distance matrix as artifact if small enough
        num_designs = len(self.design_ids)
        if num_designs <= self.max_distance_matrix_designs:
            scheduler = get_scheduler(job.scheduler_key)
            output_dir = scheduler.get_output_dir(job.job_id)

            # Distance matrix filename from pipeline
            matrix_filename = f"contig1_batch1/{self.params.similarity_method}_distance_matrix.csv.gz"
            local_matrix_path = os.path.join(output_dir, matrix_filename)

            if os.path.exists(local_matrix_path):
                # Upload to storage
                storage_path = f"{job.project_id}/{job.id}/distance_matrix_{self.params.similarity_method}.csv.gz"
                storage.store_file_path(local_matrix_path, storage_path)

                # Create artifact
                artifact = DistanceMatrixArtifact(
                    file_path=storage_path,
                )

                project_artifact = ProjectArtifact(
                    project_id=job.project_id,
                    descriptor_job_id=job.id,
                    artifact_type=artifact.artifact_type,
                    artifact=artifact,
                    author=job.author,
                )
                db.save(project_artifact)

        return descriptor_values + [job]

    def validate(self):
        super().validate()

        if self.params.threshold is None:
            raise ValueError("Threshold value must be specified for hierarchical clustering workflows.")
        if self.params.threshold < 0:
            raise ValueError("Threshold value must be non-negative.")

        criterion = getattr(self.params, "criterion", None)
        if criterion == "maxclust":
            if not isinstance(self.params.threshold, int) or self.params.threshold < 1:
                raise ValueError("Threshold value must be a positive integer for maxclust criterion.")
        elif not (0 <= self.params.threshold <= 1) and self.params.similarity_method in [
            "sequence",
            "secondary_structure",
            "interface_residues",
        ]:
            raise ValueError("Threshold value must be between 0 and 1 for similarity-based clustering methods.")

        # Only validate structures for workflows that require them
        if self.requires_structures:
            from ovo import db

            designs = db.select(Design, id__in=self.design_ids)
            designs_without_structures = [d.id for d in designs if not d.structure_path]
            if designs_without_structures:
                raise ValueError(
                    f"This clustering workflow requires structure files, "
                    f"but {len(designs_without_structures)} design(s) have no structure_path: "
                    f"{', '.join(designs_without_structures[:5])}"
                    f"{'...' if len(designs_without_structures) > 5 else ''}"
                )


@WorkflowTypes.register("Sequence Hierarchical Clustering workflow")
@dataclass
class SequenceHierarchicalClusteringWorkflow(BaseHierarchicalClusteringWorkflow):
    tool_key: str = SEQUENCE_HIERARCHICAL_UMAP_PIPELINE.tool_key
    params: HierarchicalClusteringParams = field(
        default_factory=lambda: HierarchicalClusteringParams(similarity_method="sequence", threshold=0.5),
        metadata=dict(tool_name="Sequence Hierarchical Clustering"),
    )
    requires_structures: bool = False

    def validate(self):
        from ovo import db

        super().validate()

        # Sequence clustering can work without structures, but needs sequences in spec
        designs = db.select(Design, id__in=self.design_ids)
        designs_without_sequences = []
        for design in designs:
            if not design.spec or not design.spec.chains:
                designs_without_sequences.append(design.id)
                continue
            # Check if at least one chain has a sequence
            has_sequence = any(
                chain.sequence
                for chain in design.spec.chains
                for chain_id in chain.chain_ids
                if chain_id in self.chains
            )
            if not has_sequence:
                designs_without_sequences.append(design.id)

        if designs_without_sequences:
            raise ValueError(
                f"Sequence hierarchical clustering requires all designs to have sequences in their spec, "
                f"but {len(designs_without_sequences)} design(s) are missing sequences: "
                f"{', '.join(designs_without_sequences[:5])}"
                f"{'...' if len(designs_without_sequences) > 5 else ''}"
            )


@WorkflowTypes.register("CEAlign RMSD Hierarchical Clustering workflow")
@dataclass
class RMSDHierarchicalClusteringWorkflow(BaseHierarchicalClusteringWorkflow):
    tool_key: str = RMSD_HIERARCHICAL_UMAP_PIPELINE.tool_key
    params: HierarchicalClusteringParams = field(
        default_factory=lambda: HierarchicalClusteringParams(similarity_method="rmsd", threshold=5.0),
        metadata=dict(tool_name="RMSD Hierarchical Clustering"),
    )
    requires_structures: bool = True


@WorkflowTypes.register("Secondary Structure Hierarchical Clustering workflow")
@dataclass
class SecondaryStructureHierarchicalClusteringWorkflow(BaseHierarchicalClusteringWorkflow):
    tool_key: str = SECONDARY_STRUCTURE_UMAP_PIPELINE.tool_key
    params: HierarchicalClusteringParams = field(
        default_factory=lambda: HierarchicalClusteringParams(similarity_method="secondary_structure", threshold=0.2),
        metadata=dict(tool_name="Secondary Structure Hierarchical Clustering"),
    )
    requires_structures: bool = False

    def validate(self):
        from ovo import db

        super().validate()

        # Check that all designs have secondary structure descriptor calculated
        descriptor_values = db.select_descriptor_values(PYDSSP_STRING.key, design_ids=self.design_ids)
        if descriptor_values.isna().any():
            designs_with_na_descriptor = descriptor_values[descriptor_values.isna()].index.tolist()

            raise ValueError(
                f"Designs are missing required descriptor '{PYDSSP_STRING.key}' for Secondary Structure Hierarchical Clustering. "
                f"Please calculate this descriptor for these designs before running the workflow: {', '.join(designs_with_na_descriptor)}"
            )


@WorkflowTypes.register("Interface Residues Hierarchical Clustering workflow")
@dataclass
class InterfaceResiduesHierarchicalClusteringWorkflow(BaseHierarchicalClusteringWorkflow):
    tool_key: str = INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE.tool_key
    designs_target: List[Design] = field(default_factory=list)
    params: HierarchicalClusteringParams = field(
        default_factory=lambda: HierarchicalClusteringParams(similarity_method="interface_residues", threshold=0.5),
        metadata=dict(tool_name="Interface Residues Hierarchical Clustering"),
    )
    requires_structures: bool = False
    input_descriptor_key: str = PYROSETTA_INTERFACE_TARGET_RESIDUES_AA.key

    def validate(self):
        from ovo import db

        super().validate()

        # Check that all designs have interface residues descriptor calculated
        descriptor_values = db.select_descriptor_values(self.input_descriptor_key, design_ids=self.design_ids)
        if descriptor_values.isna().any():
            designs_with_na_descriptor = descriptor_values[descriptor_values.isna()].index.tolist()

            raise ValueError(
                f"Designs are missing required descriptor '{self.input_descriptor_key}' for Interface Residues Hierarchical Clustering. "
                f"Please calculate this descriptor for these designs before running the workflow: {', '.join(designs_with_na_descriptor)}"
            )


PROTEIN_CLUSTERING_TOOLS = [
    FOLDSEEK_UMAP_PIPELINE,
    SEQUENCE_HIERARCHICAL_UMAP_PIPELINE,
    RMSD_HIERARCHICAL_UMAP_PIPELINE,
    SECONDARY_STRUCTURE_UMAP_PIPELINE,
    INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE,
]
PROTEIN_CLUSTERING_TOOLS_BY_KEY = {tool.tool_key: tool for tool in PROTEIN_CLUSTERING_TOOLS}

CLUSTERING_WORKFLOWS_BY_TOOL_KEY = {
    FOLDSEEK_UMAP_PIPELINE.tool_key: FoldseekClusteringWorkflow,
    SEQUENCE_HIERARCHICAL_UMAP_PIPELINE.tool_key: SequenceHierarchicalClusteringWorkflow,
    RMSD_HIERARCHICAL_UMAP_PIPELINE.tool_key: RMSDHierarchicalClusteringWorkflow,
    SECONDARY_STRUCTURE_UMAP_PIPELINE.tool_key: SecondaryStructureHierarchicalClusteringWorkflow,
    INTERFACE_RESIDUES_HIERARCHICAL_PIPELINE.tool_key: InterfaceResiduesHierarchicalClusteringWorkflow,
}
