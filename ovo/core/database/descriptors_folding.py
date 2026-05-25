"""Descriptors for folding workflows (Boltz, AlphaFold, etc.)"""

from ovo.core.database.descriptors_refolding import REFOLDING_DESCRIPTORS
from ovo.core.database.models import (
    NumericGlobalDescriptor,
    StructureFileDescriptor,
    FileDescriptor,
)

# Structure path descriptors
BOLTZ_PREDICTED_STRUCTURE_PATH = StructureFileDescriptor(
    name="Boltz prediction",
    description="Structure predicted by Boltz structure prediction",
    tool="Boltz",
    key="folding|boltz2|predicted_structure_path",
    structure_type="prediction",
    b_factor_value="fractional_plddt",
)

# Boltz confidence metrics
BOLTZ_PLDDT = NumericGlobalDescriptor(
    name="Boltz pLDDT",
    description="Average pLDDT confidence score of the whole structure (0 = worst, 100 = best)",
    tool="Boltz",
    key="folding|boltz2|boltz_plddt",
    min_value=0,
    max_value=100,
    comparison="higher_is_better",
    color_scale="plddt",
)

BOLTZ_PTM = NumericGlobalDescriptor(
    name="Boltz pTM",
    description="Predicted TM score of the full structure (0 = worst, 1 = best)",
    tool="Boltz",
    key="folding|boltz2|boltz_ptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

BOLTZ_IPTM = NumericGlobalDescriptor(
    name="Boltz ipTM",
    description="Interface predicted TM score (0 = worst, 1 = best)",
    tool="Boltz",
    key="folding|boltz2|boltz_iptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

BOLTZ_CONFIDENCE = NumericGlobalDescriptor(
    name="Boltz Confidence",
    description="Boltz overall confidence score (0 = worst, 1 = best)",
    tool="Boltz",
    key="folding|boltz2|boltz_confidence",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

# All descriptors list
DESCRIPTORS = [
    BOLTZ_PREDICTED_STRUCTURE_PATH,
    BOLTZ_PLDDT,
    BOLTZ_PTM,
    BOLTZ_IPTM,
    BOLTZ_CONFIDENCE,
]

DESCRIPTORS_BY_KEY = {d.key: d for d in DESCRIPTORS}

FOLDING_DESCRIPTORS = [d for d in DESCRIPTORS if not isinstance(d, FileDescriptor)] + REFOLDING_DESCRIPTORS
