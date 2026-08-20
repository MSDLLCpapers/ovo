from ovo.core.database import descriptors_rfdiffusion
from ovo.core.database.descriptors_refolding import AF2_PRIMARY_DESCRIPTORS, ESMFOLD_DESCRIPTORS
from ovo.core.database.models import NumericGlobalDescriptor, Descriptor

# SEQUENCE COMPOSITION

LENGTH = NumericGlobalDescriptor(
    name="Sequence length",
    description="Number of amino acids",
    tool="Sequence composition",
    key="proteinqc|seq_composition|length",
    comparison="does_not_apply",
)

# Warning value: 1.5 times the natural abundance
# Error value: 2 times the natural abundance

A_PERC = NumericGlobalDescriptor(
    name="Ala %",
    description="Percentage of alanine residues. Natural abundance in proteins: 8.76%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|A_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=13.14,
    error_value=17.52,
)

C_PERC = NumericGlobalDescriptor(
    name="Cys %",
    description="Percentage of cysteine residues. Natural abundance in proteins: 1.38%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|C_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=2.07,
    error_value=2.76,
)

D_PERC = NumericGlobalDescriptor(
    name="Asp %",
    description="Percentage of aspartic acid residues. Natural abundance in proteins: 5.49%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|D_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=8.234999999999999,
    error_value=10.98,
)

E_PERC = NumericGlobalDescriptor(
    name="Glu %",
    description="Percentage of glutamic acid residues. Natural abundance in proteins: 6.32%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|E_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=9.480000000000001,
    error_value=12.64,
)

F_PERC = NumericGlobalDescriptor(
    name="Phe %",
    description="Percentage of phenylalanine residues. Natural abundance in proteins: 3.87%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|F_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=5.805,
    error_value=7.74,
)

G_PERC = NumericGlobalDescriptor(
    name="Gly %",
    description="Percentage of glycine residues. Natural abundance in proteins: 7.03%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|G_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=10.545,
    error_value=14.06,
)

H_PERC = NumericGlobalDescriptor(
    name="His %",
    description="Percentage of histidine residues. Natural abundance in proteins: 2.26%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|H_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=3.39,
    error_value=4.52,
)

I_PERC = NumericGlobalDescriptor(
    name="Ile %",
    description="Percentage of isoleucine residues. Natural abundance in proteins: 5.49%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|I_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=8.234999999999999,
    error_value=10.98,
)

K_PERC = NumericGlobalDescriptor(
    name="Lys %",
    description="Percentage of lysine residues. Natural abundance in proteins: 5.19%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|K_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=7.785,
    error_value=10.38,
)

L_PERC = NumericGlobalDescriptor(
    name="Leu %",
    description="Percentage of leucine residues. Natural abundance in proteins: 9.68%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|L_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=14.52,
    error_value=19.36,
)

M_PERC = NumericGlobalDescriptor(
    name="Met %",
    description="Percentage of methionine residues. Natural abundance in proteins: 2.32%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|M_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=3.48,
    error_value=4.64,
)

N_PERC = NumericGlobalDescriptor(
    name="Asn %",
    description="Percentage of asparagine residues. Natural abundance in proteins: 3.93%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|N_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=5.895,
    error_value=7.86,
)

P_PERC = NumericGlobalDescriptor(
    name="Pro %",
    description="Percentage of proline residues. Natural abundance in proteins: 5.02%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|P_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=7.53,
    error_value=10.04,
)

Q_PERC = NumericGlobalDescriptor(
    name="Gln %",
    description="Percentage of glutamine residues. Natural abundance in proteins: 3.93%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|Q_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=5.895,
    error_value=7.86,
)

R_PERC = NumericGlobalDescriptor(
    name="Arg %",
    description="Percentage of arginine residues. Natural abundance in proteins: 5.78%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|R_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=8.67,
    error_value=11.56,
)

S_PERC = NumericGlobalDescriptor(
    name="Ser %",
    description="Percentage of serine residues. Natural abundance in proteins: 7.14%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|S_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=10.71,
    error_value=14.28,
)

T_PERC = NumericGlobalDescriptor(
    name="Thr %",
    description="Percentage of threonine residues. Natural abundance in proteins: 5.53%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|T_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=8.295,
    error_value=11.06,
)

