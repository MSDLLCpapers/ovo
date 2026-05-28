import os
import argparse
import glob
from typing import List

import pandas as pd

from Bio.PDB import PDBParser
from Bio import Align, PDB
from Bio.SeqUtils import seq1
from Bio.PDB.cealign import CEAligner
from scipy.spatial.distance import cdist

pdb_parser: PDBParser = PDBParser(QUIET=True)

# Sequence aligner: corresponsds to pairwise2.align,globalxx
sequence_aligner = Align.PairwiseAligner()
sequence_aligner.mode = "global"
sequence_aligner.match_score = 1
sequence_aligner.mismatch_score = 0
sequence_aligner.open_gap_score = 0
sequence_aligner.extend_gap_score = 0

# Structure aligner
cealigner = CEAligner()

# DSSP aligner
# Could define a custom substitution matrix for secondary structure elements (relevant for DSSP - multiple helix types etc., for pyDSSP probably not needed)
dssp_aligner = Align.PairwiseAligner()
dssp_aligner.mode = "global"
dssp_aligner.match_score = 1
dssp_aligner.mismatch_score = 0
dssp_aligner.open_gap_score = 0
dssp_aligner.extend_gap_score = 0


#######################
# Sequence similarity #
#######################
def get_sequences_from_pdb_file(file_path: str, chains: List[str]) -> list[tuple[str, str]]:
    """
    Get pairs of sequences and chain identifiers from the pdb structure file.
    """
    with open(file_path) as f:
        parsed_structure = pdb_parser.get_structure("", f)
        available_chains = [c.get_id() for c in parsed_structure[0].get_chains()]
        seqs_concat = []
        for chain in chains:
            if chain not in available_chains:
                raise ValueError(
                    f"Chain {chain} not found in structure {os.path.basename(file_path)}, available chains: {available_chains}"
                )
            sequence = []
            for residue in parsed_structure[0][chain]:
                if residue.has_id("CA"):
                    sequence.append(seq1(residue.get_resname()))
            seqs_concat.append(("".join(sequence), chain))
        return seqs_concat


def cyclic_sequence_alignment_score(seq1: str, seq2: str, aligner: Align.PairwiseAligner) -> float:
    """
    Calculate the best alignment score for two cyclic peptides by considering all possible rotations of one sequence.
    """
    cyclic_seq1 = seq1 + seq1
    best_score = float("-inf")

    for i in range(len(seq1)):
        current_slice = cyclic_seq1[i : i + len(seq1)]
        score = aligner.score(current_slice, seq2)
        if score > best_score:
            best_score = score

    return best_score


def linear_sequence_alignment_score(seq1: str, seq2: str, aligner: Align.PairwiseAligner) -> float:
    """
    Calculate the alignment score for two linear proteins.
    """

    return aligner.score(seq1, seq2)


def get_sequence_distance_matrix(
    sequences: pd.DataFrame, aligner: Align.PairwiseAligner, seq_columns: List[str], cyclic: bool = False
) -> pd.DataFrame:
    """
    Calculate the sequence distance matrix for a set of sequences. If cyclic is True, calculate the best alignment score for cyclic peptides.
    The alignment scores are normalized to the range [0, 1] by dividing by the length of the longer sequence and subtracting from 1 to get a distance-like measure (where 0 means identical and 1 means completely different).
    """
    distance_matrix = pd.DataFrame(index=sequences.index, columns=sequences.index, dtype=float)

    for i in range(len(sequences)):
        print(f"Calculating matrix: {i + 1}/{len(sequences)}")
        for j in range(i, len(sequences)):
            if i <= j:
                if i == j:
                    distance_matrix.iloc[i, j] = 0.0  # Distance of a sequence with itself is 0.0
                    continue
                else:
                    # concatenate multiple chains into one sequence
                    # we assume that chains with the same ID should align to each other,
                    # so we don't need to test different permutations of chain orderings in the alignments
                    seq1 = "".join(sequences.iloc[i][seq_column] for seq_column in seq_columns)
                    seq2 = "".join(sequences.iloc[j][seq_column] for seq_column in seq_columns)
                    if cyclic:
                        score = cyclic_sequence_alignment_score(seq1, seq2, aligner)
                    else:
                        score = linear_sequence_alignment_score(seq1, seq2, aligner)
                    normalized_score = 1 - (score / max(len(seq1), len(seq2)))  # Normalize to get distance
                    distance_matrix.iloc[i, j] = normalized_score
                    distance_matrix.iloc[j, i] = normalized_score

    return distance_matrix


