#!/usr/bin/env python3
#
# Calculates contact molecular surface and various other metrics suggested by
# Brian Coventry. XML is unaltered from Brian.
#
# Adapted by David Prihoda for RFpeptide scoring based on RFpeptide supplement
#
# Usage:
#
#   ./pyrosetta_interface_metrics.py PDB_FOLDER OUT_CSV
#
# where FOLDER contains PDBs of complexes you want to score.
#


import os
import glob
import argparse
import multiprocessing
import json
import sys
import site

from pyrosetta import *
from rosetta.protocols.rosetta_scripts import *

script_dir = os.path.dirname(__file__)

p = argparse.ArgumentParser()
p.add_argument("data_dir", help="Folder of FastDesign outputs to process. Must contain both binder and receptor.")
p.add_argument("out_jsonl", help="Output jsonl file name")
p.add_argument(
    "--suffix",
    default="",
    help="Suffix on outputs to process. e.g. if --suffix=complex, then only processes files named *complex.pdb",
)
p.add_argument("--relax", action="store_true", default=False, help="Relax structures before scoring")
p.add_argument("--out-pdb", help="Save PDB structures to this directory after applying movers")
p.add_argument("--debug", action="store_true", default=False, help="Exit on error")
args = p.parse_args()

# Resolve DAlphaBall.gcc from the current Python environment's bin directory (sys.prefix/bin).
# In conda: set by main.nf after building from source and copying into $BIN.
# In Docker: pre-installed into /usr/local/bin at image build time (sys.prefix == /usr/local).
dalphaball_path = "/opt/DAlphaBall.gcc"
if not os.path.isfile(dalphaball_path):
    dalphaball_path = os.path.join(site.getsitepackages()[0], "DAlphaBall", "src", "DAlphaBall.gcc")
if not os.path.isfile(dalphaball_path):
    raise FileNotFoundError(
        "DAlphaBall.gcc not found in expected locations. Please ensure DAlphaBall is installed and DAlphaBall.gcc is /opt/ or python site-packages/DAlphaBall/src/."
    )
init(f"-corrections::beta_nov16 -detect_disulf false -run:preserve_header true -holes:dalphaball {dalphaball_path}")
parser = RosettaScriptsParser()
protocol_path = script_dir + "/interface_metrics_rfdesign.xml"

ncpu = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
print(f"Using {ncpu} cores")


def calculate(pdb_path):
    basename = os.path.basename(pdb_path).removesuffix(".pdb")
    row = {"id": basename}
    try:
        pose = pose_from_pdb(pdb_path)

        if args.relax:
            objs = XmlObjects.create_from_file(protocol_path)
            relax = objs.get_mover("FastRelax")
            relax.apply(pose)

        # We re-initialize the mover for each PDB to avoid remembering stuff from previous peptides, like peptide length
        protocol = parser.generate_mover(protocol_path)
        # Apply movers
        protocol.apply(pose)

        if args.out_pdb:
            os.makedirs(args.out_pdb, exist_ok=True)
            # save pose
            pose.dump_pdb(os.path.join(args.out_pdb, str(basename) + "_relaxed.pdb"))

        print("SCORES", pose.scores)
        for k, v in pose.scores.items():
            row[k] = float(v)
        row["buns_percent"] = (row["buns_heavy_ball_1.1D"] / row["nres_int"]) * 100 if row["nres_int"] else float("NaN")
    except Exception as e:
        row["error"] = f"{e} ({type(e).__name__})"
        print(f"ERROR processing {basename}: {row['error']}")
        if args.debug:
            raise
    return row


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(args.data_dir, f"*{args.suffix}.pdb")))

    if not files:
        print("No files found in", args.data_dir)
        sys.exit(0)

    if args.debug:
        records = map(calculate, files)
    else:
        with multiprocessing.Pool(min(ncpu, len(files))) as p:
            records = p.map(calculate, files)

    num_errors = 0
    with open(args.out_jsonl, "wt") as f:
        for record in records:
            json.dump(record, f)
            if record.get("error"):
                num_errors += 1
            f.write("\n")

    if num_errors == len(files):
        raise ValueError(f"All results failed: {record['error']}")

    print("Saved to:", args.out_jsonl)
