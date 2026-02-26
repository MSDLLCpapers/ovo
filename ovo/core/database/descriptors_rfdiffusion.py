from ovo.core.database.models import (
    NumericGlobalDescriptor,
    ResidueNumberDescriptor,
    StructureFileDescriptor,
    FileDescriptor,
    CategoricalResidueDescriptor,
    Descriptor,
)

# HOTSPOT INTERFACE METRICS
RADIUS_OF_GYRATION = NumericGlobalDescriptor(
    name="Radius of gyration (backbone)",
    description="Radius of gyration of the CA atoms of the protein",
    tool="Backbone metrics",
    key="rfd_ee|backbone_metrics|radius_of_gyration",
    comparison="lower_is_better",
)

N_CONTACTS_TO_INTERFACE = NumericGlobalDescriptor(
    name="N binder-target backbone contacts",
    description="Number of contacts between binder CA atoms and target CA atoms. "
    "Two CA atoms are in contact if they are within 8A from each other",
    tool="Backbone metrics",
    key="rfd_ee|backbone_metrics|N_contact_interface",
    min_value=0,
    comparison="higher_is_better",
)
INTERFACE_TARGET_RESIDUES = ResidueNumberDescriptor(
    name="Interface target residues",
    description="List of residue numbers of the target in contact with the binder backbone (CA within 8A)",
    tool="Backbone metrics",
    key="rfd_ee|backbone_metrics|interface_target_residues",
)

N_CONTACTS_TO_HOTSPOTS = NumericGlobalDescriptor(
    name="N binder-hotspots backbone contacts",
    description="Number of contacts between binder CA atoms and user-defined hotspots CA atoms. "
    "Two CA atoms are in contact if they are within 8A from each other",
    tool="Backbone metrics",
    key="rfd_ee|backbone_metrics|N_contact_hotspots",
    min_value=0,
    comparison="higher_is_better",
)

N_HOTSPOTS_ON_INTERFACE = NumericGlobalDescriptor(
    name="N hotspots on interface",
    description="Number of user-defined hotspot residues found on the binder-target backbone interface (CA within 8A)",
    tool="Backbone metrics",
    key="rfd_ee|backbone_metrics|N_hotspots_on_interface",
    min_value=0,
    comparison="does_not_apply",
)

PYDSSP_STRING = CategoricalResidueDescriptor(
    name="PyDSSP String",
    description="Secondary structure representation of the protein according to PyDSSP (H = helix, E = strand, - = loop)",
    tool="PyDSSP",
    key="rfd_ee|backbone_metrics|pydssp_str",
    category_labels={"H": "Helix", "E": "Strand", "-": "Loop"},
)

