from ovo.core.database.models import (
    NumericGlobalDescriptor,
    StructureFileDescriptor,
    ResidueNumberDescriptor,
    Descriptor,
)

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
    "af2_model_1_ptm_binderalone_3rec": (
        "AF2 monomer, binder sequence alone, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model), no initial guess and no template input. Used for an unbiased prediction of binder structure alone.",
    ),
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
    "boltz2_binder_alone": (
        "Boltz-2 binder sequence alone",
        "Boltz-2 structure prediction of the binder sequence alone, without the target and with no template input. Used for an unbiased prediction of binder structure alone.",
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

REFOLDING_TESTS_SEQUENCE = {
    "af2_model_1_ptm_seq_3rec": (
        "AF2 monomer, sequence only, 3 recycles",
        "AlphaFold2 model_1_ptm (monomer model), sequence input only - no initial guess and no template input. Low risk of over-confidence, but may fail to predict the structure (since no MSA input is provided either).",
    )
}


REFOLDING_TESTS_BY_TYPE = {
    "scaffold": REFOLDING_TESTS_SCAFFOLD,
    "binder": REFOLDING_TESTS_BINDER,
    "sequence": REFOLDING_TESTS_SEQUENCE,
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

AF2_PRIMARY_BINDER_ALONE_BB_RMSD = NumericGlobalDescriptor(
    name="AF2 Binder Alone Backbone RMSD",
    description="RMSD between Ca backbone atoms of design and AF2 prediction of binder sequence alone",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|binder_alone_bb_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

AF2_PRIMARY_BINDER_ALONE_AA_RMSD = NumericGlobalDescriptor(
    name="AF2 Binder Alone All-atom RMSD",
    description="RMSD between all atoms of design and AF2 prediction of binder sequence alone",
    unit="Å",
    tool="AF2 Initial Guess",
    key="refolding|af2_primary|binder_alone_aa_rmsd",
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

AF2_REF_STRUCTURE_ALL_ATOM_RMSD = NumericGlobalDescriptor(
    name="AF2 Reference Structure All Atom RMSD",
    description="Aligned RMSD between all atoms of the reference structure and the design structure AF2 prediction, after aligning the sequences",
    unit="Å",
    tool="AlphaFold2",
    key="refolding|af2_primary|ref_structure_all_atom_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)

AF2_REF_STRUCTURE_BACKBONE_RMSD = NumericGlobalDescriptor(
    name="AF2 Reference Structure Backbone RMSD",
    description="Aligned RMSD between backbone Ca atoms of the reference structure and the design structure AF2 prediction, after aligning the sequences",
    unit="Å",
    tool="AlphaFold2",
    key="refolding|af2_primary|ref_structure_backbone_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
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
    AF2_PRIMARY_BINDER_ALONE_BB_RMSD,
    AF2_PRIMARY_BINDER_ALONE_AA_RMSD,
    AF2_PRIMARY_INTERFACE_TARGET_RESIDUES,
    # scaffold
    AF2_PRIMARY_DESIGN_RMSD,
    AF2_PRIMARY_NATIVE_MOTIF_RMSD,
    AF2_PRIMARY_PAE,
    AF2_PRIMARY_PLDDT,
    # sequence
    AF2_REF_STRUCTURE_ALL_ATOM_RMSD,
    AF2_REF_STRUCTURE_BACKBONE_RMSD,
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
                description=f"Average pLDDT score when upweighting interface tokens (0 = worst, 1 = best) using {description}",
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
                name="AF2 Binder Alone Backbone RMSD",
                description=f"RMSD between Ca backbone atoms of design and AF2 prediction of binder sequence alone using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|binder_alone_bb_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="AF2 Binder Alone All-atom RMSD",
                description=f"RMSD between all atoms of design and AF2 prediction of binder sequence alone using {description}",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|binder_alone_aa_rmsd",
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
                key=f"refolding|{test}|target_aligned_binder_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Binder Alone Backbone RMSD",
                description=f"RMSD between Ca backbone atoms of design and Boltz prediction of binder sequence alone using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|binder_alone_bb_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="Boltz Binder Alone All-atom RMSD",
                description=f"RMSD between all atoms of design and Boltz prediction of binder sequence alone using {description}",
                unit="Å",
                tool=f"Boltz ({label})",
                key=f"refolding|{test}|binder_alone_aa_rmsd",
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
                description=f"Average pLDDT score when upweighting interface tokens (0 = worst, 1 = best) using {description}",
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


for test, (label, description) in REFOLDING_TESTS_SEQUENCE.items():
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
                name="AF2 Reference Structure All Atom RMSD",
                description=f"Aligned RMSD between all atoms of the reference structure and the AF2 prediction of the design sequence using {description}, after aligning the sequences",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ref_structure_all_atom_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
            ),
            NumericGlobalDescriptor(
                name="AF2 Reference Structure Backbone RMSD",
                description=f"Aligned RMSD between backbone Ca atoms of the reference structure and the AF2 prediction of the design sequence using {description}, after aligning the sequences",
                unit="Å",
                tool=f"AlphaFold2 ({label})",
                key=f"refolding|{test}|ref_structure_backbone_rmsd",
                min_value=0,
                comparison="lower_is_better",
                color_scale="rmsd",
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


BOLTZ_PRIMARY_STRUCTURE_PATH = StructureFileDescriptor(
    name=f"Boltz-2 prediction",
    description=f"Structure predicted by Boltz",
    tool="Boltz",
    key=f"refolding|boltz_primary|boltz_predicted_structure_path",
    structure_type="prediction",
    b_factor_value="plddt",
)
BOLTZ_PRIMARY_DESIGN_RMSD = NumericGlobalDescriptor(
    name="Boltz Design RMSD",
    description=f"Aligned RMSD between the backbone of the designed structure and its Boltz prediction",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|design_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_NATIVE_MOTIF_RMSD = NumericGlobalDescriptor(
    name="Boltz Native Motif RMSD",
    description=f"Aligned RMSD of all atoms of the fixed input motif residues in the original input structure and the Boltz prediction",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|native_motif_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_CONFIDENCE_SCORE = NumericGlobalDescriptor(
    name="Boltz Confidence Score",
    description=f"Boltz confidence score for the predicted structure. Corresponds to 0.8 * complex_plddt + 0.2 * iptm (ptm for single chains). 0 = worst, 1 = best.",
    tool="Boltz",
    key=f"refolding|boltz_primary|confidence_score",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_PTM_SCORE = NumericGlobalDescriptor(
    name="Boltz pTM score",
    description=f"Predicted TM score of the full structure by Boltz (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|ptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_IPTM_SCORE = NumericGlobalDescriptor(
    name="Boltz ipTM score",
    description=f"Boltz interface predicted TM score (0 = worst, 1 = best) based on all pairs of residues between the interacting chains",
    tool="Boltz",
    key=f"refolding|boltz_primary|iptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_LIGAND_IPTM_SCORE = NumericGlobalDescriptor(
    name="Boltz Ligand ipTM score",
    description=f"Boltz interface predicted TM score for ligand interactions (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|ligand_iptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_PROTEIN_IPTM_SCORE = NumericGlobalDescriptor(
    name="Boltz Protein ipTM score",
    description=f"Boltz interface predicted TM score for protein-protein interactions (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|protein_iptm",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_PLDDT = NumericGlobalDescriptor(
    name="Boltz pLDDT",
    description=f"Average pLDDT confidence score of the whole structure (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|complex_plddt",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_IPLDDT = NumericGlobalDescriptor(
    name="Boltz ipLDDT",
    description=f"Average pLDDT score when upweighting interface tokens (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|complex_iplddt",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)
BOLTZ_PRIMARY_PDE = NumericGlobalDescriptor(
    name="Boltz pDE",
    description=f"Predicted distance error of the whole structure",
    tool="Boltz",
    key=f"refolding|boltz_primary|complex_pde",
    min_value=0,
    comparison="lower_is_better",
)
BOLTZ_PRIMARY_IPDE = NumericGlobalDescriptor(
    name="Boltz ipDE",
    description=f"Predicted distance error of the complex interface",
    tool="Boltz",
    key=f"refolding|boltz_primary|complex_ipde",
    min_value=0,
    comparison="lower_is_better",
)
BOLTZ_PRIMARY_TARGET_ALIGNED_BINDER_RMSD = NumericGlobalDescriptor(
    name="Boltz Target-aligned Binder RMSD",
    description=f"Target-aligned RMSD between the backbone of the binder structure and its Boltz prediction",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|target_aligned_binder_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_BINDER_ALONE_BB_RMSD = NumericGlobalDescriptor(
    name="Boltz Binder Alone Backbone RMSD",
    description="RMSD between Ca backbone atoms of design and Boltz prediction of binder sequence alone",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|binder_alone_bb_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_BINDER_ALONE_AA_RMSD = NumericGlobalDescriptor(
    name="Boltz Binder Alone All-atom RMSD",
    description="RMSD between all atoms of design and Boltz prediction of binder sequence alone",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|binder_alone_aa_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_COMPLEX_RMSD = NumericGlobalDescriptor(
    name="Boltz Complex RMSD",
    description=f"Aligned RMSD between the backbone of the complex structure and its Boltz prediction",
    unit="Å",
    tool="Boltz",
    key=f"refolding|boltz_primary|complex_rmsd",
    min_value=0,
    comparison="lower_is_better",
    color_scale="rmsd",
)
BOLTZ_PRIMARY_BINDER_PLDDT = NumericGlobalDescriptor(
    name="Boltz Binder pLDDT",
    description=f"Average pLDDT confidence score of the binder chain (0 = worst, 1 = best)",
    tool="Boltz",
    key=f"refolding|boltz_primary|binder_plddt",
    min_value=0,
    max_value=1,
    comparison="higher_is_better",
)

REFOLDING_DESCRIPTORS.extend(
    [v for k, v in globals().items() if isinstance(v, Descriptor) and k.startswith("BOLTZ_PRIMARY")]
)

DESCRIPTORS = REFOLDING_DESCRIPTORS
DESCRIPTORS_BY_KEY = {d.key: d for d in DESCRIPTORS}

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
    {
        "label": "Boltz pDE & Design RMSD",
        "x": BOLTZ_PRIMARY_PDE,
        "y": BOLTZ_PRIMARY_DESIGN_RMSD,
    },
    {
        "label": "Boltz ipDE & Binder RMSD",
        "x": BOLTZ_PRIMARY_IPDE,
        "y": BOLTZ_PRIMARY_TARGET_ALIGNED_BINDER_RMSD,
    },
]