V_PERC = NumericGlobalDescriptor(
    name="Val %",
    description="Percentage of valine residues. Natural abundance in proteins: 6.73%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|V_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=10.095,
    error_value=13.46,
)

W_PERC = NumericGlobalDescriptor(
    name="Trp %",
    description="Percentage of tryptophan residues. Natural abundance in proteins: 1.25%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|W_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=1.8750000000000003,
    error_value=2.5,
)

Y_PERC = NumericGlobalDescriptor(
    name="Tyr %",
    description="Percentage of tyrosine residues. Natural abundance in proteins: 2.91%.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|Y_perc",
    comparison="lower_is_better",  # High content of the same residue is suspicious
    min_value=0,
    max_value=100,
    warning_value=4.365,
    error_value=5.82,
)

NONPOLAR_PERC = NumericGlobalDescriptor(
    name="Nonpolar residues %",
    description="Percentage of nonpolar residues (G, A, V, L, I)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|nonpolar_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=90,
    error_value=99,
)

POLAR_UNCHARGED_PERC = NumericGlobalDescriptor(
    name="Polar uncharged residues %",
    description="Percentage of polar uncharged residues (S, T, C, N, Q, Y)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|polar_uncharged_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=90,
    error_value=99,
)

POSITIVE_PERC = NumericGlobalDescriptor(
    name="Positive residues %",
    description="Percentage of positively charged residues (K, R, H)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|positive_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=50,
    error_value=90,
)

NEGATIVE_PERC = NumericGlobalDescriptor(
    name="Negative residues %",
    description="Percentage of negatively charged residues (D, E)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|negative_perc",
    min_value=0,
    max_value=100,
    warning_value=50,
    error_value=90,
)

TURN_FORMING_PERC = NumericGlobalDescriptor(
    name="Turn forming residues %",
    description="Percentage of turn forming residues (N, G, P, S)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|turn_forming_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=50,
    error_value=90,
)

AROMATIC_PERC = NumericGlobalDescriptor(
    name="Aromatic residues %",
    description="Percentage of aromatic residues (F, Y, W)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|aromatic_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=50,
    error_value=90,
)

DENQ_PERC = NumericGlobalDescriptor(
    name="DENQ %",
    description="Percentage of aspartic acid (D), glutamic acid (E), asparagine (N), and glutamine (Q) residues",
    tool="Sequence composition",
    key="proteinqc|seq_composition|denq_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=50,
    error_value=90,
)

# Sequence composition - BIOPYTHON

AROMATICITY = NumericGlobalDescriptor(
    name="Aromaticity",
    description="Aromaticity value of a protein according to Lobry, 1994",
    tool="Sequence composition",
    key="proteinqc|seq_composition|aromaticity",
    comparison="lower_is_better",  # High aromaticity is associated with lower solubility, they are also expensive for biosynthesis so there is evolutionary pressure to reduce aromaticity, on the other hand they play important role in reactions and can stabilize the protein
    min_value=0,
    max_value=1,
    warning_value=0.2,
    error_value=0.5,
)

CHARGE_5_5 = NumericGlobalDescriptor(
    name="Charge at pH 5.5",
    description="Net charge of the protein sequence at pH 5.5",
    tool="Sequence composition",
    key="proteinqc|seq_composition|charge_5_5",
    comparison="does_not_apply",
)

CHARGE_7_4 = NumericGlobalDescriptor(
    name="Charge at pH 7.4",
    description="Net charge of the protein sequence at pH 7.4",
    tool="Sequence composition",
    key="proteinqc|seq_composition|charge_7_4",
    comparison="does_not_apply",
)

ISOELECTRIC_POINT = NumericGlobalDescriptor(
    name="Isoelectric point",
    description="pH at which protein carries no net eletrical charge",
    tool="Sequence composition",
    key="proteinqc|seq_composition|isoelectric_point",
    comparison="does_not_apply",
)  # FIXME: Maybe there should be a comparison

MEC_REDUCED = NumericGlobalDescriptor(
    name="MEC reduced",
    description="Molecular Extinction Coefficient (MEC) assuming cysteines (reduced)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|MEC_reduced",
    comparison="does_not_apply",
)

MEC_CYSTINES = NumericGlobalDescriptor(
    name="MEC cystines",
    description="Molecular Extinction Coefficient (MEC) assuming cystines residues (Cys-Cys-bond)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|MEC_cystines",
    comparison="does_not_apply",
)

