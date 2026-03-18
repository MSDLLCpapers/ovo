import argparse
import os
import glob
import json

import numpy as np
import pandas as pd
import string

from biopandas.pdb import PandasPdb
from copy import deepcopy

# CONTIG: A1-10/10-20/A30-40/0 B23-40/.../0 C10-25
# CONTIG_CHAINS: list or comma-separated list = A1-10/10-20/A30-40/0, B23-40/.../0, C10-25
# MASKED_CONTIG_CHAINS: CONTIG_CHAINS read from trb file
# SEGMENTS: list or comma-separated list = A1-10, 10-20, A30-40, B23-40, ...

ALPHABET = string.ascii_uppercase


def is_designed(contig_chain_or_segment: str) -> bool:
    """
    Check if the contig chain is fixed or not.
    :param contig_chain: str, the contig chain string
    :return: bool, True if designed, False if is fixed
    """
    for segment in contig_chain_or_segment.removesuffix("/0").split("/"):
        if not segment[0].isalpha():
            return True
    return False


def order_designed_contig(contig_chains: list[str], trb_ref_pdb_idx: list[tuple[str, str]]) -> list[str]:
    """
    Order the contig segments by designed and fixed segments. It is needed to guarantee the correct mapping with
    the output pdb numbering as in the output pdb designed input residues are first listed in A,
    then fixed residues listed in B.
    First, create a list with designed + fixed contig segments.
    Then, scans the segments and check if the segments are ordered correctly comparing with the rfdiffusion output.
    Example:
        - input contig_chains [A1-10/10-20/A30-40/0, B23-40/.../0, C10-25] (designed + fixed)
        - For each contig segment splits it in segments: i.e. A1-10, 10-20, A30-40, B23-40, ...
            For fixed segments (namely A1-10, A30-40, B23-40) check if the segments are ordered as in the trb ref pdb
            idx.
            This latter gets only fixed segments trb_ref_pdb_idx:
            [(A, 1), (A, 2), ... (A, 10), (A, 30), (A, 31), ..., (B, 23), (B, 24), ..., (B, 40), ..., (C, 10), (C, 11)
            ...]
    """
    designed_segments, fixed_segments = [], []

    for contig_chain in contig_chains:
        if is_designed(contig_chain):
            designed_segments.append(contig_chain)
        else:
            fixed_segments.append(contig_chain)

    ordered_contig_chains = designed_segments + fixed_segments

    # SANITY CHECK
    # Check if the segments are ordered correctly comparing with the rfdiffusion output
    trb_mask_idx = 0
    for ordered_contig_chain in ordered_contig_chains:
        for segment in ordered_contig_chain.removesuffix("/0").split("/"):
            # Check if segment is designed
            if is_designed(segment):
                continue

            chain = segment[0]
            start_resnum, end_resnum = map(int, segment[1:].split("-"))
            for res_num in range(start_resnum, end_resnum + 1):
                if (chain, res_num) != trb_ref_pdb_idx[trb_mask_idx]:
                    raise ValueError(
                        f"Mismatch between parsed residue {(chain, res_num)} and "
                        f"expected rf-diffusion output {trb_ref_pdb_idx[trb_mask_idx]} in the {trb_mask_idx} "
                        f"trb mask location: check 'trb['complex_con_ref_pdb_idx']'"
                    )
                trb_mask_idx += 1

    return ordered_contig_chains


