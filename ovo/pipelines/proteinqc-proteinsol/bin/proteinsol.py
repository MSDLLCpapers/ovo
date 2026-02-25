import protein_sol_api
import os
import argparse
import glob

from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from Bio import SeqIO

from typing import Tuple, List

import pandas as pd
import numpy as np

pdb_parser: PDBParser = PDBParser(QUIET=True)
AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
PROTEINSOL_MIN_LENGTH = 21


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


def filter_short_sequences(sequences: dict, min_length: int = 21) -> Tuple[dict, dict]:
    """
    Split the sequences into two dictionaries: one with sequences longer than min_length and one with sequences shorter than min_length.
    """
    min_length_sequences = {}
    short_sequences = {}
    for seq_id, sequence in sequences.items():
        if len(sequence) >= min_length:
            min_length_sequences[seq_id] = sequence
        else:
            short_sequences[seq_id] = sequence
    return short_sequences, min_length_sequences


def get_charge_perc(x) -> Tuple[float, float]:
    """
    Calculate the percentage of positive and negative charges in a list of charges.
    """
    x_wo_none = [value for value in x if value is not None]
    positive_perc = len([value for value in x_wo_none if value > 0]) / len(x_wo_none) * 100
    negative_perc = len([value for value in x_wo_none if value < 0]) / len(x_wo_none) * 100
    return (positive_perc, negative_perc)


def charged_avg(x) -> Tuple[float, float]:
    """
    Calculate the average positive and negative charges in a list of charges.
    """
    x_wo_none = [value for value in x if value is not None]
    positive_avg = np.mean([value for value in x_wo_none if value > 0])
    negative_avg = np.mean([value for value in x_wo_none if value < 0])
    return (positive_avg, negative_avg)


def expand_chains_per_structure(filename: str, seqs_concat: list[tuple[str, str]]) -> dict[str, str]:
    """
    Create a dictionary mapping of structure with chain ID to its corresponding sequences.

    Example:
        >>> expand_chains_per_structure("1abc", [("ACDE", "A"), ("FGHI", "B")])
        {'1abc_A': 'ACDE', '1abc_B': 'FGHI'}
    """
    if not seqs_concat:
        return {}
    return {"_".join([filename, chain]): seq for seq, chain in seqs_concat}


def weighted_avg(x: pd.DataFrame, col: str) -> float:
    """
    Computes weighted average for a given column with respect to sequence length.
    """
    return (x[col] * x["seq_len"]).sum() / x["seq_len"].sum()


def custom_agg(x: pd.DataFrame, agg_map: dict, weighted_cols: list) -> pd.Series:
    """
    Aggregate columns with specified functions and do weighted averages on selected columns.
    """
    result = {}
    for col, func in agg_map.items():
        result[col] = func(x[col])
    for col in weighted_cols:
        result[col] = weighted_avg(x, col)
    return pd.Series(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_csv", type=str)
    parser.add_argument("-c", "--chains", type=str, default="A", help="Chain to extract the sequence from")
    options = parser.parse_args()

    chains = [chain.strip() for chain in options.chains.split(",")]

    if os.path.isdir(options.input_path):
        paths = sorted(glob.glob(os.path.join(options.input_path, "*.pdb")))
        print(f"Reading sequences from {len(paths):,} PDBs")
        sequences_by_id = {
            struct_chain_id: sequence
            for path in paths
            for struct_chain_id, sequence in expand_chains_per_structure(
                os.path.splitext(os.path.basename(path))[0], get_sequences_from_pdb_file(path, chains=chains)
            ).items()
        }
    elif options.input_path.endswith((".pdb",)):
        sequences_by_id = {
            struct_chain_id: sequence
            for struct_chain_id, sequence in expand_chains_per_structure(
                os.path.splitext(os.path.basename(options.input_path))[0],
                get_sequences_from_pdb_file(options.input_path, chains=chains),
            ).items()
        }
    elif options.input_path.endswith((".fasta", ".fa")):
        sequences_by_id = {
            record.id.split("|")[0]: str(record.seq) for record in SeqIO.parse(options.input_path, "fasta")
        }
    else:
        raise ValueError("Input must be a directory with PDB files, a PDB file, or a FASTA file")

    # ProteinSol only predicts for sequences >= 21aa
    # Filter out too short sequences
    short_sequences_by_id, normal_sequences_by_id = filter_short_sequences(sequences_by_id, PROTEINSOL_MIN_LENGTH)

    # If no long-enough sequences are found
    if not normal_sequences_by_id:
        with open(options.output_csv, "w") as f:
            df = pd.DataFrame({"id": short_sequences_by_id.keys()})
            df["error"] = "Sequence too short"
    else:
        result = protein_sol_api.protein_sol(list(normal_sequences_by_id.values()))
        df = pd.DataFrame(result)
        df["seq_len"] = pd.Series(list(normal_sequences_by_id.values())).apply(lambda x: x.__len__())

        # Add ids to the dataframe
        df.insert(0, "id", normal_sequences_by_id.keys())

        # Add short sequences to the dataframe
        short_df = pd.DataFrame({"id": short_sequences_by_id.keys()})
        short_df["error"] = "Sequence too short"
        df = pd.concat([df, short_df], ignore_index=True)

    # Separate structure id from processed chains
    df["chains"] = df["id"].apply(lambda x: x.rsplit("_", 1)[1] if "_" in x else "")
    df["id"] = df["id"].apply(lambda x: x.rsplit("_", 1)[0] if "_" in x else x)

    # Aggregate protein id, chains, errors and compute weighted average for specified numeric values
    AGG_MAP = {
        "id": lambda x: np.unique(x)[0],
        "chains": lambda x: ",".join(x.dropna().astype(str)),
        "error": lambda x: list(x.dropna().astype(str)),
    }

    NUMERIC_VALUES = ["percent-sol", "scaled-sol", "population-sol"]

    # Fixed behavior in Pandas 3.0
    df = (
        df.groupby("id")[list(AGG_MAP) + NUMERIC_VALUES + ["seq_len"]]
        .apply(lambda g: custom_agg(g, AGG_MAP, NUMERIC_VALUES))
        .reset_index(drop=True)
    )
    df.to_csv(options.output_csv, index=False)
