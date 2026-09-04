# The ipSAE, pDockQ, pDockQ2 and LIS calculations in this file are taken from ipsae.py
# (https://github.com/DunbrackLab/IPSAE), whose license notice is reproduced below.
#
#     ipsae.py
#     script for calculating the ipSAE score for scoring pairwise protein-protein interactions in
#     AlphaFold2 and AlphaFold3 models
#     https://www.biorxiv.org/content/10.1101/2025.02.10.637595v2
#
#     Also calculates:
#        pDockQ: Bryant, Pozotti, and Eloffson. https://www.nature.com/articles/s41467-022-28865-w
#        pDockQ2: Zhu, Shenoy, Kundrotas, Elofsson. https://academic.oup.com/bioinformatics/article/39/7/btad424/7219714
#        LIS: Kim, Hu, Comjean, Rodiger, Mohr, Perrimon. https://www.biorxiv.org/content/10.1101/2024.02.19.580970v1
#
#     Roland Dunbrack
#     Fox Chase Cancer Center
#     version 4
#     January 3, 2026: Fixed Boltz2 issues (PDB and mmCIF format; chainIDs)
#     MIT license: script can be modified and redistributed for non-commercial and commercial use,
#     as long as this information is reproduced.
"""Publish the Boltz predictions as PDB files and calculate their metrics.

Two things happen here, both of which have to happen before anything else looks at a prediction:

1. The predicted mmCIF is turned into the PDB file that is published as the prediction. A target
   chain that is broken up into segments is predicted as one chain per segment (see
   prepare_inputs.py), and the segments are merged back into the target chain(s) of the design,
   with the residue numbering of the design (the same convention as the AlphaFold2 initial guess
   tests use). The PDB format has no room for the segment chain IDs (B1, B2, ...), so the merging
   has to happen before the prediction is written out at all.

2. All interface metrics are calculated here rather than taken from Boltz. Boltz averages its own
   interface metrics over all pairs of different chains, so a split target dilutes every one of
   them with segment-to-segment pairs that say nothing about the binder. The metrics written here
   are always binder against the whole target, which for a target of one chain is what Boltz
   reports anyway, and additionally ipSAE, pDockQ, pDockQ2 and LIS.
"""

import argparse
import glob
import json
import math
import os

import numpy as np
from Bio import PDB

# PAE cutoff for the ipSAE scores, in Angstrom, the value recommended by the ipSAE authors
PAE_CUTOFF = 10.0
# Cbeta-Cbeta distance up to which two residues are counted as a contact, in Angstrom. The same
# cutoff is used by pDockQ and by the interface metrics of Boltz (see boltz.model.modules.confidence)
CONTACT_CUTOFF = 8.0
# PAE up to which a residue pair contributes to the LIS score, in Angstrom
LIS_CUTOFF = 12.0


def ptm_func(x, d0):
    """Predicted TM score contribution of an aligned error x, given d0. Taken from ipsae.py."""
    return 1.0 / (1 + (x / d0) ** 2.0)


def calc_d0(length: float) -> float:
    """TM score normalization length, from Yang and Skolnick, Proteins 57:702-710 (2004).

    Taken from ipsae.py, keeping only the protein case (minimum value 1.0). The two functions clamp
    short lengths slightly differently (1.0 up to 27 here, up to 26 in :func:`calc_d0_array`), which
    is deliberate: it is what ipsae.py does, and matching it keeps our scores identical to theirs.
    """
    length = float(length)
    if length > 27:
        d0 = 1.24 * (length - 15) ** (1.0 / 3.0) - 1.8
    else:
        d0 = 1.0
    return max(1.0, d0)


def calc_d0_array(lengths: np.ndarray) -> np.ndarray:
    """:func:`calc_d0` for an array of lengths, taken from ipsae.py."""
    lengths = np.maximum(26, np.array(lengths, dtype=float))
    return np.maximum(1.0, 1.24 * (lengths - 15) ** (1.0 / 3.0) - 1.8)


def get_residues(model: PDB.Model.Model, chain_ids: list[str] | None = None) -> list[PDB.Residue.Residue]:
    """Return the residues of the given chains (all of them by default), in structure order."""
    if chain_ids is None:
        chain_ids = [chain.id for chain in model]
    return [residue for chain_id in chain_ids for residue in model[chain_id] if "CA" in residue]


