import traceback

from biopandas.pdb import PandasPdb
import pandas as pd
import numpy as np
import glob
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.SASA import ShrakeRupley
from scipy.spatial import distance
from biotite.structure import CellList
import argparse

import os
from io import StringIO
from utils import PDBSelector, get_resname_resnum_atomname_atomnum_str
import re
import pydssp_numpy

# Author: Christopher Warren, Marco Ancona, David Prihoda

pdb_parser: PDBParser = PDBParser(QUIET=True)

BACKBONE_CONTACT_DISTANCE = 10.0
SIDECHAIN_CONTACT_DISTANCE = 3.0


def get_all_metrics(
    pdbs: list | str, hotspots: list[int] | None = None, only_CA: bool = True, cyclic: bool = False
) -> dict[str, dict[str, float]]:
    """Calculate all metrics for a list of PDB files.

    :parameter:
        pdbs (list | str): List of PDB files or a single PDB file path.
        hotspots (list[int] | None): List of hotspot residues. Default: None.
        only_CA (bool): Use only CA atoms. Default: True.
    :returns:
        dict[str, dict[str, str]]: Dictionary with the calculated metrics.
    """

    if isinstance(pdbs, str):
        pdbs = [pdbs]

    scores = {}

    threshold_distance = BACKBONE_CONTACT_DISTANCE if only_CA else SIDECHAIN_CONTACT_DISTANCE

    for pdb in pdbs:
        glycosolated_target_residues = None
        glycosolated_binder_residues = None

        distances_interface_df = None
        average_interface_dist = None
        average_dist_interface_only_contacts = None
        N_contact_interface = 0

        distances_hotspots_df = None
        average_hotspots_dist = None
        average_dist_hotspots_only_contacts = None
        N_contact_hotspots = 0

        # Calculate all metrics
        pdb_name = os.path.basename(pdb).removesuffix(".pdb")

        # Read atom dataframe using BioPandas
        atom_ppdb = PandasPdb().read_pdb(pdb).df["ATOM"]

        # TODO we should parse this from the PDB standardized file header instead
        chain_ids = sorted(atom_ppdb.chain_id.unique())
        if chain_ids == ["A", "B"]:
            binder_chain, target_chain = chain_ids
        elif chain_ids == ["A"]:
            binder_chain, target_chain = chain_ids[0], None
        else:
            raise ValueError(f"Expected chains A and B, found {chain_ids} in {pdb}")

        Rg = radius_of_gyration(atom_ppdb, chain_id=binder_chain)

        glycosolated_binder_residues = glycosylation_sites(atom_ppdb, chain_id=binder_chain, cyclic=cyclic)

        scores[pdb_name] = {
            "radius_of_gyration": Rg,
            "glycosolated_binder_residues": glycosolated_binder_residues,
        }

        if target_chain:
            glycosolated_target_residues = glycosylation_sites(atom_ppdb, chain_id=target_chain)

            target_interfaces_str, binder_interfaces_str, binder_res_str = get_interface(
                pdb, threshold_distance, target_chain=target_chain, binder_chain=binder_chain, only_CA=only_CA
            )

            target_interface_residues = (
                [int(res_str.split("_")[1]) for res_str in target_interfaces_str.split(",")]
                if target_interfaces_str
                else []
            )
            # binder_interface_residues = [int(res_str.split('_')[1]) for res_str in binder_interfaces_str.split(',')] \
            #     if binder_interfaces_str else None
            binder_residues = (
                [int(res_str.split("_")[1]) for res_str in binder_res_str.split(",")] if binder_interfaces_str else []
            )

            if target_interface_residues and binder_residues:
                (
                    distances_interface_df,
                    average_interface_dist,
                    average_dist_interface_only_contacts,
                    N_contact_interface,
                ) = distance_matrix_binder_target_interface(
                    pdb,
                    target_chain=target_chain,
                    binder_chain=binder_chain,
                    target_interface_residues=target_interface_residues,
                    binder_interface_residues=binder_residues,
                    only_CA=only_CA,
                )

            scores[pdb_name].update(
                {
                    "glycosolated_target_residues": glycosolated_target_residues,
                    "interface_target_residues": ",".join([f"{target_chain}{r}" for r in target_interface_residues]),
                    "interface_binder_residues": ",".join([f"{binder_chain}{r}" for r in binder_residues]),
                    "N_contact_interface": N_contact_interface,
                    # "distances_binder_interface_against_target_interface": distances_interface_df,
                    # "average_dist_binder_to_target_interface": average_interface_dist,
                    # "average_dist_binder_to_target_interface_contacts": average_dist_interface_only_contacts,
                }
            )

            if hotspots:
                if binder_residues:
                    (
                        distances_hotspots_df,
                        average_hotspots_dist,
                        average_dist_hotspots_only_contacts,
                        N_contact_hotspots,
                    ) = distance_matrix_binder_target_interface(
                        pdb,
                        target_chain=target_chain,
                        binder_chain=binder_chain,
                        target_interface_residues=hotspots,
                        binder_interface_residues=binder_residues,
                        only_CA=only_CA,
                    )
                hotspots_on_interface = (
                    sorted(set(hotspots) & set(target_interface_residues))
                    if hotspots and target_interface_residues
                    else []
                )
                scores[pdb_name].update(
                    {
                        # "average_dist_binder_to_hotspots_contacts": average_dist_hotspots_only_contacts,
                        # "distances_binder_interface_against_hotspots": distances_hotspots_df,
                        "interface_target_hotspot_residues": ",".join(
                            [f"{target_chain}{r}" for r in hotspots_on_interface]
                        ),
                        "average_dist_binder_to_hotspots": average_hotspots_dist,
                        "N_hotspots_on_interface": len(hotspots_on_interface),
                        "N_contact_hotspots": N_contact_hotspots,
                    }
                )

        try:
            pydssp_str = pydssp_assign(pdb, chain_id=binder_chain, cyclic=cyclic)
            scores[pdb_name].update(
                {
                    "pydssp_str": pydssp_str,  # DSSP line for the PDB file (H = alpha-helix, E = beta-strand, - = loop)
                    "pydssp_loop_percent": pydssp_str.count("-") / len(pydssp_str) * 100,
                    "pydssp_helix_percent": pydssp_str.count("H") / len(pydssp_str) * 100,
                    "pydssp_strand_percent": pydssp_str.count("E") / len(pydssp_str) * 100,
                }
            )
        except Exception as e:
            traceback.print_exc()
            scores[pdb_name]["pydssp_error"] = f"Unexpected pydssp error: {e}"

    return scores


