from ovo.core.database.models import Descriptor, NumericGlobalDescriptor, StringGlobalDescriptor

# FOLDSEEK

FOLDSEEK_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in FoldSeek",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|cluster_repr",
    required_descriptor_job=True,
)
FOLDSEEK_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|cluster_id",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_x_10",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_y_10",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_x_30",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_y_30",
    required_descriptor_job=True,
)

FOLDSEEK_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_x_100",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Foldseek",
    key="protein_clustering|foldseek_clustering|umap_y_100",
    required_descriptor_job=True,
)
FOLDSEEK_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="Foldseek",
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


SEQ_HIERARCHICAL_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in Sequence Hierarchical Clustering",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|cluster_repr",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|cluster_id",
    required_descriptor_job=True,
)

SEQ_HIERARCHICAL_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_x_10",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_y_10",
    required_descriptor_job=True,
)

SEQ_HIERARCHICAL_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_x_30",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_y_30",
    required_descriptor_job=True,
)

SEQ_HIERARCHICAL_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_x_100",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|umap_y_100",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="Sequence Hierarchical Clustering",
    key="protein_clustering|sequence_hierarchical_clustering|error",
    required_descriptor_job=True,
)
SEQ_HIERARCHICAL_CLUSTERING_DESCRIPTORS = [
    SEQ_HIERARCHICAL_REPR_CLUSTER,
    SEQ_HIERARCHICAL_REPR_CLUSTER_ID,
    SEQ_HIERARCHICAL_NEIGHBORS_X_10,
    SEQ_HIERARCHICAL_NEIGHBORS_Y_10,
    SEQ_HIERARCHICAL_NEIGHBORS_X_30,
    SEQ_HIERARCHICAL_NEIGHBORS_Y_30,
    SEQ_HIERARCHICAL_NEIGHBORS_X_100,
    SEQ_HIERARCHICAL_NEIGHBORS_Y_100,
    SEQ_HIERARCHICAL_NEIGHBORS_ERROR,
]

RMSD_HIERARCHICAL_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in RMSD Hierarchical Clustering",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|cluster_repr",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|cluster_id",
    required_descriptor_job=True,
)

RMSD_HIERARCHICAL_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_x_10",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_y_10",
    required_descriptor_job=True,
)

RMSD_HIERARCHICAL_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_x_30",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_y_30",
    required_descriptor_job=True,
)

RMSD_HIERARCHICAL_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_x_100",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|umap_y_100",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="CEAlign RMSD Hierarchical Clustering",
    key="protein_clustering|rmsd_hierarchical_clustering|error",
    required_descriptor_job=True,
)
RMSD_HIERARCHICAL_CLUSTERING_DESCRIPTORS = [
    RMSD_HIERARCHICAL_REPR_CLUSTER,
    RMSD_HIERARCHICAL_REPR_CLUSTER_ID,
    RMSD_HIERARCHICAL_NEIGHBORS_X_10,
    RMSD_HIERARCHICAL_NEIGHBORS_Y_10,
    RMSD_HIERARCHICAL_NEIGHBORS_X_30,
    RMSD_HIERARCHICAL_NEIGHBORS_Y_30,
    RMSD_HIERARCHICAL_NEIGHBORS_X_100,
    RMSD_HIERARCHICAL_NEIGHBORS_Y_100,
    RMSD_HIERARCHICAL_NEIGHBORS_ERROR,
]

DSSP_HIERARCHICAL_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in Secondary Structure Hierarchical Clustering",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|cluster_repr",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|cluster_id",
    required_descriptor_job=True,
)

DSSP_HIERARCHICAL_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_x_10",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_y_10",
    required_descriptor_job=True,
)

DSSP_HIERARCHICAL_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_x_30",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_y_30",
    required_descriptor_job=True,
)

