from ovo.core.database.models import NumericGlobalDescriptor, StructureFileDescriptor, ResidueNumberDescriptor

# Hardcoded test options for refolding
REFOLDING_TESTS_SCAFFOLD = {
    "af2_model_1_ptm_nt_3rec": (
        "AF2 monomer, no template, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model), initial guess with no template input. Low risk of over-confidence, but may fail to predict the structure (since no MSA input is provided either).",
    ),
    "af2_model_1_ptm_ft_3rec": (
        "AF2 monomer, fixed motif template, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model), initial guess with template input for fixed regions. Medium risk of over-confidence.",
    ),
    "af2_model_1_multimer_nt_3rec": (
        "AF2 multimer, no template, 3 recycles",
        "AlphaFold2 model_1_multimer, initial guess with no template input. Low risk of over-confidence, but may fail to predict the structure (since no MSA input is provided either).",
    ),
    "af2_model_1_multimer_ft_3rec": (
        "AF2 multimer, fixed motif template, 3 recycles",
        "AlphaFold2 model_1_multimer, initial guess with template input for fixed regions. Medium risk of over-confidence.",
    ),
    "esmfold": (
        "ESMFold, 4 recycles",
        "Unbiased, sequence input only, low risk of over-confidence.",
    ),
    "boltz1_scaffold_nt": (
        "Boltz-1 scaffold, no template",
        "Boltz-1 structure prediction with no template input. Low risk of over-confidence.",
    ),
    "boltz2_scaffold_nt": (
        "Boltz-2 scaffold, no template",
        "Boltz-2 structure prediction with no template input. Low risk of over-confidence.",
    ),
}

REFOLDING_TESTS_BINDER = {
    "af2_model_1_ptm_tt_3rec": (
        "AF2 monomer, target template, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model) with residue index offset to predict two separate chains, initial guess with template input for target chain. Low risk of over-confidence.",
    ),
    "af2_model_1_ptm_tbt_3rec": (
        "AF2 monomer, target & binder template, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model) with residue index offset to predict two separate chains, initial guess with separate template input for target chain and binder chain. Medium risk of over-confidence.",
    ),
    "af2_model_1_ptm_ct_3rec": (
        "AF2 monomer, complex template, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model) with residue index offset to predict two separate chains, initial guess with template input for whole target and binder complex. High risk of over-confidence.",
    ),
    "af2_model_1_multimer_tt_3rec": (
        "AF2 multimer, target template, 3 recycles",
        "AlphaFold2 model_1_multimer, initial guess with template input for target chain. Low risk of over-confidence.",
    ),
    "af2_model_1_multimer_tbt_3rec": (
        "AF2 multimer, target & binder template, 3 recycles",
        "AlphaFold2 model_1_multimer, initial guess with separate template input for target chain and binder chain. Medium risk of over-confidence.",
    ),
    "af2_model_1_multimer_ct_3rec": (
        "AF2 multimer, complex template, 3 recycles",
        "AlphaFold2 model_1_multimer, initial guess with template input for whole target and binder complex. High risk of over-confidence.",
    ),
    "boltz1_binder_nt": (
        "Boltz-1 binder, no template",
        "Boltz-1 structure prediction with no template input. Low risk of over-confidence.",
    ),
    "boltz1_binder_tt": (
        "Boltz-1 binder, target template",
        "Boltz-1 structure prediction with template input for target chain only. Low risk of over-confidence.",
    ),
    "boltz2_binder_nt": (
        "Boltz-2 binder, no template",
        "Boltz-2 structure prediction with no template input. Low risk of over-confidence.",
    ),
    "boltz2_binder_tt": (
        "Boltz-2 binder, target template",
        "Boltz-2 structure prediction with template input for target chain only. Low risk of over-confidence.",
    ),
}


REFOLDING_TESTS_BY_TYPE = {
    "scaffold": REFOLDING_TESTS_SCAFFOLD,
    "binder": REFOLDING_TESTS_BINDER,
}

REFOLDING_TESTS = {k: v for tests in REFOLDING_TESTS_BY_TYPE.values() for k, v in tests.items()}

