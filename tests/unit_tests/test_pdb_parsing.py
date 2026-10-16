import importlib.util
import os

import pytest

import ovo
from ovo import DesignSpec
from ovo.core.utils.pdb import (
    ChainNotFoundError,
    filter_and_relabel_chains_pdb_str,
    get_sequences_from_pdb_str,
    get_pdb,
    get_standardized_remarks_from_pdb_str,
    replace_standardized_remarks_in_pdb_str,
)

TWO_CHAIN_PDB_STR = """MODEL        1
ATOM      1  N   ASN A  20     -36.584  27.168 -12.725  1.00136.17           N
ATOM      2  CA  ASN A  20     -36.216  25.856 -13.251  1.00135.78           C
ATOM      3  N   THR A  21     -38.058  25.035 -14.630  1.00128.94           N
ATOM      4  CA  THR A  21     -38.984  24.002 -15.067  1.00125.21           C
TER       5      THR A  21
ATOM      6  N   MET B  10     -16.584  27.168 -12.725  1.00136.17           N
ATOM      7  CA  MET B  10     -16.216  25.856 -13.251  1.00135.78           C
TER       8      MET B  10
CONECT    1    2
ENDMDL
MODEL        2
ATOM      9  CA  GLY A  40     -36.216  25.856 -13.251  1.00135.78           C
ENDMDL
END
"""


def test_design_spec_from_pdb(example_pdb_path):
    with open(example_pdb_path, "r") as f:
        pdb_data = f.read()
    assert get_sequences_from_pdb_str(pdb_data, chains=["A"]) == {
        "A": "NTTVFQGVAGQSLQVSCPYDSMKHWGRRKAWCRQLGEKGPCQRVVSTHNLWLLSFLRRWNGSTAITDDTLGGTLTITLRNLQPHDAGLYQCQSLHGSEADTLRKVLVEVLAD"
    }
    spec = DesignSpec.from_pdb_str(pdb_data, chains=["A"])
    assert len(spec.chains) == 1
    assert spec.chains[0].chain_ids == ["A"]
    assert (
        spec.chains[0].sequence
        == "NTTVFQGVAGQSLQVSCPYDSMKHWGRRKAWCRQLGEKGPCQRVVSTHNLWLLSFLRRWNGSTAITDDTLGGTLTITLRNLQPHDAGLYQCQSLHGSEADTLRKVLVEVLAD"
    )


def test_get_sequences_from_pdb_str_by_residue_number():
    seqs = get_sequences_from_pdb_str(
        """
ATOM      1  N   ASN A  20     -36.584  27.168 -12.725  1.00136.17           N  
ATOM      2  CA  ASN A  20     -36.216  25.856 -13.251  1.00135.78           C  
ATOM      9  N   THR A  21     -38.058  25.035 -14.630  1.00128.94           N  
ATOM     10  CA  THR A  21     -38.984  24.002 -15.067  1.00125.21           C  
ATOM     11  N   MET A  21A    -38.058  25.035 -14.630  1.00128.94           N  
ATOM     12  CA  MET A  21A    -38.984  24.002 -15.067  1.00125.21           C  
ATOM     16  N   THR A  22     -38.951  21.718 -15.865  1.00123.94           N  
ATOM     17  CA  THR A  22     -38.364  20.499 -16.400  1.00125.01           C  
""",
        chains=["A"],
        by_residue_number=True,
    )
    assert seqs["A"]["20"] == "N"
    assert seqs["A"]["21"] == "T"
    assert seqs["A"]["21A"] == "M"
    assert seqs["A"]["22"] == "T"


def test_get_sequences_from_pdb_str_multiple_models():
    seqs = get_sequences_from_pdb_str(
        """
MODEL        1
ATOM      1  N   ASN A  20     -36.584  27.168 -12.725  1.00136.17           N  
ATOM      2  CA  ASN A  20     -36.216  25.856 -13.251  1.00135.78           C  
ATOM      9  N   THR A  21     -38.058  25.035 -14.630  1.00128.94           N  
ATOM     10  CA  THR A  21     -38.984  24.002 -15.067  1.00125.21           C  
ENDMDL
MODEL        2
ATOM      1  N   ASN A  40     -36.584  27.168 -12.725  1.00136.17           N
ATOM      2  CA  ASN A  40     -36.216  25.856 -13.251  1.00135.78           C
""",
        chains=["A"],
    )
    assert seqs["A"] == "NT"


def test_get_sequences_from_pdb_str_duplicate_atom():
    """E.g. if altloc is present, same residue can appear multiple times"""
    seqs = get_sequences_from_pdb_str(
        """
ATOM      1  N   ASN A  20     -36.584  27.168 -12.725  1.00136.17           N  
ATOM      2  CA  ASN A  20     -36.216  25.856 -13.251  1.00135.78           C  
ATOM      3  CA  ASN A  20     -36.216  25.856 -13.251  1.00135.78           C  
""",
        chains=["A"],
    )
    assert seqs["A"] == "N"


def test_get_sequences_from_pdb_str_non_standard():
    """Dimethyllysine (MLY) is a non-standard amino acid."""
    seqs = get_sequences_from_pdb_str(
        """
HETATM    1  CA  MLY A  20     -36.584  27.168 -12.725  1.00136.17           C  
""",
        chains=["A"],
    )
    assert seqs["A"] == "X"