DSSP_HIERARCHICAL_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_x_100",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|umap_y_100",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="Secondary Structure Hierarchical Clustering",
    key="protein_clustering|secondary_structure_hierarchical_clustering|error",
    required_descriptor_job=True,
)
DSSP_HIERARCHICAL_CLUSTERING_DESCRIPTORS = [
    DSSP_HIERARCHICAL_REPR_CLUSTER,
    DSSP_HIERARCHICAL_REPR_CLUSTER_ID,
    DSSP_HIERARCHICAL_NEIGHBORS_X_10,
    DSSP_HIERARCHICAL_NEIGHBORS_Y_10,
    DSSP_HIERARCHICAL_NEIGHBORS_X_30,
    DSSP_HIERARCHICAL_NEIGHBORS_Y_30,
    DSSP_HIERARCHICAL_NEIGHBORS_X_100,
    DSSP_HIERARCHICAL_NEIGHBORS_Y_100,
    DSSP_HIERARCHICAL_NEIGHBORS_ERROR,
]

INTERFACE_HIERARCHICAL_REPR_CLUSTER = StringGlobalDescriptor(
    name="Representative Structure of Cluster",
    description="Cluster identifier for each reference cluster in Interface Residues Hierarchical Clustering",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|cluster_repr",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID = NumericGlobalDescriptor(
    name="Representative Cluster ID",
    description="Unique cluster identifier",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|cluster_id",
    required_descriptor_job=True,
)

