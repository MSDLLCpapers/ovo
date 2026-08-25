import os
import warnings
import glob
import yaml
import argparse
import re
from Bio import SeqIO

warnings.simplefilter(action="ignore")


def convert_to_boltz_cif(input_path: str, output_path: str | None = None) -> str:
    """Convert a PDB or CIF file to a Boltz-compatible mmCIF with full entity metadata.

    Uses gemmi to add required mmCIF categories (_entity, _entity_poly,
    _entity_poly_seq, _struct_asym) that Boltz needs for template parsing.
    Without these, gemmi's make_structure_from_block() produces empty entities
    and Boltz fails with KeyError on chain lookup.
    """
    import gemmi

    st = gemmi.read_structure(input_path)
    st.setup_entities()
    st.assign_label_seq_id()

    seqs = []
    for ent in st.entities:
        if ent.entity_type == gemmi.EntityType.Polymer and ent.subchains:
            polymer = st[0].get_subchain(ent.subchains[0])
            seqs.append(gemmi.one_letter_code([res.name for res in polymer]))
        else:
            seqs.append("")
    st.assign_best_sequences(seqs)

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        if ext.lower() == ".cif":
            output_path = f"{base}_processed.cif"
        else:
            output_path = f"{base}.cif"

    st.make_mmcif_document().write_file(output_path)
    return output_path


def prepare_inputs_scaffold(
    input_dir: str,
    output_dir: str,
    chains: str | list[str],
    template: str | None = None,
    template_chains: str | None = None,
    template_force_threshold: float | None = None,
    **kwargs,
):
    if isinstance(chains, str):
        chains = chains.split(",")

    paths = sorted(glob.glob(os.path.join(input_dir, "*.pdb")))
    structures = {}
    for path in paths:
        name = os.path.basename(path).removesuffix(".pdb")
        structure_chains = list(SeqIO.parse(path, "pdb-atom"))
        print(f"{structure_chains=}")
        print(f"{chains=}")
        print(f"{[chain.annotations for chain in structure_chains]=}")
        parsed_chains = []
        for chain in structure_chains:
            if chain.annotations["chain"] in chains:
                parsed_chains.append((chain.annotations["chain"], str(chain.seq)))
        print(f"{parsed_chains=}")
        structures[name] = parsed_chains

    if template is not None:
        template = convert_to_boltz_cif(template)

    os.makedirs(output_dir, exist_ok=True)
    for name, parsed_chains in structures.items():
        input_dict = {
            "sequences": [
                {
                    "protein": {
                        "id": chain_id,
                        "sequence": seq,
                        "msa": "empty",
                    },
                }
                for chain_id, seq in parsed_chains
            ],
            "version": 1,
        }

        if template is not None:
            template_entry = {
                "cif": os.path.basename(template),
                # copy to avoid issues with references in yaml
                "chain_id": chains.copy(),
            }

            if template_chains is not None and "," in template_chains:
                template_entry["template_id"] = template_chains.split(",")

            if template_force_threshold is not None:
                template_entry["force"] = True
                template_entry["threshold"] = template_force_threshold

            input_dict["templates"] = [template_entry]

        with open(os.path.join(output_dir, f"{name}.yaml"), "w") as f:
            yaml.dump(input_dict, f)