def get_target_chain_ids(model: PDB.Model.Model, binder_chain: str) -> list[str]:
    """Return the non-binder chain IDs of a structure, in the order they appear in it."""
    return [chain.id for chain in model if chain.id != binder_chain]


def get_sequence(residues: list[PDB.Residue.Residue]) -> str:
    """Return the one letter sequence of the given residues."""
    return "".join(PDB.Polypeptide.protein_letters_3to1.get(residue.resname, "X") for residue in residues)


def restore_design_target_chains(predicted: PDB.Model.Model, design: PDB.Model.Model, binder_chain: str) -> None:
    """Put the predicted target back under the chain IDs and residue numbering of the design.

    A target chain that is broken up by jumps in its residue numbering or by its backbone is
    predicted as one chain per segment, renumbered from 1 (see prepare_inputs.py). This merges those
    chains back into the target chain(s) of the design, so that the published prediction can be
    compared to the design residue by residue. A target that was not split is left as it is.

    The residues are mapped in structure order, which is the order the segments were given to Boltz
    in. The predicted model is modified in place.
    """
    design_target_chains = get_target_chain_ids(design, binder_chain)
    design_residue_ids = [
        (chain_id, residue.id) for chain_id in design_target_chains for residue in get_residues(design, [chain_id])
    ]

    predicted_chain_ids = get_target_chain_ids(predicted, binder_chain)
    predicted_residues = get_residues(predicted, predicted_chain_ids)
    if len(predicted_residues) != len(design_residue_ids):
        raise ValueError(
            f"Predicted target chains {predicted_chain_ids} have {len(predicted_residues)} residues, "
            f"the design target has {len(design_residue_ids)}"
        )
    design_sequence = get_sequence(get_residues(design, design_target_chains))
    predicted_sequence = get_sequence(predicted_residues)
    if design_sequence != predicted_sequence:
        raise ValueError(
            f"Target does not match its prediction:\n"
            f"  design chains {design_target_chains}: {design_sequence}\n"
            f"  predicted chains {predicted_chain_ids}: {predicted_sequence}"
        )

    if [
        (chain_id, residue.id) for chain_id in predicted_chain_ids for residue in predicted[chain_id]
    ] == design_residue_ids:
        return

    for chain_id in predicted_chain_ids:
        predicted.detach_child(chain_id)
    restored_chains = {}
    for (chain_id, residue_id), residue in zip(design_residue_ids, predicted_residues):
        residue.id = residue_id
        if chain_id not in restored_chains:
            restored_chains[chain_id] = PDB.Chain.Chain(chain_id)
        restored_chains[chain_id].add(residue)
    for chain in restored_chains.values():
        predicted.add(chain)


def get_contact_distances(residues: list[PDB.Residue.Residue]) -> np.ndarray:
    """Pairwise Cbeta-Cbeta distance matrix (Calpha for glycine), as used by ipsae.py."""
    coords = np.array([residue["CB" if "CB" in residue else "CA"].coord for residue in residues])
    return np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2))