# ESMFold descriptors

ESMFOLD_STRUCTURE_PATH = StructureFileDescriptor(
    name="ESMFold prediction",
    description="Structure predicted by ESMFold, using only sequence input",
    tool="ESMFold",
    key="refolding|esmfold|esmfold_predicted_structure_path",
    structure_type="prediction",
    b_factor_value="fractional_plddt",
)

ESMFOLD_PLDDT = NumericGlobalDescriptor(
    name="ESMFold pLDDT",
    description="Average pLDDT confidence score of the whole structure (0 = worst, 100 = best)",
    tool="ESMFold",
    key="refolding|esmfold|pLDDT",
    min_value=0,
    max_value=100,
    comparison="higher_is_better",
    color_scale="plddt",
)

ESMFOLD_PTM = NumericGlobalDescriptor(
    name="ESMFold pTM score",
    description="Predicted TM score of the full structure (0 = worst, 1 = best)",
    tool="ESMFold",
    key="refolding|esmfold|pTM",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

ESMFOLD_PAE = NumericGlobalDescriptor(
    name="ESMFold PAE",
    description="Average predicted absolute error of the whole structure (in Angstrom)",
    unit="Å",
    tool="ESMFold",
    key="refolding|esmfold|pAE",
    min_value=0,
    comparison="lower_is_better",
    color_scale="pae",
)

ESMFOLD_DESIGN_BACKBONE_RMSD = NumericGlobalDescriptor(
    name="ESMFold Design Backbone RMSD",
    description="Aligned RMSD between the backbone of the designed structure and its ESMFold prediction",
    unit="Å",
    tool="ESMFold",
    key="refolding|esmfold|RMSD_backbone",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

ESMFOLD_DESIGN_ALL_ATOM_RMSD = NumericGlobalDescriptor(
    name="ESMFold Design All-atom RMSD",
    description="Aligned RMSD between all atoms of the designed structure and its ESMFold prediction",
    unit="Å",
    tool="ESMFold",
    key="refolding|esmfold|RMSD_all_atom",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

ESMFOLD_DESCRIPTORS = [
    ESMFOLD_DESIGN_BACKBONE_RMSD,
    ESMFOLD_PAE,
    ESMFOLD_PLDDT,
    ESMFOLD_PTM,
    ESMFOLD_DESIGN_ALL_ATOM_RMSD,
]

# INITIAL GUESS DESCRIPTORS
AF2_PRIMARY_STRUCTURE_PATH = StructureFileDescriptor(
    name="AlphaFold2 Initial Guess prediction",
    description="AlphaFold2 structure prediction using Initial Guess protocol initialized with designed structure, with optional structure template input",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|af2_structure_path",
    structure_type="prediction",
    b_factor_value="plddt",
)

AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD = NumericGlobalDescriptor(
    name="AF2 Target-aligned Binder RMSD",
    description="Target-aligned binder RMSD between Ca backbone atoms of design and AF2 prediction",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|target_aligned_binder_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

AF2_PRIMARY_IPAE = NumericGlobalDescriptor(
    name="AF2 iPAE",
    description="AlphaFold2 interaction PAE, predicted aligned error of quadrants of the PAE matrix corresponding to all pairs of residues between the interacting chains (in Angstrom)",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|ipae",
    min_value=0,
    comparison="lower_is_better",
    color_scale="pae",
)

AF2_PRIMARY_IPTM = NumericGlobalDescriptor(
    name="AF2 ipTM score",
    description="AlphaFold2 interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|iptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

AF2_PRIMARY_BINDER_PAE = NumericGlobalDescriptor(
    name="AF2 Binder PAE",
    description="Predicted aligned error of the binder chain (in Angstrom)",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|binder_pae",
    min_value=0,
    comparison="lower_is_better",
    color_scale="pae",
)

AF2_PRIMARY_PLDDT_BINDER = NumericGlobalDescriptor(
    name="AF2 Binder pLDDT",
    description="Average pLDDT confidence score of the binder chain (0 = worst, 100 = best)",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|binder_plddt",
    min_value=0,
    max_value=100,
    comparison="higher_is_better",
    color_scale="plddt",
)

AF2_PRIMARY_DESIGN_RMSD = NumericGlobalDescriptor(
    name="AF2 Design RMSD",
    description="Aligned RMSD between the backbone of the designed structure and its AF2 prediction",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|design_backbone_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

AF2_PRIMARY_NATIVE_MOTIF_RMSD = NumericGlobalDescriptor(
    name="AF2 Native Motif RMSD",
    description="Aligned RMSD between all atoms of the fixed input motif and its AF2 prediction",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|native_motif_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

AF2_PRIMARY_PTM = NumericGlobalDescriptor(
    name="AF2 pTM score",
    description="Predicted TM score of the full structure (0 = worst, 1 = best)",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|ptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)


AF2_PRIMARY_PAE = NumericGlobalDescriptor(
    name="AF2 PAE",
    description="Average predicted absolute error of the whole structure (in Angstrom)",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|pae",
    min_value=0,
    comparison="lower_is_better",
    color_scale="pae",
)

AF2_PRIMARY_PLDDT = NumericGlobalDescriptor(
    name="AF2 pLDDT",
    description="Average pLDDT score of the whole structure (0 = worst, 100 = best)",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|plddt",
    min_value=0,
    max_value=100,
    comparison="higher_is_better",
    color_scale="plddt",
)

AF2_PRIMARY_INTERFACE_TARGET_RESIDUES = ResidueNumberDescriptor(
    name="AF2 Interface target residues",
    description="Predicted AF2 target residues in contact with the binder backbone (CA within 8A)",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|interface_target_residues",
)


# Initial guess descriptors
AF2_PRIMARY_DESCRIPTORS = [
    # shared
    AF2_PRIMARY_IPAE,
    AF2_PRIMARY_IPTM,
    AF2_PRIMARY_PTM,
    # binder
    AF2_PRIMARY_BINDER_PAE,
    AF2_PRIMARY_PLDDT_BINDER,
    AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD,
    AF2_PRIMARY_INTERFACE_TARGET_RESIDUES,
    # scaffold
    AF2_PRIMARY_DESIGN_RMSD,
    AF2_PRIMARY_NATIVE_MOTIF_RMSD,
    AF2_PRIMARY_PAE,
    AF2_PRIMARY_PLDDT,
]
AF2_STRUCTURE_PATHS = [AF2_PRIMARY_STRUCTURE_PATH]


# Refolding
REFOLDING_DESCRIPTORS = [
    *ESMFOLD_DESCRIPTORS,
    ESMFOLD_STRUCTURE_PATH,
    *AF2_PRIMARY_DESCRIPTORS,
    *AF2_STRUCTURE_PATHS,
]


for test, (label, description) in REFOLDING_TESTS_SCAFFOLD.items():
    if test.startswith("af2"):
        REFOLDING_DESCRIPTORS += [
            StructureFileDescriptor(
                name=f"AF2 prediction ({label})",
                description=f"Structure predicted by AlphaFold2 using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|af2_structure_path",
                structure_type="prediction",
                b_factor_value="plddt",
            ),
            NumericGlobalDescriptor(
                name="AF2 Design RMSD",
                description=f"Aligned RMSD between the backbone of the designed structure and its AF2 prediction using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|design_backbone_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="AF2 Native Motif RMSD",
                description=f"Aligned RMSD between all atoms of the fixed input motif and its AF2 prediction using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|native_motif_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 iPAE",
                description=f"AlphaFold2 interaction PAE, predicted aligned error of quadrants of the PAE matrix corresponding to all pairs of residues between the interacting chains (in Angstrom) using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ipae",
                min_value=0,
                comparison="lower_is_better",
                color_scale="pae",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 pLDDT",
                description=f"Average pLDDT score of the whole structure (0 = worst, 100 = best) using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|plddt",
                min_value=0,
                max_value=100,
                comparison="higher_is_better",
                color_scale="plddt",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 PAE",
                description=f"Average predicted absolute error of the whole structure (in Angstrom) using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|pae",
                min_value=0,
                comparison="lower_is_better",
                color_scale="pae",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 ipTM score",
                description=f"AlphaFold2 interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="AF2 pTM score",
                description=f"Predicted TM score of the full structure (0 = worst, 1 = best) using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
        ]
    elif test.startswith("boltz"):
        REFOLDING_DESCRIPTORS += [
            StructureFileDescriptor(
                name=f"{label} prediction",
                description=f"Structure predicted by Boltz using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|boltz_predicted_structure_path",
                structure_type="prediction",
                b_factor_value="plddt",
            ),
            NumericGlobalDescriptor(
                name="Boltz Design RMSD",
                description=f"Aligned RMSD between the backbone of the designed structure and its Boltz prediction using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|design_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Native Motif RMSD",
                description=f"Aligned RMSD of all atoms of the fixed input motif residues in the original input structure and the Boltz prediction using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|native_motif_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Confidence Score",
                description=f"Boltz confidence score for the predicted structure. Corresponds to 0.8 * complex_plddt + 0.2 * iptm (ptm for single chains). 0 = worst, 1 = best. using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|confidence_score",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pTM score",
                description=f"Predicted TM score of the full structure by Boltz (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|ptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipTM score",
                description=f"Boltz interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz Ligand ipTM score",
                description=f"Boltz interface predicted TM score for ligand interactions (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|ligand_iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz Protein ipTM score",
                description=f"Boltz interface predicted TM score for protein-protein interactions (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|protein_iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pLDDT",
                description=f"Average pLDDT confidence score of the whole structure (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_plddt",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipLDDT",
                description=f"Interface pLDDT confidence score of the whole structure (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_iplddt",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pDE",
                description=f"Predicted distance error of the whole structure using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_pde",
                min_value=0,
                comparison="lower_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipDE",
                description=f"Predicted distance error of the complex interface using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_ipde",
                min_value=0,
                comparison="lower_is_better",
            ),
        ]


for test, (label, description) in REFOLDING_TESTS_BINDER.items():
    if test.startswith("af2"):
        REFOLDING_DESCRIPTORS += [
            StructureFileDescriptor(
                name=f"AF2 prediction ({label})",
                description=f"Structure predicted by AlphaFold2 using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|af2_structure_path",
                structure_type="prediction",
                b_factor_value="plddt",
            ),
            NumericGlobalDescriptor(
                name="AF2 Target-aligned Binder RMSD",
                description=f"Target-aligned binder RMSD between Ca backbone atoms of design and AF2 prediction using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|target_aligned_binder_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 iPAE",
                description=f"AlphaFold2 interaction PAE, predicted aligned error of quadrants of the PAE matrix corresponding to all pairs of residues between the interacting chains (in Angstrom) using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ipae",
                min_value=0,
                comparison="lower_is_better",
                color_scale="pae",
            ),
            NumericGlobalDescriptor(
                name="AF2 Binder pLDDT",
                description=f"Average pLDDT confidence score of the binder chain (0 = worst, 100 = best) using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|binder_plddt",
                min_value=0,
                max_value=100,
                comparison="higher_is_better",
                color_scale="plddt",
            ),
            NumericGlobalDescriptor(
                name="AF2 Binder PAE",
                description=f"Predicted aligned error of the binder chain (in Angstrom) using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|binder_pae",
                min_value=0,
                comparison="lower_is_better",
                color_scale="pae",
            ),
            NumericGlobalDescriptor(
                name=f"AF2 ipTM score",
                description=f"AlphaFold2 interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="AF2 pTM score",
                description=f"Predicted TM score of the full structure (0 = worst, 1 = best) using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            ResidueNumberDescriptor(
                name="AF2 Interface target residues",
                description=f"Predicted AF2 target residues in contact with the binder backbone (CA within 8A) using {description}",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|interface_target_residues",
            ),
        ]
    elif test.startswith("boltz"):
        REFOLDING_DESCRIPTORS += [
            StructureFileDescriptor(
                name=f"{label} prediction",
                description=f"Structure predicted by Boltz using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|boltz_predicted_structure_path",
                structure_type="prediction",
                b_factor_value="plddt",
            ),
            NumericGlobalDescriptor(
                name="Boltz Target-aligned Binder RMSD",
                description=f"Target-aligned RMSD between the backbone of the binder structure and its Boltz prediction using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|binder_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Complex RMSD",
                description=f"Aligned RMSD between the backbone of the complex structure and its Boltz prediction using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Confidence Score",
                description=f"Boltz confidence score for the predicted structure. Corresponds to 0.8 * complex_plddt + 0.2 * iptm (ptm for single chains). 0 = worst, 1 = best. using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|confidence_score",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pTM score",
                description=f"Predicted TM score of the full structure by Boltz (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|ptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipTM score",
                description=f"Boltz interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz Ligand ipTM score",
                description=f"Boltz interface predicted TM score for ligand interactions (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|ligand_iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz Protein ipTM score",
                description=f"Boltz interface predicted TM score for protein-protein interactions (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|protein_iptm",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pLDDT",
                description=f"Average pLDDT confidence score of the whole structure (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_plddt",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz Binder pLDDT",
                description=f"Average pLDDT confidence score of the binder chain (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|binder_plddt",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipLDDT",
                # TODO is this a valid description?
                description=f"Interface pLDDT confidence score of the whole structure (0 = worst, 1 = best) using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_iplddt",
                min_value=0,
                max_value=1,
                comparison="higher_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz pDE",
                description=f"Predicted distance error of the whole structure using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_pde",
                min_value=0,
                comparison="lower_is_better",
            ),
            NumericGlobalDescriptor(
                name="Boltz ipDE",
                description=f"Predicted distance error of the complex interface using {description}",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|complex_ipde",
                min_value=0,
                comparison="lower_is_better",
            ),
        ]

DESCRIPTORS = REFOLDING_DESCRIPTORS
DESCRIPTORS_BY_KEY = {d.key: d for d in DESCRIPTORS}

BOLTZ2_SCAFFOLD_NT_PREDICTED_STRUCTURE_PATH = DESCRIPTORS_BY_KEY[
    "refolding|boltz2_scaffold_nt|boltz_predicted_structure_path"
]
BOLTZ2_SCAFFOLD_NT_DESIGN_RMSD = DESCRIPTORS_BY_KEY["refolding|boltz2_scaffold_nt|design_rmsd"]
BOLTZ2_SCAFFOLD_NT_NATIVE_MOTIF_RMSD = DESCRIPTORS_BY_KEY["refolding|boltz2_scaffold_nt|native_motif_rmsd"]
BOLTZ2_SCAFFOLD_NT_PLDDT = DESCRIPTORS_BY_KEY["refolding|boltz2_scaffold_nt|complex_plddt"]
BOLTZ2_SCAFFOLD_NT_PDE = DESCRIPTORS_BY_KEY["refolding|boltz2_scaffold_nt|complex_pde"]

BOLTZ2_BINDER_TT_PREDICTED_STRUCTURE_PATH = DESCRIPTORS_BY_KEY[
    "refolding|boltz2_binder_tt|boltz_predicted_structure_path"
]
BOLTZ2_BINDER_TT_TARGET_ALIGNED_BINDER_RMSD = DESCRIPTORS_BY_KEY["refolding|boltz2_binder_tt|binder_rmsd"]
BOLTZ2_BINDER_TT_IPDE = DESCRIPTORS_BY_KEY["refolding|boltz2_binder_tt|complex_ipde"]
BOLTZ2_BINDER_TT_BINDER_PLDDT = DESCRIPTORS_BY_KEY["refolding|boltz2_binder_tt|binder_plddt"]


PRESETS = [
    {
        "label": "AF2 PAE & RMSD",
        "x": AF2_PRIMARY_PAE,
        "y": AF2_PRIMARY_DESIGN_RMSD,
    },
    {
        "label": "AF2 iPAE & RMSD",
        "x": AF2_PRIMARY_IPAE,
        "y": AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD,
    },
    {
        "label": "ESMFold PAE & RMSD",
        "x": ESMFOLD_PAE,
        "y": ESMFOLD_DESIGN_BACKBONE_RMSD,
    },
]
