#!/usr/bin/env python
"""
Copy REMARK lines from backbone PDB files and prepend them to matching
sequence-designed PDB files, saving results to an output directory.

For each `<name>.pdb` in backbone_dir, finds all `<name>_*.pdb` in seq_dir,
extracts REMARK lines from the backbone file, prepends them to each seq file,
and writes the combined output to output_dir preserving the seq filename.
"""

import argparse
import glob
import os


def copy_remarks(backbone_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    backbone_files = sorted(glob.glob(os.path.join(backbone_dir, "*.pdb")))
    if not backbone_files:
        print(f"No PDB files found in {backbone_dir}")
        return

    for backbone_path in backbone_files:
        basename = os.path.basename(backbone_path)
        stem = basename.removesuffix(".pdb")

        # Extract REMARK lines from the backbone PDB
        with open(backbone_path, "r") as f:
            remark_lines = [line for line in f if line.startswith("REMARK")]

        # Find all matching sequence PDBs
        seq_pattern = os.path.join(output_dir, f"{stem}_*.pdb")
        seq_files = sorted(glob.glob(seq_pattern))

        if not seq_files:
            raise ValueError(f"No matching seq files for {seq_pattern}")

        for seq_path in seq_files:
            with open(seq_path, "r") as f:
                seq_lines = f.readlines()

            with open(seq_path, "w") as f:
                header_lines = [line for line in seq_lines if line.startswith("HEADER")]
                other_lines = [line for line in seq_lines if not line.startswith("HEADER")]
                f.writelines(header_lines)
                f.writelines(remark_lines)
                f.writelines(other_lines)
    print("Saved to:", output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy REMARK lines from backbone PDBs to sequence-designed PDBs.")
    parser.add_argument("backbone_dir", type=str, help="Input directory with backbone PDB files")
    parser.add_argument("output_dir", type=str, help="Output directory for combined PDB files")

    args = parser.parse_args()
    copy_remarks(args.backbone_dir, args.output_dir)
