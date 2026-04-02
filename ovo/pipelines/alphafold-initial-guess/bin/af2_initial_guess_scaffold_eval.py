import glob
import os
import time
import argparse
from colabdesign import mk_af_model
import json

import numpy as np
from Bio import PDB
from io import StringIO


REMARK_KEYS = ["Input contig", "Standardized contig", "Chains", "Input hotspots", "Standardized hotspots"]


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


def parse_remark_lines(stripped_remark_lines: list[str]) -> dict[str, str]:
    """
    :param stripped_remark_lines:
        str, lines from the PDB file header, stripped of the "REMARK   1" prefix
    :return: dict, parsed remarks: {
       "Input contig": "A45-46/10-15/A45-46/0 B24-26/5/B24-26/0 C10-20",
       "Standardized contig": "A45-46/13-13/A45-46/0 B24-26/5-5/B24-26/0 C10-20/0",
       "Chains": "A B C",
       ...
    }

    Example: example header to read
        REMARK   1 Input contig: "A45-46/10-15/A45-46/0 B24-26/5/B24-"
        REMARK   1 Input contig: "26/0 C10-20"
        REMARK   1 Standardized contig: "A45-46/13-13/A45-46/0 B24-26/5-5/B24-26/"
        REMARK   1 Standardized contig: "0 C10-20/0"
        REMARK   1 Chains: "A B C"
        REMARK   1 Input hotspots:
        REMARK   1 Standardized hotspots:
    """

    parsed_remark = {}
    for key in REMARK_KEYS:
        # Get lines that begin with this key
        remark_lines = [line.removeprefix(f"{key}:").strip() for line in stripped_remark_lines if line.startswith(key)]
        if not remark_lines and key not in ["Input hotspots", "Standardized hotspots"]:
            raise ValueError(f"Missing REMARK line for key: {key}")

        values = []
        for line in remark_lines:
            if not line and key not in ["Input hotspots", "Standardized hotspots"]:
                raise ValueError("Empty JSON value after key")
            if not line and key in ["Input hotspots", "Standardized hotspots"]:
                continue

            values.append(json.loads(line))

        parsed_remark[key] = "".join(values)

    return parsed_remark


def get_designed_residues_mask(
    remark_dict: dict[str, str],
) -> tuple[list[tuple[str, list[int]]], list[tuple[str, list[int]]], list[str]]:
    """
    Get the designed residues from the PDB file (True = designed, False = fixed)
    :Arg:
        remark_dict: dict, parsed remarks
    :Return:
        input_motif_residues: residue numbers of fixed regions in the input PDB (source motif),
                              for this input contig: 'A123-124/5/A10-11/5/B1-2
                              returns: [('A', [123, 124]), ('A', [10, 11]), ('B', [1, 2])]
        output_motif_residues: same as input_motif_residues, but with respect to the initial guess output PDB
        designed_residues: list[str], designed residues in the format [True, True, False, False, ...]
    """

    contigs_str = remark_dict.get("Standardized contig", None)
    chains_str = remark_dict.get("Chains", None)
    assert contigs_str, "No Standardized contigs found."
    assert chains_str, "No Standardized contigs found."

    contig_chains = contigs_str.split(" ")
    chains = chains_str.split(" ")

    assert len(contig_chains) == len(chains), (
        f"Number of contigs and chains do not match: {len(contig_chains)} != {len(chains)}"
    )

    input_motif_residues = []
    output_motif_residues = []
    designed_residues_mask = []
    for output_chain_id, contig_chain in zip(chains, contig_chains):
        segments = contig_chain.removesuffix("/0").split("/")
        is_fixed_chain = all(segment[0].isalpha() for segment in segments)
        standard_res = 1
        first_input_res = None
        for segment in segments:
            if not segment[0].isalpha():
                # designed segment
                start_len, end_len = map(int, segment.split("-"))
                assert start_len == end_len, (
                    f"Start len and end len of design segment should coincide: "
                    f"{start_len} != {end_len} in {contig_chain} "
                )
                designed_residues_mask.extend([True] * start_len)
                standard_res += start_len
            else:
                # fixed segment
                input_chain_id = segment[0]
                start, end = map(int, segment[1:].split("-"))
                if first_input_res is None:
                    first_input_res = start
                length = end - start + 1
                input_numbering = list(range(start, end + 1))
                standard_numbering = list(range(standard_res, standard_res + length))
                input_motif_residues.append((input_chain_id, input_numbering))

                # TODO enable this when we add standardization to initial guess output PDB
                # our standardization procedure will keep original numbering if there are no designed segments
                # so use input numbering for those chains, otherwise use consecutive numbering from 1
                #
                # output_motif_residues.append((output_chain_id, input_numbering if is_fixed_chain else standard_numbering))
                # AF2 starts numbering from 1, but then preserves the chain breaks
                af2_numbering = [r - first_input_res + 1 for r in input_numbering]
                output_motif_residues.append((output_chain_id, af2_numbering if is_fixed_chain else standard_numbering))

                designed_residues_mask.extend([False] * length)
                standard_res += length

    return input_motif_residues, output_motif_residues, designed_residues_mask


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

        for chain_id, residues in mappings:
            coords, res_final = get_atom_coordinates(structure, chain_id, residues, all_atom=all_atom)
            if coords:
                structure_coords.extend(coords)
                structure_residues.extend(res_final)
            else:
                raise ValueError(f"No atoms found in structure {i + 1} for chain {chain_id} and residues {residues}")

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