# TODO: add this in the utils.py file
def get_coords_from_ppdb(atom_ppdb: pd.DataFrame) -> np.ndarray | None:
    """Get coordinates from a PandasPdb DataFrame.

    :parameter:
        atom_ppdb (pd.DataFrame): Pandas DataFrame with ATOM records.
    :returns:
        np.ndarray: NumPy array with coordinates.
    """

    if atom_ppdb.empty:
        return None

    assert atom_ppdb.record_name.unique() == ["ATOM"], "Only ATOM records are allowed when getting coordinates."

    return atom_ppdb[["x_coord", "y_coord", "z_coord"]].values


def radius_of_gyration(ppdb_atoms, chain_id: str | None, only_CA: bool = True) -> float | None:
    """Calculate radius of gyration of polymer, i.e. compactness score of a protein structure.

    :parameter:
        pdb_path: PDB file path.
        chain_id (str | None): Chain ID to use, or None to use all chains
    :returns:
        float: Compactness score.
    """

    if only_CA:
        ppdb_atoms = ppdb_atoms.query("atom_name == 'CA'")

    if chain_id is not None:
        ppdb_atoms = ppdb_atoms.query("chain_id==@chain_id")

    coords = get_coords_from_ppdb(ppdb_atoms)

    if coords is None:
        return None

    center_of_mass = coords.mean(axis=0)
    squared_distances = np.sum((coords - center_of_mass) ** 2, axis=1)
    Rg = np.sqrt(np.mean(squared_distances))

    return float(Rg)