########################
# Structure similarity #
########################
def get_safe_window_size(structure: PDB.Structure.Structure) -> int:
    """
    Calculate appropriate window_size for CEAligner based on structure length.
    CEAligner can fail for short peptides with the default window size.
    For short sequences, use a smaller window corresponding to half the sequence length; for longer sequences, use the default (8).
    """
    n_residues = sum(1 for _ in structure.get_residues())
    default_window_size = 8
    half_length = n_residues // 2
    window_size = min(default_window_size, half_length)
    if window_size < 1:
        raise ValueError(f"Structure has too few residues ({n_residues}) for CEAligner, cannot set a valid window_size")
    if window_size != default_window_size:
        print(f"Adjusting CEAligner window_size to {window_size} for structure with {n_residues} residues")
    return window_size


def get_ce_align_rmsd_matrix(
    pdb_paths: List[str], structure_ids: List[str], chain: str, cyclic: bool = False
) -> pd.DataFrame:
    """
    Calculate the RMSD similarity matrix for a set of protein structures. The RMSD is calculated based on the specified chain and CA atoms.
    The structures are aligned using the CEAligner which supports flexible alignments and can handle cases where the structures have different lengths.
    """
    distance_matrix = pd.DataFrame(index=structure_ids, columns=structure_ids, dtype=float)

    structures = [pdb_parser.get_structure(f"Protein{i + 1}", pdb_path) for i, pdb_path in enumerate(pdb_paths)]

    # Select only specified chain and CA atoms
    chain_structures = [select_chain_and_ca_atoms(structure, chain) for structure in structures]

    for i in range(len(pdb_paths)):
        print(f"Calculating matrix: {i + 1}/{len(pdb_paths)}")
        for j in range(i, len(pdb_paths)):
            if i <= j:
                if i == j:
                    distance_matrix.iloc[i, j] = 0.0  # RMSD of a structure with itself is 0.0
                    continue
                else:
                    if cyclic:
                        rmsd = cyclic_ce_align_rmsd_score(chain_structures[i], chain_structures[j], chain_id=chain)
                    else:
                        rmsd = linear_ce_align_rmsd_score(chain_structures[i], chain_structures[j])
                    distance_matrix.iloc[i, j] = rmsd
                    distance_matrix.iloc[j, i] = rmsd

    return distance_matrix


def linear_ce_align_rmsd_score(structure1: PDB.Structure.Structure, structure2: PDB.Structure.Structure) -> float:
    """
    Calculate the RMSD score between two structures using CEAligner.
    Window size is automatically adjusted based on the shorter structure length.
    """
    # Set window_size based on the shorter structure
    window_size = min(get_safe_window_size(structure1), get_safe_window_size(structure2))
    cealigner.window_size = window_size

    cealigner.set_reference(structure1)
    cealigner.align(structure2)
    return cealigner.rms


def cyclic_ce_align_rmsd_score(
    structure1: PDB.Structure.Structure, structure2: PDB.Structure.Structure, chain_id: str
) -> float:
    """Calculate the best RMSD score between two cyclic structures by considering all possible rotations of one structure.
    The rotations are generated by rotating the sequence and renumbering the residues accordingly, and then aligning each rotated structure to the reference structure using CEAligner. The minimum RMSD across all rotations is returned as the final score.
    Window size is automatically adjusted based on the shorter structure length.
    """
    # Set window_size based on the shorter structure
    window_size = min(get_safe_window_size(structure1), get_safe_window_size(structure2))
    cealigner.window_size = window_size

    cealigner.set_reference(structure1)
    rotated_structures = get_all_rotations(structure2, chain_id=chain_id)
    rmsds = []
    for rotated_structure in rotated_structures:
        cealigner.align(rotated_structure)
        rmsds.append(cealigner.rms)
    return min(rmsds)


