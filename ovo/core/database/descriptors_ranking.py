from ovo.core.database.models import Descriptor, NumericGlobalDescriptor

# Ranking descriptors

RANK = NumericGlobalDescriptor(
    name="Rank",
    description="Rank position of the design (1 = best, 2 = second best, etc.)",
    tool="Ranking",
    key="ranking|general|rank",
    comparison="lower_is_better",
    min_value=1,
    required_descriptor_job=True,
)

RANKING_DESCRIPTORS = [
    RANK,
]

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]
