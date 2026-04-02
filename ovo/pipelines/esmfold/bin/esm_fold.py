import os
import sys
import argparse
import logging
import torch
import time
import re
import json
import numpy as np

from glob import glob
from Bio import SeqIO, PDB
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from io import StringIO
from dataclasses import dataclass

from transformers import EsmForProteinFolding
from transformers.models.esm.openfold_utils import residue_constants
from transformers.models.esm.modeling_esmfold import collate_dense_tensors


@dataclass
class InputSequence:
    id: str
    sequence: str
    original_pdb_path: str | None = None


def get_sequence_from_pdb_file(file_path: str, chain: str = "A") -> InputSequence:
    """
    Get the sequence of a structure from a pdb file.
    """
    pdb_parser = PDBParser(QUIET=True)
    seq_id = re.sub(r"\.pdb$", "", os.path.basename(file_path))
    with open(file_path) as f:
        parsed_structure = pdb_parser.get_structure("", f)
        sequence = []
        for residue in parsed_structure[0][chain]:
            if residue.has_id("CA"):
                sequence.append(seq1(residue.get_resname()))
    return InputSequence(id=seq_id, sequence="".join(sequence), original_pdb_path=file_path)


def get_sequence_from_fasta_file(file_path: str) -> InputSequence:
    """
    Get the first sequence from a FASTA file.
    """
    seq_id = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path) as f:
        for record in SeqIO.parse(f, "fasta"):
            return InputSequence(id=seq_id, sequence=str(record.seq))
    raise ValueError(f"No valid sequences found in {file_path}")


def get_sequences_from_fasta_file(file_path: str) -> list[InputSequence]:
    """
    Get all sequences from a FASTA file.
    """
    input_sequences = []
    with open(file_path) as f:
        for record in SeqIO.parse(f, "fasta"):
            input_sequences.append(InputSequence(id=record.id, sequence=str(record.seq)))
    if len(input_sequences) == 0:
        raise ValueError(f"No valid sequences found in {file_path}")
    return input_sequences


def setup_logger(output_dir: str) -> logging.Logger:
    """Set up logging to both file and console."""
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "logs.txt")
    open(log_file, "w").close()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger


@torch.no_grad()
def infer(
    model: EsmForProteinFolding,
    seqs: str | list[str],
    num_recycles: int,
    position_ids: torch.Tensor | None = None,
) -> dict:
    # Returns the raw outputs of the model given an input sequence.
    if isinstance(seqs, str):
        seqs = [seqs]
    device = next(model.parameters()).device
    aatype = collate_dense_tensors(
        [
            torch.from_numpy(
                residue_constants.sequence_to_onehot(
                    sequence=seq,
                    mapping=residue_constants.restype_order_with_x,
                    map_unknown_to_x=True,
                )
            )
            .to(device)
            .argmax(dim=1)
            for seq in seqs
        ]
    )  # B=1 x L
    mask = collate_dense_tensors([aatype.new_ones(len(seq)) for seq in seqs])
    position_ids = (
        torch.arange(aatype.shape[1], device=device).expand(len(seqs), -1)
        if position_ids is None
        else position_ids.to(device)
    )
    if position_ids.ndim == 1:
        position_ids = position_ids.unsqueeze(0)
    return model(
        aatype,
        mask,
        position_ids=position_ids,
        num_recycles=num_recycles,
    )


def get_atom_coordinates(
    structure: PDB.Structure.Structure,
    chain_id: str | None,
    residues: list[int] | None,
    all_atom: bool = False,
    model_index: int = 0,
) -> tuple[list[dict[str, np.ndarray]], list[PDB.Residue.Residue]]:
    coords = []
    res_final = []

    model = structure[model_index]

    for chain in model:
        if chain_id and chain.id != chain_id:
            continue
        for residue in chain:
            if residues and residue.id[1] not in residues:
                continue
            coords_dict = {}
            for atom in residue:
                if all_atom or atom.id == "CA":
                    coords_dict[atom.id] = atom.coord
            if coords_dict:
                coords.append(coords_dict)
                res_final.append(residue)
    return coords, res_final


