#!/usr/bin/env python3
"""Convert RFdiffusion3 output .cif.gz files to standardized PDB format.

Applies the same chain/residue conventions as rfdiffusion-backbone/standardize_pdb.py:
  - Designed (new) chains -> chain A, B, ... (renumbered from 1)
  - Fixed (input) chains  -> next available letters (original residue numbers preserved)

REMARK lines are added for contig, hotspot, and chain provenance.
"""

import argparse
import glob
import gzip
import json
import os
import re
import tempfile

import gemmi

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parse_fixed_chain_ids(contig_v3: str) -> set:
    """Extract fixed chain IDs from a v3 contig string.

    Fixed segments are those prefixed with a chain letter (e.g. 'E6-155', 'A30-40').
    Designed segments have no chain prefix (e.g. '40-120', '10').
    """
    fixed = set()
    for seg in re.split(r",", contig_v3):
        seg = seg.strip()
        if not seg or seg == "/0":
            continue
        if seg[0].isupper():
            fixed.add(seg[0])
    return fixed


def has_chain_break(contig_v3: str) -> bool:
    return "/0" in contig_v3


def build_standardized_contig_v1(input_contig_v1: str, model: gemmi.Model, chain_rename: dict, fixed_chain_ids: set) -> str:
    """Build v1-style standardized contig for the REMARK header.

    prepare_json.py (LigandMPNN) expects v1 format: segments separated by '/',
    designed segments as 'N-N', fixed segments as 'ChainStart-End'.
    Space-separated groups for multi-chain (binder) designs.

    Scaffold (no chain break): parse input v1 segments sequentially, simulate residue numbering.
    Binder (has chain break): per-chain — designed chains get 'N-N', fixed chains get 'ChainX-Y'.
    """
    contig_has_break = "/0" in input_contig_v1 or (
        " " in input_contig_v1.strip() and any(c.isdigit() for c in input_contig_v1.split()[1][:1])
    )

    if not contig_has_break:
        return _scaffold_standardized_contig(input_contig_v1, model)
    else:
        return _binder_standardized_contig(model, chain_rename, fixed_chain_ids)


def _scaffold_standardized_contig(input_contig_v1: str, model: gemmi.Model) -> str:
    """Scaffold: one chain with interleaved fixed/designed segments."""
    chain = list(model)[0]
    total_residues = len(list(chain.first_conformer()))
    new_chain_letter = chain.name

    segs = [s.strip() for s in input_contig_v1.split("/") if s.strip()]

    # Compute fixed residue counts and designed segment specs
    total_fixed = 0
    total_known_designed = 0
    n_range_segs = 0
    for s in segs:
        if s[0].isalpha():
            m = re.match(r"[A-Z](\d+)(?:-(\d+))?", s)
            start, end = int(m.group(1)), int(m.group(2)) if m.group(2) else int(m.group(1))
            total_fixed += end - start + 1
        else:
            parts = s.split("-")
            if len(parts) == 1:
                total_known_designed += int(s)
            else:
                n_range_segs += 1

    remaining_for_ranges = total_residues - total_fixed - total_known_designed

    seg_strs = []
    for s in segs:
        if s[0].isalpha():
            # Fixed: preserve original residue numbers so downstream AF2 can look them up in native PDB
            m = re.match(r"([A-Z])(\d+(?:-\d+)?)", s)
            seg_strs.append(f"{new_chain_letter}{m.group(2)}")
        else:
            parts = s.split("-")
            if len(parts) == 1:
                count = int(s)
            else:
                count = remaining_for_ranges // max(n_range_segs, 1)
            seg_strs.append(f"{count}-{count}")

    return "/".join(seg_strs)


def _binder_standardized_contig(model: gemmi.Model, chain_rename: dict, fixed_chain_ids: set) -> str:
    """Binder: designed chains get 'N-N', fixed chains get 'ChainX-Y'."""
    old_for_new = {v: k for k, v in chain_rename.items()}
    parts = []
    for chain in model:
        n = len(list(chain.first_conformer()))
        old_name = old_for_new.get(chain.name, chain.name)
        if old_name not in fixed_chain_ids:
            parts.append(f"{n}-{n}")
        else:
            parts.append(f"{chain.name}1-{n}")
    return " ".join(parts)


