import os

import freesasa
import argparse
import pandas as pd
import glob


def analyze_pdb(pdb_path: str, chains: str) -> dict:
    """Analyze a PDB file with freesasa, calculating polar and apolar SASA for the specified chains.

    :param pdb_path: path to the PDB file
    :param chains: string representing chains to analyze, e.g. "A,B".
                   Note that ProteinQC also supports "A,B;C" format to analyze chains A and B together and chain C separately,
                   or keywords FULL (full structure) and EACH (each chain separately),
                   but that is not supported by this example script.
    """
    assert ";" not in chains, "Only one chain group is supported (use 'A,B' to analyze chains A and B together)"
    chain_groups = "".join(chains.split(","))
    structures = freesasa.structureArray(pdb_path, {"separate-chains": False, "chain-groups": chain_groups})
    assert len(structures) == 2, f"Unexpected freesasa array, got {len(structures)} structures"
    _, chain_structure = structures
    result = freesasa.calc(chain_structure)
    area_classes = freesasa.classifyResults(result, chain_structure)
    print("CHAIN", area_classes)
    return {"ID": os.path.basename(pdb_path).rsplit(".", 1)[0], **area_classes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdb_input", help="Path to the pdb file or directory with PDB files")
    parser.add_argument("--chains", help="Chain(s) to analyze")
    parser.add_argument("output_csv", help="Path to the output csv file")
    args = parser.parse_args()

    if os.path.isdir(args.pdb_input):
        pdb_paths = glob.glob(os.path.join(args.pdb_input, "*.pdb"))
    else:
        assert args.pdb_input.endswith(".pdb"), f"Expected a PDB file, got: {args.pdb_input}"
        pdb_paths = [args.pdb_input]

    print(f"Analyzing {len(pdb_paths):,} PDB files...")
    results = [analyze_pdb(pdb_path, chains=args.chains) for pdb_path in pdb_paths]
    df = pd.DataFrame(results)
    print(df.head())
    df.to_csv(args.output_csv, index=False)
    print(f"Saved {len(df)} results to to: {args.output_csv}")
