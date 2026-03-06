from ovo.core.database.models import Descriptor, NumericGlobalDescriptor, StringGlobalDescriptor

# FOLDSEEK

FOLDSEEK_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in FoldSeek",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|cluster_repr",
    required_descriptor_job=True,
)
FOLDSEEK_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|cluster_id",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_x_10",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_y_10",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_x_30",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_y_30",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_x_100",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|umap_y_100",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="Protein-clustering",
    key="protein_clustering|foldseek_clustering|error",
    required_descriptor_job=True,
)
FOLDSEEK_CLUSTERING_DESCRIPTORS = [
    FOLDSEEK_REPR_CLUSTER,
    FOLDSEEK_REPR_CLUSTER_ID,
    FOLDSEEK_NEIGHBORS_X_10,
    FOLDSEEK_NEIGHBORS_Y_10,
    FOLDSEEK_NEIGHBORS_X_30,
    FOLDSEEK_NEIGHBORS_Y_30,
    FOLDSEEK_NEIGHBORS_X_100,
    FOLDSEEK_NEIGHBORS_Y_100,
    FOLDSEEK_NEIGHBORS_ERROR,
]


PROTEIN_CLUSTERING_DESCRIPTORS = FOLDSEEK_CLUSTERING_DESCRIPTORS
PROTEIN_CLUSTERING_DESCRIPTORS_BY_KEY = {d.key: d for d in PROTEIN_CLUSTERING_DESCRIPTORS}

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

# NOTE: The references below map the clustering tool to the representative cluster descriptors
# For each tool specify the descriptor for the representative structure and the representative cluster ID
CLUSTER_INFO_REFERENCES = {
    "foldseek_clustering": {"representative": FOLDSEEK_REPR_CLUSTER, "id": FOLDSEEK_REPR_CLUSTER_ID}
}

# Distinguished presets from Explorer presets (presets specific to clustering)
CLUSTERING_PRESETS = {
    "Foldseek & UMAP on 10 neighbours": {
        "x": FOLDSEEK_NEIGHBORS_X_10,
        "y": FOLDSEEK_NEIGHBORS_Y_10,
    },
    "Foldseek & UMAP on 30 neighbours": {
        "x": FOLDSEEK_NEIGHBORS_X_30,
        "y": FOLDSEEK_NEIGHBORS_Y_30,
    },
    "Foldseek & UMAP on 100 neighbours": {
        "x": FOLDSEEK_NEIGHBORS_X_100,
        "y": FOLDSEEK_NEIGHBORS_Y_100,
    },
}
