import itertools
import json
import string
from collections import defaultdict
from dataclasses import dataclass
from io import StringIO
from typing import List, Dict
from Bio.PDB import PDBParser

from ovo.core.utils.formatting import ColorPicker, mix_colors


def from_residues_to_segments(
    chain_id: str, residues: list[int], start_res: int | None = None, end_res: int | None = None
) -> list[str]:
    """Convert a list of residues [3,4,5,6,9,10,...] into a list of segments [3-6,9-10,...].

    Args:
        chain_id (str): Required. The chain ID.
        residues (list[int]): Required. A list of residues.
        start_res (int, optional): The start residue. If specified, trims residues from start_res. Defaults to None.
        end_res (int, optional): The end residue. If specified, trims residues to end_res. Defaults to None.

    Returns:
        list(str): A list of segments, i.e. [3-6,9-10,...]
    """

    if not residues:
        return []

    if start_res is not None:
        residues = [res for res in residues if res >= start_res]
    if end_res is not None:
        residues = [res for res in residues if res <= end_res]

    segments = []
    start = end = residues[0]
    for i in range(1, len(residues)):
        if residues[i] == residues[i - 1] + 1:
            end = residues[i]
        else:
            segments.append(f"{chain_id}{start}-{end}")
            start = end = residues[i]
    segments.append(f"{chain_id}{start}-{end}")
    return segments


def from_residues_to_hotspots(chain_id: str, residues: list[int]):
    """Convert a chain_id (i.e. A) and list of residues [3,4,...] into list of hotspots [A3, A4, ...]."""
    return [f"{chain_id}{res}" for res in residues]


def parse_selections(selections: str) -> list[str]:
    """
    Input: a JSON-encoded representation of the selections that looks like this
        {"sequenceSelections":[{"chainId":"A","residues":[10,11,12,13,15,16,17,18,19,20"]}]}
    Outputs list o segments ["A10-13", "A15-20"]
    """

    if selections is None:
        return []

    selections_json = json.loads(selections)
    selections_list = selections_json["sequenceSelections"]

    # for each of these, let's create a different representation
    result = []
    for selection in selections_list:
        chain_id = selection["chainId"]
        residues = selection["residues"]
        result += from_residues_to_segments(chain_id, residues)

    return result


def get_chains_and_contigs(pdb_str: str | None) -> Dict[str, str] | None:
    if pdb_str is None:
        return None

    parser = PDBParser(QUIET=True)

    struc = parser.get_structure("PDB_structure", StringIO(pdb_str))

    segments_by_chain = {}
    # Iterate through models, chains, and residues
    for model in struc:
        for chain in model:
            chain_id = chain.id  # Get the chain identifier
            residues = set()  # Use a set to hold unique residues

            for residue in chain:
                # Ensure the residue is an ATOM or ALA/GLY/other relevant residue
                if residue.id[0] == " " and int(residue.id[1]) > -1:
                    residues.add(int(residue.get_id()[1]))  # Get the residue number (not the insertion code)

            segments_by_chain[chain_id] = sorted(residues)

    segments_by_chain_json = {
        chain: parse_selections(json.dumps({"sequenceSelections": [{"chainId": chain, "residues": list(residues)}]}))
        for chain, residues in segments_by_chain.items()
    }

    return {chain: "/".join(segments) for chain, segments in segments_by_chain_json.items()}


def from_hotspots_to_segments(hotspots: str) -> list[str] | None:
    hotspots_by_chain = defaultdict(list)

    if not hotspots:
        return None

    # TODO: Maybe some more regex checks?
    for s in hotspots.split(","):
        hotspots_by_chain[s[0]].append(int(s[1:].replace(" ", "")))

    result = []
    for chain, hotspot_nums in hotspots_by_chain.items():
        hotspot_nums.sort()
        result.extend(from_residues_to_segments(chain, hotspot_nums))

    return result


def from_segments_to_hotspots(segments: list[str] | None) -> str:
    """Convert a list of segments ["A3-5","A9-10",...] to a STRING of hotspots "A3,A4,A5,A9,A10"."""

    if not segments:
        return ""

    hotspots = []
    for segment in segments:
        chain = segment[0]
        start_resnum = int(segment[1:].split("-")[0])
        end_resnum = int(segment[1:].split("-")[-1])
        hotspots.extend([f"{chain}{resnum}" for resnum in range(start_resnum, end_resnum + 1)])

    return ",".join(hotspots)


def from_contig_to_residues(chain_segment: str | None) -> list[int] | None:
    """Convert a str chain_segment / contig "A3-5/A9-10" to a list of residues [3,4,5,9,10]."""

    if not chain_segment:
        return None

    contig_segments = chain_segment.split(" ")[0].removesuffix("/0").split("/")

    residues = []
    # Merge non-consecutive residues into a list
    for segment in contig_segments:
        start_resnum = int(segment[1:].split("-")[0])
        end_resnum = int(segment[1:].split("-")[-1])
        residues += list(range(start_resnum, end_resnum + 1))

    return residues


