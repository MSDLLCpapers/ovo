import os
import argparse
import glob

from typing import List, Tuple

import pandas as pd
import numpy as np

from Bio.PDB import PDBParser
from Bio import PDB
from Bio.PDB.Polypeptide import is_aa
from Bio.SeqUtils import seq1


def save_first_model_with_chains(
    pdb_file_path: str, out_pdb_file_path: str, chains_to_keep: List[str] = [], skip_unknown: bool = True
):
    """
    Save the first model of a PDB file if it contains multiple models.
    Also if chains_to_keep is provided, only those chains will be saved.
    If skip_unk is True, chains containing UNK residues will not be saved.

    """

    class _SelectChains(PDB.Select):
        def accept_chain(self, chain):
            if chain.id not in chains_to_keep:
                return False
            # Only keep chains with at least one protein residue
            for residue in chain.get_residues():
                if is_aa(residue.get_resname(), standard=True):
                    return True
            return False

        def accept_residue(self, residue):
            if skip_unknown and residue.get_resname() == "UNK":
                return False
            # Only keep standard amino acids
            return is_aa(residue.get_resname(), standard=True)

    # Check if the PDB file contains multiple models
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("structure", pdb_file_path)
    first_model = structure[0]
    io = PDB.PDBIO()
    io.set_structure(first_model)
    io.save(out_pdb_file_path, _SelectChains())
    return


def validate_chains_present(pdb_file_path: str, expected_chains: List[str]):
    """
    Validate that the filtered PDB file contains all expected chains.
    Raises ValueError if any expected chains are missing or if the file is empty.
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("structure", pdb_file_path)

    if not list(structure.get_models()):
        raise ValueError(f"Filtered file is empty and chains not found: {pdb_file_path}")
    first_model = structure[0]

    # Get the chain IDs present in the file
    present_chains = set(chain.id for chain in first_model)

    # Check if file is empty (no chains)
    if not present_chains:
        raise ValueError(f"No chains found in filtered file: {pdb_file_path}")

    # Check if all expected chains are present
    expected_set = set(expected_chains)
    missing_chains = expected_set - present_chains

    if missing_chains:
        raise ValueError(
            f"Requested chain {', '.join(missing_chains)} is missing in structure: {pdb_file_path}, available chains: {', '.join(present_chains)}"
        )

    return True


def check_short_sequences(pdb_file_path: str, min_length: int = 21):
    """
    Check the sequences to be processed by foldseek comply with the lower sequence length limit.
    Raises ValueError if any chain has a sequence shorter than min_length.
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("structure", pdb_file_path)
    first_model = structure[0]

    short_sequences = {}

    for chain in first_model:
        # Extract sequence from chain
        sequence = []
        for residue in chain:
            if is_aa(residue.get_resname(), standard=True):
                sequence.append(seq1(residue.get_resname()))

        seq_str = "".join(sequence)
        if len(seq_str) < min_length:
            short_sequences[chain.id] = seq_str

    if short_sequences:
        error_msg = f"Found chains with sequences shorter than {min_length} residues in {pdb_file_path}:\n"
        for chain_id, seq in short_sequences.items():
            error_msg += f"  Chain {chain_id}: {len(seq)} residues\n"
        raise ValueError(error_msg)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing PDB files")
    parser.add_argument("--chains", type=str, required=True, help="Comma-separated list of chains to keep")
    parser.add_argument("--min_length", type=int, default=21, help="Minimum sequence length (default: 21)")

    args = parser.parse_args()
    chains_to_keep = args.chains.split(",")

    # Find all PDB files in the directory
    pdb_files = glob.glob(os.path.join(args.input_dir, "*.pdb"))
    if not pdb_files:
        raise FileNotFoundError(f"No PDB files found in directory: {args.input_dir}")

    print(f"Found {len(pdb_files)} PDB files to process in {args.input_dir}")

    # Process each PDB file
    failed_files = []
    for pdb_file in pdb_files:
        # Extract the desired chains
        save_first_model_with_chains(pdb_file, pdb_file, chains_to_keep)
        # Check file contains the desired chains
        validate_chains_present(pdb_file, chains_to_keep)
        # Check sequences meet the minimum length requirement
        check_short_sequences(pdb_file, args.min_length)
