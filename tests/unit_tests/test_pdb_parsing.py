from ovo import DesignSpec
from ovo.core.utils.pdb import get_sequences_from_pdb_str, get_pdb


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


def test_pdb_online_download():
    content = get_pdb("5ELI")
    assert b"HEADER" in content
    content = get_pdb("Q9NZC2")
    assert b"HEADER" in content