def calculate_ipsae(pae: np.ndarray, mask1: np.ndarray, mask2: np.ndarray) -> dict[str, float]:
    """ipSAE scores of the chain selected by mask1 aligned on the chain selected by mask2.

    Taken from ipsae.py, keeping the asymmetric per-chain-pair values of the three ipSAE variants.
    Each is the maximum over the residues of the first chain of its by-residue value, which is the
    mean predicted TM score of that residue against the residues of the second chain that it is
    confidently placed relative to (PAE below the cutoff).

    The variants differ in the length that normalizes the TM score (d0):
    d0chn from the number of residues of both chains, d0dom from the residues of both chains with a
    PAE below the cutoff, and d0res (the ipSAE score itself) from the residues of the second chain
    with a PAE below the cutoff for the given residue of the first chain.
    """
    valid_pairs = np.outer(mask1, mask2) & (pae < PAE_CUTOFF)
    valid_counts = valid_pairs.sum(axis=1)

    def max_by_residue(ptm: np.ndarray, pairs: np.ndarray) -> float:
        counts = pairs.sum(axis=1)
        means = np.where(counts > 0, (ptm * pairs).sum(axis=1) / np.maximum(counts, 1), 0.0)
        return float(means.max(initial=0.0))

    # Number of residues in both chains
    n0chn = int(mask1.sum() + mask2.sum())
    ptm_d0chn = ptm_func(pae, calc_d0(n0chn))
    # Number of residues in both chains that are confidently placed relative to the other chain
    n0dom = int(np.count_nonzero(valid_pairs.any(axis=1)) + np.count_nonzero(valid_pairs.any(axis=0)))
    ptm_d0dom = ptm_func(pae, calc_d0(n0dom))
    # Number of residues of the second chain that each residue of the first chain is confidently
    # placed relative to, which gives every residue of the first chain its own d0
    ptm_d0res = ptm_func(pae, calc_d0_array(valid_counts)[:, None])

    return {
        "ipsae_d0chn": max_by_residue(ptm_d0chn, valid_pairs),
        "ipsae_d0dom": max_by_residue(ptm_d0dom, valid_pairs),
        "ipsae": max_by_residue(ptm_d0res, valid_pairs),
    }


def calculate_pdockq(pae: np.ndarray, plddt: np.ndarray, contacts: np.ndarray) -> tuple[float, float]:
    """pDockQ and pDockQ2 of a chain pair, taken from ipsae.py.

    :param plddt: per-residue pLDDT on the 0-100 scale that both fits were made on
    :param contacts: boolean matrix of the residue pairs of the two chains that are in contact
    :return: (pDockQ, pDockQ2)
    """
    num_pairs = int(contacts.sum())
    if num_pairs == 0:
        return 0.0, 0.0

    # Mean pLDDT over the residues of both chains that are in contact with the other chain
    interface = contacts.any(axis=1) | contacts.any(axis=0)
    mean_plddt = float(plddt[interface].mean())

    x = mean_plddt * math.log10(num_pairs)
    pdockq = 0.724 / (1 + math.exp(-0.052 * (x - 152.611))) + 0.018

    mean_ptm = float(ptm_func(pae[contacts], 10.0).mean())
    x2 = mean_plddt * mean_ptm
    pdockq2 = 1.31 / (1 + math.exp(-0.075 * (x2 - 84.733))) + 0.005

    return pdockq, pdockq2


def calculate_lis(pae: np.ndarray, mask1: np.ndarray, mask2: np.ndarray) -> float:
    """Local Interaction Score of a chain pair, taken from ipsae.py."""
    selected_pae = pae[np.ix_(mask1, mask2)]
    valid_pae = selected_pae[selected_pae < LIS_CUTOFF]
    if not valid_pae.size:
        return 0.0
    return float(((LIS_CUTOFF - valid_pae) / LIS_CUTOFF).mean())


def calculate_binder_target_iptm(
    pair_chains_iptm: dict[str, dict[str, float]], chain_ids: list[str], chain_lengths: list[int], binder_chain: str
) -> float:
    """ipTM of the binder with the target, leaving out the target-target chain pairs.

    Boltz reports the ipTM of every chain pair, but only the ipTM of the whole complex as a single
    number, which averages over all pairs of different chains and is therefore diluted by the
    segment-to-segment pairs of a split target. This averages the ipTM of the binder with each
    target chain, weighted by the number of residues of that chain. For a target of one chain it is
    the ipTM that Boltz itself reports.

    :param chain_ids: chain IDs in the order they appear in the prediction, which is the order the
        chain pairs of Boltz are keyed by
    """
    binder_index = chain_ids.index(binder_chain)
    values = []
    weights = []
    for index, (chain_id, length) in enumerate(zip(chain_ids, chain_lengths)):
        if chain_id == binder_chain:
            continue
        values.append(pair_chains_iptm[str(binder_index)][str(index)])
        weights.append(length)
    return float(np.average(values, weights=weights))


