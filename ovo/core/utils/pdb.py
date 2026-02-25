from collections import defaultdict
import gzip
import json

import numpy as np
import os
import requests

from biopandas.pdb import PandasPdb

import pandas as pd
from copy import deepcopy
from Bio import PDB, Align
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

from io import StringIO
from scipy.spatial.transform import Rotation as R


aa3to1 = {
    "CYS": "C",
    "ASP": "D",
    "SER": "S",
    "GLN": "Q",
    "LYS": "K",
    "ILE": "I",
    "PRO": "P",
    "THR": "T",
    "PHE": "F",
    "ASN": "N",
    "GLY": "G",
    "HIS": "H",
    "LEU": "L",
    "ARG": "R",
    "TRP": "W",
    "ALA": "A",
    "VAL": "V",
    "GLU": "E",
    "TYR": "Y",
    "MET": "M",
}


# Pre-calculated transformed displacements using 5eli NAG as template in the CB-ND2 z-axis reference frame
transformed_displacements = np.array(
    [
        [-0.4082622, -0.45912408, -1.30803404],
        [-0.70450961, 0.68773313, -2.28396899],
        [-0.22737329, 0.32573119, -3.6814555],
        [1.27596815, 0.09700733, -3.66800543],
        [1.63672552, -0.96640494, -2.63479564],
        [2.61316972, -0.48611626, -1.5859937],
        [-2.5847387, 2.26184417, -2.25385266],
        [-4.0755428, 2.41315718, -2.28422532],
        [-2.12259706, 1.0096836, -2.29977646],
        [-0.55055668, 1.37749703, -4.58249662],
        [1.71515412, -0.32738686, -4.95309542],
        [0.46600102, -1.44944231, -1.94881529],
        [3.87324501, -1.12614701, -1.72277423],
        [-1.83356036, 3.2290743, -2.18745253],
    ]
)


def fix_contigs(contigs, parsed_pdb):
    def fix_contig(contig):
        INF = float("inf")
        X = contig.split("/")
        Y = []
        for n, x in enumerate(X):
            if x[0].isalpha():
                C, x = x[0], x[1:]
                S, E = -INF, INF
                if x.startswith("-"):
                    E = int(x[1:])
                elif x.endswith("-"):
                    S = int(x[:-1])
                elif "-" in x:
                    (S, E) = (int(y) for y in x.split("-"))
                elif x.isnumeric():
                    S = E = int(x)
                new_x = ""
                c_, i_ = None, 0
                for c, i in parsed_pdb["pdb_idx"]:
                    if c == C and i >= S and i <= E:
                        if c_ is None:
                            new_x = f"{c}{i}"
                        else:
                            if c != c_ or i != i_ + 1:
                                new_x += f"-{i_}/{c}{i}"
                        c_, i_ = c, i
                Y.append(new_x + f"-{i_}")
            elif "-" in x:
                # sample length
                s, e = x.split("-")
                m = np.random.randint(int(s), int(e) + 1)
                Y.append(f"{m}-{m}")
            elif x.isnumeric() and x != "0":
                Y.append(f"{x}-{x}")
        return "/".join(Y)

    return [fix_contig(x) for x in contigs]


def get_pdb(pdb_code: str) -> bytes:
    if len(pdb_code) == 4:
        base_url = f"https://files.rcsb.org/download/{pdb_code}.pdb"
    else:
        base_url = f"https://alphafold.ebi.ac.uk/files/AF-{pdb_code.upper()}-F1-model_v6.pdb"

    # NO_VERIFY_SSL is set to true in gh action for testing purposes (problem with self-signed certificate)
    response = requests.get(base_url, verify=not os.getenv("NO_VERIFY_SSL", False))

    if not response.ok:
        raise ValueError(f"Error downloading PDB {pdb_code}")
    if base_url.endswith(".gz"):
        return gzip.decompress(response.content)
    return response.content


