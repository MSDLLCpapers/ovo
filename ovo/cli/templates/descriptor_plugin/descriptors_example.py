from ovo.core.database import NumericGlobalDescriptor, Descriptor, FileDescriptor

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

EXAMPLE_FILE = FileDescriptor(  # Note that there are specific such as StructureFileDescriptor subclass that can be used for predicted structures
    name="FreeSASA stats file",
    description="Example file descriptor for files produced by the FreeSASA pipeline.",
    tool="FreeSASA",
    key="__PIPELINE_NAME__|__MODULE_SUFFIX__|sasa_stats",
)

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

PRESETS = [
    # {
    #     "label": "Example preset",
    #     "x": X_DESCRIPTOR,
    #     "y": Y_DESCRIPTOR,
    # },
]
