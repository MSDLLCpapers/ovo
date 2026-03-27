#!/usr/bin/env python3
"""Build an RFdiffusion3 input JSON from simplified parameters.

Accepts v1-style contig strings (slash-separated) and converts them to
RFdiffusion3 (v3) comma-separated contig syntax for the JSON spec file.
"""

import argparse
import json
import os
import re
import sys


def convert_contig_v1_to_v3(contig_v1: str) -> str:
    """Convert RFdiffusion v1 contig syntax to RFdiffusion3 (v3) syntax.

    Examples:
        "A30-40/10/A50-60"  ->  "A30-40,10,A50-60"
        "A30-50/0 10-10"    ->  "A30-50,/0,10-10"
        "A52-156/0 50-60"   ->  "A52-156,/0,50-60"
    """
    contig = contig_v1.strip()
    # Step 1: replace all "/" with "," first
    contig = contig.replace("/", ",")
    # Step 2: convert chain-break token ",0" back to ",/0"
    # Only match ",0" NOT followed by "-" (to preserve designed ranges like "0-10")
    contig = re.sub(r",0(?!-)", ",/0", contig)
    # Step 3: replace ",/0 " (chain break before next segment separated by space) with ",/0,"
    contig = re.sub(r",/0\s+", ",/0,", contig)
    # Clean up double commas and leading/trailing commas
    contig = re.sub(r",+", ",", contig)
    contig = contig.strip(",")
    return contig


def has_chain_break(contig_v3: str) -> bool:
    return "/0" in contig_v3


def build_spec(input_pdb: str, contig_v3: str, hotspot: str) -> dict:
    """Build a single RFD3 InputSpecification dict."""
    spec = {
        "dialect": 2,
        "input": os.path.abspath(input_pdb),
        "contig": contig_v3,
    }
    if has_chain_break(contig_v3):
        # Binder design: add hotspot orientation strategy
        spec["infer_ori_strategy"] = "hotspots"
        if hotspot:
            spec["select_hotspots"] = hotspot
    return spec


def main():
    parser = argparse.ArgumentParser(description="Build RFdiffusion3 input JSON from params")
    parser.add_argument("--input_pdb", type=str, help="Input PDB/CIF file path")
    parser.add_argument("--contig", type=str, help="Contig string in v1 format (e.g. 'A30-50/0 10-10')")
    parser.add_argument("--hotspot", type=str, default="", help="Hotspot residues e.g. A78,A79")
    parser.add_argument("--input_json", type=str, default=None, help="Pre-built RFD3 JSON (pass-through mode)")
    parser.add_argument("--output_json", type=str, required=True, help="Output JSON path")
    args = parser.parse_args()

    input_json_name = os.path.basename(args.input_json) if args.input_json else None
    if args.input_json and input_json_name != "NO_FILE":
        # Pass-through: validate it's valid JSON and copy to output path
        with open(args.input_json) as f:
            spec = json.load(f)
        with open(args.output_json, "w") as f:
            json.dump(spec, f, indent=2)
        print(f"Using provided input JSON: {args.input_json}")
        return

    if not args.input_pdb or not args.contig:
        print("ERROR: --input_pdb and --contig are required when --input_json is not provided", file=sys.stderr)
        sys.exit(1)

    contig_v3 = convert_contig_v1_to_v3(args.contig)
    print(f"Converted contig: '{args.contig}' -> '{contig_v3}'")

    hotspot = args.hotspot.strip() if args.hotspot else ""
    spec = build_spec(args.input_pdb, contig_v3, hotspot)
    output = {"design": spec}

    with open(args.output_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written input JSON to: {args.output_json}")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