def input_output_standard_mapping(
    contig_chains: list[str],
) -> tuple[list[tuple[str, str] | None], list[tuple[str, str]], list[tuple[str, str]]]:
    """Create the input, output and standardized numbering for the PDB file
    :param contig_segments: list of str with the contig segments ordered by order_designed_contig
        [A1-10/10-20/A30-40/0, B23-40/.../0, C10-25]
        [chain designed, chain designed, chain fixed]
    :return: tuple of three lists with the input, output and standardized numbering
        Split each chain into segments.
        If the segment is designed, the input numbering is None (there are no correspondence in the input)
        Rf diffusion output pdb numbering is consecutive starting from 1 (guaranteed beacuse of the order of the segments)
        designed chains are in 'A' and fixed chain(s) are in 'B'.
        Standardized numbering include:
            - Consecutive chain id, new_chain := ALPHABET[i] where 'i' runs with the contig (chains) segments,
                each chain break is a different chain.
            - Standard numbering: use the input pdb numbering if chain is fixed,
                otherwise use consecutive numbering starting from 1 in each chain
        Example:
            Input pdb numbering:
            First designed chain                                                Second designed chain  Third (fixed) chain
            [(A, 1), (A, 2), ..., None   , None   , ..., (A, 30), (A, 31), ..., (B, 23), (B, 24), ..., (C, 10), (C, 11), ...]
            Rf diffusion output pdb numbering:
            [(A, 1), (A, 2), ..., (A, 11), (A, 12), ..., (A, 30), (A, 31), ..., (A, n), (B, n+1), ..., (B, n+k), (B, n+k+1), ...]
            Standardized pdb numbering:
            [(A, 1), (A, 2), ..., (A, 11), (A, 12), ..., (A, 30), (A, 31), ..., (B, 1), (B, 2), ..., (C, 10), (C, 11), ...]
    """

    input_numbering = []
    rfdiff_output_numbering = []
    standardized_numbering = []
    rfdiff_output_num = 1
    for i, contig_chain in enumerate(contig_chains):
        rfdiff_output_chain = "A" if is_designed(contig_chain) else "B"

        new_chain = ALPHABET[i]
        standard_resnum = 1

        for segment in contig_chain.removesuffix("/0").split("/"):
            if is_designed(segment):
                start_len, end_len = map(int, segment.split("-"))
                assert start_len == end_len, (
                    f"Start len and end len of design segment should coincide: "
                    f"{start_len} != {end_len} in {contig_chain} "
                )

                for _ in range(start_len):
                    input_numbering.append(None)
                    rfdiff_output_numbering.append((rfdiff_output_chain, str(rfdiff_output_num)))
                    standardized_numbering.append((new_chain, str(standard_resnum)))
                    standard_resnum += 1
                    rfdiff_output_num += 1
            else:
                input_chain = segment[0]
                start_resnum, end_resnum = map(int, segment[1:].split("-"))

                for input_num in range(start_resnum, end_resnum + 1):
                    input_numbering.append((input_chain, str(input_num)))
                    rfdiff_output_numbering.append((rfdiff_output_chain, str(rfdiff_output_num)))
                    if rfdiff_output_chain == "A":
                        standardized_numbering.append((new_chain, str(standard_resnum)))
                        standard_resnum += 1
                    else:
                        standardized_numbering.append((new_chain, str(input_num)))
                    rfdiff_output_num += 1

    return input_numbering, rfdiff_output_numbering, standardized_numbering


def chunk_string(s: str | None, chunk_size: int = 40) -> str | None:
    """
    Splits the input string `s` into chunks of size `chunk_size`.
    Args:
        s (str or None): The input string to be chunked.
        chunk_size (int): The maximum length of each chunk.
    Yields:
        str: A chunk of the input string, or returns None if input is None.
    """
    if s is None:
        return None

    for i in range(0, len(s), chunk_size):
        yield s[i : i + chunk_size]


