import os
import argparse
import glob
import json

from biotite.structure import AtomArray
import biotite.structure as struc
import biotite.structure.io as strucio
import numpy as np
from scipy.spatial.distance import cdist
import pandas as pd
import hydride


def atom_id(structure: AtomArray, idx: int) -> str:
    """Stable atom identifier: {chain}{resid}{ins_code}:{atom_name}, e.g. A25:N or B123A:OD1"""
    atom = structure[idx]
    ins = atom.ins_code.strip() if hasattr(atom, "ins_code") else ""
    return f"{atom.chain_id}{atom.res_id}{ins}:{atom.atom_name}"


POSITIVE_ATOMS = {
    "LYS": ["NZ"],
    "ARG": ["NH1", "NH2"],
    "HIS": ["ND1", "NE2"],  # only if protonated
}

NEGATIVE_ATOMS = {"ASP": ["OD1", "OD2"], "GLU": ["OE1", "OE2"]}


def set_charges(structure: AtomArray) -> None:
    """
    Set the charge annotation for each atom in the structure.
    Positive residues: LYS, ARG
    Negative residues: ASP, GLU

    This is needed for salt bridge calculations and pi-cation interactions detection.
    """
    charge = np.zeros(structure.array_length(), dtype=int)
    charge[(structure.res_name == "LYS") & np.isin(structure.atom_name, POSITIVE_ATOMS["LYS"])] = +1
    charge[(structure.res_name == "ARG") & np.isin(structure.atom_name, POSITIVE_ATOMS["ARG"])] = +1
    charge[(structure.res_name == "ASP") & np.isin(structure.atom_name, NEGATIVE_ATOMS["ASP"])] = -1
    charge[(structure.res_name == "GLU") & np.isin(structure.atom_name, NEGATIVE_ATOMS["GLU"])] = -1

    structure.set_annotation("charge", charge)


def load_structure(file_path: str) -> AtomArray:
    structure = strucio.load_structure(file_path)
    structure.bonds = struc.connect_via_residue_names(structure)
    set_charges(structure)
    # Add missing hydrogens and relax them - needed for hydrogen bond detection
    structure = structure[structure.element != "H"]  # remove existing hydrogens
    structure, _ = hydride.add_hydrogen(structure)
    structure.coord = hydride.relax_hydrogen(structure)
    return structure


def get_interface_hydrogen_bonds(
    structure: AtomArray, binder_chain_id: str = "A", target_chain_id: str = "B"
) -> list[dict]:
    """Get hydrogen bonds between two chains in a structure."""

    # Hydrogen bonds between binder chain and target chain
    triplets = struc.hbond(
        structure, selection1=structure.chain_id == binder_chain_id, selection2=structure.chain_id == target_chain_id
    )  # donor_idx, atom_idx, acceptor_idx

    bonds = []
    for donor_idx, atom_idx, acceptor_idx in triplets:
        if structure[donor_idx].chain_id == binder_chain_id:
            bonds.append(
                {
                    "binder": [atom_id(structure, donor_idx)],
                    "target": [atom_id(structure, acceptor_idx)],
                    "binder_aa": structure[donor_idx].res_name,
                    "target_aa": structure[acceptor_idx].res_name,
                }
            )
        else:
            bonds.append(
                {
                    "binder": [atom_id(structure, acceptor_idx)],
                    "target": [atom_id(structure, donor_idx)],
                    "binder_aa": structure[acceptor_idx].res_name,
                    "target_aa": structure[donor_idx].res_name,
                }
            )

    return bonds