def select_chain_and_ca_atoms(structure: PDB.Structure.Structure, chain_id: str) -> PDB.Structure.Structure:
    """
    Create a new structure containing only the specified chain and CA atoms from the original structure.
    """
    new_structure = PDB.Structure.Structure(structure.id)
    model = structure[0]
    new_model = PDB.Model.Model(model.id)
    new_structure.add(new_model)

    if chain_id in model:
        chain = model[chain_id]
        new_chain = PDB.Chain.Chain(chain.id)
        new_model.add(new_chain)

        for residue in chain:
            new_residue = PDB.Residue.Residue(residue.id, residue.resname, residue.segid)
            new_chain.add(new_residue)

            for atom in residue:
                if atom.get_id() == "CA":
                    new_atom = PDB.Atom.Atom(
                        atom.name,
                        atom.coord,
                        atom.bfactor,
                        atom.occupancy,
                        atom.altloc,
                        atom.fullname,
                        atom.serial_number,
                        element=atom.element,
                    )
                    new_residue.add(new_atom)

    return new_structure


def get_all_rotations(ca_structure: PDB.Structure.Structure, chain_id: str) -> List[PDB.Structure.Structure]:
    """
    Generate all possible rotations of the structure by rotating the sequence and renumbering the residues accordingly.
    This is a helper function for cyclic CEAligner RMSD calculation.
    """
    ca_residues = [residue for residue in ca_structure.get_residues() if "CA" in residue]
    n = len(ca_residues)

    rotated_structures = []

    # Create rotated versions by building structures directly
    for shift in range(0, n):
        # Build new structure from scratch
        new_structure = PDB.Structure.Structure(ca_structure.id)
        new_model = PDB.Model.Model(0)
        new_chain = PDB.Chain.Chain(chain_id)
        new_structure.add(new_model)
        new_model.add(new_chain)

        # Add residues in rotated order with renumbered IDs
        for i in range(n):
            old_index = (i - shift) % n
            # Copy the residue
            residue = ca_residues[old_index]
            new_residue = PDB.Residue.Residue((" ", i + 1, " "), residue.resname, residue.segid)

            # Copy the CA atom
            ca_atom = residue["CA"]
            new_atom = PDB.Atom.Atom(
                ca_atom.name,
                ca_atom.coord.copy(),
                ca_atom.bfactor,
                ca_atom.occupancy,
                ca_atom.altloc,
                ca_atom.fullname,
                i + 1,  # Update serial number
                element=ca_atom.element,
            )
            new_residue.add(new_atom)
            new_chain.add(new_residue)
        rotated_structures.append(new_structure)
    return rotated_structures


