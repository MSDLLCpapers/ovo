from ovo.core.database import NumericGlobalDescriptor, Descriptor

POLAR_SASA = NumericGlobalDescriptor(
    name="Polar SASA",
    description="Solvent accessible surface area (SASA) of polar residues in A² calculated using FreeSASA with default settings. ",
    tool="FreeSASA",
    key="__PIPELINE_NAME__|__MODULE_SUFFIX__|Polar",
    # Comparison type (higher_is_better, lower_is_better, does_not_apply)
    # comparison = None
)

NON_POLAR_SASA = NumericGlobalDescriptor(
    name="Non-polar SASA",
    description="Solvent accessible surface area (SASA) of non-polar residues in A² calculated using FreeSASA with default settings. ",
    tool="FreeSASA",
    key="__PIPELINE_NAME__|__MODULE_SUFFIX__|Apolar",
    # Comparison type (higher_is_better, lower_is_better, does_not_apply)
    # comparison = None
)

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

PRESETS = [
    # {
    #     "label": "Example preset",
    #     "x": X_DESCRIPTOR,
    #     "y": Y_DESCRIPTOR,
    # },
]