def calculate_interface_metrics(
    model: PDB.Model.Model, boltz_metrics: dict, plddt: np.ndarray, pae: np.ndarray, pde: np.ndarray, binder_chain: str
) -> dict[str, float]:
    """Interface metrics of a predicted binder-target complex.

    Everything is calculated for the binder against the whole target, no matter how many chains the
    target is split into. The keys that Boltz also reports are overwritten, so that the interface
    metrics of a split target mean the same thing as those of a target of one chain.

    :param model: the predicted complex, before the target segments are merged back
    :param boltz_metrics: the confidence json of the prediction
    :param plddt: per-residue pLDDT of the prediction (0-1), in structure order
    :param pae: per-residue-pair predicted aligned error of the prediction, in structure order
    :param pde: per-residue-pair predicted distance error of the prediction, in structure order
    """
    chain_ids = [chain.id for chain in model]
    residues_by_chain = [get_residues(model, [chain_id]) for chain_id in chain_ids]
    residues = [residue for chain_residues in residues_by_chain for residue in chain_residues]
    num_residues = len(residues)
    for name, array in [("pLDDT", plddt), ("PAE", pae), ("PDE", pde)]:
        assert array.shape[0] == num_residues, (
            f"Expected {num_residues} tokens in the {name} of the prediction, got {array.shape}. "
            "Boltz gives every residue of a protein one token, other molecule types are not supported here."
        )

    is_binder = np.array([residue.parent.id == binder_chain for residue in residues])
    is_target = ~is_binder
    assert is_binder.any() and is_target.any(), f"Expected a binder chain {binder_chain} and a target, got {chain_ids}"

    # Residue pairs between the binder and the target, in both directions
    cross_chain = np.outer(is_binder, is_target) | np.outer(is_target, is_binder)
    contacts = cross_chain & (get_contact_distances(residues) <= CONTACT_CUTOFF)

    # The ipSAE scores of a chain pair are asymmetric, the maximum of both directions is reported
    forward = calculate_ipsae(pae, is_binder, is_target)
    reverse = calculate_ipsae(pae, is_target, is_binder)
    ipsae_metrics = {key: max(forward[key], reverse[key]) for key in forward}

    # pDockQ is the same in both directions, pDockQ2 is not
    pdockq, pdockq2 = calculate_pdockq(pae, plddt * 100, np.outer(is_binder, is_target) & contacts)
    _, reverse_pdockq2 = calculate_pdockq(pae, plddt * 100, np.outer(is_target, is_binder) & contacts)

    iptm = calculate_binder_target_iptm(
        boltz_metrics["pair_chains_iptm"],
        chain_ids,
        [len(chain_residues) for chain_residues in residues_by_chain],
        binder_chain,
    )
    # Boltz upweights the interface tokens by a factor of 10 (see boltz.model.modules.confidence)
    interface_weights = np.where(contacts.any(axis=1), 10.0, 1.0)

    return {
        # Overwrites the values of Boltz, which average over all pairs of different chains
        "iptm": iptm,
        # There are no ligands in a refolding prediction, so the protein ipTM is the ipTM
        "protein_iptm": iptm,
        "confidence_score": 0.8 * boltz_metrics["complex_plddt"] + 0.2 * iptm,
        "complex_iplddt": float(np.average(plddt, weights=interface_weights)),
        # Boltz weights the interface pairs by their contact probability from the distogram, which
        # it does not publish, so the pairs actually in contact in the prediction are used instead
        "complex_ipde": float(pde[contacts].mean()) if contacts.any() else float(pde[cross_chain].mean()),
        # Interface PAE, the same metric that the AlphaFold2 initial guess tests report
        "ipae": float(pae[cross_chain].mean()),
        "pdockq": pdockq,
        "pdockq2": max(pdockq2, reverse_pdockq2),
        # The Local Interaction Score of a chain pair is the mean of both directions
        "lis": (calculate_lis(pae, is_binder, is_target) + calculate_lis(pae, is_target, is_binder)) / 2,
        **ipsae_metrics,
    }