# Inspired by BoltzGen count_noncovalents
# https://github.com/HannesStark/boltzgen/blob/135a4a5a973d70a7d576b99320a840a532fec8f3/src/boltzgen/task/analyze/analyze_utils.py#L183
def get_interface_salt_bridges(
    structure: AtomArray, binder_chain_id: str = "A", target_chain_id: str = "B"
) -> list[dict]:
    """
    Get salt bridges between two chains in a structure.
    A salt bridge is defined as a pair of oppositely charged atoms within 4 Å.

    Returns a list of dicts with keys 'binder' and 'target' mapping to lists of atom indices
    """
    pos_atoms = structure[structure.charge > 0]
    neg_atoms = structure[structure.charge < 0]

    # Get the mapping from filtered indices to original structure indices
    pos_atoms_indices = np.where(structure.charge > 0)[0]
    neg_atoms_indices = np.where(structure.charge < 0)[0]

    pos_neg_distances = cdist(pos_atoms.coord, neg_atoms.coord)
    pos_idxs, neg_idxs = np.where((pos_neg_distances > 0.5) & (pos_neg_distances < 4))

    # Get indices of salt bridges between chains
    binder_chain_sb_mask = (pos_atoms.chain_id[pos_idxs] == binder_chain_id) & (
        neg_atoms.chain_id[neg_idxs] == target_chain_id
    )
    target_chain_sb_mask = (pos_atoms.chain_id[pos_idxs] == target_chain_id) & (
        neg_atoms.chain_id[neg_idxs] == binder_chain_id
    )

    # Combine both directions
    inter_chain_sb_mask = binder_chain_sb_mask | target_chain_sb_mask

    # Get the actual residue pairs
    interactions_unique = []
    for i in np.where(inter_chain_sb_mask)[0]:
        pos_idx = pos_idxs[i]
        neg_idx = neg_idxs[i]

        # Map back to original structure indices
        pos_atom_idx = pos_atoms_indices[pos_idx]
        neg_atom_idx = neg_atoms_indices[neg_idx]
        interaction = (pos_atom_idx, neg_atom_idx)
        if interaction not in interactions_unique:
            interactions_unique.append(interaction)

    # Sort to have consistent order (binder first, target second)
    interactions = []
    for pos_atom_idx, neg_atom_idx in interactions_unique:
        if structure[pos_atom_idx].chain_id == binder_chain_id:
            interactions.append(
                {
                    "binder": [atom_id(structure, pos_atom_idx)],
                    "target": [atom_id(structure, neg_atom_idx)],
                    "binder_aa": structure[pos_atom_idx].res_name,
                    "target_aa": structure[neg_atom_idx].res_name,
                }
            )
        else:
            interactions.append(
                {
                    "binder": [atom_id(structure, neg_atom_idx)],
                    "target": [atom_id(structure, pos_atom_idx)],
                    "binder_aa": structure[neg_atom_idx].res_name,
                    "target_aa": structure[pos_atom_idx].res_name,
                }
            )

    return interactions


def get_interface_pi_cation_interactions(
    structure: AtomArray, binder_chain_id: str = "A", target_chain_id: str = "B"
) -> list[dict[str, list[int]]]:
    """
    Get pi-cation interactions between two chains in a structure.
    A pi-cation interaction is defined as an interaction between an aromatic ring and a cation

    Returns a list of dicts with keys 'binder' and 'target' mapping to lists of atom indices.
    """
    interactions = struc.find_pi_cation_interactions(structure)

    # pi-cation interactions between aromatic rings and cations
    # Each element in the list represents one pi-cation interaction. The first element of each tuple represents atom indices of the aromatic ring, the second element is the atom index of the cation.
    interface_interactions = []

    for ring_idxs, cation_idx in interactions:
        chain1 = structure.chain_id[ring_idxs[0]]
        chain2 = structure.chain_id[cation_idx]
        if chain1 not in [binder_chain_id, target_chain_id] or chain2 not in [binder_chain_id, target_chain_id]:
            continue
        if chain1 != chain2:
            if chain1 == binder_chain_id:
                interface_interactions.append(
                    {
                        "binder": [atom_id(structure, idx) for idx in ring_idxs],
                        "target": [atom_id(structure, cation_idx)],
                        "binder_aa": structure[ring_idxs[0]].res_name,
                        "target_aa": structure[cation_idx].res_name,
                    }
                )
            else:
                interface_interactions.append(
                    {
                        "binder": [atom_id(structure, cation_idx)],
                        "target": [atom_id(structure, idx) for idx in ring_idxs],
                        "binder_aa": structure[cation_idx].res_name,
                        "target_aa": structure[ring_idxs[0]].res_name,
                    }
                )

    return interface_interactions


def get_interface_stacking_interactions(
    structure: AtomArray, binder_chain_id="A", target_chain_id="B"
) -> list[dict[str, list[int]]]:
    """
    Get stacking interactions between two chains in a structure.

    Returns a list of dicts with keys 'binder' and 'target' mapping to lists of atom indices.
    """

    # The stacking interactions between aromatic rings. Each element in the list represents one stacking interaction. The first two elements of each tuple represent atom indices of the stacked rings. The third element of each tuple is the type of stacking interaction.
    interactions = struc.find_stacking_interactions(structure)

    interface_interactions = []

    for ring1_idxs, ring2_idxs, interaction_type in interactions:
        chain1 = structure.chain_id[ring1_idxs[0]]
        chain2 = structure.chain_id[ring2_idxs[0]]
        if chain1 not in [binder_chain_id, target_chain_id] or chain2 not in [binder_chain_id, target_chain_id]:
            continue
        if chain1 != chain2:
            # Sort to have consistent order (binder first, target second)
            if chain1 == binder_chain_id:
                interface_interactions.append(
                    {
                        "binder": [atom_id(structure, idx) for idx in ring1_idxs],
                        "target": [atom_id(structure, idx) for idx in ring2_idxs],
                        "binder_aa": structure[ring1_idxs[0]].res_name,
                        "target_aa": structure[ring2_idxs[0]].res_name,
                    }
                )
            else:
                interface_interactions.append(
                    {
                        "binder": [atom_id(structure, idx) for idx in ring2_idxs],
                        "target": [atom_id(structure, idx) for idx in ring1_idxs],
                        "binder_aa": structure[ring2_idxs[0]].res_name,
                        "target_aa": structure[ring1_idxs[0]].res_name,
                    }
                )

    return interface_interactions