def from_residues_to_chain_breaks(residues: list[int]) -> List[str] | None:
    residues.sort()
    chain_break_segments = []
    for i in range(1, len(residues)):
        # Check for a gap between consecutive numbers
        if residues[i] - residues[i - 1] > 1:
            missing_start_res = residues[i - 1]
            missing_end_res = residues[i]
            chain_break_segments.append(f"{missing_start_res}-{missing_end_res}")

    return chain_break_segments


def parse_partial_diffusion_binder_contig(binder_contig: str) -> tuple[int, list[str]]:
    """Get binder length and DESIGNED segments from binder contig as they correspond to positions in binder chain A

    default case for a peptide of 12 residues is simply binder_contig="12-12" turned into ["A1-12"]
    or when redesigning only A1 and A3-7 in a peptide of 12 residues, this would be
    binder_contig="1-1/A2-2/5-5/A8-12" turned into ["A1-1", "A3-7"]

    :param binder_contig: binder contig, e.g. 12-12 or 1-1/A2-2/5-5/A8-12
    :return: binder length (int) and list of designed segments (list of str, e.g. ["A1-1", "A3-7"])
    """
    assert " " not in binder_contig, f"Expected single chain in binder_contig, got: {binder_contig}"
    pos = 0
    designed_segments = []
    for segment in binder_contig.split("/"):
        if segment[0].isalpha():
            # fixed segment
            assert segment[0] == "A", f"Expected first contig in partial diffusion to be in chain A, got: {segment}"
            assert "-" in segment, f"Expected fixed segment in partial diffusion to be in format A2-3, got: {segment}"
            start, end = segment[1:].split("-")
            assert int(start) <= int(end), (
                f"Invalid fixed segment in partial diffusion, start must be <= end, got: {segment}"
            )
            assert int(start) == pos + 1, (
                f"Segment {segment} at generated position {pos + 1} should start with A{pos + 1} in partial diffusion"
            )
            pos += int(end) - int(start) + 1
        else:
            # designed segment
            assert "-" in segment, f"Expected designed segment in partial diffusion to be in format 5-5, got: {segment}"
            segment_length, _ = segment.split("-")
            assert segment_length == _, (
                f"Designed segments should have same start and end residue in partial diffusion, got: {segment}"
            )
            designed_segments.append(f"A{pos + 1}-{pos + int(segment_length)}")
            pos += int(segment_length)
    return pos, designed_segments


def create_partial_diffusion_binder_contig(redesigned_segments: list[str], binder_length: int) -> str:
    """Create a new binder contig for partial diffusion from the designed segments and old binder contig

    default case for a peptide of 12 residues:
    redesigned_segments=[] -> binder_contig="12-12"
    or when redesigning only A1 and A3-7 in a peptide of 12 residues,
    redesigned_segments=["A1-1", "A3-7"] -> binder_contig="1-1/A2-2/5-5/A8-12"

    :param redesigned_segments: list of designed segments (list of str, e.g. ["A1-1", "A3-7"])
    :param binder_length: length of binder (int)
    :return: new binder contig (str)
    """
    assert all([segment[0] == "A" for segment in redesigned_segments]), (
        f"Expected all redesigned segments to be in chain A, got: {redesigned_segments}"
    )
    redesigned_str = from_segments_to_hotspots(redesigned_segments)
    redesigned_positions = [int(res[1:]) for res in redesigned_str.split(",")] if redesigned_str else []
    all_positions = list(range(1, binder_length + 1))
    new_binder_segments = []
    for is_redesigned, positions in itertools.groupby(all_positions, lambda x: x in redesigned_positions):
        positions = list(positions)
        if is_redesigned:
            new_binder_segments.append(f"{len(positions)}-{len(positions)}")
        else:
            new_binder_segments.append(f"A{positions[0]}-{positions[-1]}")

    return "/".join(new_binder_segments)


@dataclass
class ContigSegment:
    """Class for annotating a segment of the structure.

    :param start: Starting residue number of the segment (inclusive).
    :param end: Ending residue number of the segment (inclusive).
    :param chain: Chain ID of the segment.
    :param color: Color of the segment in hex format (e.g. "0x00ff00"), optional.
    :param start_label: Label to show at the start of the segment, optional.
    :param middle_label: Label to show in the middle of the segment, optional.
    :param end_label: Label to show at the end of the segment, optional.
    """

    start: int
    end: int
    chain: str
    color: str | None = None
    start_label: str = None
    middle_label: str = None
    end_label: str = None


@dataclass
class MappedContigSegment(ContigSegment):
    """Class for annotating a segment of the structure with mapping to input structure numbering.

    In addition to ContigSegment fields, also includes:
    :param input_start: Starting residue number of the segment in the input structure (inclusive).
    :param input_end: Ending residue number of the segment in the input structure (inclusive).
    :param input_chain: Chain ID of the segment in the input structure.
    """

    input_start: int | None = None
    input_end: int | None = None
    input_chain: str | None = None