def glycosylation_sites(atom_ppdb: pd.DataFrame, chain_id: str, cyclic: bool = False) -> str | None:
    """Find glycosylation sites in a PDB file. Calls detect_glycosylation_sites

    :returns:
        str: Comma-separated list of glycosylated residue numbers. None if no glycosylation sites are found.
    """

    glycosylation_dict = detect_glycosylation_sites(atom_ppdb, chains=chain_id, cyclic=cyclic)
    if not glycosylation_dict:
        return None

    return ",".join([str(resnum) for (chain, resnum) in glycosylation_dict])


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


def calculate_sasa_per_chain(struc, chain, **args) -> pd.Series:
    """Calculate the solvent-accessible surface area (SASA) for a chain in a PDB structure."""

    # This is the most time-consuming calculation
    sr = ShrakeRupley(**args)

    sr.compute(struc, level="R")

    sasa = {}
    for residue in struc[0][chain]:
        sasa[residue.id] = residue.sasa

    return pd.Series(sasa)


def DeltaSASA(complex_pdb_file: str, chain: str, **args) -> pd.DataFrame:
    """Calculate the DeltaSASA for a chain in a complex PDB file.
    :parameter:
        complex_pdb_file (str): Path to the PDB file.
        chain (str): Chain ID.
    :returns:
        pd.DataFrame: DataFrame with the DeltaSASA values.
    """

    parser = PDBParser(QUIET=True)
    complex_structure = parser.get_structure("complex", complex_pdb_file)

    io = PDBIO()
    io.set_structure(complex_structure)

    target_pdb_file = StringIO()
    io.save(target_pdb_file, select=PDBSelector(chain))

    target_structure = parser.get_structure("target", StringIO(target_pdb_file.getvalue()))

    # Calculate SASA for the entire complex
    complex_sasa = calculate_sasa_per_chain(complex_structure, chain, **args)
    target_sasa = calculate_sasa_per_chain(target_structure, chain, **args)

    interface_deltaSASA = pd.concat(
        [
            pd.Series([res.resname for res in target_structure[0][chain]], index=complex_sasa.index, name="residue"),
            complex_sasa.rename("complex_SASA"),
            target_sasa.rename("target_SASA"),
            (complex_sasa - target_sasa).rename("DeltaSASA"),
        ],
        axis=1,
    )

    return interface_deltaSASA


def get_interface(
    complex_pdb_file, threshold_distance, target_chain: str, binder_chain: str, only_CA=True
) -> tuple[str | None, str | None, str | None]:
    """Get the interface residues from a PDB file.

    :parameter:
        complex_pdb_file (str): Path to the PDB file.
        threshold_distance (float): Threshold distance to consider a contact.
        target_chain: ID of the target chain (usually B).
        binder_chain: ID of the binder chain (usually A).
        only_CA (bool): Use only CA atoms. Default: True.
    :returns:
        Tuple with the target (comma-separated list) residues and binder interfaces (comma-separated list) residues.
        In the format: RESNAME_RESNUM_ATOMNAME_ATOMNUM
    """
    ppdb = PandasPdb().read_pdb(complex_pdb_file)
    atom_ppdb = ppdb.df["ATOM"]
    unique_chains = set(atom_ppdb.chain_id.unique())
    assert unique_chains == {target_chain, binder_chain}, (
        f"Only target ({target_chain}) and binder ({binder_chain}) chains should be found in PDB, "
        f"found: {unique_chains}"
    )

    if only_CA:
        atom_ppdb = atom_ppdb[atom_ppdb.atom_name == "CA"]

    indices_binder = atom_ppdb.query("chain_id == @binder_chain").index
    indices_target = atom_ppdb.query("chain_id == @target_chain").index

    matrix = CellList(get_coords_from_ppdb(atom_ppdb), threshold_distance).create_adjacency_matrix(threshold_distance)
    matrix = pd.DataFrame(matrix, index=atom_ppdb.index, columns=atom_ppdb.index).loc[indices_target, indices_binder]

    # Select interacting matrix
    interacting_matrix = matrix.loc[matrix.any(axis=1), matrix.any(axis=0)]

    if interacting_matrix.empty:
        return None, None, None

    # Select target and binder interfaces residues (RESNAME_RESNUM_ATOMNAME_ATOMNUM)
    target_interfaces_str = get_resname_resnum_atomname_atomnum_str(atom_ppdb, list(interacting_matrix.index))
    binder_interfaces_str = get_resname_resnum_atomname_atomnum_str(atom_ppdb, list(interacting_matrix.columns))
    binder_str = get_resname_resnum_atomname_atomnum_str(atom_ppdb, list(indices_binder))

    return target_interfaces_str, binder_interfaces_str, binder_str