def renumber_rfdiffusion_pdb(pdb_file: str, trb_file: str, output_pdb: str):
    """Renumber the RF-diffusion target chain residues in the input PDB file
    :param:
        pdb_file: str with the path to the rfdiffusion PDB file
        trb_file: str with the path to the rfdiffusion TRB file
        output_pdb: str with the path to save the standardized PDB file

    """

    trb = pd.read_pickle(trb_file)
    ppdb = PandasPdb().read_pdb(pdb_file)

    # Adding hotspot in a REMARK line
    renum_ppdb = deepcopy(ppdb)

    # # trb sampled_mask contains the exact length of generated segments in case of ranged input
    masked_contig_chains = trb["sampled_mask"]

    if "complex_con_ref_pdb_idx" in trb:
        trb_ref_pdb_idx = trb["complex_con_ref_pdb_idx"]
        # Order first designed chains and after fixed chains
        ordered_contig_chains = order_designed_contig(masked_contig_chains, trb_ref_pdb_idx)
    else:
        # If no complex_con_ref_pdb_idx, use the masked segments as is
        ordered_contig_chains = masked_contig_chains

    standardized_contig = " ".join(ordered_contig_chains)

    input_num, output_num, standard_num = input_output_standard_mapping(ordered_contig_chains)

    for (out_chain, out_resnum), (standard_chain, standard_res_num) in zip(output_num, standard_num):
        query_resnum = int(out_resnum)

        queried_ids = ppdb.df["ATOM"].query("residue_number==@query_resnum & chain_id==@out_chain").index

        assert ppdb.df["ATOM"].residue_number.dtype == type(query_resnum) == int, (
            f"Unexpected error standardizing PDB, residue_number should be int: {pdb_file} "
            f"residue_number=={ppdb.df['ATOM'].residue_number.dtype} != {type(query_resnum)}"
        )

        assert len(queried_ids), (
            f"Unexpected error standardizing PDB, residue not found in {pdb_file}: "
            f"residue_number=={query_resnum} chain_id=={out_chain}"
        )

        renum_ppdb.df["ATOM"].loc[queried_ids, "residue_number"] = [standard_res_num] * len(queried_ids)
        renum_ppdb.df["ATOM"].loc[queried_ids, "chain_id"] = [standard_chain] * len(queried_ids)

    # Get input contig and hotspots format for standardized pdb
    input_contig = trb["config"]["contigmap"]["contigs"][0]
    input_hotspots_list = trb["config"]["ppi"]["hotspot_res"]
    input_hotspots = ",".join(input_hotspots_list) if input_hotspots_list else None

    # Standardize the hotspots
    out_hotspots = []
    if input_hotspots_list:
        for hotspot in input_hotspots_list:
            chain, hotspot_num = hotspot[0], hotspot[1:]
            if (chain, hotspot_num) not in input_num:
                raise ValueError(f"Hotspot {hotspot} not valid for structure {pdb_file}")
            res_tuple = standard_num[input_num.index((chain, hotspot_num))]
            out_hotspots.append("".join(res_tuple))

    standardized_hotspots = ",".join(out_hotspots) if out_hotspots else None

    # Get designed and fixed chains
    chains = " ".join([ALPHABET[i] for i, _ in enumerate(ordered_contig_chains)])

    # Get inpaint sequence if available
    inpaint_seq = (
        "/".join(trb["config"]["contigmap"]["inpaint_seq"]) if trb["config"]["contigmap"]["inpaint_seq"] else None
    )

    # Write REMARK lines in the standardized pdb
    # TODO: Consider using some code 1070 (only int allowed)
    for chunk in chunk_string(input_contig, 40):
        renum_ppdb.add_remark(code=1, text=f" Input contig: {json.dumps(chunk)}")

    for chunk in chunk_string(standardized_contig, 40):
        renum_ppdb.add_remark(code=1, text=f" Standardized contig: {json.dumps(chunk)}")

    if inpaint_seq:
        for chunk in chunk_string(inpaint_seq, 40):
            renum_ppdb.add_remark(code=1, text=f" Inpaint seq: {json.dumps(chunk)}")

    for chunk in chunk_string(chains, 40):
        renum_ppdb.add_remark(code=1, text=f" Chains: {json.dumps(chunk)}")

    if not input_hotspots:
        renum_ppdb.add_remark(code=1, text=" Input hotspots: ")

    for chunk in chunk_string(input_hotspots, 40):
        renum_ppdb.add_remark(code=1, text=f" Input hotspots: {json.dumps(chunk)}")

    if not standardized_hotspots:
        renum_ppdb.add_remark(code=1, text=" Standardized hotspots: ")

    for chunk in chunk_string(standardized_hotspots, 40):
        renum_ppdb.add_remark(code=1, text=f" Standardized hotspots: {json.dumps(chunk)}")

    renum_ppdb.to_pdb(output_path)

    # Add FIXED remarks for fastrelax protocol
    if "receptor_con_hal_pdb_idx" in trb:
        # Identify the last residue number in A chain
        last_res_id = int(trb["receptor_con_hal_pdb_idx"][0][1]) - 1

        # Identify where inpaint seq is True, ie, kept fixed
        indices = np.where(trb["inpaint_seq"][:last_res_id])[0]
    else:
        # Identify where inpaint seq is True in the only chain
        indices = np.where(trb["inpaint_seq"])[0]

    with open(output_pdb, "a") as f:
        f.write("\n")
        for position in indices:
            f.write(f"REMARK PDBinfo-LABEL:{position + 1: >5} FIXED\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdb_path", type=str)
    parser.add_argument("input_trb_path", type=str)
    parser.add_argument("output_pdb_path", type=str)
    options = parser.parse_args()

    if os.path.isdir(options.input_pdb_path):
        pdb_paths = sorted(glob.glob(os.path.join(options.input_pdb_path, "*.pdb")))
        trb_paths = sorted(glob.glob(os.path.join(options.input_trb_path, "*.trb")))
    else:
        pdb_paths = [options.input_pdb_path]
        trb_paths = [options.input_trb_path]

    # Create sets to hold the base names (without extensions)
    pdb_basenames = {os.path.splitext(os.path.basename(pdb))[0] for pdb in pdb_paths}
    trb_basenames = {os.path.splitext(os.path.basename(trb))[0] for trb in trb_paths}

    # Find paired and unpaired files
    paired_filename, unpaired_pdb, unpaired_trb = [], [], []
    for basename in pdb_basenames:
        if basename in trb_basenames:
            paired_filename.append(
                (os.path.join(options.input_pdb_path, basename), os.path.join(options.input_trb_path, basename))
            )
        else:
            unpaired_pdb.append(basename)

    for basename in trb_basenames:
        if basename not in pdb_basenames:
            unpaired_trb.append(basename)

    assert not unpaired_pdb and not unpaired_trb, (
        f"Unpaired pdb files {unpaired_pdb}, trb files {unpaired_trb} found. "
        f"Please check the input directories {options.input_pdb_path}, {options.input_trb_path}."
    )

    assert paired_filename, "No paired pdb and trb files found in the input directories."

    print(f"Renumbering and standardizing {len(paired_filename)} PDB files.")
    for pdb_name, trb_name in paired_filename:
        output_path = os.path.join(options.output_pdb_path, os.path.basename(pdb_name) + "_standardized.pdb")
        renumber_rfdiffusion_pdb(pdb_name + ".pdb", trb_name + ".trb", output_path)
    print("Saved to:", options.output_pdb_path)
