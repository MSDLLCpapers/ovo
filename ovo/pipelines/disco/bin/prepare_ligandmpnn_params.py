"""Prepare LigandMPNN multi-input JSONs for side-chain packing DISCO designs.

DISCO already designs the sequence and writes backbone-only PDBs. We want
LigandMPNN to add side chains *without* changing any residue identity, so every
standard protein residue is marked fixed and only the packer runs. The fixed set
differs per design (lengths / chains / hetero content vary), which is exactly
what LigandMPNN's ``--fixed_residues_multi`` handles, so the whole batch is
packed in a single LigandMPNN invocation rather than one run per PDB.

Two JSON files are written, mirroring the ``ligandmpnn-sequence-design``
workflow's convention:

* ``--pdb-path-multi-json``: ``{<pdb_path>: ""}`` for LigandMPNN's
  ``--pdb_path_multi`` (only the keys are read).
* ``--fixed-residues-json``: ``{<pdb_path>: "<chain><resnum> ...>"}`` for
  ``--fixed_residues_multi``.

Both JSONs are keyed by the exact ``*.pdb`` paths found under ``--pdb-dir``, so
LigandMPNN looks the fixed-residue list up by the same path string it reads from
the path-multi JSON.
"""

import argparse
import glob
import json
import os
import pathlib

from Bio.PDB import PDBParser


def fixed_residues(pdb_path: str) -> str:
    """Return all standard protein residues as space-separated ``<chain><resnum>``."""
    structure = PDBParser(QUIET=True).get_structure(pathlib.Path(pdb_path).stem, pdb_path)
    residues: list[str] = []
    model = structure[0]
    for chain in model:
        for residue in chain:
            hetflag, resnum, _ = residue.id
            # if hetflag.strip() or not is_aa(residue, standard=True):
            #     continue
            residues.append(f"{chain.id}{resnum}")
    return " ".join(residues)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdb-dir", required=True, help="Directory of DISCO design PDBs")
    parser.add_argument("--pdb-path-multi-json", required=True, help="Output path for the --pdb_path_multi JSON")
    parser.add_argument("--fixed-residues-json", required=True, help="Output path for the --fixed_residues_multi JSON")
    args = parser.parse_args()

    # Exclude any *_packed.pdb so re-runs don't try to pack previous output.
    pdb_paths = sorted(p for p in glob.glob(os.path.join(args.pdb_dir, "*.pdb")) if not p.endswith("_packed.pdb"))
    if not pdb_paths:
        raise SystemExit(f"No design PDBs found in {args.pdb_dir}")

    pathlib.Path(args.pdb_path_multi_json).write_text(json.dumps({p: "" for p in pdb_paths}))
    pathlib.Path(args.fixed_residues_json).write_text(json.dumps({p: fixed_residues(p) for p in pdb_paths}))
