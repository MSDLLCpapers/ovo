import glob
import os
import time
import numpy as np
import argparse
from colabdesign import mk_af_model
from colabdesign.af.alphafold.common import protein
import json
import jax


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
    parser.add_argument("--blind", action="store_true", default=False, help="Do NOT use AlphaFold initial guess")
    parser.add_argument(
        "--multimer", action="store_true", default=False, help="Use AlphaFold multimer model (default = monomer)"
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
    options = parser.parse_args()

    if options.blind:
        assert not options.use_binder_template, "Cannot use both --blind and --use-binder-template"
        assert not options.use_interface_template, "Cannot use both --blind and --use-interface-template"

    if options.use_interface_template:
        assert options.use_binder_template, "--use-interface-template requires --use-binder-template"

    model = mk_af_model(
        protocol="binder",
        data_dir=options.params,
        use_multimer=options.multimer,
        model_names=["model_1_multimer_v3" if options.multimer else "model_1_ptm"],
        use_initial_guess=not options.blind,
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

    os.makedirs(options.output_name, exist_ok=True)
    with open(options.output_name.rstrip("/") + ".jsonl", "wt") as f:
        for i, path in enumerate(paths, start=1):
            basename = os.path.basename(path).removesuffix(".pdb")
            print(f"Predicting PDB {i:,}/{len(paths):,}: {basename}")
            start_time = time.time()
            model.prep_inputs(
                path,
                # TODO add support for multiple target or binder chains
                # We can take inspiration from here: https://github.com/sokrypton/ColabDesign/blob/4127b5ab889f5b62a56644d3d1cbdd5cb313a0d0/colabdesign/rf/refolding_test.py#L87-L98
                # A comma-separated list can be passed here
                binder_chain="A",
                target_chain="B",
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
            metrics["ipae"] = metrics["ipae"] * 31.0
            metrics["time"] = time.time() - start_time
            ca_pos = model.aux["atom_positions"][:, 1]  # 1 = CA index
            ca_dist = np.sqrt(
                np.square(ca_pos[model._target_len :, None] - ca_pos[None, : model._target_len]).sum(axis=-1) + 1e-8
            )
            target_interface_res = model.aux["residue_index"][: model._target_len][ca_dist.min(axis=0) <= 8]
            metrics["interface_target_residues"] = ",".join(f"B{pos}" for pos in target_interface_res)
            metrics_str = " | ".join(f"{k} = {v:.2f}" for k, v in metrics.items() if isinstance(v, float))
            print(" Prediction done in {:.1f}s | {}".format(metrics["time"], metrics_str))
            json.dump(metrics, f)
            f.write("\n")
            f.flush()
            suffix = os.path.basename(options.output_name.rstrip("/"))
            save_binder_design_pdb(model, os.path.join(options.output_name, f"{basename}_{suffix}.pdb"))
