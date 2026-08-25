#!/usr/bin/env python3
"""Convert RFdiffusion3 output .cif.gz files to standardized PDB format.

Applies the same chain/residue conventions as rfdiffusion-backbone/standardize_pdb.py:
  - Designed (new) chains -> chain A, B, ... (renumbered from 1)
  - Fixed (input) chains  -> next available letters (original residue numbers preserved)

REMARK lines are added for contig, hotspot, and chain provenance.
"""

import argparse
import glob
import json
import os
import sys
import itertools

import gemmi

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def get_standardized_contig(diffused_index_map: dict[str, str], sampled_contig: str):
    """Get contig where the order of segments corresponds to order in the structure"""
    # get chain lengths from sampled_contig
    sampled_contig_positions = sampled_contig.split(",")
    chain_lengths = [0]
    # output chain -> output residue index -> fixed input position (for verification below)
    verify_positions = {"A": {}}
    chain = "A"
    for pos in sampled_contig_positions:
        if pos == "/0":
            chain_lengths.append(0)
            chain = chr(ord(chain) + 1)
            verify_positions[chain] = {}
        elif pos[0].isnumeric():
            # Remove modality suffix if present (P = protein, R = RNA, D = DNA)
            pos = pos.removesuffix("P").removesuffix("R").removesuffix("D")
            chain_lengths[-1] += int(pos)
        else:
            assert pos[0].isalpha() and "-" not in pos, f"Expected format 123 or A123, got: {pos} in {sampled_contig}"
            chain_lengths[-1] += 1
            verify_positions[chain][chain_lengths[-1]] = pos
    # output chain -> output pos -> metadata
    mapping_by_chain = {}
    chain = "A"
    for length in chain_lengths:
        # prefill all positions as generated
        mapping_by_chain[chain] = {f"{chain}{p}": {"fixed": False} for p in range(1, length + 1)}
        # add metadata for fixed positions
        for input_pos, output_pos in diffused_index_map.items():
            if output_pos[0] == chain:
                mapping_by_chain[chain][output_pos] = {"fixed": True, "input_pos": input_pos}
        # verify that all fixed positions from sampled_contig exist in diffused_index_map
        for output_index, expected_pos in verify_positions[chain].items():
            input_pos = mapping_by_chain[chain].get(f"{chain}{output_index}", {}).get("input_pos")
            assert expected_pos == input_pos, (
                f"Expected fixed {expected_pos} position at output position "
                f"{chain}{output_index} based on sampled_contig, "
                f"but got {input_pos} in diffused_index_map"
            )
        # start next chain
        chain = chr(ord(chain) + 1)
    if chain_lengths[-1] == 0:
        # edge case - remove chain break at the end
        chain_lengths = chain_lengths[:-1]
    contigs = []
    for chain, mapping in mapping_by_chain.items():
        contig = []
        for fixed, region in itertools.groupby(mapping.values(), key=lambda m: m["fixed"]):
            region = list(region)
            if fixed:
                subregions = []
                subregion = []
                for pos in region:
                    chain = pos["input_pos"][0]
                    resnum = int(pos["input_pos"][1:])
                    if subregion and (chain != subregion[-1][0] or resnum != subregion[-1][1] + 1):
                        subregions.append(subregion)
                        subregion = []
                    subregion.append((chain, resnum))
                if subregion:
                    subregions.append(subregion)
                contig += [
                    f"{s[0][0]}{s[0][1]}-{s[-1][1]}"
                    for s in subregions
                    # f"{s[0][0]}{s[0][1]}" if len(s) == 1 else f"{s[0][0]}{s[0][1]}-{s[-1][1]}" for s in subregions
                ]
            else:
                contig.append(f"{len(region)}-{len(region)}")
        contigs.append(contig)
    return ["/".join(contig) for contig in contigs]


def is_designed(contig_chain_or_segment: str) -> bool:
    """Whether a contig chain or a single contig segment contains any generated residue.

    Generated segments are lengths ("20-20"), fixed segments start with a chain letter ("A74-79").
    """
    for segment in contig_chain_or_segment.removesuffix("/0").split("/"):
        if not segment[0].isalpha():
            return True
    return False


def chunk_string(s: str, chunk_size: int = 40) -> list:
    if not s:
        return []
    return [s[i : i + chunk_size] for i in range(0, len(s), chunk_size)]


