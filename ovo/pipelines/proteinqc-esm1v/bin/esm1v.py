import os
import argparse
import glob

from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from Bio import SeqIO

from esm import pretrained
import torch
import pandas as pd

pdb_parser: PDBParser = PDBParser(QUIET=True)
AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")


def get_sequences_from_pdb_file(file_path: str, chains: str) -> list[tuple[str, str]]:
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


def load_model(models_path, model_idx):
    model = f"esm1v_t33_650M_UR90S_{model_idx}.pt"
    model_path = os.path.join(models_path, model)
    model, alphabet = pretrained.load_model_and_alphabet(model_path)
    return (model, alphabet)


def run_wildtype_marginals_predictions(data, model, alphabet):
    model.eval()
    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")
    device = next(model.parameters()).device
    batch_converter = alphabet.get_batch_converter()
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    batch_tokens = batch_tokens.to(device)

    with torch.no_grad():
        token_probs = torch.softmax(model(batch_tokens)["logits"], dim=-1)
    return token_probs


def get_results_df(data, token_probs, alphabet):
    results = []
    for (label, sequence), token_prob in zip(data, token_probs):
        struct, chain = label.rsplit("_", 1)
        probs_df = pd.DataFrame(token_prob.cpu()[1 : len(sequence) + 1], columns=alphabet.all_toks)
        # Compute the sum of softmax probabilities for the native sequence
        native_seq_softmax_sum = sum(row[aa] for (_, row), aa in zip(probs_df.iterrows(), sequence))
        results.append((struct, chain, sequence, native_seq_softmax_sum))
    # Group results by structure ID to compute results for each structure (supports multichain logic)
    results_df = (
        pd.DataFrame(results, columns=["id", "chain", "sequence", "native_seq_softmax_sum"])
        .groupby("id")
        .agg({"chain": list, "sequence": list, "native_seq_softmax_sum": "sum"})
        .reset_index()
    )
    results_df["chain"] = results_df["chain"].str.join(",")
    results_df["sequence"] = results_df["sequence"].str.join("")
    # Compute average softmax probability per structure given total sequence length (concatenated sequences of processed chain)
    results_df["native_seq_avg_softmax"] = results_df.apply(
        lambda row: row["native_seq_softmax_sum"] / len(row["sequence"]), axis=1
    )
    results_df.drop(columns=["native_seq_softmax_sum"], inplace=True)
    return results_df


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_csv", type=str)
    parser.add_argument("-c", "--chains", type=str, default="A", help="Chain to extract the sequence from")
    parser.add_argument("--esm_models_dir", type=str, help="Path to the ESM models directory")
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
    elif options.input_path.endswith(".csv"):
        csv_df = pd.read_csv(options.input_path, index_col=0)
        # Verify all chain columns exist
        for chain in chains:
            if chain not in csv_df.columns:
                raise ValueError(f"Column '{chain}' not found in CSV file. Available columns: {list(csv_df.columns)}")
        # Extract and concatenate sequences from specified chain columns
        sequences_by_id = {}
        for seq_id, row in csv_df.iterrows():
            for chain in chains:
                if pd.notna(row[chain]):  # Only add non-empty sequences
                    sequences_by_id[f"{seq_id}_{chain}"] = str(row[chain])
        print(f"Reading sequences from CSV with chains: {chains}")
    else:
        raise ValueError("Input must be a directory with PDB files, a PDB file, a FASTA file, or a CSV file")

    models_path = options.esm_models_dir

    data = [(sequence_id, sequence) for sequence_id, sequence in sequences_by_id.items()]

    # TODO: Add window-based prediction for long proteins
    token_probs_by_model = []

    n_models = 5
    for model_idx in range(1, n_models + 1):
        # Load the model
        model, alphabet = load_model(models_path, model_idx)

        # Calculate the probabilities
        token_probs = run_wildtype_marginals_predictions(data, model, alphabet)

        token_probs_by_model.append(token_probs)

    avg_token_probs = sum(token_probs_by_model) / n_models
    result = get_results_df(
        data, avg_token_probs, alphabet
    )  # We use alphabet only for column aa identification and it is the same across models
    result.to_csv(options.output_csv, index=False)