# Code source: Patrick Kunzmann
# License: BSD 3 clause


def detect_disulfide_bonds(structure, distance=2.05, distance_tol=0.05, dihedral=90, dihedral_tol=10):
    # Array where detected disulfide bonds are stored
    disulfide_bonds = []
    # A mask that selects only S-gamma atoms of cysteins
    sulfide_mask = (structure.res_name == "CYS") & (structure.atom_name == "SG")
    # sulfides in adjacency to other sulfides are detected in an
    # efficient manner via a cell list
    cell_list = struc.CellList(structure, cell_size=distance + distance_tol, selection=sulfide_mask)
    # Iterate over every index corresponding to an S-gamma atom
    for sulfide_i in np.where(sulfide_mask)[0]:
        # Find indices corresponding to other S-gamma atoms,
        # that are adjacent to the position of structure[sulfide_i]
        # We use the faster 'get_atoms_in_cells()' instead of
        # `get_atoms()`, as precise distance measurement is done
        # afterwards anyway
        potential_bond_partner_indices = cell_list.get_atoms_in_cells(coord=structure.coord[sulfide_i])
        # Iterate over every index corresponding to an S-gamma atom
        # as bond partner
        for sulfide_j in potential_bond_partner_indices:
            if sulfide_i == sulfide_j:
                # A sulfide cannot create a bond with itself:
                continue
            # Create 'Atom' instances
            # of the potentially bonds S-gamma atoms
            sg1 = structure[sulfide_i]
            sg2 = structure[sulfide_j]
            # For dihedral angle measurement the corresponding
            # C-beta atoms are required, too
            cb1 = structure[
                (structure.chain_id == sg1.chain_id) & (structure.res_id == sg1.res_id) & (structure.atom_name == "CB")
            ]
            cb2 = structure[
                (structure.chain_id == sg2.chain_id) & (structure.res_id == sg2.res_id) & (structure.atom_name == "CB")
            ]
            # Measure distance and dihedral angle and check criteria
            bond_dist = struc.distance(sg1, sg2)
            bond_dihed = np.abs(np.rad2deg(struc.dihedral(cb1, sg1, sg2, cb2)))
            if (
                bond_dist > distance - distance_tol
                and bond_dist < distance + distance_tol
                and bond_dihed > dihedral - dihedral_tol
                and bond_dihed < dihedral + dihedral_tol
            ):
                # Atom meet criteria -> we found a disulfide bond
                # -> the indices of the bond S-gamma atoms
                # are put into a tuple with the lower index first
                bond_tuple = sorted((sulfide_i, sulfide_j))
                # Add bond to list of bonds, but each bond only once
                if bond_tuple not in disulfide_bonds:
                    disulfide_bonds.append(bond_tuple)
    return np.array(disulfide_bonds, dtype=int)


def get_interface_disulfide_bonds(structure: AtomArray, binder_chain_id="A", target_chain_id="B"):
    disulfide_bonds = detect_disulfide_bonds(structure)

    interface_bonds = []

    for sg1_index, sg2_index in disulfide_bonds:
        chain1 = structure.chain_id[sg1_index]
        chain2 = structure.chain_id[sg2_index]
        if (
            chain1 != chain2
            and chain1 in [binder_chain_id, target_chain_id]
            and chain2 in [binder_chain_id, target_chain_id]
        ):
            if chain1 == binder_chain_id:
                interface_bonds.append(
                    {
                        "binder": [atom_id(structure, sg1_index)],
                        "target": [atom_id(structure, sg2_index)],
                        "binder_aa": structure[sg1_index].res_name,
                        "target_aa": structure[sg2_index].res_name,
                    }
                )
            else:
                interface_bonds.append(
                    {
                        "binder": [atom_id(structure, sg2_index)],
                        "target": [atom_id(structure, sg1_index)],
                        "binder_aa": structure[sg2_index].res_name,
                        "target_aa": structure[sg1_index].res_name,
                    }
                )
    return interface_bonds


SIDECHAIN_CONTACT_DISTANCE = 4.5