def test_get_sequences_from_pdb_str_ligands():
    """Ligands should be ignored (they don't have CA)."""
    seqs = get_sequences_from_pdb_str(
        """
ATOM      1  C   123 A  20     -36.584  27.168 -12.725  1.00136.17           C  
HETATM    2  C   456 A  20     -36.584  27.168 -12.725  1.00136.17           C  
ATOM      3  CA  ASN A  21     -36.216  25.856 -13.251  1.00135.78           C  
""",
        chains=["A"],
    )
    assert seqs["A"] == "N"


def test_filter_and_relabel_chains_pdb_str():
    """Keeping a single chain should relabel it to A, dropping the other chain and the second model."""
    filtered = filter_and_relabel_chains_pdb_str(TWO_CHAIN_PDB_STR, chains=["B"])

    assert get_sequences_from_pdb_str(filtered) == {"A": "M"}
    # Residue numbering is kept as is, atom serial numbers are renumbered from 1
    assert "ATOM      1  N   MET A  10" in filtered
    assert "TER       3      MET A  10" in filtered
    # CONECT records and additional models are dropped
    assert "CONECT" not in filtered
    assert "GLY" not in filtered


def test_filter_and_relabel_chains_pdb_str_swap():
    """Chains should not be merged when relabelling to a chain ID that is still present in the structure."""
    filtered = filter_and_relabel_chains_pdb_str(TWO_CHAIN_PDB_STR, chains=["B", "A"])

    assert get_sequences_from_pdb_str(filtered) == {"A": "M", "B": "NT"}
    # The chains are written in the requested order, with their serial numbers renumbered to follow
    kept_lines = [line for line in filtered.splitlines() if line.startswith(("ATOM", "TER"))]
    assert [line[21] for line in kept_lines] == list("AAABBBBB")
    assert [int(line[6:11]) for line in kept_lines] == [1, 2, 3, 4, 5, 6, 7, 8]
    # The TER of a chain stays with it
    assert "TER       3      MET A  10" in filtered
    assert "TER       8      THR B  21" in filtered


def test_filter_and_relabel_chains_pdb_str_custom_chain_ids():
    filtered = filter_and_relabel_chains_pdb_str(TWO_CHAIN_PDB_STR, chains=["A"], new_chain_ids=["X"])

    assert get_sequences_from_pdb_str(filtered) == {"X": "NT"}


def test_filter_and_relabel_chains_pdb_str_missing_chain():
    with pytest.raises(ChainNotFoundError, match="C"):
        filter_and_relabel_chains_pdb_str(TWO_CHAIN_PDB_STR, chains=["C"])


def test_pdb_online_download():
    content = get_pdb("5ELI")
    assert b"HEADER" in content
    content = get_pdb("Q9NZC2")
    assert b"HEADER" in content


def test_replace_standardized_remarks_in_pdb_str():
    # The remarks of the design the structure comes from are replaced, not kept
    pdb_str = (
        'REMARK   1 Standardized contig: "A5-6/0 B10-10/0"\n'
        "REMARK 350 PREVIOUS DESIGN\n"
        "REMARK PDBinfo-LABEL:    1 FIXED\n" + TWO_CHAIN_PDB_STR
    )
    replaced = replace_standardized_remarks_in_pdb_str(pdb_str, contig="1-1/A2-2/0 B10-10", fixed_residues=[2])

    assert get_standardized_remarks_from_pdb_str(replaced) == {
        "Standardized contig": "1-1/A2-2/0 B10-10",
        "Chains": "A B",
    }
    assert "PREVIOUS DESIGN" not in replaced
    # Only the atoms of the input are kept, under the new remark header
    assert get_sequences_from_pdb_str(replaced) == get_sequences_from_pdb_str(TWO_CHAIN_PDB_STR)
    # The labels of the residues kept fixed are replaced as well, written after the atoms
    assert replaced.splitlines()[-1] == "REMARK PDBinfo-LABEL:    2 FIXED"
    assert len([line for line in replaced.splitlines() if "PDBinfo-LABEL" in line]) == 1

    # The sequence design pipeline reads the redesigned residues from these remarks
    prepare_json = import_pipeline_script("ligandmpnn-sequence-design", "prepare_json.py")
    remark_lines = [line.removeprefix("REMARK   1 ") for line in replaced.splitlines() if line.startswith("REMARK   1")]
    assert prepare_json.get_designed_residues(prepare_json.parse_remark_lines(remark_lines)) == "A1"

    # A contig longer than a remark line is split into several of them and read back as one value
    long_contig = "10-10/" + "/".join(f"A{index}-{index}" for index in range(11, 30))
    replaced = replace_standardized_remarks_in_pdb_str(TWO_CHAIN_PDB_STR, contig=long_contig)

    assert len([line for line in replaced.splitlines() if "Standardized contig" in line]) > 1
    assert get_standardized_remarks_from_pdb_str(replaced) == {"Standardized contig": long_contig, "Chains": "A"}


def import_pipeline_script(pipeline_name: str, script_name: str):
    """Import a script of the bin directory of the given pipeline as a module."""
    path = os.path.join(os.path.dirname(ovo.__file__), "pipelines", pipeline_name, "bin", script_name)
    spec = importlib.util.spec_from_file_location(script_name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