class PDBSegmentSelector(PDB.Select):
    def __init__(self, segments: list[str]):
        """Select only the specified segments from a PDB structure.

        :param: segments: list of str with the segments to select, e.g. ["A5", "A10-20", "B30-40", "C"]
        """
        self.parsed_segments = []
        for segment in segments:
            chain_id = segment[0]
            assert chain_id.isalpha(), f"Invalid chain ID in segment, expected A123-456, got: {segment}"
            if len(segment) == 1:
                # full chain
                self.parsed_segments.append((chain_id, 1, np.inf))
            elif "-" in segment:
                # residue range
                start_residue, end_residue = segment[1:].split("-")
                self.parsed_segments.append((chain_id, int(start_residue), int(end_residue)))
            else:
                # single residue
                residue_number = int(segment[1:])
                self.parsed_segments.append((chain_id, residue_number, residue_number))

    def accept_model(self, model):
        return True  # Accept all models

    def accept_chain(self, chain):
        return chain.id in [seg[0] for seg in self.parsed_segments]  # Pre-filter chains

    def accept_residue(self, residue):
        residue_chain_id = residue.full_id[2]
        residue_number = residue.id[1]
        return any(
            residue_chain_id == chain_id and (start <= residue_number <= end)
            for chain_id, start, end in self.parsed_segments
        )

    def accept_atom(self, model):
        return True  # Accept all atoms


def detect_glycosylation_sites(
    atom_ppdb: pd.DataFrame,
    chains: list[str] | str | None = None,
    query_atoms: list[str] | None = None,
    cyclic: bool = False,
) -> dict | None:
    """Find glycosylation sites in the PDB file
    :param:
        atom_ppdb: Pandas DataFrame with the ATOM records of the PDB file
        chains: str or list of str with the chain IDs to search for glycosylation sites
        query_atoms : list of str with the atom names to search for glycosylation sites

    :return:
        glycosylation_dict: dictionary with the coordinates of the query glycosylated atoms
    """
    glycosylation_pattern = ["ASN", "* except PRO", ["THR", "SER"]]  # Define the pattern N*S N*T

    if query_atoms is None:
        query_atoms = ["CA", "C", "CB", "ND2"]

    if isinstance(chains, str):
        chains = [chains]
    elif chains is None:
        chains = atom_ppdb["chain_id"].unique()

    atom_ppdb = atom_ppdb.query("chain_id in @chains")

    residues = atom_ppdb[["chain_id", "residue_number", "residue_name"]].drop_duplicates().set_index("residue_number")

    # Create a DataFrame of overlapping residue triplets (e.g. resnum
    # Before dropna three_mers looks like this:
    # num chain res[num] res[num+1] res[num+2]
    # 129   A     ASN       THR        THR
    # 130   A     THR       THR        VAL
    # 131   A     THR       VAL        PHE
    # 132   A     VAL       PHE        None
    # 132   A     PHE       None       None

    three_mers = pd.concat(
        [residues.chain_id] + [residues.residue_name.shift(-i) for i in range(len(glycosylation_pattern))], axis=1
    )

    three_mers.columns = ["chain_id", "resname1", "resname2", "resname3"]

    if cyclic:
        three_mers.loc[three_mers.index[-1], "resname2"] = three_mers.iloc[0].loc["resname1"]
        three_mers.loc[three_mers.index[-1], "resname3"] = three_mers.iloc[0].loc["resname2"]
        three_mers.loc[three_mers.index[-2], "resname3"] = three_mers.iloc[0].loc["resname1"]

    three_mers = three_mers.dropna()

    # Check for the glycosylation pattern
    is_glycosylated = three_mers.apply(
        lambda row: (row.iloc[1] == glycosylation_pattern[0])
        and (row.iloc[2] != "PRO")
        and (row.iloc[3] in glycosylation_pattern[2]),
        axis=1,
    )

    glycosylated_residues = three_mers[is_glycosylated]

    if glycosylated_residues.empty:
        return None

    glycosylated_chains = glycosylated_residues.chain_id.unique()
    glycosylation_dict = {}
    for chain in glycosylated_chains:
        chain_atom_ppdb = atom_ppdb.query("chain_id==@chain")
        for resnum in glycosylated_residues[glycosylated_residues.chain_id == chain].index:
            glycosylation_dict[(chain, resnum)] = {}
            for atom in query_atoms:
                res_coords_df = chain_atom_ppdb.query("residue_number==@resnum")
                glycosylation_dict[(chain, resnum)][atom] = res_coords_df.query("atom_name==@atom")[
                    ["x_coord", "y_coord", "z_coord"]
                ].values.flatten()

    return glycosylation_dict


