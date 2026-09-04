import os
import warnings
import glob
import yaml
import argparse
from dataclasses import dataclass
from Bio import SeqIO

warnings.simplefilter(action="ignore")

# Directory for the template mmCIF files, relative to the working directory. Boltz resolves the
# template path of a yaml input relative to the working directory, not to the yaml file.
TEMPLATES_DIR = "templates"


def _write_boltz_cif(st, output_path: str) -> str:
    """Add the entity metadata that Boltz needs for template parsing and write the mmCIF.

    Boltz reads templates through gemmi's make_structure_from_block(), which produces empty
    entities (and then fails with a KeyError on chain lookup) unless _entity, _entity_poly,
    _entity_poly_seq and _struct_asym are present.
    """
    import gemmi

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

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    st.make_mmcif_document().write_file(output_path)
    return output_path


def convert_to_boltz_cif(input_path: str, output_path: str | None = None, chains: list[str] | None = None) -> str:
    """Convert a PDB or CIF file to a Boltz-compatible mmCIF with full entity metadata.

    :param chains: keep only the given chains, used to turn a design structure into a target template
    """
    import gemmi

    st = gemmi.read_structure(input_path)
    if chains is not None:
        for model in st:
            for chain in [chain.name for chain in model if chain.name not in chains]:
                model.remove_chain(chain)

    if output_path is None:
        base = os.path.basename(input_path)
        stem, ext = os.path.splitext(base)
        if ext.lower() == ".cif":
            stem = f"{stem}_processed"
        output_path = os.path.join(TEMPLATES_DIR, f"{stem}.cif")

    return _write_boltz_cif(st, output_path)


# Maximum length of the peptide bond between two consecutive residues, anything longer is a chain
# break (the same criterion and cutoff as check_rfdiffusion_input in ovo.core.utils.pdb)
MAX_AMIDE_DISTANCE = 3.0
# Fallback cutoff on the Ca-Ca distance, used when a residue is missing its backbone C or N atom
MAX_CA_DISTANCE = 4.5


def is_chain_break(previous_residue, residue) -> bool:
    """Whether two consecutive residues of a chain are not connected by a peptide bond.

    Takes gemmi residues. Uses the C-N distance, falling back to the Ca-Ca distance if either
    backbone atom is missing.
    """
    previous_atom, atom, cutoff = previous_residue.find_atom("C", "*"), residue.find_atom("N", "*"), MAX_AMIDE_DISTANCE
    if previous_atom is None or atom is None:
        previous_atom, atom, cutoff = (
            previous_residue.find_atom("CA", "*"),
            residue.find_atom("CA", "*"),
            MAX_CA_DISTANCE,
        )
    if previous_atom is None or atom is None:
        # Nothing to measure, keep the residues in the same segment
        return False
    return previous_atom.pos.dist(atom.pos) > cutoff


@dataclass
class TargetSegment:
    """One contiguous piece of a target chain, given to Boltz as its own chain."""

    chain_id: str  # chain ID of this segment in the Boltz input
    source_chain: str  # chain ID of the design structure this segment was cut from
    first_res: int  # first residue number in the design structure (inclusive)
    last_res: int  # last residue number in the design structure (inclusive)
    sequence: str

    def __str__(self) -> str:
        source = f"{self.source_chain}{self.first_res}-{self.last_res}"
        return f"chain {self.chain_id} ({source}, {len(self.sequence)} residues)"


