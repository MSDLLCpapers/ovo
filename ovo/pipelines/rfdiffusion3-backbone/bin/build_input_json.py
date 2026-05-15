#!/usr/bin/env python3
"""Build an RFdiffusion3 input JSON from simplified parameters.

Accepts v1-style contig strings (slash-separated) and converts them to
RFdiffusion3 (v3) comma-separated contig syntax for the JSON spec file.
"""

import argparse
import json
import os


def convert_contig_v1_to_v3(contig_v1: str) -> str:
    # split contig into list of lists of segments
    subcontigs: list[list[str]] = [
        subcontig.removesuffix("/0").split("/") for subcontig in contig_v1.replace("/0", "/0 ").split() if subcontig
    ]
    # move fixed subcontigs to the end
    subcontigs = sorted(subcontigs, key=lambda segments: all(s[0].isalpha() for s in segments))
    # create RFD3 contig
    return ",/0,".join(",".join(segments) for segments in subcontigs)


def build_spec(input_structure_path: str, contig_v3: str, hotspot: str, spec_overrides: dict | None = None) -> dict:
    """Build a single RFD3 InputSpecification dict."""
    spec = {
        "dialect": 2,
        "input": os.path.abspath(input_structure_path),
        "contig": contig_v3,
    }
    if "/0" in contig_v3:
        if hotspot:
            spec["infer_ori_strategy"] = "hotspots"
            spec["select_hotspots"] = hotspot
        else:
            spec["infer_ori_strategy"] = "com"
    # User overrides applied last — can override auto-derived fields (e.g. infer_ori_strategy)
    if spec_overrides:
        spec.update(spec_overrides)
    return spec


def main():
    parser = argparse.ArgumentParser(description="Build RFdiffusion3 input JSON from params")
    parser.add_argument("--input_structure_path", type=str, required=True, help="Input PDB/CIF file path")
    parser.add_argument("--contig", type=str, required=True, help="Contig string in v1 format (e.g. 'A30-50/0 10-10')")
    parser.add_argument("--hotspot", type=str, default="", help="Hotspot residues e.g. A78,A79")
    parser.add_argument("--output_json", type=str, required=True, help="Output JSON path")
    parser.add_argument(
        "--spec_overrides_file",
        type=str,
        default="",
        help="Path to JSON file of spec field overrides to merge into the spec",
    )
    args = parser.parse_args()

    contig_v3 = convert_contig_v1_to_v3(args.contig)
    print(f"Converted contig: '{args.contig}' -> '{contig_v3}'")

    hotspot = args.hotspot.strip() if args.hotspot else ""
    spec_overrides = {}
    if args.spec_overrides_file:
        with open(args.spec_overrides_file) as f:
            spec_overrides = json.load(f)
    if spec_overrides:
        print(f"Applying spec overrides: {spec_overrides}")
    spec = build_spec(args.input_structure_path, contig_v3, hotspot, spec_overrides)
    output = {"design": spec}

    with open(args.output_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written input JSON to: {args.output_json}")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