HELIX_SEQ_PERC = NumericGlobalDescriptor(
    name="Helix-forming residues %",
    description="Percentage of residues which tend to be in Helix (V, I, Y, F, W, L)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|helix_perc",
    comparison="does_not_apply",
)

SHEET_SEQ_PERC = NumericGlobalDescriptor(
    name="Sheet-forming residues %",
    description="Percentage of residues which tend to be in Sheet (E, M, A, L)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|sheet_perc",
    comparison="does_not_apply",
)

TURN_SEQ_PERC = NumericGlobalDescriptor(
    name="Turn-forming residues %",
    description="Percentage of residues which tend to be in Turn (N, P, G, S)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|turn_perc",
    comparison="does_not_apply",
)

FLEXIBILITY_AVG = NumericGlobalDescriptor(
    name="Flexibility average",
    description="Average flexibility value of the protein sequence (according to Vihinen, 1994)",
    tool="Sequence composition",
    key="proteinqc|seq_composition|flexibility_avg",
    comparison="does_not_apply",
)

GRAVY = NumericGlobalDescriptor(
    name="GRAVY",
    description="Grand average of hydropathicity (GRAVY) value of the protein sequence (according to Kyte and Doolittle). Positive value indicates hydrophobic protein while negative values indicate hydrophilic protein.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|gravy",
    comparison="does_not_apply",
)

INSTABILITY_INDEX = NumericGlobalDescriptor(
    name="Instability index",
    description="Instability index of the protein sequence (according to Guruprasad et al., 1990). Any value above 40 means the protein is unstable (has a short half life).",
    tool="Sequence composition",
    key="proteinqc|seq_composition|instability_index",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
    warning_value=40,
    error_value=50,
)

MOLECULEAR_WEIGHT = NumericGlobalDescriptor(
    name="Molecular weight",
    description="Molecular weight of the protein sequence",
    tool="Sequence composition",
    key="proteinqc|seq_composition|molecular_weight",
    comparison="does_not_apply",
)

ENTROPY = NumericGlobalDescriptor(
    name="Sequence entropy",
    description="Diversity/orderedness of amino acids in a protein sequence; high values = more variety, low values = more compositional bias. For each overlapping 21-residue window (if sequence is longer than 21), the binary Shannon entropy of the amino acid composition is calculated and averaged to produce a single metric for the sequence. A sequence of identical amino acids has entropy 0, while a sequence with a uniform distribution of all 20 amino acids in each segment reaches log2(20) ~ 4.32.",
    tool="Sequence composition",
    key="proteinqc|seq_composition|avg_entropy",
    comparison="higher_is_better",
    min_value=2.976720519480519,
    max_value=3.580661971830986,
    warning_value=3.2,
    error_value=3,
)

# ESM-1v

ESM1V = NumericGlobalDescriptor(
    name="ESM-1v likelihood",
    description="Likelihood of native amino acid sequence based on pLM trained on large number of sequences",
    tool="ESM-1v",
    key="proteinqc|esm_1v|native_seq_avg_softmax",
    comparison="higher_is_better",
    min_value=0,
    max_value=1,
    warning_value=0.7,
    error_value=0.5,
)

# ESM-IF

ESMIF = NumericGlobalDescriptor(
    name="ESM-IF likelihood",
    description="Likelihood of native amino acid sequence based on the input structure",
    tool="ESM-IF",
    key="proteinqc|esm_if|native_seq_avg_softmax",
    comparison="higher_is_better",
    min_value=0,
    max_value=1,
    warning_value=0.3,
    error_value=0.2,
)

ESM_IF_NATIVE_SEQ_AVG_LOGITS = NumericGlobalDescriptor(
    name="ESM-IF native sequence average logits",
    description="Average logits for the native amino acid sequence based on the input structure",
    tool="ESM-IF",
    key="proteinqc|esm_if|native_seq_avg_logits",
    comparison="does_not_apply",
)

ESM_IF_NATIVE_SEQ_SUM_LOGITS = NumericGlobalDescriptor(
    name="ESM-IF native sequence sum logits",
    description="Sum of logits for the native amino acid sequence based on the input structure",
    tool="ESM-IF",
    key="proteinqc|esm_if|native_seq_sum_logits",
    comparison="does_not_apply",
)
# PROTEIN-SOL