def read_binder_and_target_segments(input_path: str, binder_chain: str) -> tuple[str, list[TargetSegment]]:
    """Read the binder sequence and the target segments of a design structure.

    Designs against a patch of a larger target keep the pieces of that patch in a single chain,
    separated by jumps in the residue numbering (for example 1-49, 100-147, 198-217, ...). Boltz
    cannot express a chain break: a chain is one contiguous polymer, and the sequence of a chain
    read as a whole would pad every jump with unknown residues that Boltz then models as real UNK
    residues linking the pieces. Each piece is therefore given to Boltz as a separate chain, and
    the target template (see :func:`write_target_template_cif`) keeps them in the same one file so
    that their relative arrangement is preserved.

    A chain is cut wherever its residue numbering jumps or its backbone is not connected (see
    :func:`is_chain_break`), so a break that was not marked in the numbering is split as well.

    A target chain that is not broken keeps its own chain ID, so ordinary binder designs are
    unaffected. The segments of a split chain are named after it: chain B becomes B1, B2, ...

    :return: (binder sequence, target segments in the order they appear in the structure)
    """
    import gemmi

    st = gemmi.read_structure(input_path)
    st.setup_entities()
    model = st[0]

    binder_sequence = None
    segments_by_chain = {}
    for chain in model:
        residues = list(chain.get_polymer())
        if not residues:
            continue
        if chain.name == binder_chain:
            binder_sequence = gemmi.one_letter_code([res.name for res in residues]).upper()
            continue
        chain_segments = []
        previous_residue = None
        for res in residues:
            continues = (
                previous_residue is not None
                and res.seqid.num == chain_segments[-1][1] + 1
                and not is_chain_break(previous_residue, res)
            )
            if continues:
                chain_segments[-1][1] = res.seqid.num
                chain_segments[-1][2].append(res.name)
            else:
                chain_segments.append([res.seqid.num, res.seqid.num, [res.name]])
            previous_residue = res
        segments_by_chain[chain.name] = chain_segments

    assert binder_sequence, f"Binder chain {binder_chain} not found in {input_path}"

    taken_chain_ids = {binder_chain} | set(segments_by_chain)

    segments = []
    for source_chain, chain_segments in segments_by_chain.items():
        for i, (first_res, last_res, res_names) in enumerate(chain_segments):
            # The segments of a split chain are named after it - B becomes B1, B2, ...,
            # which both mmCIF and Boltz allow (see the chain name dtype in boltz.data.types).
            # The PDB format does not, the segments are merged back into the chain of the design
            # before the prediction is written as PDB (see restore_design_target_chains in calculate_metrics.py).
            chain_id = source_chain if len(chain_segments) == 1 else f"{source_chain}{i + 1}"
            assert chain_id == source_chain or chain_id not in taken_chain_ids, (
                f"Chain ID {chain_id} of a segment of chain {source_chain} is already used in {input_path}"
            )
            segments.append(
                TargetSegment(
                    chain_id=chain_id,
                    source_chain=source_chain,
                    first_res=first_res,
                    last_res=last_res,
                    sequence=gemmi.one_letter_code(res_names).upper(),
                )
            )

    return binder_sequence, segments


def write_target_template_cif(input_path: str, output_path: str, segments: list[TargetSegment]) -> str:
    """Write a Boltz template holding the target segments of a design, one chain per segment.

    All segments go into a single template file on purpose: Boltz gives every chain templated from
    the same file the same visibility ID (see boltz.data.feature.featurizerv2), and the template
    pair features are masked to pairs that share a visibility ID, so the template constrains the
    arrangement of the segments relative to each other and not just each segment on its own.

    Segments are renumbered from 1, the residue numbering of the design is not needed here: Boltz
    matches template to query chain by aligning their sequences.
    """
    import gemmi

    st = gemmi.read_structure(input_path)
    st.setup_entities()
    source_model = st[0]

    template = gemmi.Structure()
    template.name = os.path.basename(output_path).removesuffix(".cif")
    model = gemmi.Model("1")
    for segment in segments:
        chain = gemmi.Chain(segment.chain_id)
        for res in source_model[segment.source_chain].get_polymer():
            if segment.first_res <= res.seqid.num <= segment.last_res:
                chain.add_residue(res)
                chain[-1].seqid = gemmi.SeqId(len(chain), " ")
                # The residues carry the subchain of the source chain, which setup_entities() would
                # keep, giving every segment the same label_asym_id (and entity) in the written cif
                chain[-1].subchain = ""
        assert len(chain) == len(segment.sequence), (
            f"Expected {len(segment.sequence)} residues in template {segment}, got {len(chain)}"
        )
        model.add_chain(chain)
    template.add_model(model)

    return _write_boltz_cif(template, output_path)