def calculate_coords_from_transformed_displacements(P1, P2) -> np.ndarray:
    """Calculate the coordinates of the glycan atoms based on the transformed displacements

    It uses the pre-calculated transformed displacements to calculate the coordinates of the glycan atoms

    :param: P1, P2: 3D coordinates in the PDB reference frame of the ND2 and CB atoms of the glycosylated residue
    :return: 3D coordinates in the PDB reference frame of the glycan atoms
    """

    # Convert points to numpy arrays
    P1 = np.array(P1)
    P2 = np.array(P2)

    # Vector from P1 to P2
    V = P2 - P1
    U = V / np.linalg.norm(V)  # Normalize

    # Z-axis unit vector
    z_axis = np.array([0, 0, 1])

    # Calculate the rotation matrix aligning U to the Z-axis
    rotation_matrix = R.align_vectors([z_axis], [U])[0].as_matrix()

    # Inverse rotation
    inverse_rotation = rotation_matrix.T

    # Compute inverse translation
    inverse_translation = -inverse_rotation @ P1  # Inverse translation based on the rotation

    # Create the inverse transformation matrix
    inverse_matrix = np.eye(4)
    inverse_matrix[:3, :3] = inverse_rotation
    inverse_matrix[:3, 3] = inverse_translation

    original_displacements = []
    for displacement in transformed_displacements:
        # Convert to homogeneous coordinates
        displacement_homogeneous = np.array([*displacement, 0])  # The last element is 0 for a displacement
        # Apply inverse transformation matrix
        original_displacement_homogeneous = inverse_matrix @ displacement_homogeneous
        original_displacement = original_displacement_homogeneous[:3]  # Get x, y, z
        original_displacements.append(tuple(original_displacement))

    coords = np.array(original_displacements) + P1

    return coords