#################################
# Interface residues similarity #
#################################
def get_interface_residues_distance_matrix(
    structure_ids: List[str], interface_residues_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the Jaccard distance matrix for interface residues.
    """
    if "design_id" in interface_residues_df.columns:
        interface_residues_df.set_index("design_id", inplace=True)

    # Assert that the order of structure_ids matches the order of rows in interface_residues_df
    interface_residues_df = interface_residues_df.loc[structure_ids]
    assert interface_residues_df.index.to_list() == structure_ids, (
        "Expected columns of interface_residues_df to match structure_ids"
    )

    print(f"Calculating Jaccard distance matrix {len(structure_ids):,}x{len(structure_ids):,} pairs")
    distance_matrix = pd.DataFrame(
        cdist(interface_residues_df, interface_residues_df, metric="jaccard"),
        index=structure_ids,
        columns=structure_ids,
        dtype=float,
    )

    return distance_matrix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate pairwise distance matrix for protein structures. "
        "Outputs DISTANCE matrices where 0 = identical and higher values = more different."
    )
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing PDB files")
    parser.add_argument("--output_matrix", type=str, required=True, help="Path to output distance matrix CSV file")
    parser.add_argument("--chains", type=str, required=True, help="Comma-separated list of chains to keep")
    parser.add_argument("--method", type=str, required=True, help="Similarity method")
    parser.add_argument(
        "--cyclic",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        default=False,
        help="Whether the sequence is cyclic (default: False)",
    )
    parser.add_argument(
        "--dssp_csv",
        type=str,
        default=None,
        help="Path to CSV file with DSSP annotations (required if method is 'secondary_structure')",
    )
    parser.add_argument(
        "--interface_residues_csv",
        type=str,
        default=None,
        help="Path to CSV file with interface residues (required if method is 'interface_residues')",
    )

    args = parser.parse_args()

    chains = [chain.strip() for chain in args.chains.split(",")]
    cyclic = args.cyclic

    methods_supported = ["sequence", "rmsd", "secondary_structure", "interface_residues"]
    method = args.method.lower()
    if method not in methods_supported:
        raise ValueError(f"Unsupported similarity method: {method}, supported methods: {methods_supported}")

    pdb_files = glob.glob(os.path.join(args.input_dir, "*.pdb"))
    csv_files = glob.glob(os.path.join(args.input_dir, "*.csv"))
    if not pdb_files and not csv_files:
        raise FileNotFoundError(f"No PDB or CSV files found in directory: {args.input_dir}")
    if pdb_files and csv_files:
        raise ValueError(
            f"Both PDB and CSV files found in directory: {args.input_dir}, please provide only one type of input"
        )
    if csv_files and len(csv_files) > 1:
        raise ValueError(
            f"Multiple CSV files found in directory: {args.input_dir}, please provide only one CSV file as input"
        )

    if csv_files:
        csv_file = csv_files[0]
        print(f"Found CSV file to process: {csv_file}")
        seqs = pd.read_csv(csv_file, index_col=0)
        seqs.index.name = "ID"
        for chain in chains:
            if chain not in seqs.columns:
                raise ValueError(
                    f"Specified chain {chain} not found in input CSV columns: {seqs.columns}. The input CSV should contain index with design IDs and a column for each chain with the sequences."
                )
        available_structures = False
    else:
        print(f"Found {len(pdb_files)} PDB files to process in {args.input_dir}")
        available_structures = True

        # Extract sequences from PDB files
        seqs = pd.DataFrame(
            [
                {
                    "ID": os.path.splitext(os.path.basename(pdb_file))[0],
                    **{chain: seq for seq, chain in get_sequences_from_pdb_file(pdb_file, chains=chains)},
                }
                for pdb_file in pdb_files
            ],
        ).set_index("ID")

    if method == "sequence":
        distance_matrix = get_sequence_distance_matrix(
            seqs, cyclic=cyclic, aligner=sequence_aligner, seq_columns=chains
        )
    elif method == "rmsd":
        if len(chains) > 1:
            raise NotImplementedError("RMSD calculation for multiple chains is not implemented yet")
        if not available_structures:
            raise ValueError(
                "RMSD similarity method requires PDB files as input, but a CSV file was provided. Please provide a directory with PDB files as input."
            )
        distance_matrix = get_ce_align_rmsd_matrix(pdb_files, seqs.index.to_list(), chain=chains[0], cyclic=cyclic)
    elif method == "interface_residues":
        if args.interface_residues_csv is None:
            raise ValueError(
                "Path to CSV file with interface residues must be provided for 'interface_residues' method"
            )
        interface_residues_df = pd.read_csv(args.interface_residues_csv, index_col=0)
        distance_matrix = get_interface_residues_distance_matrix(seqs.index.tolist(), interface_residues_df)
    elif method == "secondary_structure":
        if args.dssp_csv is None:
            raise ValueError("Path to CSV file with DSSP annotations must be provided for 'secondary_structure' method")
        dssp_df = pd.read_csv(args.dssp_csv, index_col=0)
        dssp_df.index.name = "index"
        # NOTE: "-" is not treated as a gap by the aligner, so we can keep it as is to represent no secondary structure in the secondary structure sequences
        distance_matrix = get_sequence_distance_matrix(
            dssp_df, cyclic=cyclic, aligner=dssp_aligner, seq_columns=["rfd_ee|backbone_metrics|pydssp_str"]
        )
    else:
        raise NotImplementedError(f"Similarity method {method} is not implemented yet")

    distance_matrix.to_csv(args.output_matrix)
