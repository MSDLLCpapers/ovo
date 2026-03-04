from typing import List, Callable

from ovo.core.database import DescriptorJob
from ovo.core.database.models import DescriptorWorkflow, WorkflowParams, WorkflowTypes, Design
from dataclasses import dataclass, field


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


@WorkflowTypes.register("Foldseek Clustering workflow")
@dataclass
class FoldseekClusteringWorkflow(ProteinClusteringWorkflow):
    # TODO: Implement passing target (optional) structures to run foldseek search against these target designs
    # instead of running the search against itself (default is empty list -> in nextflow 'designs_query' copied into designs_target)
    designs_target: List[Design] = field(default_factory=list)
    params: FoldseekParams = field(default_factory=FoldseekParams, metadata=dict(tool_name="Foldseek Clustering"))

    def get_pipeline_name(self) -> str:
        return "ovo.protein-clustering"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.descriptor_logic import prepare_foldseek_clustering_workflow_params

        return prepare_foldseek_clustering_workflow_params(self, workdir=workdir)

    def process_results(self, job: DescriptorJob, callback: Callable = None):
        from ovo import db
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse
            filenames={"protein_clustering|foldseek_clustering": "final_clustering"},
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )

        db.save_all(descriptor_values + [job])
        return descriptor_values + [job]

    def validate(self):
        super().validate()
        if len(self.chains) > 1:
            raise NotImplementedError("Currently only single chain clustering is supported.")


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

PROTEIN_CLUSTERING_TOOLS = [FOLDSEEK_UMAP_PIPELINE]
PROTEIN_CLUSTERING_TOOLS_BY_KEY = {tool.tool_key: tool for tool in PROTEIN_CLUSTERING_TOOLS}

CLUSTERING_WORKFLOWS_BY_TOOL_KEY = {
    FOLDSEEK_UMAP_PIPELINE.tool_key: FoldseekClusteringWorkflow,
}