def add_glycan_to_pdb(pdb_str: str) -> tuple[str, list[str] | None]:
    """Add glycan atoms to the PDB string"""

    # Read PDB file as df from string
    ppdb = PandasPdb().read_pdb_from_list(pdb_str.splitlines(True))

    # calculate glycosylated sites per (chain, residue)
    glycosylated_residues = detect_glycosylation_sites(ppdb.df["ATOM"])

    if not glycosylated_residues:
        return pdb_str, None

    glycosylated_residues_str = [f"{chain_resnum[0]}{chain_resnum[1]}" for chain_resnum in glycosylated_residues]

    # calculate coords for glycanes sites per (chain, residue)
    coords_to_insert_glycane_per_resnum = {}
    for chain_and_resnum, atoms_coords_dict in glycosylated_residues.items():
        ND2_coords, CB_coords, CA_coords, C_coords = (
            atoms_coords_dict["ND2"],
            atoms_coords_dict["CB"],
            atoms_coords_dict["CA"],
            atoms_coords_dict["C"],
        )

        # This allows to visualize the glycan atoms also if ND2, CB are missing
        P1, P2 = None, None
        if C_coords.size > 0 and CA_coords.size > 0:
            P1, P2 = C_coords, CA_coords
        if CA_coords.size > 0 and CB_coords.size > 0:
            P1, P2 = CB_coords, CA_coords
        if ND2_coords.size > 0 and CB_coords.size > 0:
            P1, P2 = ND2_coords, CB_coords

        if P1 is not None and P2 is not None:
            coords_to_insert_glycane_per_resnum[chain_and_resnum] = calculate_coords_from_transformed_displacements(
                P1, P2
            )

    # Create a PandasPdb object to store the glycan atoms
    atom_names_nag = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "N2", "O3", "O4", "O5", "O6", "O7"]

    N_rows = len(atom_names_nag) * len(coords_to_insert_glycane_per_resnum)

    glycan_ppdb = deepcopy(ppdb)

    ppdb_hetatm = pd.DataFrame()

    ppdb_hetatm["record_name"] = ["HETATM"] * N_rows
    ppdb_hetatm["atom_number"] = list(range(1, N_rows + 1))
    ppdb_hetatm["blank_1"] = [""] * N_rows
    ppdb_hetatm["alt_loc"] = [""] * N_rows
    ppdb_hetatm["residue_name"] = ["NAG"] * N_rows
    ppdb_hetatm["blank_2"] = [""] * N_rows
    ppdb_hetatm["insertion"] = [""] * N_rows
    ppdb_hetatm["blank_3"] = [""] * N_rows
    ppdb_hetatm["atom_name"] = atom_names_nag * len(coords_to_insert_glycane_per_resnum)

    chain_id = []
    residue_number = []
    x_coords, y_coords, z_coords = [], [], []
    element_symbol = []
    for nag_resnum, ((NAG_chain, resnum), glycan_atoms) in enumerate(coords_to_insert_glycane_per_resnum.items()):
        chain_id += [NAG_chain] * len(atom_names_nag)
        residue_number += [int(nag_resnum + 1)] * len(atom_names_nag)
        x_coords += list(glycan_atoms[:, 0])
        y_coords += list(glycan_atoms[:, 1])
        z_coords += list(glycan_atoms[:, 2])
        element_symbol += ["C"] * 8 + ["N"] + ["O"] * 5

    ppdb_hetatm["chain_id"] = chain_id
    ppdb_hetatm["residue_number"] = residue_number
    ppdb_hetatm["x_coord"] = x_coords
    ppdb_hetatm["y_coord"] = y_coords
    ppdb_hetatm["z_coord"] = z_coords
    ppdb_hetatm["element_symbol"] = element_symbol

    ppdb_hetatm["occupancy"] = [1.0] * N_rows
    ppdb_hetatm["b_factor"] = [1.0] * N_rows
    ppdb_hetatm["blank_4"] = [""] * N_rows
    ppdb_hetatm["segment_id"] = [""] * N_rows
    ppdb_hetatm["charge"] = [np.nan] * N_rows
    ppdb_hetatm["line_idx"] = [np.nan] * N_rows

    if ppdb_hetatm.empty:
        return pdb_str, None

    glycan_ppdb.df["HETATM"] = ppdb_hetatm.loc[:, ppdb.df["ATOM"].columns]

    # Save the glycan PDB to a string
    pdb_glycan_string = glycan_ppdb.to_pdb_stream()

    return pdb_glycan_string.getvalue(), glycosylated_residues_str


def get_atom_coordinates(
    structure: PDB.Structure.Structure,
    chain_id: str | None,
    residues: list[int] | None,
    all_atom: bool = False,
    model_index=0,
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


def _align_sequences_and_get_indices(seqs: list[str]):
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
) -> tuple[list[str], float]:
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

    seqs = ["".join([aa3to1.get(residue.resname, "X") for residue in residues]) for residues in residues_list]

    sequence_alignment = force_sequence_alignment or any(len(seqs[i]) != len(seqs[0]) for i in range(1, len(seqs)))
    if sequence_alignment:
        aligned_seqs_indices = _align_sequences_and_get_indices(seqs)
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

    aligned_structures_pdb = [get_aligned_structure_as_string(structure) for structure in structures]
    rmsd = super_imposer.rms
    return aligned_structures_pdb, rmsd