def contains_amino_acids(chain: gemmi.Chain) -> bool:
    """
    Determine if chain contains any polymer residues (i.e. is not a ligand/non-polymer).
    Ligands may be present as a "chain" in the CIF, but we want to ignore these when determining chain breaks and contigs.
    """
    return any(residue.get_ca() is not None for residue in chain)


def standardize(
    cif_gz_path: str,
    json_path: str,
    output_pdb_path: str,
    input_contig_v1: str,
    hotspot: str,
):
    """Convert a single .cif.gz to a standardized PDB with REMARK annotations."""
    # Read CIF.gz
    structure = gemmi.read_structure(cif_gz_path)
    structure.setup_entities()
    model = structure[0]
    all_chain_names = [chain.name for chain in model if contains_amino_acids(chain)]
    chains_str = " ".join(all_chain_names)

    # Load input spec JSON to get the v3 contig
    with open(json_path) as f:
        json_data = json.load(f)
    contig_v3 = json_data["specification"]["contig"]
    # diffused_index_map: where each fixed input residue ended up in the output, e.g.
    # {"A74": "B1", ..., "A97": "B19"} -- e.g. input structure positions: raw output positions
    # (chains named in contig order, each renumbered from 1). Differently from RFD1,
    # it includes also the unindexed residues, fixed residues kept "structurally" but locally
    # diffused by RFD3. They are fixed, but not included in the contig string.
    diffused_index_map = json_data["diffused_index_map"]
    # sampled_contig: the contig RFD3 actually realized, e.g.
    # "20P,/0,A74,A75,A76,A77,A78,A79,A85,A86,A87,A88,A89,A90,A91,A92,A93,A94,A95,A96,A97"
    # 20P = 20 generated residues, /0 = chain break, A74-A97 = fixed residues taken from the input
    sampled_contig = json_data["specification"]["extra"]["sampled_contig"]

    # Build the v1-style contig: contig chains in output order, e.g. ["20-20", "A74-79/A85-97"]
    contig_chains = get_standardized_contig(diffused_index_map=diffused_index_map, sampled_contig=sampled_contig)
    std_contig_v1 = "/0 ".join(contig_chains)

    # Renumber the output structure: RFdiffusion3 numbers every chain from 1, the standardized
    # convention keeps the input residue numbers on chains without any generated residue.
    for chain_id, contig_chain in zip(all_chain_names, contig_chains, strict=True):
        if is_designed(contig_chain):
            continue
        standard_nums = []
        for segment in contig_chain.removesuffix("/0").split("/"):
            start_resnum, end_resnum = map(int, segment[1:].split("-"))
            standard_nums += range(start_resnum, end_resnum + 1)
        residues = [residue for residue in model[chain_id] if residue.get_ca() is not None]
        for residue, standard_num in zip(residues, standard_nums, strict=True):
            residue.seqid.num = standard_num

    # Standardize hotspots (remap chain letters using the rename mapping)
    std_hotspots = ""
    if hotspot:
        parts = []
        for res in hotspot.split(","):
            if not res:
                continue
            if res in diffused_index_map:
                parts.append(diffused_index_map[res])
            else:
                print(f"WARNING: Hotspot residue {res} not found in diffused_index_map. Skipping.", file=sys.stderr)
        std_hotspots = ",".join(parts)

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

    # Prepend REMARK lines to the PDB file and write to file
    pdb_content = structure.make_pdb_string()
    os.makedirs(os.path.dirname(output_pdb_path) or ".", exist_ok=True)
    with open(output_pdb_path, "w") as f:
        f.write("\n".join(remarks) + "\n")
        f.write(pdb_content)


def main():
    parser = argparse.ArgumentParser(description="Standardize RFdiffusion3 CIF.gz outputs to PDB")
    parser.add_argument("--cif_dir", type=str, required=True, help="Directory with .cif.gz files")
    parser.add_argument(
        "--json_dir",
        type=str,
        required=True,
        help="Directory with .json files generated by RFD3 (used to get contig info)",
    )
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
        json_path = os.path.join(args.json_dir, stem + ".json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Expected JSON file {json_path} for CIF {cif_path} not found.")
        output_pdb = os.path.join(args.output_dir, f"{stem}_standardized.pdb")
        print(f"  {basename} -> {os.path.basename(output_pdb)}")
        standardize(
            cif_gz_path=cif_path,
            json_path=json_path,
            output_pdb_path=output_pdb,
            input_contig_v1=args.input_contig,
            hotspot=args.hotspot,
        )

    print(f"Saved {len(cif_files)} standardized PDBs to {args.output_dir}")


if __name__ == "__main__":
    main()