PERC_SOLUBILITY = NumericGlobalDescriptor(
    name="Sequence solubility (percentage)",
    description="Predicted solubility from the sequence. Percentage values can exceed 100%",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|percent-sol",
    comparison="does_not_apply",
)

SOLUBILITY = NumericGlobalDescriptor(
    name="Sequence solubility (scaled)",
    description="Predicted solubility from the sequence (range: 0-1). Any scaled solubility value greater than 0.45 is predicted to have a higher solubility than the average soluble E.coli protein from the experimental solubility dataset Niwa et al 2009, and any protein with a lower scaled solubility value is predicted to be less soluble.",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|scaled-sol",
    comparison="higher_is_better",
    min_value=0,
    max_value=1,
    warning_value=0.45,
    error_value=0.3,
)

AVG_CHARGE = NumericGlobalDescriptor(
    name="Sequence charge",
    description="Average charge of the protein sequence",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|avg_charge",
    comparison="does_not_apply",
)

AVG_CHARGE_NEGATIVE = NumericGlobalDescriptor(
    name="Negative residue charge",
    description="Average charge of the negatively charged residues",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|negative_avg",
    comparison="does_not_apply",
)

AVG_CHARGE_POSITIVE = NumericGlobalDescriptor(
    name="Positive residue charge",
    description="Average charge of the positively charged residues",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|positive_avg",
    comparison="does_not_apply",
)