def get_aligned_structure_as_string(structure) -> str:
    """Returns the PDB representation of the given structure as a string."""
    io = StringIO()
    pdb_io = PDB.PDBIO()
    pdb_io.set_structure(structure)
    pdb_io.save(io)
    return io.getvalue()


# Taken from AUTOBAN
def pad_line(line):
    """Helper function to pad line to 80 characters in case it is shorter"""
    size_of_line = len(line)
    if size_of_line < 80:
        padding = 80 - size_of_line + 1
        line = line.strip("\n") + " " * padding + "\n"
    return line[:81]  # 80 + newline character


def pdb_to_mmcif_iter(pdb_data: str, structure_id: str, bfactor_to_plddt=False, fractional_plddt=False):
    """
    ADAPTED from pdb-tools pdb_tocif - added section that converts b-factor to pLDDT metric

    Convert a structure in PDB format to mmCIF format.

    This function is a generator.

    Parameters
    ----------
    pdb_data: string with PDB data
    structure_id: entry ID
    bfactor_to_plddt: convert b-factor to alphafold pLDDT metric
    fractional_plddt: multiply pLDDT by 100 to get 0-100, used for ESMFold PDB which has values in 0-1 range

    Yields
    ------
    str (line-by-line)
        The structure in mmCIF format.
    """
    _pad_line = pad_line

    # The spacing here is just aesthetic purposes when printing the file
    _a = "{:<6s} {:5d} {:2s} {:6s} {:1s} {:3s} {:3s} {:1s} {:5s} {:1s} "
    _a += "{:10.3f} {:10.3f} {:10.3f} {:10.3f} {:10.3f} {:1s} "
    _a += "{:5s} {:3s} {:1s} {:4s} {:1d}\n"

    yield "# Converted to mmCIF by pdb-tools\n"
    yield "#\n"

    yield "data_{}\n".format(structure_id)

    yield "#\n"
    yield "loop_\n"
    yield "_atom_site.group_PDB\n"
    yield "_atom_site.id\n"
    yield "_atom_site.type_symbol\n"
    yield "_atom_site.label_atom_id\n"
    yield "_atom_site.label_alt_id\n"
    yield "_atom_site.label_comp_id\n"
    yield "_atom_site.label_asym_id\n"
    yield "_atom_site.label_entity_id\n"
    yield "_atom_site.label_seq_id\n"
    yield "_atom_site.pdbx_PDB_ins_code\n"
    yield "_atom_site.Cartn_x\n"
    yield "_atom_site.Cartn_y\n"
    yield "_atom_site.Cartn_z\n"
    yield "_atom_site.occupancy\n"
    yield "_atom_site.B_iso_or_equiv\n"
    yield "_atom_site.pdbx_formal_charge\n"
    yield "_atom_site.auth_seq_id\n"
    yield "_atom_site.auth_comp_id\n"
    yield "_atom_site.auth_asym_id\n"
    yield "_atom_site.auth_atom_id\n"
    yield "_atom_site.pdbx_PDB_model_num\n"

    # Coordinate data
    model_no = 1
    serial = 0

    records = ("ATOM", "HETATM")
    models_bfactors = []
    model_bfactors = {}
    for line in pdb_data.splitlines():
        if line.startswith(records):
            line = _pad_line(line)

            record = line[0:6].strip()
            serial += 1

            element = line[76:78].strip()
            if not element:
                element = "?"

            atname = line[12:16].strip()
            atname = atname.replace('"', "'")
            if "'" in atname:
                atname = '"{}"'.format(atname)

            altloc = line[16]
            if altloc == " ":
                altloc = "?"

            resname = line[17:20]
            chainid = line[21]
            if chainid == " ":
                chainid = "?"

            resnum = line[22:26].strip()
            icode = line[26]
            if icode == " ":
                icode = "?"

            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])

            occ = float(line[54:60])
            bfac = float(line[60:66])

            charge = line[78:80].strip()
            if charge == "":
                charge = "?"

            entityid = "1"

            if atname == "CA":
                if chainid not in model_bfactors:
                    model_bfactors[chainid] = {}
                model_bfactors[chainid][resnum] = (resname, bfac)

            yield _a.format(
                record,
                serial,
                element,
                atname,
                altloc,
                resname,
                chainid,
                entityid,
                resnum,
                icode,
                x,
                y,
                z,
                occ,
                bfac,
                charge,
                resnum,
                resname,
                chainid,
                atname,
                model_no,
            )

        elif line.startswith("ENDMDL"):
            model_no += 1
            models_bfactors.append(model_bfactors)
            model_bfactors = {}
        else:
            continue

    models_bfactors.append(model_bfactors)

    yield "#\n"  # close block

    if bfactor_to_plddt:
        yield "loop_\n"
        yield "_ma_qa_metric.id\n"
        yield "_ma_qa_metric.mode\n"
        yield "_ma_qa_metric.name\n"
        yield "_ma_qa_metric.software_group_id\n"
        yield "_ma_qa_metric.type\n"
        yield "1 global pLDDT 1 pLDDT\n"
        yield "2 local  pLDDT 1 pLDDT\n"
        yield "#\n"
        for modelid, model_bfactors in enumerate(models_bfactors, start=1):
            mean_bfactor = np.mean(
                [bfactor for chain_bfactors in model_bfactors.values() for resname, bfactor in chain_bfactors.values()]
            )
            if fractional_plddt:
                mean_bfactor *= 100.0
            yield "_ma_qa_metric_global.metric_id    1\n"
            yield f"_ma_qa_metric_global.metric_value {mean_bfactor}\n"
            yield f"_ma_qa_metric_global.model_id     {modelid}\n"
            yield f"_ma_qa_metric_global.ordinal_id   {modelid}\n"
        yield "#\n"
        yield "loop_\n"
        yield "_ma_qa_metric_local.label_asym_id\n"
        yield "_ma_qa_metric_local.label_comp_id\n"
        yield "_ma_qa_metric_local.label_seq_id\n"
        yield "_ma_qa_metric_local.metric_id\n"
        yield "_ma_qa_metric_local.metric_value\n"
        yield "_ma_qa_metric_local.model_id\n"
        yield "_ma_qa_metric_local.ordinal_id\n"
        for modelid, model_bfactors in enumerate(models_bfactors, start=1):
            if not model_bfactors:
                continue
            for chainid, chain_bfactors in model_bfactors.items():
                for resno, (resname, bfactor) in chain_bfactors.items():
                    if fractional_plddt:
                        bfactor *= 100.0
                    yield f"{chainid:2s} {resname} {str(resno):4s} 2 {bfactor:.2f} {str(modelid):2s} {str(resno):4s}\n"
        yield "#\n"


