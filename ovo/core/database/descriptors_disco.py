from ovo.core.database.models import (
    NumericGlobalDescriptor,
    StructureFileDescriptor,
)

DISCO_BACKBONE_STRUCTURE_PATH = StructureFileDescriptor(
    name="DISCO backbone design",
    description="DISCO-generated backbone structure (backbone atoms only, no side chains)",
    tool="DISCO",
    key="disco|disco|backbone_structure_path",
    structure_type="backbone_design",
)

DISCO_PACKED_STRUCTURE_PATH = StructureFileDescriptor(
    name="DISCO packed design",
    description="DISCO design with side chains packed by LigandMPNN",
    tool="DISCO",
    key="disco|disco|packed_structure_path",
    structure_type="sequence_design",
)

SEQUENCE_LENGTH = NumericGlobalDescriptor(
    name="Sequence length",
    description="Number of amino acids in the designed protein sequence",
    tool="DISCO",
    key="disco|sequence|length",
    comparison="does_not_apply",
    min_value=0,
)

LIGANDMPNN_OVERALL_CONFIDENCE = NumericGlobalDescriptor(
    name="LigandMPNN overall confidence",
    description="Overall confidence score from LigandMPNN side-chain packing (0 = worst, 1 = best)",
    tool="LigandMPNN",
    key="disco|ligandmpnn|overall_confidence",
    comparison="higher_is_better",
    min_value=0,
    max_value=1,
)

LIGANDMPNN_LIGAND_CONFIDENCE = NumericGlobalDescriptor(
    name="LigandMPNN ligand confidence",
    description="Ligand confidence score from LigandMPNN side-chain packing (0 = worst, 1 = best)",
    tool="LigandMPNN",
    key="disco|ligandmpnn|ligand_confidence",
    comparison="higher_is_better",
    min_value=0,
    max_value=1,
)

DESCRIPTORS = [
    DISCO_BACKBONE_STRUCTURE_PATH,
    DISCO_PACKED_STRUCTURE_PATH,
    SEQUENCE_LENGTH,
    LIGANDMPNN_OVERALL_CONFIDENCE,
    LIGANDMPNN_LIGAND_CONFIDENCE,
]

_descriptors_by_key = {desc.key: desc for desc in DESCRIPTORS}

PRESETS = [
    {
        "label": "DISCO LigandMPNN Confidence",
        "x": LIGANDMPNN_OVERALL_CONFIDENCE,
        "y": LIGANDMPNN_LIGAND_CONFIDENCE,
    },
]