def _parse_range(range_str: str) -> tuple[int, int]:
    try:
        if "-" in range_str:
            start, end = range_str.split("-")
            return int(start), int(end)
        else:
            num = int(range_str)
            return num, num
    except ValueError:
        raise ValueError(f"Invalid range format: {range_str}")


def parse_contig_for_input_structure(contig: str, include_generated: bool = False) -> list[ContigSegment]:
    """Parse contig string and return segment annotations mapping to the INPUT structure numbering

    By default, includes only fixed segments (originating from input structure).

    :param contig: contig string, e.g. "A1-5/A6-10 B1-8" or "A1-5/5-10 B1-8"
    :param include_generated: include generated segments (e.g. 5-10) in the output, defaults to False.
                              Note that generated segments will have start, end, and chain set to None!
    """
    input_segments = []
    color_picker = ColorPicker()
    for subcontig in contig.split():
        for segment in subcontig.removesuffix("/0").replace(",", "/").split("/"):
            if not segment:
                # skip empty segments
                continue
            if segment[0].isalpha():
                # fixed input segment
                chain = segment[0]
                start, end = _parse_range(segment[1:])
                input_segments.append(
                    ContigSegment(
                        start=start,
                        end=end,
                        chain=chain,
                        start_label=f"{chain}{start}",
                        end_label=f"{chain}{end}",
                        color=color_picker((start, end, chain)),
                    )
                )
            else:
                # variable segment, do not add but validate format
                _parse_range(segment)
                if include_generated:
                    # add placeholder segment when requested
                    # can be used to compute number of fixed and generated segments
                    input_segments.append(
                        ContigSegment(
                            start=None,
                            end=None,
                            chain=None,
                            middle_label=segment,
                            color=None,
                        )
                    )
    return input_segments


def parse_contig_for_output_structure(contig: str) -> list[MappedContigSegment]:
    """Parse contig string and return segment annotations mapping to our standardized RFdiffusion OUTPUT structure numbering.

    See standardize_pdb.py script inside rfdiffusion pipeline.

    Assumptions:
    - The "subcontigs" in the contig (split by whitespace) are ordered same as the chains in the output structure (contigs with generated segments come first, then contigs with only fixed segments)
    - Generated segments should be "resolved", meaning that they should have same start and end in the range (5-5, not 5-10)
    - Chains that contain any RFdiffusion-generated segments are renumbered starting from 1 in the output structure, and they are in chains A, B, ... in order of appearance (in case of multiple generated chains, typically just A)
    - Fixed chains (with no designed segments) are numbered same as in the input structure, and assigned remaining chains B, C, etc. in order of appearance
    """
    output_segments = []
    color_picker = ColorPicker()
    prev_is_fixed = False
    for output_chain, subcontig in zip(string.ascii_uppercase, contig.split()):
        segments = subcontig.removesuffix("/0").replace(",", "/").split("/")
        is_fixed_chain = all(segment[0].isalpha() for segment in segments if segment)
        if prev_is_fixed and not is_fixed_chain:
            raise ValueError(
                f"Standardized contig format error. Generated chain contigs should come before fixed segments in contig: {contig}"
            )
        prev_is_fixed = is_fixed_chain
        output_start = 1
        for segment in segments:
            if not segment:
                raise ValueError(f"Empty segment found in contig: {contig}")
            if segment[0].isalpha():
                # fixed segment
                input_chain = segment[0]
                input_start, input_end = _parse_range(segment[1:])
                length = input_end - input_start + 1
                output_segments.append(
                    MappedContigSegment(
                        # when whole chain is fixed (no generated segments), original input numbering is preserved
                        start=input_start if is_fixed_chain else output_start,
                        end=input_end if is_fixed_chain else output_start + length - 1,
                        chain=output_chain,
                        start_label=f"{input_chain}{input_start}",
                        end_label=f"{input_chain}{input_end}",
                        color=color_picker((input_start, input_end, input_chain)),
                        input_start=input_start,
                        input_end=input_end,
                        input_chain=input_chain,
                    )
                )
                output_start += length
            else:
                # generated segment
                length, length2 = _parse_range(segment)
                if length != length2:
                    raise ValueError(
                        f"Generated segments in standardized contig should be resolved to single positions, got: {segment} in contig: {contig}"
                    )
                output_segments.append(
                    MappedContigSegment(
                        start=output_start,
                        end=output_start + length - 1,
                        chain=output_chain,
                        middle_label=str(length),
                        color=None,
                    )
                )
                output_start += length

    # assign color to generated segments based on neighboring fixed segments
    for prev_seg, seg, next_seg in zip([None] + output_segments[:-1], output_segments, output_segments[1:] + [None]):
        if seg.color is None:
            if prev_seg:
                # mid generated segment
                seg.color = mix_colors(mix_colors(prev_seg.color, "#ffffff"), "#ffffff")
            elif next_seg:
                # start segment (N term)
                seg.color = "#eeeeee"

    return output_segments