def pdb_to_mmcif(pdb_data: str, structure_id: str, bfactor_to_plddt=False, fractional_plddt=False):
    return "".join(
        pdb_to_mmcif_iter(
            pdb_data,
            structure_id,
            bfactor_to_plddt=bfactor_to_plddt,
            fractional_plddt=fractional_plddt,
        )
    )


class ChainNotFoundError(Exception):
    pass


def get_sequences_from_pdb_str(
    pdb_str: str,
    chains: list[str] = None,
    by_residue_number: bool = False,
) -> dict[str, str] | dict[str, dict[str, str]]:
    """Get the sequence of a structure from the pdb file.

    :param pdb_str: str, PDB file contents as string
    :param chains: list of str, chain IDs to extract sequences from, if None, all chains are extracted
    :param by_residue_number: if True, return a dict with residue numbers (strings) as keys and amino acids as values

    Sequence is extracted based on CA atoms. If a residue has CA atom, it is included in the sequence, either
    as the amino acid letter (if one of 20 standard amino acids) or as X (if non-standard amino acid).
    If a residue does not have CA atom (e.g. a ligand), it is ignored.

    Chain breaks (for example a jump from 123 to 134) are NOT filled with X but ignored.

    Assumes sorted residue ids in the PDB file within each chain. (E.g. BioPython does as well return it in the original
        order.)

    Only the first model in the PDB file is parsed (everything after ENDMDL is ignored).
    """
    lines = pdb_str.splitlines()
    if len(lines) == 1 and pdb_str.endswith(".pdb"):
        raise ValueError(f"Expected PDB file contents, got path instead: {pdb_str}")

    # PDB column layout (0-indexed, exlusive end):
    #   0:6   record type (ATOM  / HETATM)
    #  12:16  atom name (e.g. CA)
    #  17:20  residue name
    #  21     chain ID
    #  22:26  residue sequence number
    #  26     insertion code

    sequences: dict[str, list] = defaultdict(list)  # chain ID -> residues in order of appearance in the PDB file
    seen: set = defaultdict(set)  # Keep track of seen (residue number, insertion code) for each chain to
    # avoid duplicates (e.g. due to multiple atoms per residue)

    for line in lines:
        record = line[:6].strip()

        if record == "ENDMDL":
            # break as soon as the first model ends
            break

        if record not in ("ATOM", "HETATM"):
            continue

        atom_name = line[12:16].strip()

        if atom_name != "CA":
            # Only consider amino acid residues (standard or non-standard)
            continue

        res_name = line[17:20].strip()
        chain_id = line[21]
        res_num = int(line[22:26])
        ins_code = line[26].strip()

        if chains is not None and chain_id not in chains:
            continue

        key = (res_num, ins_code)

        # Need to check if seen (e.g. if alternate locations are present)
        if key not in seen[chain_id]:
            seen[chain_id].add(key)
            aa = aa3to1.get(res_name, "X")
            if by_residue_number:
                res_num_str = str(res_num) + ins_code
                sequences[chain_id].append((res_num_str, aa))
            else:
                sequences[chain_id].append(aa)

    if chains is not None:
        for chain_id in chains:
            if chain_id not in sequences:
                raise ChainNotFoundError(chain_id)

    return {chain_id: (dict(seq) if by_residue_number else "".join(seq)) for chain_id, seq in sequences.items()}