def distance_matrix_binder_target_interface(
    complex_pdb_file,
    target_chain: str,  # used in pandas query
    binder_chain: str,  # used in pandas query
    target_interface_residues: list[int],
    binder_interface_residues: list[int],
    only_CA: bool = True,
) -> tuple[pd.DataFrame | None, float | None, float | None, int | None]:
    """Calculate the distance matrix between the target and binder interfaces in a PDB file (complex).

    :parameter:
        complex_pdb_file (str): Path to the PDB file.
        target_interface_residues (list[int]): List of target interface residues.
        binder_interface_residues (list[int]): List of binder interface residues.
        target_chain: ID of the target chain (usually B).
        binder_chain: ID of the binder chain (usually A).
        only_CA (bool): Use only CA atoms. Default: True.
    :returns:
        Tuple with the distance matrix, average distance, average distance and number of contacts.
    """

    ppdb = PandasPdb().read_pdb(complex_pdb_file)

    assert target_interface_residues is not None, (
        f"Target interface residues must be provided, found: {target_interface_residues}"
    )
    assert binder_interface_residues is not None, (
        f"Target interface residues must be provided, found: {binder_interface_residues}"
    )

    target_interface = ppdb.df["ATOM"].query(
        "(residue_number in @target_interface_residues) & (chain_id == @target_chain)"
    )
    binder_interface = ppdb.df["ATOM"].query(
        "(residue_number in @binder_interface_residues) & (chain_id == @binder_chain)"
    )

    if only_CA:
        target_interface = target_interface.query("atom_name=='CA'")
        binder_interface = binder_interface.query("atom_name=='CA'")

    coords_target_interface = get_coords_from_ppdb(target_interface)
    coords_binder_interface = get_coords_from_ppdb(binder_interface)

    if coords_target_interface is None or coords_binder_interface is None:
        return None, None, None, 0

    # Calculate pairwise distances
    distances = distance.cdist(coords_target_interface, coords_binder_interface, metric="euclidean")

    index_target = target_interface.apply(
        lambda row: "_".join([row.residue_name, str(row.residue_number), row.atom_name, str(row.atom_number)]), axis=1
    )
    index_binder = binder_interface.apply(
        lambda row: "_".join([row.residue_name, str(row.residue_number), row.atom_name, str(row.atom_number)]), axis=1
    )

    distances_df = pd.DataFrame(distances, index=index_target, columns=index_binder)

    average_dist = distances_df.mean().mean()
    contact_distance = BACKBONE_CONTACT_DISTANCE if only_CA else SIDECHAIN_CONTACT_DISTANCE
    N_contacts = (distances < contact_distance).sum() if len(distances) else 0

    average_dist_only_contacts = distances[distances < contact_distance].mean() if N_contacts else None

    return distances_df, average_dist, average_dist_only_contacts, N_contacts


