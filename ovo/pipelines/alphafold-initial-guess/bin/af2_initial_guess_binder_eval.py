import glob
import os
import time
import numpy as np
import argparse
from colabdesign import mk_af_model
from colabdesign.af.alphafold.common import protein
import json
import jax
from Bio import PDB
from io import StringIO


def add_cyclic_offset(self, offset_type=2):
    """add cyclic offset to connect N and C term"""

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


# adopted from colabdesign save_pdb
def save_binder_design_pdb(self, filename=None, get_best=True):
    """
    save pdb coordinates (if filename provided, otherwise return as string)
    - set get_best=False, to get the last sampled sequence

    saves binder as chain A, renumbered consecutively from 1
      and target as chain B, with original residue numbering from the input PDB
    """
    aux = self._tmp["best"]["aux"] if (get_best and "aux" in self._tmp["best"]) else self.aux
    aux = aux["all"]

    p = {k: aux[k] for k in ["aatype", "residue_index", "atom_positions", "atom_mask"]}
    p["b_factors"] = 100 * p["atom_mask"] * aux["plddt"][..., None]

    for k, v in p.items():
        assert p[k].shape[1] == self._target_len + self._binder_len, (
            f"Expected {self._target_len} + {self._binder_len} residues, got {p[k].shape[1]} in {k}"
        )
        # flip target and binder positions to have binder first (chain A) and target second (chain B)
        p[k] = np.concatenate([p[k][:, self._target_len :], p[k][:, : self._target_len]], axis=1)

    def to_pdb_str(x, n=None):
        p_str = protein.to_pdb(protein.Protein(**x))

        # mapping original residue index -> new residue index
        binder_mapping = dict(zip(x["residue_index"][: self._binder_len], range(1, self._binder_len + 1)))

        lines = []
        for line in p_str.splitlines()[1:-2]:
            if line.startswith(("ATOM", "HETATM")):
                resno = int(line[22:26].strip())
                if resno in binder_mapping:
                    lines.append(line[:21] + "A" + str(binder_mapping[resno]).rjust(4) + line[26:])
                else:
                    lines.append(line[:21] + "B" + line[22:])
        lines.append("")
        p_str = "\n".join(lines)
        if n is not None:
            p_str = f"MODEL{n:8}\n{p_str}\nENDMDL\n"
        return p_str

    p_str = ""
    for n in range(p["atom_positions"].shape[0]):
        p_str += to_pdb_str(jax.tree_util.tree_map(lambda x: x[n], p), n + 1)
    p_str += "END\n"

    if filename is None:
        return p_str
    else:
        with open(filename, "w") as f:
            f.write(p_str)


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
    "rmsd": "target_aligned_binder_rmsd",
    "plddt": "binder_plddt",  # 0-100
    "pae": "binder_pae",  # pAE of binder chain
    "ptm": "ptm",  # predicted TM score of the whole binder-target complex, largely depending on target (0 = worst, 1 = best)
    "con": "con_loss",  # intramolecular contacts loss of each binder residue to 2 nearest neighbors (by default) within the chain, excluding immediate sequence neighbours
    "i_pae": "ipae",
    "i_ptm": "iptm",  # interaction predicted TM score (0 = worst, 1 = best)
    "i_con": "i_con_loss",  # intermolecular contacts loss of each binder residue to 1 nearest neighbor (by default) in the target chain, limited to the target hotspot if specified
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str)
    parser.add_argument("output_name", type=str)
    parser.add_argument("--params", required=True, type=str, help="Path to AlphaFold2 parameter data dir")
    parser.add_argument(
        "--num-recycles", type=int, default=3, help="Number of AlphaFold2 recycles (0, 1, 2, 3, ..., default 1)"
    )
    parser.add_argument(
        "--use-binder-template",
        action="store_true",
        default=False,
        help="Include binder structure as in initial guess template",
    )
    parser.add_argument(
        "--use-interface-template",
        action="store_true",
        default=False,
        help="Include target-binder as single structure in initial guess template to inform about their interface",
    )
    parser.add_argument(
        "--no-initial-guess", "--blind", action="store_true", default=False, help="Do NOT use AlphaFold initial guess"
    )
    parser.add_argument(
        "--no-templates", action="store_true", default=False, help="Do NOT use templates for target or binder"
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
        help="Add cyclic offset to connect N and C term in binder (chain A)",
    )
    parser.add_argument(
        "--hotspot",
        default=None,
        help="Target hotspot positions - used only to compute contact loss metric (i_con), comma-separated",
    )
    parser.add_argument(
        "--binder-alone",
        action="store_true",
        default=False,
        help="Predict only the binder structure, without the target",
    )
    options = parser.parse_args()

    if options.no_templates:
        assert not options.use_binder_template, "Cannot use both --no-templates and --use-binder-template"
        assert not options.use_interface_template, "Cannot use both --no-templates and --use-interface-template"

    if options.use_interface_template:
        assert options.use_binder_template, "--use-interface-template requires --use-binder-template"

    model = mk_af_model(
        protocol="fixbb" if options.binder_alone else "binder",
        data_dir=options.params,
        use_multimer=options.multimer,
        model_names=["model_1_multimer_v3" if options.multimer else "model_1_ptm"],
        use_initial_guess=not options.no_initial_guess,
        use_templates=not options.no_templates,
    )
    paths = sorted(glob.glob(os.path.join(options.input_dir, "*.pdb")))
    print(f"Getting sequence lengths from {len(paths):,} PDBs")

    total_lengths = {}
    for pdb_path in paths:
        total_lengths[pdb_path] = get_pdb_total_length(pdb_path)

    if (num_distinct_lengths := len(set(total_lengths.values()))) > 1:
        print(f"Processing {len(paths)} PDBs with {num_distinct_lengths} distinct lengths.")
        print("Each length change will cause a spike in AF2 duration!")
    else:
        print(f"Processing {len(paths)} PDBs with identical lengths. This is optimal for AF2.")

    # sort paths by total sequence length
    # to avoid spikes in duration caused by changes in input length
    paths = sorted(paths, key=lambda p: total_lengths[p])

    if options.binder_alone:
        # binder alone RMSD is computed from the design and predicted PDB files instead
        METRICS = {old_key: new_key for old_key, new_key in METRICS.items() if old_key != "rmsd"}

    os.makedirs(options.output_name, exist_ok=True)
    with open(options.output_name.rstrip("/") + ".jsonl", "wt") as f:
        for i, path in enumerate(paths, start=1):
            basename = os.path.basename(path).removesuffix(".pdb")
            print(f"Predicting PDB {i:,}/{len(paths):,}: {basename}")
            start_time = time.time()
            if options.binder_alone:
                model.prep_inputs(
                    path,
                    chain=options.designed_chains,
                )
            else:
                if options.designed_chains == "A":
                    target_chain = "B"
                elif options.designed_chains == "B":
                    target_chain = "A"
                else:
                    raise NotImplementedError("Expected binder chain to be A or B")
                model.prep_inputs(
                    path,
                    # TODO add support for multiple target or binder chains
                    # We can take inspiration from here: https://github.com/sokrypton/ColabDesign/blob/4127b5ab889f5b62a56644d3d1cbdd5cb313a0d0/colabdesign/rf/refolding_test.py#L87-L98
                    # A comma-separated list can be passed here
                    binder_chain=options.designed_chains,
                    target_chain=target_chain,
                    rm_target=False,
                    rm_binder=not options.use_binder_template,
                    rm_template_ic=not options.use_interface_template,
                    # Hotspots are used for connectivity loss
                    # NOTE that rfdiffusion renumbers the target chain from 1 so you need to recalculate the position numbers
                    hotspot=options.hotspot if options.hotspot else None,
                )
            if options.cyclic:
                add_cyclic_offset(model, offset_type=2)
            model.set_seq(mode="wildtype")
            model.set_opt(num_recycles=options.num_recycles)
            model.predict(num_models=1, verbose=False)
            metrics = {"id": basename}
            metrics.update({new_key: model.aux["log"].get(old_key) for old_key, new_key in METRICS.items()})
            metrics["binder_plddt"] *= 100
            metrics["binder_pae"] = (
                metrics["binder_pae"] * 31.0
            )  # de-normalization of https://github.com/sokrypton/ColabDesign/blob/4c0bc6d67f8f967135ecccc135a26b3bfded25e8/colabdesign/af/loss.py#L252
            suffix = os.path.basename(options.output_name.rstrip("/"))
            out_path = os.path.join(options.output_name, f"{basename}_{suffix}.pdb")
            if options.binder_alone:
                predicted_pdb_str = model.save_pdb()
                with open(out_path, "wt") as pdb_f:
                    pdb_f.write(predicted_pdb_str)
                with open(path) as design_f:
                    design_pdb_str = design_f.read()
                print("Computing binder alone RMSD")
                # the prediction contains the designed chain only (saved as chain A by colabdesign),
                # so the whole predicted structure is aligned to the designed chain of the input PDB
                binder_alone_mappings = [
                    [(chain, None) for chain in options.designed_chains.split(",")],
                    None,
                ]
                metrics["binder_alone_bb_rmsd"] = align_multiple_proteins_pdb(
                    pdb_strs=[design_pdb_str, predicted_pdb_str],
                    chain_residue_mappings=binder_alone_mappings,
                    all_atom=False,
                )
                metrics["binder_alone_aa_rmsd"] = align_multiple_proteins_pdb(
                    pdb_strs=[design_pdb_str, predicted_pdb_str],
                    chain_residue_mappings=binder_alone_mappings,
                    all_atom=True,
                )
            else:
                save_binder_design_pdb(model, out_path)
                metrics["ipae"] = metrics["ipae"] * 31.0
                ca_pos = model.aux["atom_positions"][:, 1]  # 1 = CA index
                ca_dist = np.sqrt(
                    np.square(ca_pos[model._target_len :, None] - ca_pos[None, : model._target_len]).sum(axis=-1) + 1e-8
                )
                target_interface_res = model.aux["residue_index"][: model._target_len][ca_dist.min(axis=0) <= 8]
                metrics["interface_target_residues"] = ",".join(f"B{pos}" for pos in target_interface_res)
            metrics["time"] = time.time() - start_time
            metrics_str = " | ".join(f"{k} = {v:.2f}" for k, v in metrics.items() if isinstance(v, float))
            print(" Prediction done in {:.1f}s | {}".format(metrics["time"], metrics_str))
            json.dump(metrics, f)
            f.write("\n")
            f.flush()
