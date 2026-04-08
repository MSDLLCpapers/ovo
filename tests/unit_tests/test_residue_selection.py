import json

from ovo.core.utils.residue_selection import (
    from_residues_to_segments,
    from_residues_to_hotspots,
    parse_selections,
    get_chains_and_contigs,
    from_hotspots_to_segments,
    from_segments_to_hotspots,
    from_contig_to_residues,
    from_residues_to_chain_breaks,
    parse_partial_diffusion_binder_contig,
    create_partial_diffusion_binder_contig,
    parse_contig_for_input_structure,
    parse_contig_for_output_structure,
    ContigSegment,
    MappedContigSegment,
)


def test_from_residues_to_segments_simple():
    assert from_residues_to_segments("A", [3, 4, 5, 6, 9, 10]) == ["A3-6", "A9-10"]


def test_from_residues_to_hotspots_simple():
    assert from_residues_to_hotspots("A", [3, 4]) == ["A3", "A4"]


def test_parse_selections_simple():
    selections = json.dumps({"sequenceSelections": [{"chainId": "A", "residues": [10, 11, 12, 15, 16]}]})
    assert parse_selections(selections) == ["A10-12", "A15-16"]


def test_get_chains_and_contigs_simple():
    pdb_str = """\
ATOM      1  N   ALA A   1      11.104  13.207   2.100  1.00 20.00           N  
ATOM      2  CA  ALA A   2      12.000  13.000   3.000  1.00 20.00           C  
ATOM      3  N   GLY B   5      10.000  10.000   1.000  1.00 20.00           N  
ATOM      4  CA  GLY B   6      10.500  11.000   1.500  1.00 20.00           C  
END
"""
    result = get_chains_and_contigs(pdb_str)
    assert result == {"A": "A1-2", "B": "B5-6"}


def test_from_hotspots_to_segments_simple():
    assert from_hotspots_to_segments("A3,A4,A5,A9,A10") == ["A3-5", "A9-10"]


def test_from_segments_to_hotspots_simple():
    assert from_segments_to_hotspots(["A3-5", "A9-10"]) == "A3,A4,A5,A9,A10"


def test_from_contig_to_residues_simple():
    assert from_contig_to_residues("A3-5/A9-10") == [3, 4, 5, 9, 10]


def test_from_residues_to_chain_breaks_simple():
    assert from_residues_to_chain_breaks([1, 2, 5, 6]) == ["2-5"]


def test_parse_partial_diffusion_binder_contig_default():
    length, designed = parse_partial_diffusion_binder_contig("12-12")
    assert length == 12
    assert designed == ["A1-12"]


def test_parse_partial_diffusion_binder_contig_no_redesigned():
    length, designed = parse_partial_diffusion_binder_contig("A1-12")
    assert length == 12
    assert designed == []


def test_parse_partial_diffusion_binder_contig_simple():
    length, designed = parse_partial_diffusion_binder_contig("1-1/A2-2/5-5/A8-12")
    assert length == 12
    assert designed == ["A1-1", "A3-7"]


def test_create_partial_diffusion_binder_contig_default():
    result = create_partial_diffusion_binder_contig(["A1-12"], 12)
    assert result == "12-12"


def test_create_partial_diffusion_binder_contig_no_redesigned():
    result = create_partial_diffusion_binder_contig([], 12)
    assert result == "A1-12"


def test_create_partial_diffusion_binder_contig_simple():
    result = create_partial_diffusion_binder_contig(["A1-1", "A3-7"], 12)
    assert result == "1-1/A2-2/5-5/A8-12"


def test_multichain_contig_parsing():
    contig = "A64-78/6-6/B85-94/3-3/0 C20-30/0"

    input_segments = parse_contig_for_input_structure(contig)

    assert len(input_segments) == 3
    assert input_segments == [
        ContigSegment(
            start=64,
            end=78,
            chain="A",
            color="#1f77b4",
            start_label="A64",
            end_label="A78",
        ),
        ContigSegment(
            start=85,
            end=94,
            chain="B",
            color="#ff7f0e",
            start_label="B85",
            end_label="B94",
        ),
        ContigSegment(
            start=20,
            end=30,
            chain="C",
            color="#2ca02c",
            start_label="C20",
            end_label="C30",
        ),
    ]

    output_segments = parse_contig_for_output_structure(contig)
    assert len(output_segments) == 5
    assert output_segments == [
        MappedContigSegment(
            start=1,
            end=15,
            chain="A",
            color="#1f77b4",
            start_label="A64",
            middle_label=None,
            end_label="A78",
            input_start=64,
            input_end=78,
            input_chain="A",
        ),
        MappedContigSegment(
            start=16,
            end=21,
            chain="A",
            color="#c7ddec",
            start_label=None,
            middle_label="6",
            end_label=None,
        ),
        MappedContigSegment(
            start=22,
            end=31,
            chain="A",
            color="#ff7f0e",
            start_label="B85",
            middle_label=None,
            end_label="B94",
            input_start=85,
            input_end=94,
            input_chain="B",
        ),
        MappedContigSegment(
            start=32,
            end=34,
            chain="A",
            color="#ffdfc2",
            start_label=None,
            middle_label="3",
            end_label=None,
        ),
        MappedContigSegment(
            start=20,
            end=30,
            chain="B",
            color="#2ca02c",
            start_label="C20",
            middle_label=None,
            end_label="C30",
            input_start=20,
            input_end=30,
            input_chain="C",
        ),
    ]