def get_remark_header(pdb_path: str) -> tuple[str, list[str]]:
    """
    Get the REMARK header from the PDB file.
    :param pdb_path: str, path to the PDB file
    :return: str, REMARK header
    """
    with open(pdb_path, "r") as f:
        lines = f.readlines()

    all_remark_lines = []
    remark_header = ""
    for line in lines:
        if line.startswith("REMARK   1"):
            all_remark_lines.append(line.strip().removeprefix("REMARK   1 "))
            remark_header += line

    return remark_header, all_remark_lines


REMARK_KEYS = ["Input contig", "Standardized contig", "Chains", "Input hotspots", "Standardized hotspots"]


def get_standardized_remarks_from_pdb_str(pdb_str: str) -> dict[str, str]:
    """Parse "standardized" remarks from the PDB file

    :param pdb_str: PDB file contents as string
    :return: dict, parsed remarks {"Input contig": "A45-46/10-15/A45-46/0 B24-26/5/B24-26/0 C10-20", ...}
    Example: example header to read
        REMARK   1 Input contig: "A45-46/10-15/A45-46/0 B24-26/5/B24-26/0 "
        REMARK   1 Input contig: "C10-20"
        REMARK   1 Standardized contig: "A45-46/13-13/A45-46/0 B24-26/5-5/B24-26/"
        REMARK   1 Standardized contig: "0 C10-20/0"
        REMARK   1 Chains: "A B C"
        REMARK   1 Input hotspots:
        REMARK   1 Standardized hotspots:
    """

    parsed_remarks = {}
    stripped_remark_lines = [
        l.removeprefix("REMARK   1").strip() for l in pdb_str.splitlines() if l.startswith("REMARK   1")
    ]
    for key in REMARK_KEYS:
        # Get lines that begin with this key
        remark_lines = [line.removeprefix(f"{key}:").strip() for line in stripped_remark_lines if line.startswith(key)]
        if not remark_lines:
            # Only parse remarks that exist in the PDB
            continue

        values = []
        for line in remark_lines:
            if not line and key not in ["Input hotspots", "Standardized hotspots"]:
                raise ValueError("Empty JSON value after key")
            if not line and key in ["Input hotspots", "Standardized hotspots"]:
                continue

            values.append(json.loads(line))

        parsed_remarks[key] = "".join(values)

    return parsed_remarks


