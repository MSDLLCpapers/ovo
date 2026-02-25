from Bio import Align


def align_protein_global(a: str, b: str) -> Align.Alignment:
    aligner = Align.PairwiseAligner(mode="global", scoring="blastp")
    alignments = aligner.align(a, b)
    return alignments[0]


# These are the amino acid pairs that are considered similar when calculating sequence similarity.
# Based on positive scores in BLOSUM62 (should correspond to BLAST similarity)
SIMILAR_PAIRS = frozenset(
    {
        "AA",
        "AS",
        "CC",
        "DD",
        "DE",
        "DN",
        "ED",
        "EE",
        "EK",
        "EQ",
        "FF",
        "FW",
        "FY",
        "GG",
        "HH",
        "HN",
        "HY",
        "II",
        "IL",
        "IM",
        "IV",
        "KE",
        "KK",
        "KQ",
        "KR",
        "LI",
        "LL",
        "LM",
        "LV",
        "MI",
        "ML",
        "MM",
        "MV",
        "ND",
        "NH",
        "NN",
        "NS",
        "PP",
        "QE",
        "QK",
        "QQ",
        "QR",
        "RK",
        "RQ",
        "RR",
        "SA",
        "SN",
        "SS",
        "ST",
        "TS",
        "TT",
        "VI",
        "VL",
        "VM",
        "VV",
        "WF",
        "WW",
        "WY",
        "YF",
        "YH",
        "YW",
        "YY",
        # ambiguous aminoacid codes
        "XX",
        "BB",
        "BN",
        "NB",
        "BD",
        "DB",
        "ZZ",
        "ZQ",
        "QZ",
        "ZE",
        "EZ",
        "JJ",
        "JL",
        "LJ",
        "JI",
        "IJ",
        "UU",
        "OO",
    }
)


def are_similar(aa1: str, aa2: str) -> bool:
    """Check if amino acid pair is considered similar based on hard-coded similar pairs.

    :param aa1: First amino acid
    :param aa2: Second amino acid

    :returns: True if they are considered similar, else False
    """
    return aa1 + aa2 in SIMILAR_PAIRS
