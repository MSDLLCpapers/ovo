import glob
import os
from typing import Tuple, Dict
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
import pandas as pd
import numpy as np
import argparse
from scipy.stats import entropy

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
NONPOLAR = list("GAVLI")
POLAR_UNCHARGED = list("STCNQY")
POSITIVE = list("KRH")
NEGATIVE = list("DE")
TURN = list("NGPS")  # (Asn, Gly, Pro and Ser)
AROMATIC = list("FYW")
DENQ = list("DENQ")
GROUPS = [NONPOLAR, POLAR_UNCHARGED, POSITIVE, NEGATIVE, TURN, AROMATIC, DENQ]

pdb_parser: PDBParser = PDBParser(QUIET=True)


def get_sequence_from_pdb_file(file_path: str, chains: list[str]) -> str:
    """
    Get the sequence of a structure from the pdb file.
    """
    with open(file_path) as f:
        parsed_structure = pdb_parser.get_structure("", f)
        sequence = []
        for chain in chains:
            for residue in parsed_structure[0][chain]:
                if residue.has_id("CA"):
                    sequence.append(seq1(residue.get_resname()))
        return "".join(sequence)


def get_protein_analysis_df(sequences_by_ids: Dict[str, str]) -> pd.DataFrame:
    """
    Get a DataFrame of sequence composition (relative abundance of each aa and aa group) and the output file of ProteinAnalysis.
    """
    df = pd.DataFrame({"sequence": sequences_by_ids})
    df.index.name = "id"

    AMINO_ACIDS_perc = [f"{aa}_perc" for aa in AMINO_ACIDS]
    df["length"] = df["sequence"].apply(len)
    df[AMINO_ACIDS_perc] = (
        df.apply(lambda x: pd.Series([x["sequence"].count(aa) / x["length"] * 100 for aa in AMINO_ACIDS]), axis=1)
        if not df.empty
        else None
    )
    cols = [
        "nonpolar_perc",
        "polar_uncharged_perc",
        "positive_perc",
        "negative_perc",
        "turn_forming_perc",
        "aromatic_perc",
        "denq_perc",
    ]
    df[cols] = (
        df.apply(
            lambda x: pd.Series(
                [np.sum([x["sequence"].count(a) for a in group]) / x["length"] * 100 for group in GROUPS]
            ),
            axis=1,
        )
        if not df.empty
        else None
    )

    protein_analysis = df["sequence"].apply(lambda x: ProteinAnalysis(x))
    df["aromaticity"] = protein_analysis.apply(lambda x: safe_aromaticity(x))
    df["charge_5_5"] = protein_analysis.apply(lambda x: safe_charge(x, 5.5))
    df["charge_7_4"] = protein_analysis.apply(lambda x: safe_charge(x, 7.4))
    df["isoelectric_point"] = protein_analysis.apply(lambda x: safe_ip(x))
    df[["MEC_reduced", "MEC_cystines"]] = (
        protein_analysis.apply(lambda x: pd.Series(safe_mec(x))) if not df.empty else None
    )
    df[["helix_perc", "turn_perc", "sheet_perc"]] = (
        protein_analysis.apply(lambda x: pd.Series(safe_sec_str(x))) if not df.empty else None
    )

    sequence_wo_X = df["sequence"].apply(lambda x: "".join([aa for aa in list(x) if aa != "X"]))
    protein_analysis_wo_X = sequence_wo_X.apply(lambda x: ProteinAnalysis(x))
    df["flexibility_avg"] = protein_analysis_wo_X.apply(lambda x: safe_flexibility_avg(x))
    df["gravy"] = protein_analysis_wo_X.apply(lambda x: safe_gravy(x))
    df["instability_index"] = protein_analysis_wo_X.apply(lambda x: safe_instability_index(x))
    df["molecular_weight"] = protein_analysis_wo_X.apply(lambda x: safe_molecular_weight(x))
    df["avg_entropy"] = df["sequence"].apply(lambda x: average_entropy(x))

    return df


def get_charge_perc(x) -> Tuple[float, float]:
    """
    Calculate the percentage of positive and negative charges in a list of charges.
    """
    x_wo_none = [value for value in x if value is not None]
    positive_perc = len([value for value in x_wo_none if value > 0]) / len(x_wo_none)
    negative_perc = len([value for value in x_wo_none if value < 0]) / len(x_wo_none)
    return (positive_perc, negative_perc)


def charged_avg(x) -> Tuple[float, float]:
    """
    Calculate the average positive and negative charges in a list of charges.
    """
    x_wo_none = [value for value in x if value is not None]
    positive_avg = np.mean([value for value in x_wo_none if value > 0])
    negative_avg = np.mean([value for value in x_wo_none if value < 0])
    return (positive_avg, negative_avg)


def safe_aromaticity(analysis: ProteinAnalysis) -> float:
    """
    Calculate the aromaticity - relative frequency of Phe+Trp+Tyr.
    """
    try:
        return analysis.aromaticity()
    except Exception:
        return np.nan


def safe_charge(analysis: ProteinAnalysis, pH=5.5) -> float:
    """
    Calculate the charge of a protein at given pH.
    """
    try:
        return analysis.charge_at_pH(pH)
    except Exception:
        return np.nan