INTERFACE_HIERARCHICAL_NEIGHBORS_X_10 = NumericGlobalDescriptor(
    name="UMAP X (10 neighbors)",
    description="X coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_x_10",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_NEIGHBORS_Y_10 = NumericGlobalDescriptor(
    name="UMAP Y (10 neighbors)",
    description="Y coordinate of UMAP embedding with 10 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_y_10",
    required_descriptor_job=True,
)

INTERFACE_HIERARCHICAL_NEIGHBORS_X_30 = NumericGlobalDescriptor(
    name="UMAP X (30 neighbors)",
    description="X coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_x_30",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_NEIGHBORS_Y_30 = NumericGlobalDescriptor(
    name="UMAP Y (30 neighbors)",
    description="Y coordinate of UMAP embedding with 30 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_y_30",
    required_descriptor_job=True,
)

INTERFACE_HIERARCHICAL_NEIGHBORS_X_100 = NumericGlobalDescriptor(
    name="UMAP X (100 neighbors)",
    description="X coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_x_100",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_NEIGHBORS_Y_100 = NumericGlobalDescriptor(
    name="UMAP Y (100 neighbors)",
    description="Y coordinate of UMAP embedding with 100 nearest neighbors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|umap_y_100",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_NEIGHBORS_ERROR = StringGlobalDescriptor(
    name="Errors connected with protein clustering workflow",
    description="List of errors",
    tool="Interface Residues Hierarchical Clustering",
    key="protein_clustering|interface_residues_hierarchical_clustering|error",
    required_descriptor_job=True,
)
INTERFACE_HIERARCHICAL_CLUSTERING_DESCRIPTORS = [
    INTERFACE_HIERARCHICAL_REPR_CLUSTER,
    INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID,
    INTERFACE_HIERARCHICAL_NEIGHBORS_X_10,
    INTERFACE_HIERARCHICAL_NEIGHBORS_Y_10,
    INTERFACE_HIERARCHICAL_NEIGHBORS_X_30,
    INTERFACE_HIERARCHICAL_NEIGHBORS_Y_30,
    INTERFACE_HIERARCHICAL_NEIGHBORS_X_100,
    INTERFACE_HIERARCHICAL_NEIGHBORS_Y_100,
    INTERFACE_HIERARCHICAL_NEIGHBORS_ERROR,
]

PROTEIN_CLUSTERING_DESCRIPTORS = (
    FOLDSEEK_CLUSTERING_DESCRIPTORS
    + SEQ_HIERARCHICAL_CLUSTERING_DESCRIPTORS
    + RMSD_HIERARCHICAL_CLUSTERING_DESCRIPTORS
    + DSSP_HIERARCHICAL_CLUSTERING_DESCRIPTORS
    + INTERFACE_HIERARCHICAL_CLUSTERING_DESCRIPTORS
)
PROTEIN_CLUSTERING_DESCRIPTORS_BY_KEY = {d.key: d for d in PROTEIN_CLUSTERING_DESCRIPTORS}

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

# NOTE: The references below map the clustering tool to the representative cluster descriptors
# For each tool specify the descriptor for the representative structure and the representative cluster ID
CLUSTER_INFO_REFERENCES = {
    "foldseek_clustering": {"representative": FOLDSEEK_REPR_CLUSTER, "id": FOLDSEEK_REPR_CLUSTER_ID},
    "sequence_hierarchical_clustering": {
        "representative": SEQ_HIERARCHICAL_REPR_CLUSTER,
        "id": SEQ_HIERARCHICAL_REPR_CLUSTER_ID,
    },
    "rmsd_hierarchical_clustering": {
        "representative": RMSD_HIERARCHICAL_REPR_CLUSTER,
        "id": RMSD_HIERARCHICAL_REPR_CLUSTER_ID,
    },
    "secondary_structure_hierarchical_clustering": {
        "representative": DSSP_HIERARCHICAL_REPR_CLUSTER,
        "id": DSSP_HIERARCHICAL_REPR_CLUSTER_ID,
    },
    "interface_residues_hierarchical_clustering": {
        "representative": INTERFACE_HIERARCHICAL_REPR_CLUSTER,
        "id": INTERFACE_HIERARCHICAL_REPR_CLUSTER_ID,
    },
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
    "Sequence Hierarchical & UMAP on 10 neighbours": {
        "x": SEQ_HIERARCHICAL_NEIGHBORS_X_10,
        "y": SEQ_HIERARCHICAL_NEIGHBORS_Y_10,
    },
    "Sequence Hierarchical & UMAP on 30 neighbours": {
        "x": SEQ_HIERARCHICAL_NEIGHBORS_X_30,
        "y": SEQ_HIERARCHICAL_NEIGHBORS_Y_30,
    },
    "Sequence Hierarchical & UMAP on 100 neighbours": {
        "x": SEQ_HIERARCHICAL_NEIGHBORS_X_100,
        "y": SEQ_HIERARCHICAL_NEIGHBORS_Y_100,
    },
    "RMSD Hierarchical & UMAP on 10 neighbours": {
        "x": RMSD_HIERARCHICAL_NEIGHBORS_X_10,
        "y": RMSD_HIERARCHICAL_NEIGHBORS_Y_10,
    },
    "RMSD Hierarchical & UMAP on 30 neighbours": {
        "x": RMSD_HIERARCHICAL_NEIGHBORS_X_30,
        "y": RMSD_HIERARCHICAL_NEIGHBORS_Y_30,
    },
    "RMSD Hierarchical & UMAP on 100 neighbours": {
        "x": RMSD_HIERARCHICAL_NEIGHBORS_X_100,
        "y": RMSD_HIERARCHICAL_NEIGHBORS_Y_100,
    },
    "Secondary Structure Hierarchical & UMAP on 10 neighbours": {
        "x": DSSP_HIERARCHICAL_NEIGHBORS_X_10,
        "y": DSSP_HIERARCHICAL_NEIGHBORS_Y_10,
    },
    "Secondary Structure Hierarchical & UMAP on 30 neighbours": {
        "x": DSSP_HIERARCHICAL_NEIGHBORS_X_30,
        "y": DSSP_HIERARCHICAL_NEIGHBORS_Y_30,
    },
    "Secondary Structure Hierarchical & UMAP on 100 neighbours": {
        "x": DSSP_HIERARCHICAL_NEIGHBORS_X_100,
        "y": DSSP_HIERARCHICAL_NEIGHBORS_Y_100,
    },
    "Interface Residues Hierarchical & UMAP on 10 neighbours": {
        "x": INTERFACE_HIERARCHICAL_NEIGHBORS_X_10,
        "y": INTERFACE_HIERARCHICAL_NEIGHBORS_Y_10,
    },
    "Interface Residues Hierarchical & UMAP on 30 neighbours": {
        "x": INTERFACE_HIERARCHICAL_NEIGHBORS_X_30,
        "y": INTERFACE_HIERARCHICAL_NEIGHBORS_Y_30,
    },
    "Interface Residues Hierarchical & UMAP on 100 neighbours": {
        "x": INTERFACE_HIERARCHICAL_NEIGHBORS_X_100,
        "y": INTERFACE_HIERARCHICAL_NEIGHBORS_Y_100,
    },
}