def get_pdb_total_length(pdb_path):
    unique_residues = set()

    with open(pdb_path, "r") as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                chain_id = line[21].strip()
                res_num = line[22:26].strip()
                ins_code = line[26].strip()  # column 27
                unique_residues.add((chain_id, res_num, ins_code))

    return len(unique_residues)


METRICS = {
    "rmsd": "design_backbone_rmsd",  # aligned RMSD of full structure
    "plddt": "plddt",  # 0-100
    "pae": "pae",  # predicted aligned error
    "ptm": "ptm",  # predicted TM score (0 = worst, 1 = best)
    "con": "intra_con_loss",  # intramolecular contacts loss of each residue to 2 nearest neighbors (by default) within the chain, excluding immediate sequence neighbours
    # in case of multi-chain scaffold designs
    "i_pae": "ipae",
    "i_ptm": "iptm",  # predicted interface TM score (0 = worst, 1 = best)
    "i_con": "icon_loss",  # intermolecular contacts loss of each residue to 1 nearest neighbor (by default) in another chain
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str)
    parser.add_argument("output_name", type=str)
    parser.add_argument("--native-pdb", required=False, type=str, help="Path to native PDB structure")
    parser.add_argument("--params", required=True, type=str, help="Path to AlphaFold2 parameter data dir")
    parser.add_argument(
        "--num-recycles", type=int, default=3, help="Number of AlphaFold2 recycles (0, 1, 2, 3, ..., default 1)"
    )
    parser.add_argument(
        "--no-templates", action="store_true", default=False, help="Do NOT use templates for fixed regions"
    )
    parser.add_argument(
        "--multimer", action="store_true", default=False, help="Use AlphaFold multimer model (default = monomer)"
    )
    parser.add_argument(
        "--designed_chains",
        default="A",
        help="Designed chain ID or comma-separated list of designed chain IDs. Here, we design the binder. Default: 'A'.",
    )
    options = parser.parse_args()

    model = mk_af_model(
        protocol="fixbb",
        data_dir=options.params,
        use_templates=not options.no_templates,
        use_multimer=options.multimer,
        use_initial_guess=True,
    )
    paths = sorted(glob.glob(os.path.join(options.input_dir, "*.pdb")))
    print(f"Getting info from {len(paths):,} PDBs")

    remark_lines_by_pdb_path = {}
    total_lengths = {}
    for pdb_path in paths:
        _, remark_lines = get_remark_header(pdb_path)
        if not remark_lines and (not options.no_templates or options.native_pdb):
            raise ValueError(
                f"When running with --native-pdb or with templates, "
                f'this script requires a "standardized" PDB output with the REMARK header '
                f"(as produced by the ovo rfdiffusion-backbone workflow), "
                f"no header found in: {pdb_path}"
            )
        remark_lines_by_pdb_path[pdb_path] = remark_lines
        total_lengths[pdb_path] = get_pdb_total_length(pdb_path)

    if (num_distinct_lengths := len(set(total_lengths.values()))) > 1:
        print(f"Processing {len(paths)} PDBs with {num_distinct_lengths} distinct lengths.")
        print("Each length change will cause a spike in AF2 duration!")
    else:
        print(f"Processing {len(paths)} PDBs with identical lengths. This is optimal for AF2.")

    # sort paths by total sequence length
    # to avoid spikes in duration caused by changes in input length
    paths = sorted(paths, key=lambda p: total_lengths[p])

    if options.native_pdb:
        print(os.getcwd())
        with open(options.native_pdb, "r") as pdb_f:
            native_pdb_str = pdb_f.read()
    else:
        native_pdb_str = None

    os.makedirs(options.output_name, exist_ok=True)
    with open(options.output_name.rstrip("/") + ".jsonl", "wt") as f:
        for i, path in enumerate(paths, start=1):
            basename = os.path.basename(path).removesuffix(".pdb")
            print(f"Predicting PDB {i:,}/{len(paths):,}: {basename}")
            rm_template = False  # note that when options.no_templates=True, templates are already disabled above using use_templates=False
            input_motif_residues = None
            output_motif_residues = None
            chain = (
                options.designed_chains
            )  # default to using whole structure as template, if templates are enabled and no REMARK header is found
            if not options.no_templates or native_pdb_str:
                remark_lines = remark_lines_by_pdb_path[path]
                remark_dict = parse_remark_lines(remark_lines)
                input_motif_residues, output_motif_residues, designed_residues_mask = get_designed_residues_mask(
                    remark_dict
                )
                rm_template = designed_residues_mask
                chain = ",".join(remark_dict["Chains"].split())
            if not options.no_templates:
                print(
                    f"Including template for {len(designed_residues_mask) - sum(designed_residues_mask)} fixed residues"
                )
            else:
                print("Not including template")
            start_time = time.time()
            model.prep_inputs(
                path,
                chain=chain,
                rm_template=rm_template,
            )
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
                print("Predicting native motif RMSD")
                print("  Input mapping:", input_motif_residues)
                print(" Output mapping:", output_motif_residues)
                metrics["native_motif_rmsd"] = align_multiple_proteins_pdb(
                    pdb_strs=[native_pdb_str, predicted_pdb_str],
                    chain_residue_mappings=[input_motif_residues, output_motif_residues],
                    all_atom=True,
                )
            metrics["time"] = time.time() - start_time
            metrics_str = " | ".join(f"{k} = {v:.2f}" for k, v in metrics.items() if isinstance(v, float))
            print(" Prediction done in {:.1f}s | {}".format(metrics["time"], metrics_str))
            json.dump(metrics, f)
            f.write("\n")
            f.flush()