def safe_ip(analysis: ProteinAnalysis) -> float:
    """
    Calculate the isoelectric point.
    """
    try:
        return analysis.isoelectric_point()
    except Exception:
        return np.nan


def safe_mec(analysis: ProteinAnalysis) -> Tuple[int, int]:
    """
    Molar extinction coefficient assuming cysteines (reduced) and cystines residues (Cys-Cys-bond).
    """
    try:
        return analysis.molar_extinction_coefficient()
    except Exception:
        return (np.nan, np.nan)


def safe_sec_str(analysis: ProteinAnalysis) -> Tuple[float, float, float]:
    """
    Calculate percentage of helix, turn and sheet.
    """
    try:
        return [frac * 100 for frac in analysis.secondary_structure_fraction()]
    except Exception:
        return (np.nan, np.nan, np.nan)


def safe_flexibility_avg(analysis: ProteinAnalysis) -> float:
    """
    Calculates the average flexibility of the protein.
    """
    try:
        return np.mean(analysis.flexibility())
    except Exception:
        return np.nan


def safe_gravy(analysis: ProteinAnalysis) -> float:
    """
    Calculate the GRAVY (Grand Average of Hydropathy) value.
    """
    try:
        return analysis.gravy()
    except Exception:
        return np.nan


def safe_instability_index(analysis: ProteinAnalysis) -> float:
    """
    Calculate the instability index.
    """
    try:
        return analysis.instability_index()
    except Exception:
        return np.nan


def safe_molecular_weight(analysis: ProteinAnalysis) -> float:
    """
    Calculate the molecular weight from protein sequence.
    """
    try:
        return analysis.molecular_weight()
    except Exception:
        return np.nan


def aa_entropy(sequence: str) -> float:
    """
    Calculate the amino acid entropy of a sequence.
    Non-standard amino acids (B, J, O, U, X, Z) are ignored.
    """
    counts = pd.Series(list(sequence)).value_counts().to_dict()
    return entropy([counts.get(aa, 0) for aa in AMINO_ACIDS], base=2)


def windowed_aa_entropy(sequence: str, window_size: int) -> float:
    """
    Calculate the average amino acid entropy in sliding windows of the sequence.
    """
    entropy = (
        pd.Series([sequence[i : i + window_size] for i in range(len(sequence) - (window_size - 1))])
        .apply(aa_entropy)
        .mean()
    )
    return entropy


def average_entropy(sequence, window_size=21):
    """
    Calculate the amino acid entropy of a sequence, non-standard amino acids (B, J, O, U, X, Z) are ignored.
    1. If the sequence is shorter than the window size, return the entropy of the whole sequence.
    2. Otherwise, return the average entropy of sliding windows of the given size (= 21 by default to match ProteinSol implementation).
    """
    if len(sequence) < window_size:
        return aa_entropy(sequence)
    return windowed_aa_entropy(sequence, window_size)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_csv", type=str)
    parser.add_argument(
        "-c", "--chains", type=str, required=True, help="Chain(s) to extract the sequence from, comma-separated"
    )
    options = parser.parse_args()

    chains = list(options.chains.replace(" ", "").replace(",", ""))
    print("Chains:", chains)

    if os.path.isdir(options.input_path):
        paths = sorted(glob.glob(os.path.join(options.input_path, "*.pdb")))
        print(f"Reading sequences from {len(paths):,} PDBs")
        sequences_by_id = {
            os.path.splitext(os.path.basename(path))[0]: get_sequence_from_pdb_file(path, chains=chains)
            for path in paths
        }
    elif options.input_path.endswith((".pdb",)):
        sequences_by_id = {
            os.path.splitext(os.path.basename(options.input_path))[0]: get_sequence_from_pdb_file(
                options.input_path, chains=chains
            )
        }
    elif options.input_path.endswith((".fasta", ".fa")):
        sequences_by_id = {record.id: str(record.seq) for record in SeqIO.parse(options.input_path, "fasta")}
    elif options.input_path.endswith(".csv"):
        csv_df = pd.read_csv(options.input_path, index_col=0)
        # Verify all chain columns exist
        for chain in chains:
            if chain not in csv_df.columns:
                raise ValueError(f"Column '{chain}' not found in CSV file. Available columns: {list(csv_df.columns)}")
        # Extract and concatenate sequences from specified chain columns
        id_col = csv_df.columns[0]  # First column is assumed to be the ID
        sequences_by_id = {}
        for seq_id, row in csv_df.iterrows():
            concatenated_seq = "".join([str(row[chain]) if pd.notna(row[chain]) else "" for chain in chains])
            sequences_by_id[seq_id] = concatenated_seq
        print(f"Reading sequences from CSV with chains: {chains}")
    else:
        raise ValueError("Input must be a directory with PDB files, a PDB file, a FASTA file, or a CSV file")
    print(f"Calculating sequence composition on {len(sequences_by_id):,} sequences")
    df = get_protein_analysis_df(sequences_by_id)
    print(df)
    df.to_csv(options.output_csv)
    print("Saved to:", options.output_csv)