def trim_pdb_str(pdb_input_string: str, target_chain: str, start_res: int, end_res: int) -> str:
    return filter_pdb_str(pdb_input_string, [f"{target_chain}{start_res}-{end_res}"])


def filter_pdb_str(pdb_input_string: str, segments: list[str], add_ter=False) -> str:
    """Filter a PDB string to only include specified segments.

    :param pdb_input_string: str, input PDB string
    :param segments: list of str, segments to include, e.g. ["A5", "A10-20", "B30-40", "C"]
    :param add_ter: Order ATOMs in PDB based on order in selected_segments, add TER and END in between
    :return: str, filtered PDB string
    """
    # Generate trimmed pdb
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("filtered_structure", StringIO(pdb_input_string))
    io = PDB.PDBIO()
    io.set_structure(structure)

    stringIO = StringIO()
    # Save the trimmed structure as a IO string
    if add_ter:
        # Save segments one by one to ensure same order as in segments list
        for segment in segments:
            io.save(stringIO, select=PDBSegmentSelector([segment]))
    else:
        io.save(stringIO, select=PDBSegmentSelector(segments))
    return stringIO.getvalue()


def check_rfdiffusion_input(
    pdb_input_string: str,
    target_chain: str,
    start_res_trimmed_chain: int,
    end_res_trimmed_chain: int,
    max_amide_distance: float = 3.0,
):
    """Make sure that structure does not contain chain breaks
    without a gap in residue numbering (required in refolding step)

    Also make sure that no insertion codes are present.

    Raises ValueError if chain breaks are found.
    """
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("structure_to_check", StringIO(pdb_input_string))
    model = structure[0]
    chain = model[target_chain]

    residues_with_insertion_codes = []
    for residue in chain:
        if residue.id[2] and residue.id[2].strip():
            residues_with_insertion_codes.append(f"{residue.id[1]}{residue.id[2]}")
    if residues_with_insertion_codes:
        raise ValueError(
            f"Residues with insertion codes found in chain {target_chain}: "
            f"{', '.join(residues_with_insertion_codes)}. "
            f"Please renumber the structure to remove insertion codes."
        )

    previous_residue = None
    for residue in chain:
        resnum = residue.id[1]
        if resnum < start_res_trimmed_chain or resnum > end_res_trimmed_chain:
            continue

        if previous_residue is not None:
            prev_resnum = previous_residue.id[1]
            if "C" not in previous_residue or "N" not in residue:
                # Ignore positions with missing atoms
                previous_residue = residue
                continue
            prev_C = previous_residue["C"].coord
            curr_N = residue["N"].coord
            distance = np.linalg.norm(curr_N - prev_C)
            if distance > max_amide_distance:
                if resnum == prev_resnum + 1:
                    raise ValueError(
                        f"Chain break detected between residues {prev_resnum} and {resnum} in chain {target_chain} "
                        f"with distance {distance:.2f} Å but no gap in residue numbering. "
                        f"Please renumber the structure to include a gap in residue numbering "
                        f"(use a gap of at least 50 residues to indicate different chains) "
                        f"to ensure that chain breaks are preserved by the refolding step."
                    )
        previous_residue = residue
