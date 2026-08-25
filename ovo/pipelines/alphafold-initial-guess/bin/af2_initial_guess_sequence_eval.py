import csv
import os
import time
import argparse

from Bio.Data.PDBData import protein_letters_3to1
from colabdesign import mk_af_model
import json

import numpy as np
from Bio import PDB, Align
from io import StringIO


def add_cyclic_offset(self, offset_type=2):
    """add cyclic offset to connect N and C term (head-to-tail cyclic peptide)

    Ported from af2_initial_guess_binder_eval.py. For the hallucination protocol
    (bare-sequence prediction) the cyclic offset is applied per chain over the
    full length of each chain.
    """

    def cyclic_offset(L):
        i = np.arange(L)
        ij = np.stack([i, i + L], -1)
        offset = i[:, None] - i[None, :]
        c_offset = np.abs(ij[:, None, :, None] - ij[None, :, None, :]).min((2, 3))
        if offset_type == 1:
            c_offset = c_offset
        elif offset_type >= 2:
            a = c_offset < np.abs(offset)
            c_offset[a] = -c_offset[a]
        if offset_type == 3:
            idx = np.abs(c_offset) > 2
            c_offset[idx] = (32 * c_offset[idx]) / abs(c_offset[idx])
        return c_offset * np.sign(offset)

    idx = self._inputs["residue_index"]
    offset = np.array(idx[:, None] - idx[None, :])
    if self.protocol == "binder":
        c_offset = cyclic_offset(self._binder_len)
        offset[self._target_len :, self._target_len :] = c_offset
    if self.protocol in ["fixbb", "partial", "hallucination"]:
        Ln = 0
        for L in self._lengths:
            offset[Ln : Ln + L, Ln : Ln + L] = cyclic_offset(L)
            Ln += L
    self._inputs["offset"] = offset


def _align_sequences_and_get_indices(seqs: list[str], verbose: bool = False):
    """Aligns multiple protein sequences based on their amino acid sequences.
    Returns a tuple, a list of aligned sequences and list of indices for each sequence that correspond to the aligned residues."""
    aligner = Align.PairwiseAligner()
    aligner.open_gap_score = -7.0
    aligner.extend_gap_score = -2.0

    alignments = []
    aligned_seqs_indices = []

    # Process first sequence as the reference
    aligned_indexes_ref = []

    # Align each sequence to the reference (seqs[0])
    for i, seq in enumerate(seqs):
        if i == 0:
            # Skip aligning the reference to itself
            continue

        # Align current sequence to reference
        alignment = sorted(aligner.align(seqs[0], seq), key=lambda x: x.score, reverse=True)[0]
        if verbose:
            print("Alignment:")
            print(alignment)
        alignments.append(alignment)

        # Extract aligned indices for current sequence
        aligned_indices = [idx for start, end in alignment.aligned[1] for idx in range(start, end)]
        aligned_seqs_indices.append(aligned_indices)

        # Extract aligned indices for reference sequence (only need to do once)
        if not aligned_indexes_ref:
            aligned_indexes_ref = [idx for start, end in alignment.aligned[0] for idx in range(start, end)]

    # Insert reference sequence alignment at the beginning
    aligned_seqs_indices.insert(0, aligned_indexes_ref)

    return aligned_seqs_indices