def align_multiple_proteins_pdb(
    pdb_strs: list[str], chain_residue_mappings: list[list[tuple[str, list[int] | None]] | None], all_atom: bool = False
) -> float:
    """Aligns multiple protein structures based on their atoms (CA or all).

    :param pdb_strs: list of PDB strings
    :param chain_residue_mappings: list of lists of tuples with chain ID and residues to align,
                                   if None provided, then whole chain/structure is aligned
    :param all_atom: if True, align using all atoms from matched residues (not just CA atoms)
    """
    assert len(pdb_strs) == len(chain_residue_mappings), (
        f"Expected same number of structures and chain residue mappings, got {len(pdb_strs)} != {len(chain_residue_mappings)}"
    )

    parser = PDB.PDBParser(QUIET=True)
    structures = [parser.get_structure(f"Protein{i + 1}", StringIO(pdb_str)) for i, pdb_str in enumerate(pdb_strs)]
    coords_list = []
    residues_list = []

    for i, (structure, mappings) in enumerate(zip(structures, chain_residue_mappings)):
        structure_coords = []
        structure_residues = []

        if not mappings:
            coords, res_final = get_atom_coordinates(structure, None, None, all_atom=all_atom)
            if coords:
                coords_list.append(coords)
                residues_list.append(res_final)
            else:
                raise ValueError(f"No atoms found in structure {i + 1}")
        else:
            for chain_id, residues in mappings:
                coords, res_final = get_atom_coordinates(structure, chain_id, residues, all_atom=all_atom)
                if coords:
                    structure_coords.extend(coords)
                    structure_residues.extend(res_final)
                else:
                    raise ValueError(
                        f"No atoms found in structure {i + 1} for chain {chain_id} and residues {residues}"
                    )

            coords_list.append(structure_coords)
            residues_list.append(structure_residues)

    for residues in residues_list:
        assert len(residues) == len(residues_list[0]), (
            f"Got different number of residues in structures: {len(residues)} != {len(residues_list[0])}"
        )

    super_imposer = PDB.Superimposer()

    for i in range(1, len(structures)):
        ref_atoms = []
        mod_atoms = []
        for atom_id, (ref_coords, mod_coords) in enumerate(zip(coords_list[0], coords_list[i])):
            shared_atom_names = sorted(set(ref_coords.keys()) & set(mod_coords.keys()))
            for atom_name in shared_atom_names:
                atom = atom_name[0]
                ref_atoms.append(PDB.Atom.Atom("X", ref_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
                mod_atoms.append(PDB.Atom.Atom("X", mod_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
        super_imposer.set_atoms(ref_atoms, mod_atoms)

    return super_imposer.rms


def main(args):
    logger = setup_logger(args.output_dir)

    assert 0 <= args.num_recycles <= 4, "Number of recycles must be between 0 and 4"
    assert len(args.chain) == 1, "Chain identifier must be a single character"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Load model
    model = EsmForProteinFolding.from_pretrained(args.esmfold_model_path)
    model = model.eval()
    model = model.to(device)
    if args.fp16 and device == torch.device("cuda"):  # 16bit only for GPU
        logger.info("Using mixed precision (BFloat16) for inference")
        model = model.to(torch.bfloat16)
    logger.info("Model loaded successfully.")

    # Load input sequences
    input_sequences: list[InputSequence]
    if os.path.isdir(args.input_path):
        paths_pdb = sorted(glob(os.path.join(args.input_path, "*.pdb")))
        paths_fasta = sorted(
            glob(os.path.join(args.input_path, "*.fasta")) + glob(os.path.join(args.input_path, "*.fa"))
        )
        assert (not paths_pdb) or (not paths_fasta), "Input directory cannot contain both PDB and FASTA files"
        if paths_pdb:
            input_sequences = [get_sequence_from_pdb_file(path, args.chain) for path in paths_pdb]
        else:
            input_sequences = [get_sequence_from_fasta_file(path) for path in paths_fasta]
    elif args.input_path.endswith((".pdb",)):
        input_sequences = [get_sequence_from_pdb_file(args.input_path, args.chain)]
    elif args.input_path.endswith((".fasta", ".fa")):
        input_sequences = get_sequences_from_fasta_file(args.input_path)
    else:
        raise ValueError(
            "Input must be a directory with PDB files, a directory with FASTA files, a PDB file, or a FASTA file"
        )

    logger.info(f"Processing {len(input_sequences)} sequences")

    os.makedirs(os.path.join(args.output_dir, args.name), exist_ok=True)

    # Run inference and save output PDBs
    predictions_metrics = []
    for input_sequence in input_sequences:
        logger.info(f"Processing {input_sequence.id}")
        inference_start_time = time.time()
        prediction = infer(model, input_sequence.sequence, num_recycles=args.num_recycles)
        logger.info(f"Inference time: {time.time() - inference_start_time:.2f} seconds")

        output_dict = {
            k: v.to(torch.float32) if v.dtype in (torch.bfloat16, torch.float16) else v for k, v in prediction.items()
        }
        prediction_pdb = model.output_to_pdb(output_dict)[0]

        with open(os.path.join(args.output_dir, args.name, f"{input_sequence.id}_{args.name}.pdb"), "w") as f:
            f.write(prediction_pdb)

        RMSD_all_atom, RMSD_backbone = None, None
        if input_sequence.original_pdb_path is not None:
            with open(input_sequence.original_pdb_path, "r") as f:
                original_pdb = f.read()
            RMSD_all_atom = align_multiple_proteins_pdb(
                pdb_strs=[original_pdb, prediction_pdb],
                chain_residue_mappings=[[("A", None)], None],
                all_atom=True,
            )
            RMSD_backbone = align_multiple_proteins_pdb(
                pdb_strs=[original_pdb, prediction_pdb],
                chain_residue_mappings=[[("A", None)], None],
                all_atom=False,
            )

        predictions_metrics.append(
            dict(
                id=input_sequence.id,
                pLDDT=(100.0 * prediction.plddt[0, :, 1].mean().item()),  # (Batch x Length x 37); CA is on index 1
                pTM=prediction.ptm.item(),
                RMSD_all_atom=RMSD_all_atom,
                RMSD_backbone=RMSD_backbone,
                pAE=prediction.predicted_aligned_error.mean().item(),
            )
        )

    # Save metrics to JSONL file
    with open(os.path.join(args.output_dir, f"{args.name}.jsonl"), "w") as f:
        for metric in predictions_metrics:
            json.dump(metric, f)
            f.write("\n")
            f.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_path",
        type=str,
        help="Path to the input directory containing FASTA files or PDB files or a single FASTA or PDB file",
    )
    parser.add_argument("--output_dir", type=str, help="Path to the output directory for PDB files")
    parser.add_argument("--name", default="esmfold", type=str, help="Filename prefix to use for PDB dir and stats file")
    parser.add_argument("--chain", type=str, default="A", help='Chain identifier for input PDB files. Default: "A"')
    parser.add_argument("--esmfold_model_path", type=str, help="Path to the ESMFold model directory")
    parser.add_argument(
        "--num_recycles",
        type=int,
        default=4,
        help="Number of recycles during inference. Default is the maximum used during training (4)",
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Use mixed precision (FP16) for inference",
    )
    args = parser.parse_args()
    main(args)