PERC_NEGATIVE = NumericGlobalDescriptor(
    name="Percentage of negative residues",
    description="Percentage of negative residues in the protein",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|perc_negative",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

PERC_POSITIVE = NumericGlobalDescriptor(
    name="Percentage of positive residues",
    description="Percentage of positive residues in the protein",
    tool="Protein-Sol",
    key="proteinqc|proteinsol|perc_positive",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

# DSSP

HELIX_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Helix %",
    description="% of all amino acids in helices",
    tool="DSSP",
    key="proteinqc|dssp|% H",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

SHEET_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Beta Sheet %",
    description="% of all amino acids in beta sheets",
    tool="DSSP",
    key="proteinqc|dssp|% E",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

TURN_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Turn %",
    description="% of all amino acids in turns",
    tool="DSSP",
    key="proteinqc|dssp|% T",
    comparison="lower_is_better",  # Turns are most difficult for folding -> slow folding -> expression problems
    min_value=0,
    max_value=100,
    warning_value=20,
    error_value=50,
)

ISOLATED_BETA_BRIDGE_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Isolated beta bridge residue %",
    description="% of all amino acids identified as isolated beta bridge residues",
    tool="DSSP",
    key="proteinqc|dssp|% B",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

HELIX_3_10_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP 3-10 helix %",
    description="% of all amino acids in 3-10 helices",
    tool="DSSP",
    key="proteinqc|dssp|% G",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

PI_HELIX_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Pi helix %",
    description="% of all amino acids in pi helices",
    tool="DSSP",
    key="proteinqc|dssp|% I",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

BEND_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP Bend %",
    description="% of all amino acids in bends",
    tool="DSSP",
    key="proteinqc|dssp|% S",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

NONE_PERCENTAGE = NumericGlobalDescriptor(
    name="DSSP No secondary structure residues %",
    description="% of all amino acids in no secondary structure",
    tool="DSSP",
    key="proteinqc|dssp|% -",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

# Shape descriptors from MDAnalysis

ASPHERICITY = NumericGlobalDescriptor(
    name="Asphericity",
    description="Asphericity of the protein structure, value of 0 corresponds to a perfect sphere, values closer to 1 correspond to elongated proteins.",
    tool="MDAnalysis",
    key="proteinqc|dssp|asphericity",
    comparison="lower_is_better",
    min_value=0,
    warning_value=0.4,
    error_value=0.9,
    max_value=1,
)

SHAPE_PARAMETER = NumericGlobalDescriptor(
    name="Shape parameter",
    description="Shape parameter of the protein structure, S > 0 corresponds to prolate and S < 0 represents oblate",
    tool="MDAnalysis",
    key="proteinqc|dssp|shape_parameter",
    comparison="does_not_apply",
)

RADIUS_OF_GYRATION_ALL_ATOM = NumericGlobalDescriptor(
    name="Radius of gyration (all atom)",
    description="Radius of gyration of the protein structure",
    tool="MDAnalysis",
    key="proteinqc|dssp|radius_of_gyration",
    comparison="does_not_apply",
    min_value=0,
)

RADIUS_OF_GYRATION_NORM = NumericGlobalDescriptor(
    name="Radius of gyration normalized",
    description="Radius of gyration normalized by radius of gyration of a perfect sphere.  Values < 1 correspond to tight packing, values > 1 correspond to loose packing.",
    tool="MDAnalysis",
    key="proteinqc|dssp|radius_of_gyration_normalized",
    comparison="lower_is_better",
    min_value=0,
)

RAMACHANDRAN_ALLOWED_PERCENTAGE = NumericGlobalDescriptor(
    name="Ramachandran allowed angles %",
    description="Percentage of phi and psi angles in allowed regions of the Ramachandran plot (capturing 90% data points) created from a reference set of 500 PDB files.",
    tool="MDAnalysis",
    key="proteinqc|dssp|ramachandran_allowed_perc",
    comparison="higher_is_better",
    min_value=0,
    max_value=100,
)

RAMACHANDRAN_MARGINALLY_ALLOWED_PERCENTAGE = NumericGlobalDescriptor(
    name="Ramachandran marginally allowed angles %",
    description="Percentage of phi and psi angles in marginally allowed regions of the Ramachandran plot (capturing 99% data points) created from a reference set of 500 PDB files.",
    tool="MDAnalysis",
    key="proteinqc|dssp|ramachandran_marginally_allowed_perc",
    comparison="does_not_apply",
    min_value=0,
    max_value=100,
)

RAMACHANDRAN_OUTLIERS_PERCENTAGE = NumericGlobalDescriptor(
    name="Ramachandran outliers angles %",
    description="Percentage of phi and psi angles in outlier regions of the Ramachandran plot created from a reference set of 500 PDB files.",
    tool="MDAnalysis",
    key="proteinqc|dssp|ramachandran_outliers_perc",
    comparison="lower_is_better",
    min_value=0,
    max_value=100,
)

# PEP-PATCH

# Hydrophobic
HYDROPHOBIC_TOTAL_AREA = NumericGlobalDescriptor(
    name="Hydrophobic patch area",
    description="Surface area predicted to be in a hydrophobic patch (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area,hydrophobic",
    comparison="does_not_apply",
)

HYDROPHOBIC_TOTAL_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized hydrophobic patch area",
    description="Surface area predicted to be in a hydrophobic patch, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_normalized,hydrophobic",
    comparison="lower_is_better",
    min_value=0,
    max_value=1,
    warning_value=0.25,
    error_value=0.45,
)

HYDROPHOBIC_TOP_PATCH_AREA = NumericGlobalDescriptor(
    name="Hydrophobic top1 patch area",
    description="Area of the largest hydrophobic patch on the protein surface",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area,hydrophobic",
    comparison="does_not_apply",
)

HYDROPHOBIC_TOP_PATCH_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized hydrophobic top1 patch area",
    description="Area of the largest hydrophobic patch on the protein surface, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_normalized,hydrophobic",
    comparison="does_not_apply",
)

HYDROPHOBIC_SAP_SCORE = NumericGlobalDescriptor(
    name="Hydrophobic SAP score",
    description="SAP (Spatial Aggregation Propensity) score",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sap_score,hydrophobic",
    comparison="does_not_apply",
)

HYDROPHOBIC_SASA = NumericGlobalDescriptor(
    name="Hydrophobic SASA",
    description="Solvent accessible surface area (SASA)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sasa,hydrophobic",
    comparison="does_not_apply",
)

HYDROPHOBIC_SURFACE_INTEGRAL = NumericGlobalDescriptor(
    name="Hydrophobicity potential",
    description="Integral of hydrophobicity values over solvent-accessible surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|total_surface_integral,hydrophobic",
    comparison="does_not_apply",
)