def align_multiple_proteins_pdb(
    pdb_strs: list[str],
    chain_residue_mappings: list[list[tuple[str, list[int] | None]] | None],
    force_sequence_alignment: bool = False,
    all_atom: bool = False,
    verbose: bool = False,
) -> float:
    """Aligns multiple protein structures based on their atoms (CA or all).

    :param pdb_strs: list of PDB strings
    :param chain_residue_mappings: list of lists of tuples with chain ID and residues to align,
                                   if None provided, then whole chain/structure is aligned
    :param force_sequence_alignment: if True, always align based on sequence even if lengths match
    :param all_atom: if True, align using all atoms from matched residues (not just CA atoms)
    :param verbose: if True, print information about the alignment process
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
                continue
            else:
                raise ValueError(f"No atoms found in structure {i + 1}")

        for chain_id, residues in mappings:
            coords, res_final = get_atom_coordinates(structure, chain_id, residues, all_atom=all_atom)
            if coords:
                structure_coords.extend(coords)
                structure_residues.extend(res_final)
            else:
                raise ValueError(f"No atoms found in structure {i + 1} for chain {chain_id} and residues {residues}")

        coords_list.append(structure_coords)
        residues_list.append(structure_residues)

    seqs = [
        "".join([protein_letters_3to1.get(residue.resname, "X") for residue in residues]) for residues in residues_list
    ]

    sequence_alignment = force_sequence_alignment or any(len(seqs[i]) != len(seqs[0]) for i in range(1, len(seqs)))
    if sequence_alignment:
        aligned_seqs_indices = _align_sequences_and_get_indices(seqs, verbose=verbose)
    else:
        aligned_seqs_indices = [list(range(len(seqs[0])))] * len(seqs)

    if aligned_seqs_indices and verbose:
        print(f"Found {len(aligned_seqs_indices[1])} overlapping residues between the first and second chains.")

    super_imposer = PDB.Superimposer()

    for i in range(1, len(structures)):
        ref_atoms = []
        mod_atoms = []
        for atom_id, (ref_idx, mod_idx) in enumerate(zip(aligned_seqs_indices[0], aligned_seqs_indices[i])):
            ref_coords = coords_list[0][ref_idx]
            mod_coords = coords_list[i][mod_idx]
            shared_atom_names = sorted(set(ref_coords.keys()) & set(mod_coords.keys()))
            for atom_name in shared_atom_names:
                atom = atom_name[0]
                ref_atoms.append(PDB.Atom.Atom("X", ref_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
                mod_atoms.append(PDB.Atom.Atom("X", mod_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
        super_imposer.set_atoms(ref_atoms, mod_atoms)
        super_imposer.apply(structures[i].get_atoms())

    return super_imposer.rms


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


def read_csv_inputs(csv_path: str, chains: list[str]) -> list[dict]:
    """Read CSV where first column is id and remaining columns are chain sequences."""
    entries = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {"id": row[reader.fieldnames[0]]}
            for chain in chains:
                if chain not in row:
                    raise ValueError(f"Column '{chain}' not found in CSV. Available: {list(row.keys())}")
                entry[chain] = row[chain].strip()
            entries.append(entry)
    return entries


def prep_seq(model, sequence: str):
    """
    Prep a hallucination-protocol model from a bare sequence string (no coordinates).
    Uses _prep_hallucination so no batch coordinates are needed and no NaN risk from
    coordinate losses.  Equivalent to blind AF2 prediction.
    """
    model._prep_hallucination(length=len(sequence))
    # Override the sequence that will be set by set_seq(mode="wildtype")
    import numpy as np

    _RESTYPES = ["A", "R", "N", "D", "C", "Q", "E", "G", "H", "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]
    _AA_TO_IDX = {aa: i for i, aa in enumerate(_RESTYPES)}
    model._wt_aatype = np.array([_AA_TO_IDX.get(aa, 20) for aa in sequence])


METRICS = {
    # "rmsd": "rmsd",  # RMSD is meaningless because we don't initialize the coordinates
    "plddt": "plddt",  # 0-100
    "pae": "pae",  # predicted aligned error
    "ptm": "ptm",  # predicted TM score (0 = worst, 1 = best)
    "con": "intra_con_loss",  # intramolecular contacts loss of each residue to 2 nearest neighbors (by default) within the chain, excluding immediate sequence neighbours
    # in case of multi-chain sequence designs
    "i_pae": "ipae",
    "i_ptm": "iptm",  # predicted interface TM score (0 = worst, 1 = best)
    "i_con": "icon_loss",  # intermolecular contacts loss of each residue to 1 nearest neighbor (by default) in another chain
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=str)
    parser.add_argument("output_name", type=str)
    parser.add_argument("--native-pdb", required=False, type=str, help="Path to native PDB structure")
    parser.add_argument("--params", required=True, type=str, help="Path to AlphaFold2 parameter data dir")
    parser.add_argument(
        "--num-recycles", type=int, default=3, help="Number of AlphaFold2 recycles (0, 1, 2, 3, ..., default 1)"
    )
    parser.add_argument(
        "--multimer", action="store_true", default=False, help="Use AlphaFold multimer model (default = monomer)"
    )
    parser.add_argument(
        "--designed_chains",
        default="A",
        help="Designed chain ID or comma-separated list of designed chain IDs. Here, we design the binder. Default: 'A'.",
    )
    parser.add_argument(
        "--cyclic",
        action="store_true",
        default=False,
        help="Add cyclic offset to connect N and C term (head-to-tail cyclic peptide)",
    )
    options = parser.parse_args()

    designed_chains = [c.strip() for c in options.designed_chains.split(",")]
    assert options.input_csv.endswith(".csv"), f"Expected input_csv to be a CSV file, got: {options.input_csv}"

    model = mk_af_model(
        protocol="hallucination",
        data_dir=options.params,
        use_multimer=options.multimer,
    )
    items = read_csv_inputs(options.input_csv, designed_chains)
    print(f"CSV mode: {len(items):,} sequences from {options.input_csv}")

    if options.native_pdb:
        print(os.getcwd())
        with open(options.native_pdb, "r") as pdb_f:
            native_pdb_str = pdb_f.read()
    else:
        native_pdb_str = None

    os.makedirs(options.output_name, exist_ok=True)
    with open(options.output_name.rstrip("/") + ".jsonl", "wt") as f:
        for i, item in enumerate(items, start=1):
            basename = item["id"]
            assert len(designed_chains) == 1, "CSV mode currently supports a single chain"
            sequence = item[designed_chains[0]]

            print(f"Predicting sequence {i:,}/{len(items):,}: {basename} (len={len(sequence)})")
            start_time = time.time()
            prep_seq(model, sequence)
            if options.cyclic:
                add_cyclic_offset(model, offset_type=2)
            model.set_seq(mode="wildtype")
            model.set_opt(num_recycles=options.num_recycles)
            model.predict(num_models=1, verbose=False)

            metrics: dict[str, float | str] = {"id": basename}
            metrics.update({new_key: model.aux["log"].get(old_key) for old_key, new_key in METRICS.items()})
            metrics["plddt"] *= 100
            metrics["pae"] = (
                metrics["pae"] * 31.0
            )  # de-normalization of https://github.com/sokrypton/ColabDesign/blob/4c0bc6d67f8f967135ecccc135a26b3bfded25e8/colabdesign/af/loss.py#L252
            if isinstance(metrics["ipae"], float):
                metrics["ipae"] = metrics["ipae"] * 31.0
            predicted_pdb_str = model.save_pdb()
            suffix = os.path.basename(options.output_name.rstrip("/"))
            with open(os.path.join(options.output_name, f"{basename}_{suffix}.pdb"), "wt") as pdb_f:
                pdb_f.write(predicted_pdb_str)
            if native_pdb_str:
                print("Predicting reference-seq-aligned RMSD")
                metrics["ref_structure_all_atom_rmsd"] = align_multiple_proteins_pdb(
                    pdb_strs=[native_pdb_str, predicted_pdb_str],
                    chain_residue_mappings=[None, None],
                    all_atom=True,
                    verbose=True,
                )
                metrics["ref_structure_backbone_rmsd"] = align_multiple_proteins_pdb(
                    pdb_strs=[native_pdb_str, predicted_pdb_str],
                    chain_residue_mappings=[None, None],
                    all_atom=False,
                )
            metrics["time"] = time.time() - start_time
            metrics_str = " | ".join(f"{k} = {v:.2f}" for k, v in metrics.items() if isinstance(v, float))
            print(" Prediction done in {:.1f}s | {}".format(metrics["time"], metrics_str))
            json.dump(metrics, f)
            f.write("\n")
            f.flush()