def read_boltz_output(
    boltz_pubdir: str, name: str
) -> tuple[PDB.Structure.Structure, dict, np.ndarray, np.ndarray, np.ndarray]:
    """Read the prediction of one design: structure, confidence json and the pLDDT/PAE/PDE arrays."""
    prediction_dir = os.path.join(boltz_pubdir, name)
    structure = PDB.MMCIFParser(QUIET=True).get_structure(name, os.path.join(prediction_dir, f"{name}_model_0.cif"))
    with open(os.path.join(prediction_dir, f"confidence_{name}_model_0.json")) as f:
        boltz_metrics = json.load(f)
    arrays = [
        np.load(os.path.join(prediction_dir, f"{key}_{name}_model_0.npz"))[key] for key in ["plddt", "pae", "pde"]
    ]
    return structure, boltz_metrics, *arrays


def calculate_metrics(
    input_dir: str,
    boltz_pubdir: str,
    output_pdb_dir: str,
    output_metrics_path: str,
    binder_chain: str,
    complex_prediction: bool,
) -> None:
    """Publish each prediction as a PDB file and write its metrics.

    :param binder_chain: chain ID of the binder, or of the designed chain of a scaffold design
    :param complex_prediction: whether the prediction contains the target as well as the binder,
        which is what the interface metrics need
    """
    os.makedirs(output_pdb_dir, exist_ok=True)
    test_name = os.path.basename(output_pdb_dir.rstrip("/"))

    results = []
    for design_path in sorted(glob.glob(os.path.join(input_dir, "*.pdb"))):
        name = os.path.basename(design_path).removesuffix(".pdb")
        structure, boltz_metrics, plddt, pae, pde = read_boltz_output(boltz_pubdir, name)
        model = structure[0]

        metrics = {"id": name, **boltz_metrics}
        # There are no ligands in a refolding prediction
        metrics.pop("ligand_iptm", None)

        if complex_prediction:
            print(f"{name}: chains {[chain.id for chain in model]} predicted, binder chain {binder_chain}")
            metrics.update(calculate_interface_metrics(model, boltz_metrics, plddt, pae, pde, binder_chain))
            design = PDB.PDBParser(QUIET=True).get_structure("design", design_path)[0]
            restore_design_target_chains(model, design, binder_chain)
        results.append(metrics)

        io = PDB.PDBIO()
        io.set_structure(structure)
        io.save(os.path.join(output_pdb_dir, f"{name}_{test_name}.pdb"))

    with open(output_metrics_path, "w") as f:
        for result in results:
            json.dump(result, f)
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to directory containing [Protein/Ligand]MPNN structure files.",
    )
    parser.add_argument(
        "--boltz_pubdir",
        type=str,
        required=True,
        help="Path to the directory containing Boltz prediction MMCIF files.",
    )
    parser.add_argument(
        "--design_type",
        type=str,
        choices=["scaffold", "binder"],
        required=True,
        help="Type of design, only a binder design has an interface to calculate metrics for.",
    )
    parser.add_argument(
        "--chains",
        "--designed_chains",
        type=str,
        default="A",
        help="Chain ID for the binder/designed chain, e.g. 'A'. For scaffold design, can be comma-separated list. Default: 'A'.",
    )
    parser.add_argument(
        "--boltz_version",
        type=str,
        default="boltz2",
        choices=["boltz1", "boltz2"],
        help="Not used, for compatibility with the arguments of compute_rmsd.py.",
    )
    parser.add_argument(
        "--cyclic",
        action="store_true",
        help="Not used, for compatibility with run_parameters from prepare_inputs.py.",
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        default=False,
        help="Not used, for compatibility with run_parameters from prepare_inputs.py.",
    )
    parser.add_argument(
        "--binder-alone",
        action="store_true",
        default=False,
        help="Only the binder structure was predicted, without the target. Default: False.",
    )
    parser.add_argument(
        "--output_metrics_path",
        type=str,
        required=True,
        help="Path to the output metrics file (JSONL format).",
    )
    parser.add_argument(
        "--output_pdb_dir",
        type=str,
        required=True,
        help="Path to the output directory for the published prediction PDB files.",
    )
    args = parser.parse_args()

    calculate_metrics(
        input_dir=args.input_dir,
        boltz_pubdir=args.boltz_pubdir,
        output_pdb_dir=args.output_pdb_dir,
        output_metrics_path=args.output_metrics_path,
        binder_chain=args.chains,
        complex_prediction=args.design_type == "binder" and not args.binder_alone,
    )