def chunk_string(s: str, chunk_size: int = 40) -> list:
    if not s:
        return []
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def read_cif_gz(path: str) -> gemmi.Structure:
    """Read a .cif.gz file into a gemmi Structure."""
    if path.endswith(".gz"):
        with gzip.open(path, "rb") as f:
            content = f.read()
        with tempfile.NamedTemporaryFile(suffix=".cif", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            structure = gemmi.read_structure(tmp_path)
        finally:
            os.unlink(tmp_path)
    else:
        structure = gemmi.read_structure(path)
    return structure


def rename_chains(model: gemmi.Model, mapping: dict):
    """Rename chains in-place using a temp-name pass to avoid mid-rename conflicts."""
    # First pass: rename to temp names (prefixed with '~') to avoid collisions
    temp_to_final = {}
    for chain in model:
        if chain.name in mapping:
            temp = f"~{chain.name}"
            temp_to_final[temp] = mapping[chain.name]
            chain.name = temp
    # Second pass: rename from temp to final
    for chain in model:
        if chain.name in temp_to_final:
            chain.name = temp_to_final[chain.name]


def renumber_chain_from_one(chain: gemmi.Chain):
    """Renumber all residues in a chain consecutively starting from 1."""
    for i, residue in enumerate(chain, start=1):
        residue.seqid = gemmi.SeqId(i, " ")


def standardize(
    cif_gz_path: str,
    spec_json_path: str,
    output_pdb_path: str,
    input_contig_v1: str,
    hotspot: str,
):
    """Convert a single .cif.gz to a standardized PDB with REMARK annotations."""
    # Load input spec JSON to get the v3 contig
    with open(spec_json_path) as f:
        spec_data = json.load(f)
    first_spec = list(spec_data.values())[0] if spec_data else {}
    contig_v3 = first_spec.get("contig", "")

    fixed_chain_ids = parse_fixed_chain_ids(contig_v3)

    # Read CIF.gz
    structure = read_cif_gz(cif_gz_path)
    structure.setup_entities()
    model = structure[0]

    # Classify output chains as designed (not in fixed set) or fixed
    all_chain_names = [chain.name for chain in model]
    designed_chains = [c for c in all_chain_names if c not in fixed_chain_ids]
    fixed_chains = [c for c in all_chain_names if c in fixed_chain_ids]

    # Build rename mapping: designed first -> A, B, ...; fixed after
    chain_rename = {}
    idx = 0
    for c in designed_chains:
        chain_rename[c] = ALPHABET[idx]
        idx += 1
    for c in fixed_chains:
        chain_rename[c] = ALPHABET[idx]
        idx += 1

    # Renumber designed chains from 1 before renaming (so we operate on original names)
    for chain in model:
        if chain.name in designed_chains:
            renumber_chain_from_one(chain)

    # Rename chains
    rename_chains(model, chain_rename)

    # Standardize hotspots (remap chain letters using the rename mapping)
    std_hotspots = ""
    if hotspot:
        parts = []
        for res in hotspot.split(","):
            res = res.strip()
            if res and res[0].isalpha():
                old_chain = res[0]
                new_chain = chain_rename.get(old_chain, old_chain)
                parts.append(new_chain + res[1:])
            else:
                parts.append(res)
        std_hotspots = ",".join(parts)

    # New chain order for REMARK
    new_chain_order = [chain_rename.get(c, c) for c in all_chain_names]
    chains_str = " ".join(new_chain_order)

    # Build v1-style standardized contig (required by downstream prepare_json.py)
    std_contig_v1 = build_standardized_contig_v1(input_contig_v1, model, chain_rename, fixed_chain_ids)

    # Write PDB
    os.makedirs(os.path.dirname(output_pdb_path) or ".", exist_ok=True)
    structure.write_pdb(output_pdb_path)

    # Build REMARK lines — single space after 'REMARK   1' (required by prepare_json.py parser)
    remarks = []
    display_contig = input_contig_v1 if input_contig_v1 else contig_v3
    for chunk in chunk_string(display_contig):
        remarks.append(f'REMARK   1 Input contig: "{chunk}"')
    for chunk in chunk_string(std_contig_v1):
        remarks.append(f'REMARK   1 Standardized contig: "{chunk}"')
    for chunk in chunk_string(chains_str):
        remarks.append(f'REMARK   1 Chains: "{chunk}"')
    if hotspot:
        for chunk in chunk_string(hotspot):
            remarks.append(f'REMARK   1 Input hotspots: "{chunk}"')
        for chunk in chunk_string(std_hotspots):
            remarks.append(f'REMARK   1 Standardized hotspots: "{chunk}"')
    else:
        remarks.append("REMARK   1 Input hotspots: ")
        remarks.append("REMARK   1 Standardized hotspots: ")

    # Prepend REMARK lines to the PDB file
    with open(output_pdb_path) as f:
        pdb_content = f.read()
    with open(output_pdb_path, "w") as f:
        f.write("\n".join(remarks) + "\n")
        f.write(pdb_content)


def main():
    parser = argparse.ArgumentParser(description="Standardize RFdiffusion3 CIF.gz outputs to PDB")
    parser.add_argument("--cif_dir", type=str, required=True, help="Directory with .cif.gz files")
    parser.add_argument("--spec_json", type=str, required=True, help="Input spec JSON (from build_input_json.py)")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for standardized PDBs")
    parser.add_argument("--input_contig", type=str, default="", help="Original v1-style contig for REMARK lines")
    parser.add_argument("--hotspot", type=str, default="", help="Hotspot residues for REMARK lines")
    args = parser.parse_args()

    cif_files = sorted(glob.glob(os.path.join(args.cif_dir, "*.cif.gz")))
    if not cif_files:
        print(f"WARNING: No .cif.gz files found in {args.cif_dir}")
        return

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Standardizing {len(cif_files)} CIF files -> {args.output_dir}")

    for cif_path in cif_files:
        basename = os.path.basename(cif_path)
        # Strip .cif.gz -> _standardized.pdb
        stem = basename.replace(".cif.gz", "")
        output_pdb = os.path.join(args.output_dir, f"{stem}_standardized.pdb")
        print(f"  {basename} -> {os.path.basename(output_pdb)}")
        standardize(
            cif_gz_path=cif_path,
            spec_json_path=args.spec_json,
            output_pdb_path=output_pdb,
            input_contig_v1=args.input_contig,
            hotspot=args.hotspot,
        )

    print(f"Saved {len(cif_files)} standardized PDBs to {args.output_dir}")


if __name__ == "__main__":
    main()