def get_boltz_template_chain_ids(template_cif: str, chains: list[str]) -> list[str]:
    """Return the template chain IDs that Boltz expects for the given chains of a converted template.

    Boltz names template chains after their mmCIF label_asym_id (see boltz.data.parse.mmcif, which
    builds chains from subchains), and gemmi's setup_entities() writes a suffixed subchain, turning
    chain "B" into "Bxp". The original chain IDs therefore cannot be used as "template_id" directly.

    :param template_cif: mmCIF written by :func:`convert_to_boltz_cif`
    :param chains: chain IDs as they appear in the original structure, e.g. ["B"]
    """
    import gemmi

    st = gemmi.read_structure(template_cif)
    template_ids = []
    for chain_id in chains:
        chain = st[0].find_chain(chain_id)
        assert chain is not None, f"Chain {chain_id} not found in template {template_cif}"
        polymer = chain.get_polymer()
        template_ids.append((polymer.subchain_id() if len(polymer) else chain[0].subchain) or chain_id)
    return template_ids


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
                "cif": template,
                # copy to avoid issues with references in yaml
                "chain_id": chains.copy(),
            }

            if template_chains is not None and "," in template_chains:
                template_entry["template_id"] = get_boltz_template_chain_ids(template, template_chains.split(","))

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
    template_from_design: bool = False,
):
    """
    Prepares input files for Boltz. Converts PDB files (outputs of Protein/Ligand MPNN) to YAML format.
    Currently the code assumes the target can be a same sequence with multiple ids, e.g. homo-k-mers.

    A target chain that is broken up by jumps in its residue numbering or by its backbone is given
    to Boltz as one chain
    per segment, see :func:`read_binder_and_target_segments`.

    If binder_alone is True, only the binder chain is predicted, without the target chains.

    If template_from_design is True, the target template of each design is taken from the target
    chains of that design, the same way as the AlphaFold2 initial guess tests do it. This does not
    need a separate target structure, which is not available for designs uploaded from PDB files.
    """

    if isinstance(binder_chain, list):
        assert len(binder_chain) == 1, f"Binder chain must be a single chain, got {binder_chain=}"
        binder_chain = binder_chain[0]

    assert len(binder_chain) == 1, f"Binder chain ID must be a single character, got {binder_chain=}"

    paths = sorted(glob.glob(os.path.join(input_dir, "*.pdb")))
    structures = {}
    for path in paths:
        name = os.path.basename(path).removesuffix(".pdb")
        binder_seq, segments = read_binder_and_target_segments(path, binder_chain=binder_chain)
        print(f"{name}: binder chain {binder_chain} ({len(binder_seq)} residues), target segments:")
        for segment in segments:
            print(f"  {segment}")
        structures[name] = (path, binder_seq, segments)

    if binder_alone:
        assert target_template is None, "Cannot use a target template when predicting the binder alone"
        assert not template_from_design, "Cannot use a target template when predicting the binder alone"
        # Drop the target chains, only the binder sequence is predicted
        structures = {name: (path, binder_seq, []) for name, (path, binder_seq, _) in structures.items()}

    if target_template is not None:
        assert not template_from_design, "Cannot use both a target template file and the design as template"
        split_chains = {
            segment.source_chain
            for _, _, segments in structures.values()
            for segment in segments
            if segment.chain_id != segment.source_chain
        }
        assert not split_chains, (
            f"Target chain(s) {sorted(split_chains)} are broken up into segments, "
            "which can only be templated from the design itself (--template_from_design)"
        )
        target_template = convert_to_boltz_cif(target_template)

    if target_template_chains is not None:
        target_template_chains = target_template_chains.split(",")

    os.makedirs(output_dir, exist_ok=True)
    for name, (path, binder_seq, segments) in structures.items():
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

        # Add all target sequences, one chain per segment
        for segment in segments:
            sequences.append(
                {
                    "protein": {
                        "id": segment.chain_id,
                        "sequence": segment.sequence,
                        "msa": "empty",
                    },
                }
            )

        input_dict = {
            "sequences": sequences,
            "version": 1,
        }

        design_target_chains = [segment.chain_id for segment in segments]
        design_template = None
        if template_from_design and design_target_chains:
            # Template on the target chains of the design itself, the binder chain is left out
            design_template = write_target_template_cif(
                path, output_path=os.path.join(TEMPLATES_DIR, f"{name}_target_template.cif"), segments=segments
            )

        if target_template is not None or design_template is not None:
            template_path = design_template if design_template is not None else target_template
            assert template_path.endswith(".cif"), (
                f"Target template must be in mmCIF format after conversion, got {template_path=}"
            )
            template_entry = {
                "cif": template_path,
                # copy to avoid issues with references in yaml
                "chain_id": design_target_chains.copy(),
            }

            if design_template is not None:
                # The design cif holds the same target chains as the predicted complex
                template_entry["template_id"] = get_boltz_template_chain_ids(design_template, design_target_chains)
            elif target_template_chains is not None:
                template_entry["template_id"] = get_boltz_template_chain_ids(target_template, target_template_chains)

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
        "--template_from_design",
        action="store_true",
        default=False,
        help="""
            Use the target chains of each design as its target template (binder design only).
            This does not need a separate target structure, which is not available for designs
            uploaded from PDB files. Default: False.""",
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
            template_from_design=args.template_from_design and not args.no_template and not args.binder_alone,
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