def get_interface_residues_all_atom(
    structure: AtomArray, binder_chain_id: str = "A", target_chain_id: str = "B"
) -> tuple[list[int], list[int]]:
    """Return (binder_residues, target_residues) with any heavy atom within SIDECHAIN_CONTACT_DISTANCE.
    Credit: BindCraft https://github.com/martinpacesa/BindCraft/blob/main/functions/biopython_utils.py
    """
    from scipy.spatial import cKDTree

    heavy = structure[structure.element != "H"]
    binder = heavy[heavy.chain_id == binder_chain_id]
    target = heavy[heavy.chain_id == target_chain_id]
    if len(binder) == 0 or len(target) == 0:
        return [], []
    binder_tree = cKDTree(binder.coord)
    target_tree = cKDTree(target.coord)
    pairs = binder_tree.query_ball_tree(target_tree, SIDECHAIN_CONTACT_DISTANCE)
    binder_residues = sorted(set(int(binder.res_id[i]) for i, contacts in enumerate(pairs) if contacts))
    target_residues = sorted(set(int(target.res_id[j]) for contacts in pairs for j in contacts))
    return binder_residues, target_residues


def bonds_to_json(bonds: list[dict[str, list[int]]]) -> str:
    """
    Convert a list of bonds (with 'binder' and 'target' atom indices) to a JSON string.
    """
    return json.dumps(bonds, separators=(",", ":"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_csv", type=str)
    parser.add_argument("--binder_chain", type=str, default="A", help="Binder chain identifier")
    parser.add_argument("--target_chain", type=str, default="B", help="Target chain identifier")

    options = parser.parse_args()
    binder_chain_id = options.binder_chain
    target_chain_id = options.target_chain

    if len(binder_chain_id) != 1:
        raise ValueError(f"Only single-chain binder is supported, got: {binder_chain_id}")

    if len(target_chain_id) != 1:
        raise ValueError(f"Only single-chain target is supported, got: {target_chain_id}")

    if os.path.isdir(options.input_path):
        paths = sorted(glob.glob(os.path.join(options.input_path, "*.pdb")))
        print(f"Reading sequences from {len(paths):,} PDBs")
    elif options.input_path.endswith((".pdb",)):
        paths = [options.input_path]
        print(f"Reading sequence from {options.input_path}")
    else:
        raise ValueError("Input must be a directory with PDB files, or a PDB file.")

    scores = {}
    for path in paths:
        print(f"Processing {path}...")
        filename = os.path.basename(path).removesuffix(".pdb")

        structure = load_structure(path)

        # TODO: Generalize the logic for target - use mask instead of chain_id (target could be everything except the binder chain)
        hydrogen_bonds = get_interface_hydrogen_bonds(
            structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
        )
        salt_bridges = get_interface_salt_bridges(
            structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
        )
        pi_cation_interactions = get_interface_pi_cation_interactions(
            structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
        )
        stacking_interactions = get_interface_stacking_interactions(
            structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
        )
        try:
            disulfide_bonds = get_interface_disulfide_bonds(
                structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
            )
        except Exception as e:
            print(f"Warning: Disulfide bond detection failed for {path} with error: {e}")
            disulfide_bonds = []
        binder_residues, target_residues = get_interface_residues_all_atom(
            structure, binder_chain_id=binder_chain_id, target_chain_id=target_chain_id
        )
        scores[filename] = {
            "interface_hydrogen_bonds": hydrogen_bonds,
            "n_interface_hydrogen_bonds": len(hydrogen_bonds),
            "interface_salt_bridges": salt_bridges,
            "n_interface_salt_bridges": len(salt_bridges),
            "interface_pi_cation_interactions": pi_cation_interactions,
            "n_interface_pi_cation_interactions": len(pi_cation_interactions),
            "interface_stacking_interactions": stacking_interactions,
            "n_interface_stacking_interactions": len(stacking_interactions),
            "interface_disulfide_bonds": disulfide_bonds,
            "n_interface_disulfide_bonds": len(disulfide_bonds),
            "interface_target_residues_aa": ",".join(f"{target_chain_id}{r}" for r in target_residues),
            "interface_binder_residues_aa": ",".join(f"{binder_chain_id}{r}" for r in binder_residues),
        }

    df = pd.DataFrame(scores).T.rename_axis("id")
    bond_columns = [
        "interface_hydrogen_bonds",
        "interface_salt_bridges",
        "interface_pi_cation_interactions",
        "interface_stacking_interactions",
        "interface_disulfide_bonds",
    ]
    for col in bond_columns:
        df[col] = df[col].apply(bonds_to_json)
    df.to_csv(options.output_csv)
    print("Saved metrics to:", options.output_csv)