# Electrostatic pH 5.5
CHARGED_POSITIVE_5_5_TOTAL_AREA = NumericGlobalDescriptor(
    name="Positive patch area at pH 5.5",
    description="Surface area predicted to be in a positively charged patch at pH 5.5 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_+,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_5_5_TOTAL_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized positive patch area at pH 5.5",
    description="Surface area predicted to be in a positively charged patch at pH 5.5, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_+_normalized,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_5_5_TOP_PATCH_AREA = NumericGlobalDescriptor(
    name="Positive top1 patch area at pH 5.5",
    description="Area of the largest positively charged patch on the protein surface at pH 5.5 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_+,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_5_5_TOP_PATCH_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized positive top1 patch area at pH 5.5",
    description="Area of the largest positively charged patch on the protein surface at pH 5.5, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_+_normalized,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_5_5_TOTAL_AREA = NumericGlobalDescriptor(
    name="Negative patch area at pH 5.5",
    description="Surface area predicted to be in a negatively charged patch at pH 5.5 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_-,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_5_5_TOTAL_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized negative patch area at pH 5.5",
    description="Surface area predicted to be in a negatively charged patch at pH 5.5, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_-_normalized,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_5_5_TOP_PATCH_AREA = NumericGlobalDescriptor(
    name="Negative top1 patch area at pH 5.5",
    description="Area of the largest negatively charged patch on the protein surface at pH 5.5 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_-,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_5_5_TOP_PATCH_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized negative top1 patch area at pH 5.5",
    description="Area of the largest negatively charged patch on the protein surface at pH 5.5, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_-_normalized,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_5_5 = NumericGlobalDescriptor(
    name="Electrostatic volume integral at pH 5.5",
    description="Integral of all electrostatic potential values over the solvent-accessible volume, overall measure of the electrostatic potential",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_HIGH_5_5 = NumericGlobalDescriptor(
    name="Positive electrostatic regions volume integral at pH 5.5",
    description="Integral of electrostatic potential values above a positive threshold, highlighting strongly positive regions",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_high,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_LOW_5_5 = NumericGlobalDescriptor(
    name="Negative electrostatic regions volume integral at pH 5.5",
    description="Integral of electrostatic potential values below a negative threshold, highlighting strongly negative regions",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_low,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_POSITIVE_5_5 = NumericGlobalDescriptor(
    name="Positive electrostatic volume integral at pH 5.5",
    description="Integral of all positive electrostatic potential values over the solvent-accessible volume",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_pos,electrostatic_5.5",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_NEGATIVE_5_5 = NumericGlobalDescriptor(
    name="Negative electrostatic volume integral at pH 5.5",
    description="Integral of all negative electrostatic potential values over the solvent-accessible volume",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_neg,electrostatic_5.5",
    comparison="does_not_apply",
)
# Electrostatic pH 7.4
CHARGED_POSITIVE_7_4_TOTAL_AREA = NumericGlobalDescriptor(
    name="Positive patch area at pH 7.4",
    description="Surface area predicted to be in a positively charged patch at pH 7.4 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_+,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_7_4_TOTAL_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized positive patch area at pH 7.4",
    description="Surface area predicted to be in a positively charged patch at pH 7.4, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_+_normalized,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_7_4_TOP_PATCH_AREA = NumericGlobalDescriptor(
    name="Positive top1 patch area at pH 7.4",
    description="Area of the largest positively charged patch on the protein surface at pH 7.4 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_+,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_POSITIVE_7_4_TOP_PATCH_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized positive top1 patch area at pH 7.4",
    description="Area of the largest positively charged patch on the protein surface at pH 7.4, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_+_normalized,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_7_4_TOTAL_AREA = NumericGlobalDescriptor(
    name="Negative patch area at pH 7.4",
    description="Surface area predicted to be in a negatively charged patch at pH 7.4 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_-,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_7_4_TOTAL_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized negative patch area at pH 7.4",
    description="Surface area predicted to be in a negatively charged patch at pH 7.4, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|sum_patch_area_-_normalized,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_7_4_TOP_PATCH_AREA = NumericGlobalDescriptor(
    name="Negative top1 patch area at pH 7.4",
    description="Area of the largest negatively charged patch on the protein surface at pH 7.4 (Å²)",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_-,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_NEGATIVE_7_4_TOP_PATCH_AREA_NORM = NumericGlobalDescriptor(
    name="Normalized negative top1 patch area at pH 7.4",
    description="Area of the largest negatively charged patch on the protein surface at pH 7.4, normalized by the total surface area",
    tool="PEP-Patch",
    key="proteinqc|peppatch|top1_patch_area_-_normalized,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_7_4 = NumericGlobalDescriptor(
    name="Electrostatic volume integral at pH 7.4",
    description="Integral of all electrostatic potential values over the solvent-accessible volume, overall measure of the electrostatic potential",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_HIGH_7_4 = NumericGlobalDescriptor(
    name="Positive electrostatic regions volume integral at pH 7.4",
    description="Integral of electrostatic potential values above a positive threshold, highlighting strongly positive regions",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_high,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_LOW_7_4 = NumericGlobalDescriptor(
    name="Negative electrostatic regions volume integral at pH 7.4",
    description="Integral of electrostatic potential values below a negative threshold, highlighting strongly negative regions",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_low,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_POSITIVE_7_4 = NumericGlobalDescriptor(
    name="Positive electrostatic volume integral at pH 7.4",
    description="Integral of all positive electrostatic potential values over the solvent-accessible volume",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_pos,electrostatic_7.4",
    comparison="does_not_apply",
)

CHARGED_INTEGRAL_NEGATIVE_7_4 = NumericGlobalDescriptor(
    name="Negative electrostatic volume integral at pH 7.4",
    description="Integral of all negative electrostatic potential values over the solvent-accessible volume",
    tool="PEP-Patch",
    key="proteinqc|peppatch|integral_neg,electrostatic_7.4",
    comparison="does_not_apply",
)
# Electrostatic pH 7.4
# Top descriptors
PROTEINQC_SEQUENCE_DESCRIPTORS = [
    LENGTH,
    SOLUBILITY,
    ISOELECTRIC_POINT,
    ESM1V,
    AROMATICITY,
    CHARGE_7_4,
    ENTROPY,
]
PROTEINQC_STRUCTURE_DESCRIPTORS = [
    ASPHERICITY,
    HYDROPHOBIC_TOTAL_AREA_NORM,
    CHARGED_POSITIVE_7_4_TOTAL_AREA_NORM,
    HELIX_PERCENTAGE,
    SHEET_PERCENTAGE,
    TURN_PERCENTAGE,
    ESMIF,
]

# All
SEQ_COMPOSITION_DESCRIPTORS = [
    LENGTH,
    A_PERC,
    C_PERC,
    D_PERC,
    E_PERC,
    F_PERC,
    G_PERC,
    H_PERC,
    I_PERC,
    K_PERC,
    L_PERC,
    M_PERC,
    N_PERC,
    P_PERC,
    Q_PERC,
    R_PERC,
    S_PERC,
    T_PERC,
    V_PERC,
    W_PERC,
    Y_PERC,
    NONPOLAR_PERC,
    POLAR_UNCHARGED_PERC,
    POSITIVE_PERC,
    NEGATIVE_PERC,
    TURN_FORMING_PERC,
    AROMATIC_PERC,
    DENQ_PERC,
    AROMATICITY,
    CHARGE_5_5,
    CHARGE_7_4,
    ISOELECTRIC_POINT,
    MEC_REDUCED,
    MEC_CYSTINES,
    HELIX_SEQ_PERC,
    SHEET_SEQ_PERC,
    TURN_SEQ_PERC,
    FLEXIBILITY_AVG,
    GRAVY,
    INSTABILITY_INDEX,
    MOLECULEAR_WEIGHT,
    ENTROPY,
]
ESM_DESCRIPTORS = [ESM1V, ESMIF, ESM_IF_NATIVE_SEQ_AVG_LOGITS, ESM_IF_NATIVE_SEQ_SUM_LOGITS]
PROTEIN_SOL_DESCRIPTORS = [
    SOLUBILITY,
    AVG_CHARGE,
    PERC_SOLUBILITY,
    AVG_CHARGE_NEGATIVE,
    AVG_CHARGE_POSITIVE,
    PERC_NEGATIVE,
    PERC_POSITIVE,
]
DSSP_DESCRIPTORS = [
    HELIX_PERCENTAGE,
    SHEET_PERCENTAGE,
    TURN_PERCENTAGE,
    ISOLATED_BETA_BRIDGE_PERCENTAGE,
    HELIX_3_10_PERCENTAGE,
    PI_HELIX_PERCENTAGE,
    BEND_PERCENTAGE,
    NONE_PERCENTAGE,
]
SHAPE_DESCRIPTORS = [
    ASPHERICITY,
    SHAPE_PARAMETER,
    RADIUS_OF_GYRATION_ALL_ATOM,
    RADIUS_OF_GYRATION_NORM,
    RAMACHANDRAN_ALLOWED_PERCENTAGE,
    RAMACHANDRAN_MARGINALLY_ALLOWED_PERCENTAGE,
    RAMACHANDRAN_OUTLIERS_PERCENTAGE,
]

PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS = [
    HYDROPHOBIC_SAP_SCORE,
    HYDROPHOBIC_SASA,
    HYDROPHOBIC_TOTAL_AREA,
    HYDROPHOBIC_TOTAL_AREA_NORM,
    HYDROPHOBIC_TOP_PATCH_AREA,
    HYDROPHOBIC_TOP_PATCH_AREA_NORM,
    HYDROPHOBIC_SURFACE_INTEGRAL,
]
PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS_BY_KEY = {d.key: d for d in PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS}
PEP_PATCH_CHARGE_DESCRIPTORS = [
    CHARGED_POSITIVE_5_5_TOTAL_AREA,
    CHARGED_POSITIVE_5_5_TOTAL_AREA_NORM,
    CHARGED_POSITIVE_5_5_TOP_PATCH_AREA,
    CHARGED_POSITIVE_5_5_TOP_PATCH_AREA_NORM,
    CHARGED_NEGATIVE_5_5_TOTAL_AREA,
    CHARGED_NEGATIVE_5_5_TOTAL_AREA_NORM,
    CHARGED_NEGATIVE_5_5_TOP_PATCH_AREA,
    CHARGED_NEGATIVE_5_5_TOP_PATCH_AREA_NORM,
    CHARGED_INTEGRAL_5_5,
    CHARGED_INTEGRAL_HIGH_5_5,
    CHARGED_INTEGRAL_LOW_5_5,
    CHARGED_INTEGRAL_POSITIVE_5_5,
    CHARGED_INTEGRAL_NEGATIVE_5_5,
    CHARGED_POSITIVE_7_4_TOTAL_AREA,
    CHARGED_POSITIVE_7_4_TOTAL_AREA_NORM,
    CHARGED_POSITIVE_7_4_TOP_PATCH_AREA,
    CHARGED_POSITIVE_7_4_TOP_PATCH_AREA_NORM,
    CHARGED_NEGATIVE_7_4_TOTAL_AREA,
    CHARGED_NEGATIVE_7_4_TOTAL_AREA_NORM,
    CHARGED_NEGATIVE_7_4_TOP_PATCH_AREA,
    CHARGED_NEGATIVE_7_4_TOP_PATCH_AREA_NORM,
    CHARGED_INTEGRAL_7_4,
    CHARGED_INTEGRAL_HIGH_7_4,
    CHARGED_INTEGRAL_LOW_7_4,
    CHARGED_INTEGRAL_POSITIVE_7_4,
    CHARGED_INTEGRAL_NEGATIVE_7_4,
]
PEP_PATCH_CHARGE_DESCRIPTORS_BY_KEY = {d.key: d for d in PEP_PATCH_CHARGE_DESCRIPTORS}
PEP_PATCH_DESCRIPTORS = PEP_PATCH_HYDROPHOBICITY_DESCRIPTORS + PEP_PATCH_CHARGE_DESCRIPTORS

# New descriptors
DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]

# All descriptors shown on ProteinQC page - includes descriptors from other pipelines
PROTEINQC_MAIN_DESCRIPTORS = (
    PROTEINQC_SEQUENCE_DESCRIPTORS
    + PROTEINQC_STRUCTURE_DESCRIPTORS
    + AF2_PRIMARY_DESCRIPTORS
    + ESMFOLD_DESCRIPTORS
    + descriptors_rfdiffusion.BACKBONE_METRICS
)

PRESETS = [
    {
        "label": "Sequence pI & Pep-Patch Hydrophobic SAP Score",
        "x": ISOELECTRIC_POINT,
        "y": HYDROPHOBIC_SAP_SCORE,
    },
    {
        "label": "Sequence Hydrophobicity & Charge",
        "x": GRAVY,
        "y": CHARGE_7_4,
    },
    {
        "label": "Aromatic vs. Positive residues %",
        "x": AROMATIC_PERC,
        "y": POSITIVE_PERC,
    },
]