PYDSSP_LOOP_PERCENT = NumericGlobalDescriptor(
    name="PyDSSP Loop %",
    description="Percentage of residues with loop secondary structure according to PyDSSP",
    tool="PyDSSP",
    key="rfd_ee|backbone_metrics|pydssp_loop_percent",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

PYDSSP_HELIX_PERCENT = NumericGlobalDescriptor(
    name="PyDSSP Helix %",
    description="Percentage of residues with alpha-helix secondary structure according to PyDSSP",
    tool="PyDSSP",
    key="rfd_ee|backbone_metrics|pydssp_helix_percent",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

PYDSSP_SHEET_PERCENT = NumericGlobalDescriptor(
    name="PyDSSP Beta Sheet %",
    description="Percentage of residues with beta sheet secondary structure according to PyDSSP",
    tool="PyDSSP",
    key="rfd_ee|backbone_metrics|pydssp_strand_percent",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

BACKBONE_METRICS = [
    RADIUS_OF_GYRATION,
    N_CONTACTS_TO_INTERFACE,
    N_CONTACTS_TO_HOTSPOTS,
    N_HOTSPOTS_ON_INTERFACE,
    INTERFACE_TARGET_RESIDUES,
    PYDSSP_STRING,
    PYDSSP_LOOP_PERCENT,
    PYDSSP_HELIX_PERCENT,
    PYDSSP_SHEET_PERCENT,
]
BACKBONE_METRIC_FIELD_NAMES = [d.key.removeprefix("rfd_ee|backbone_metrics|") for d in BACKBONE_METRICS]


# AVERAGE_DISTANCE_BINDER_TO_TARGET_INTERFACE = NumericGlobalDescriptor(
#     name='Binder-interface average distance',
#     description='Mean distance of binder CA-atoms to the target interface CA atoms',
#     tool='Backbone metrics',
#     key='rfd_ee|backbone_metrics|average_dist_binder_to_target_interface',
#     min_value=0,
#     comparison='does_not_apply'
# )
#
# AVERAGE_DISTANCE_BINDER_TO_TARGET_INTERFACE_CONTACTS = NumericGlobalDescriptor(
#     name='Binder-interface contacts average distance',
#     description='Mean distance of binder CA-atoms to the target interface CA atoms which contact binder CA atoms (<8A)',
#     tool='Backbone metrics',
#     key='rfd_ee|backbone_metrics|average_dist_binder_to_target_interface_contacts',
#     min_value=0,
#     comparison='does_not_apply'
# )
#
# AVERAGE_DISTANCE_BINDER_TO_HOTSPOTS = NumericGlobalDescriptor(
#     name='Binder-hotspots average distance',
#     description='Mean distance of binder CA-atoms to the target hotspot CA atoms',
#     tool='Backbone metrics',
#     key='rfd_ee|backbone_metrics|average_dist_binder_to_hotspots',
#     min_value=0,
#     comparison='does_not_apply'
# )
#
# AVERAGE_DISTANCE_BINDER_TO_HOTSPOT_CONTACTS = NumericGlobalDescriptor(
#     name='Binder-hotspots contacts average distance',
#     description='Mean distance of binder CA-atoms to the target hotspot CA atoms which contact binder CA atoms (<8A)',
#     tool='Backbone metrics',
#     key='rfd_ee|backbone_metrics|average_dist_binder_to_hotspots_contacts',
#     min_value=0,
#     comparison='does_not_apply'
# )


CUSTOM_BACKBONE_STRUCTURE_PATH = StructureFileDescriptor(
    name="Custom backbone design",
    description="Custom backbone structure input, without any side-chains, with Glycine residues at designed positions",
    tool="Custom",
    key="rfd_ee|custom_backbone|backbone_structure_path",
    structure_type="backbone_design",
)

RFDIFFUSION_STRUCTURE_PATH = StructureFileDescriptor(
    name="RFdiffusion backbone design",
    description="RFdiffusion-generated backbone structure, without any side-chains, with Glycine residues at designed positions",
    tool="RFdiffusion",
    key="rfd_ee|rfdiffusion|backbone_structure_path",
    structure_type="backbone_design",
)


RFDIFFUSION_TRB_PATH = FileDescriptor(
    name="RFdiffusion .trb file",
    description="RFdiffusion pickle file containing metadata about the designed backbone structure",
    tool="RFdiffusion",
    key="rfd_ee|rfdiffusion|backbone_trb_path",
)


LIGANDMPNN_STRUCTURE_PATH = StructureFileDescriptor(
    name="LigandMPNN sequence design",
    description="Structure for LigandMPNN-generated sequence with packed side-chains",
    tool="LigandMPNN",
    key="rfd_ee|ligandmpnn|sequence_structure_path",
    structure_type="sequence_design",
)


FASTRELAX_STRUCTURE_PATH = StructureFileDescriptor(
    name="ProteinMPNN FastRelax sequence design",
    description="Structure for sequence generated with ProteinMPNN and PyRosetta FastRelax protocol. Side-chains may or may not be relaxed depending on the cycle (last cycle is not relaxed in some implementations)",
    tool="ProteinMPNN+PyRosetta",
    key="rfd_ee|proteinmpnn_fastrelax|sequence_structure_path",
    structure_type="sequence_design",
)


# ROSETTA INTERFACE METRICS

# "contact_molecular_surface": 484.94976806640625,
# "ddg": -12.693643569946289,
# sap_score: 0.0,

PYROSETTA_DDG = NumericGlobalDescriptor(
    name="Rosetta ddG",
    description="Rosetta binding energy change (in Rosetta energy units, beta_nov16 scoring function). Lower (negative) values indicate better binding affinity.",
    tool="PyRosetta",
    key="pyrosetta_interface_metrics|pyrosetta|ddg",
    comparison="lower_is_better",
)

PYROSETTA_CMS = NumericGlobalDescriptor(
    name="Contact molecular surface",
    description="Contact molecular surface area (in Angstrom squared) calculated using Rosetta ContactMolecularSurface",
    unit="Å²",
    tool="PyRosetta",
    key="pyrosetta_interface_metrics|pyrosetta|contact_molecular_surface",
    comparison="higher_is_better",
)

PYROSETTA_SAP_SCORE = NumericGlobalDescriptor(
    name="Spatial aggregation propensity (SAP)",
    description="Hydrophobicity of surface exposed regions calculated using Rosetta SapScore. Positive values indicate hydrophobic molecules.",
    tool="PyRosetta",
    key="pyrosetta_interface_metrics|pyrosetta|sap_score",
    comparison="does_not_apply",
)

PYROSETTA_INTERFACE_DESCRIPTORS = [PYROSETTA_DDG, PYROSETTA_CMS, PYROSETTA_SAP_SCORE]

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

PRESETS = [
    {
        "label": "Rosetta ddG & CMS",
        "x": PYROSETTA_DDG,
        "y": PYROSETTA_CMS,
    },
    {
        "label": "PyDSSP Helix vs Sheet",
        "x": PYDSSP_HELIX_PERCENT,
        "y": PYDSSP_SHEET_PERCENT,
    },
]
