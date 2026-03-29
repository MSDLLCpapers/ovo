from collections import Counter
from ovo.core.database.models import StructureFileDescriptor
from ovo.core.plugins import load_variable, get_extension_points

# Add descriptors and presets from plugins
# key -> { label: str, x: Descriptor, y: Descriptor }
ALL_DESCRIPTORS = []
ALL_DESCRIPTORS_BY_KEY = {}
PRESETS = {}
for descriptor_path in [
    "ovo.core.database.descriptors_refolding",
    "ovo.core.database.descriptors_rfdiffusion",
    "ovo.core.database.descriptors_bindcraft",
    "ovo.core.database.descriptors_proteinqc",
    "ovo.core.database.descriptors_clustering",
] + get_extension_points("ovo.descriptors", str):
    assert isinstance(descriptor_path, str), (
        f"Expected descriptor path to be a string (my_module.descriptor_submodule), got {descriptor_path}"
    )
    module_name = descriptor_path.split(".")[0]
    # Load DESCRIPTORS from plugin and extend ALL_DESCRIPTORS
    _descriptors = load_variable(f"{descriptor_path}:DESCRIPTORS")
    assert isinstance(_descriptors, list), "Expected DESCRIPTORS to be a list, got {} in {}".format(
        type(_descriptors), descriptor_path
    )
    for descriptor in _descriptors:
        if descriptor.key in ALL_DESCRIPTORS:
            raise ValueError(f"Duplicate descriptor key '{descriptor.key}' found in {descriptor_path}")
        ALL_DESCRIPTORS.append(descriptor)
        ALL_DESCRIPTORS_BY_KEY[descriptor.key] = descriptor
    try:
        # Load PRESETS from plugin and update PRESETS
        _presets = load_variable(f"{descriptor_path}:PRESETS")
        assert isinstance(_presets, list), "Expected PRESETS to be list, got {} in {}".format(
            type(_presets), descriptor_path
        )
        for preset in _presets:
            assert "label" in preset and "x" in preset and "y" in preset, (
                "Expected preset to have 'label', 'x', and 'y' fields, got {}".format(preset)
            )
            label = preset["label"]
            PRESETS[f"{descriptor_path} {label}"] = preset
    except AttributeError:
        # No presets defined in the plugin
        pass

ALL_DESCRIPTOR_KEYS = [descriptor.key for descriptor in ALL_DESCRIPTORS]
ALL_DESCRIPTOR_KEYS_SET = frozenset(ALL_DESCRIPTOR_KEYS)
# NumericGlobalDescriptor keys should be unique
if len(ALL_DESCRIPTOR_KEYS) != len(ALL_DESCRIPTOR_KEYS_SET):
    counts = Counter(ALL_DESCRIPTOR_KEYS)
    duplicates = {key: value for key, value in counts.items() if value > 1}
    raise ValueError(f"Duplicate descriptor keys found: {duplicates}")
# Descriptor keys should contain two pipes ("|")
for key in ALL_DESCRIPTOR_KEYS:
    if not key:
        raise ValueError(f"Some descriptors are missing a key: {[d for d in ALL_DESCRIPTORS if not d.key]}")
    if key.count("|") != 2:
        raise ValueError(f"Descriptor key should contain two | separators (pipeline|tool|descriptor), found: {key}")

STRUCTURE_PATH_DESCRIPTORS = [d for d in ALL_DESCRIPTORS if isinstance(d, StructureFileDescriptor)]
SEQUENCE_DESIGN_PATH_DESCRIPTORS = [d for d in STRUCTURE_PATH_DESCRIPTORS if d.structure_type == "sequence_design"]