def pydssp_assign(pdb_path, chain_id: str | None, cyclic=False, tail_residues=5) -> str:
    """Return DSSP line for a PDB file using pydssp_numpy (- = loop, H = alpha-helix, E = beta-strand)"""
    C3_ALPHABET = np.array(["-", "H", "E"])
    coord = pydssp_numpy.read_pdbtext_with_checking(open(pdb_path, "r").read(), chain_id=chain_id)
    tail_residues = min(tail_residues, len(coord))
    if cyclic:
        coord = np.concatenate([coord[-tail_residues:], coord, coord[:tail_residues]], axis=0)
    # main calculation
    onehot = pydssp_numpy.assign(coord)
    if cyclic:
        onehot = onehot[tail_residues:-tail_residues]
    index = np.argmax(onehot, axis=-1)
    return "".join(list(C3_ALPHABET[index]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_csv", type=str)
    parser.add_argument("--hotspot", type=str, default=None, help="Hotspot chain-resnum(s), comma-separated")
    parser.add_argument(
        "--cyclic", action="store_true", default=False, help="Connect C and N term to form a macrocyclic peptide"
    )
    parser.add_argument(
        "--filters", type=str, default="none", help="Filters, e.g. 'N_contact_hotspots>5,pydssp_helix_percent<50'"
    )
    parser.add_argument("--filtered-output", type=str, default=None, help="Directory path to save filtered PDBs")

    options = parser.parse_args()

    if options.hotspot:
        chains, hotspots = zip(*[(chain_resnum[0], chain_resnum[1:]) for chain_resnum in options.hotspot.split(",")])
        assert set(chains) == {"B"}, (
            f"Only target chain 'B' hotspots allowed, found prefix: {set(chains)} in hotspots {options.hotspot}"
        )
        hotspots = [int(hotspot) for hotspot in hotspots]
    else:
        hotspots = None

    if os.path.isdir(options.input_path):
        paths = sorted(glob.glob(os.path.join(options.input_path, "*.pdb")))
        print(f"Reading sequences from {len(paths):,} PDBs")
    elif options.input_path.endswith((".pdb",)):
        paths = options.input_path
    else:
        raise ValueError("Input must be a directory with PDB files, or a PDB file.")

    parsed_filters = []
    for filter_str in options.filters.split(","):
        if filter_str == "none":
            continue
        comp = None
        for c in [">=", "<=", ">", "<", "="]:
            if c in filter_str:
                comp = c
                break
        if not comp:
            raise ValueError(f"Invalid filter: {filter_str}")
        field, value = filter_str.split(comp)
        field = field.strip()
        value = value.strip()
        try:
            value = float(value)
        except ValueError:
            pass
        parsed_filters.append((field, comp, value))

    if parsed_filters:
        assert options.filtered_output, "--filtered-output directory must be provided when using filters"

    scores = get_all_metrics(paths, hotspots=hotspots, cyclic=options.cyclic)

    df = pd.DataFrame(scores).T.rename_axis("id")

    if options.filtered_output:
        if not os.path.exists(options.filtered_output):
            os.makedirs(options.filtered_output)
        passed_per_design = {}
        passed_per_filter_per_design = {}
        for path in paths:
            pdb_name = os.path.basename(path).removesuffix(".pdb")
            passed = True
            if parsed_filters:
                row = df.loc[pdb_name]
                for field, comp, value in parsed_filters:
                    passed_field = True
                    if field not in row.index:
                        raise ValueError(f"Filter field {field} not found in metrics: {', '.join(row.index.tolist())}")
                    if comp == ">":
                        if pd.isna(row[field]) or not row[field] > value:
                            passed_field = False
                    elif comp == "<":
                        if pd.isna(row[field]) or not row[field] < value:
                            passed_field = False
                    elif comp == ">=":
                        if pd.isna(row[field]) or not row[field] >= value:
                            passed_field = False
                    elif comp == "<=":
                        if pd.isna(row[field]) or not row[field] <= value:
                            passed_field = False
                    elif comp == "=":
                        if not row[field] == value:
                            passed_field = False
                    else:
                        raise ValueError(f"Invalid comparison operator: {comp}")

                    if not passed_field:
                        passed = False

                    key = f"{field}{comp}{value}"
                    if key not in passed_per_filter_per_design:
                        passed_per_filter_per_design[key] = {}
                    passed_per_filter_per_design[key][pdb_name] = passed_field

            passed_per_design[pdb_name] = passed
            if passed:
                # link path
                os.symlink(os.path.abspath(path), os.path.join(options.filtered_output, pdb_name + ".pdb"))

        if parsed_filters:
            df["passed_filters"] = pd.Series(passed_per_design)
            print(f"all filters passed by {df.passed_filters.mean():.2%} designs")
            for key, vals in passed_per_filter_per_design.items():
                df[key] = pd.Series(vals)
                print(f"{key} passed by {df[key].mean():.2%} designs")
        df.to_csv(options.output_csv)
        print("Saved metrics to:", options.output_csv)
        print("Saved filtered PDBs to:", options.output_csv)