def prepare_inputs_binder(
    input_dir: str,
    output_dir: str,
    # target_chains: str,
    cyclic: bool = False,
    target_template: str | None = None,
    target_template_chains: str | None = None,
    binder_chain: str | list[str] = "A",
    template_force_threshold: float | None = None,
    binder_alone: bool = False,
):
    """
    Prepares input files for Boltz. Converts PDB files (outputs of Protein/Ligand MPNN) to YAML format.
    Currently the code assumes the target can be a same sequence with multiple ids, e.g. homo-k-mers.

    If binder_alone is True, only the binder chain is predicted, without the target chains.
    """

    if isinstance(binder_chain, list):
        assert len(binder_chain) == 1, f"Binder chain must be a single chain, got {binder_chain=}"
        binder_chain = binder_chain[0]

    assert len(binder_chain) == 1, f"Binder chain ID must be a single character, got {binder_chain=}"

    paths = sorted(glob.glob(os.path.join(input_dir, "*.pdb")))
    structures = {}
    target_chains_set = set()
    for path in paths:
        name = os.path.basename(path).removesuffix(".pdb")
        chains = list(SeqIO.parse(path, "pdb-atom"))
        print(f"{chains=}")
        binder_seq = None
        target_seqs = []  # List of (chain_id, sequence) tuples
        for chain in chains:
            chain_id = chain.annotations["chain"]
            if chain_id == binder_chain:
                binder_seq = str(chain.seq)
            else:
                target_seqs.append((chain_id, str(chain.seq)))
                target_chains_set.add(chain_id)
        structures[name] = (binder_seq, target_seqs)

    target_chains = sorted(target_chains_set)

    if binder_alone:
        assert target_template is None, "Cannot use a target template when predicting the binder alone"
        # Drop the target chains, only the binder sequence is predicted
        structures = {name: (binder_seq, []) for name, (binder_seq, _) in structures.items()}

    if target_template is not None:
        target_template = convert_to_boltz_cif(target_template)

    if target_template_chains is not None:
        target_template_chains = target_template_chains.split(",")

    os.makedirs(output_dir, exist_ok=True)
    for name, (binder_seq, target_seqs) in structures.items():
        # Build sequences list starting with binder
        sequences = [
            {
                "protein": {
                    "id": binder_chain,
                    "sequence": binder_seq,
                    "msa": "empty",
                    "cyclic": cyclic,
                },
            },
        ]

        # Add all target sequences
        for target_chain_id, target_seq in target_seqs:
            sequences.append(
                {
                    "protein": {
                        "id": target_chain_id,
                        "sequence": target_seq,
                        "msa": "empty",
                    },
                }
            )

        input_dict = {
            "sequences": sequences,
            "version": 1,
        }

        if target_template is not None:
            assert target_template.endswith(".cif"), (
                f"Target template must be in mmCIF format after conversion, got {target_template=}"
            )
            template_entry = {
                "cif": os.path.basename(target_template),
                # copy to avoid issues with references in yaml
                "chain_id": target_chains.copy(),
            }

            if target_template_chains is not None:
                template_entry["template_id"] = target_template_chains.copy()

            if template_force_threshold is not None:
                template_entry["force"] = True
                template_entry["threshold"] = template_force_threshold

            input_dict["templates"] = [template_entry]

        print(f"{input_dict=}")
        with open(os.path.join(output_dir, f"{name}.yaml"), "w") as f:
            yaml.dump(input_dict, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="""
            Path to the input directory containing PDB files,
            typically output of [Protein/Ligand]MPNN.
            Each is assumed to have a chain A (binder) and chain B (target).
        """,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to the output directory for YAML files to be used as inputs for Boltz.",
    )
    parser.add_argument(
        "--cyclic",
        action="store_true",
        default=False,
        help="Specify if the binder is cyclic. Default: False.",
    )
    parser.add_argument(
        "--chains",
        "--designed_chains",
        type=str,
        default="A",
        help="Comma-separated list of designed chain IDs for the target molecule, e.g. 'A' or 'A,B'. Default: 'A'.",
    )
    # parser.add_argument(
    #     "--binder_chain",
    #     type=str,
    #     default="A",
    #     help="Chain ID for the binder molecule. Default: 'A'.",
    # )
    parser.add_argument(
        "--template",
        type=str,
        required=False,
        help="Path to the target template file (PDB or mmCIF format).",
    )
    parser.add_argument(
        "--template_force_threshold",
        type=float,
        default=None,
        help="Force threshold for template matching. Default: None.",
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        default=False,
        help="Do not use template input (overrides --template if provided). Default: False.",
    )
    parser.add_argument(
        "--design_type",
        type=str,
        default=None,
        help="Design type for refolding tests. Either 'scaffold' or 'binder'. Default: None.",
    )
    parser.add_argument(
        "--binder-alone",
        action="store_true",
        default=False,
        help="Predict only the binder structure, without the target. Default: False.",
    )
    parser.add_argument(
        "--template_chains",
        type=str,
        default=None,
        help="""
            Comma-separated list of chain IDs for the target template, e.g. 'B' or 'B,C,D'. 
            In case of cif assembly, symmetric chains are often provided in this format: B,B-2,B-3. 
            Default: 'B'.""",
    )
    args = parser.parse_args()

    if args.design_type == "binder":
        print(f"{args.chains=}")
        prepare_inputs_binder(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            cyclic=args.cyclic,
            binder_chain=args.chains,
            # target_chains=args.chains,
            target_template=None if args.no_template else args.template,
            target_template_chains=args.template_chains,
            template_force_threshold=args.template_force_threshold,
            binder_alone=args.binder_alone,
        )
    elif args.design_type == "scaffold":
        prepare_inputs_scaffold(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            chains=args.chains,
            template=None if args.no_template else args.template,
            template_chains=args.template_chains,
            template_force_threshold=args.template_force_threshold,
        )
    else:
        raise ValueError(f"Invalid design type specified {args.design_type}. Must be either 'scaffold' or 'binder'.")
