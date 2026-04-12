import os
import json
import numpy as np
import glob
import argparse
from io import StringIO
from Bio import PDB, Align, SeqIO


aa3to1 = {
    "CYS": "C",
    "ASP": "D",
    "SER": "S",
    "GLN": "Q",
    "LYS": "K",
    "ILE": "I",
    "PRO": "P",
    "THR": "T",
    "PHE": "F",
    "ASN": "N",
    "GLY": "G",
    "HIS": "H",
    "LEU": "L",
    "ARG": "R",
    "TRP": "W",
    "ALA": "A",
    "VAL": "V",
    "GLU": "E",
    "TYR": "Y",
    "MET": "M",
}


def get_atom_coordinates(
    structure: PDB.Structure.Structure,
    chain_id: str | None,
    residues: list[int] | None,
    all_atom: bool = False,
    model_index=0,
) -> tuple[list[dict[str, np.ndarray]], list[PDB.Residue.Residue]]:
    coords = []
    res_final = []

    model = structure[model_index]
    for chain in model:
        if chain_id and chain.id != chain_id:
            continue
        for residue in chain:
            if residues and residue.id[1] not in residues:
                continue
            coords_dict = {}
            for atom in residue:
                if all_atom or atom.id == "CA":
                    coords_dict[atom.id] = atom.coord
            if coords_dict:
                coords.append(coords_dict)
                res_final.append(residue)
    return coords, res_final


def align_multiple_proteins_pdb(
    pdb_strs: list[str],
    chain_residue_mappings: list[list[tuple[str, list[int] | None]] | None],
    force_sequence_alignment: bool = False,
    all_atom: bool = False,
) -> tuple[list[str], float]:
    """Aligns multiple protein structures based on their atoms (CA or all).

    :param pdb_strs: list of PDB strings
    :param chain_residue_mappings: list of lists of tuples with chain ID and residues to align,
                                   if None provided, then whole chain/structure is aligned
    :param force_sequence_alignment: if True, always align based on sequence even if lengths match
    :param all_atom: if True, align using all atoms from matched residues (not just CA atoms)
    """
    assert len(pdb_strs) == len(chain_residue_mappings), (
        f"Expected same number of structures and chain residue mappings, got {len(pdb_strs)} != {len(chain_residue_mappings)}"
    )

    parser = PDB.PDBParser(QUIET=True)
    structures = [parser.get_structure(f"Protein{i + 1}", StringIO(pdb_str)) for i, pdb_str in enumerate(pdb_strs)]
    coords_list = []
    residues_list = []

    for i, (structure, mappings) in enumerate(zip(structures, chain_residue_mappings)):
        structure_coords = []
        structure_residues = []

        if not mappings:
            coords, res_final = get_atom_coordinates(structure, None, None, all_atom=all_atom)
            if coords:
                coords_list.append(coords)
                residues_list.append(res_final)
                continue
            else:
                raise ValueError(f"No atoms found in structure {i + 1}")

        for chain_id, residues in mappings:
            coords, res_final = get_atom_coordinates(structure, chain_id, residues, all_atom=all_atom)
            if coords:
                structure_coords.extend(coords)
                structure_residues.extend(res_final)
            else:
                raise ValueError(f"No atoms found in structure {i + 1} for chain {chain_id} and residues {residues}")

        coords_list.append(structure_coords)
        residues_list.append(structure_residues)

    seqs = ["".join([aa3to1.get(residue.resname, "X") for residue in residues]) for residues in residues_list]

    sequence_alignment = force_sequence_alignment or any(len(seqs[i]) != len(seqs[0]) for i in range(1, len(seqs)))
    if sequence_alignment:
        _, aligned_seqs_indices = align_sequences(seqs)
    else:
        aligned_seqs_indices = [list(range(len(seqs[0])))] * len(seqs)

    if aligned_seqs_indices:
        print(f"Found {len(aligned_seqs_indices[1])} overlapping residues between the first and second chains.")

    super_imposer = PDB.Superimposer()

    for i in range(1, len(structures)):
        ref_atoms = []
        mod_atoms = []
        for atom_id, (ref_idx, mod_idx) in enumerate(zip(aligned_seqs_indices[0], aligned_seqs_indices[i])):
            ref_coords = coords_list[0][ref_idx]
            mod_coords = coords_list[i][mod_idx]
            shared_atom_names = sorted(set(ref_coords.keys()) & set(mod_coords.keys()))
            for atom_name in shared_atom_names:
                atom = atom_name[0]
                ref_atoms.append(PDB.Atom.Atom("X", ref_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
                mod_atoms.append(PDB.Atom.Atom("X", mod_coords[atom_name], 1.0, 1.0, " ", "X", atom_id, atom))
        super_imposer.set_atoms(ref_atoms, mod_atoms)
        super_imposer.apply(structures[i].get_atoms())

    aligned_structures_pdb = [get_aligned_structure_as_string(structure) for structure in structures]
    rmsd = super_imposer.rms
    return aligned_structures_pdb, rmsd


def align_sequences(seqs: list[str]):
    """Aligns multiple protein sequences based on their amino acid sequences.
    Returns a tuple, a list of aligned sequences and list of indices for each sequence that correspond to the aligned residues.
    """
    aligner = Align.PairwiseAligner()
    aligner.open_gap_score = -7.0
    aligner.extend_gap_score = -2.0

    alignments = []
    aligned_seqs_indices = []

    # Process first sequence as the reference
    aligned_indexes_ref = []

    # Align each sequence to the reference (seqs[0])
    for i, seq in enumerate(seqs):
        if i == 0:
            # Skip aligning the reference to itself
            continue

        # Align current sequence to reference
        alignment = sorted(aligner.align(seqs[0], seq), key=lambda x: x.score, reverse=True)[0]
        alignments.append(alignment)

        # Extract aligned indices for current sequence
        aligned_indices = [idx for start, end in alignment.aligned[1] for idx in range(start, end)]
        aligned_seqs_indices.append(aligned_indices)

        # Extract aligned indices for reference sequence (only need to do once)
        if not aligned_indexes_ref:
            aligned_indexes_ref = [idx for start, end in alignment.aligned[0] for idx in range(start, end)]

    # Insert reference sequence alignment at the beginning
    aligned_seqs_indices.insert(0, aligned_indexes_ref)

    return alignments[0], aligned_seqs_indices


def get_aligned_structure_as_string(structure) -> str:
    """Returns the PDB representation of the given structure as a string."""
    io = StringIO()
    pdb_io = PDB.PDBIO()
    pdb_io.set_structure(structure)
    pdb_io.save(io)
    return io.getvalue()


def cif_to_pdb_str(cif_path: str) -> str:
    """Load a CIF file and return its PDB representation as a string."""
    parser = PDB.MMCIFParser(QUIET=True)
    structure = parser.get_structure("struct", cif_path)
    pdb_buffer = StringIO()
    io = PDB.PDBIO()
    io.set_structure(structure)
    io.save(pdb_buffer)
    return pdb_buffer.getvalue()


def parse_remark_lines(stripped_remark_lines: list[str]) -> dict[str, str]:
    """Parse REMARK lines from PDB header.

    :param stripped_remark_lines: lines from the PDB file header, stripped of the "REMARK   1" prefix
    :return: dict with keys like "Input contig", "Standardized contig", "Chains"
    """
    REMARK_KEYS = ["Input contig", "Standardized contig", "Chains", "Input hotspots", "Standardized hotspots"]
    parsed_remark = {}

    for key in REMARK_KEYS:
        # Get lines that begin with this key
        remark_lines = [line.removeprefix(f"{key}:").strip() for line in stripped_remark_lines if line.startswith(key)]
        if not remark_lines and key not in ["Input hotspots", "Standardized hotspots"]:
            raise ValueError(f"Missing REMARK line for key: {key}")

        values = []
        for line in remark_lines:
            if not line and key not in ["Input hotspots", "Standardized hotspots"]:
                raise ValueError("Empty JSON value after key")
            if not line and key in ["Input hotspots", "Standardized hotspots"]:
                continue
            values.append(json.loads(line))

        parsed_remark[key] = "".join(values)

    return parsed_remark


def get_remark_header(pdb_str: str) -> list[str]:
    """Extract REMARK lines from PDB string.

    :param pdb_str: PDB string content
    :return: list of stripped REMARK lines (without "REMARK   1" prefix)
    """
    lines = pdb_str.split("\n")
    all_remark_lines = []
    for line in lines:
        if line.startswith("REMARK   1"):
            all_remark_lines.append(line.strip().removeprefix("REMARK   1 "))
    return all_remark_lines


def get_motif_residues(remark_dict: dict[str, str]) -> tuple[list[tuple[str, list[int]]], list[tuple[str, list[int]]]]:
    """Extract motif (fixed) residue mappings from REMARK header.

    :param remark_dict: parsed REMARK dictionary
    :return: (input_motif_residues, output_motif_residues)
        input_motif_residues: residue numbers in the native/input PDB
        output_motif_residues: residue numbers in the designed/output PDB
    """
    contigs_str = remark_dict.get("Standardized contig", None)
    chains_str = remark_dict.get("Chains", None)
    assert contigs_str, "No Standardized contig found."
    assert chains_str, "No Chains found."

    contig_chains = contigs_str.split(" ")
    chains = chains_str.split(" ")

    assert len(contig_chains) == len(chains), (
        f"Number of contigs and chains do not match: {len(contig_chains)} != {len(chains)}"
    )

    input_motif_residues = []
    output_motif_residues = []
    for output_chain_id, contig_chain in zip(chains, contig_chains):
        segments = contig_chain.removesuffix("/0").split("/")
        standard_res = 1
        first_input_res = None
        for segment in segments:
            if not segment[0].isalpha():
                # designed segment
                start_len, end_len = map(int, segment.split("-"))
                assert start_len == end_len, (
                    f"Start len and end len of design segment should coincide: {start_len} != {end_len} in {contig_chain}"
                )
                standard_res += start_len
            else:
                # fixed segment (motif)
                input_chain_id = segment[0]
                start, end = map(int, segment[1:].split("-"))
                if first_input_res is None:
                    first_input_res = start
                length = end - start + 1
                input_numbering = list(range(start, end + 1))
                standard_numbering = list(range(standard_res, standard_res + length))
                input_motif_residues.append((input_chain_id, input_numbering))

                # Use standard consecutive numbering for output
                output_motif_residues.append((output_chain_id, standard_numbering))

                standard_res += length

    return input_motif_residues, output_motif_residues


def get_chain_plddt(cif_path: str, chain_id: str) -> float:
    """Extract mean pLDDT for a specific chain from a CIF file.

    pLDDT values are stored in the B-factor column of the CIF file.
    Returns the mean pLDDT across all residues in the chain (0-100).
    """
    parser = PDB.MMCIFParser(QUIET=True)
    structure = parser.get_structure("struct", cif_path)

    # Collect pLDDT values per residue (average across atoms in each residue)
    residue_plddts = []

    for model in structure:
        if chain_id in model:
            chain = model[chain_id]
            for residue in chain:
                if PDB.is_aa(residue, standard=True):
                    # Get B-factors (pLDDT values) for all atoms in the residue
                    atom_plddts = [atom.get_bfactor() for atom in residue]
                    if atom_plddts:
                        # Average pLDDT across atoms in the residue
                        residue_plddts.append(np.mean(atom_plddts))
        break  # Only use first model

    if not residue_plddts:
        raise ValueError(f"No residues found in chain {chain_id} in {cif_path}")

    # Return mean pLDDT across all residues
    return float(np.mean(residue_plddts))


def get_ca_coords(pdb_str: str, chain_id: str) -> np.ndarray:
    """Return Nx3 NumPy array of CA coordinates from a PDB string for a given chain."""
    parser = PDB.PDBParser(QUIET=True)
    handle = StringIO(pdb_str)
    structure = parser.get_structure("struct", handle)

    ca_coords = []
    for model in structure:
        if chain_id in model:
            chain = model[chain_id]
            for res in chain:
                if PDB.is_aa(res, standard=True) and "CA" in res:
                    ca_coords.append(res["CA"].get_coord())
        break  # Only use first model

    return np.array(ca_coords)


class PDBSelector(PDB.Select):
    def __init__(self, start_residue, end_residue, chain_id):
        self.chain_id = chain_id
        self.start_residue = start_residue
        self.end_residue = end_residue

    def accept_model(self, model):
        return True  # Accept all models

    def accept_chain(self, chain):
        return chain.id == self.chain_id

    # TODO: Handle insertion codes
    def accept_residue(self, residue):
        # Accept residue if its id[1] falls within the specified range
        return self.start_residue <= residue.id[1] <= self.end_residue

    def accept_atom(self, model):
        return True  # Accept all atoms


def trim_pdb_str(pdb_input_string: str, target_chain: str, start_res: int = 1, end_res: int = 1e4) -> str:
    # Generate trimmed pdb
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("trimmed_structure", StringIO(pdb_input_string))
    io = PDB.PDBIO()
    io.set_structure(structure)

    stringIO = StringIO()
    # Save the trimmed structure as a IO string
    io.save(stringIO, select=PDBSelector(start_res, end_res, target_chain))
    return stringIO.getvalue()


def convert_predicted_cifs_to_pdbs(boltz_pubdir: str, output_pdb_dir: str) -> None:
    """Convert all predicted CIF files in the Boltz output directory to PDB format for easier downstream analysis."""
    cif_files = sorted(glob.glob(os.path.join(boltz_pubdir, "*", "*_model_0.cif")))
    test_name = os.path.basename(output_pdb_dir.rstrip("/"))
    for cif_file in cif_files:
        pdb_str = cif_to_pdb_str(cif_file)
        design_name = os.path.basename(cif_file).removesuffix("_model_0.cif")
        with open(os.path.join(output_pdb_dir, f"{design_name}_{test_name}.pdb"), "w") as f:
            f.write(pdb_str)


def compute_rmsd_binder(
    input_dir: str,
    boltz_pubdir: str,
    binder_chain: str,
    output_metrics_path: str,
) -> None:
    # Auto-detect target chains from the first PDB file
    # Target chains are defined as all chains that are not the binder chain
    all_pdbs = sorted(glob.glob(os.path.join(input_dir, "*.pdb")))
    first_pdb = all_pdbs[0]

    # Use SeqIO to parse chains (same logic as prepare_inputs.py)
    chains = list(SeqIO.parse(first_pdb, "pdb-atom"))
    all_chain_ids = set()
    for chain in chains:
        chain_id = chain.annotations["chain"]
        all_chain_ids.add(chain_id)

    target_chains_list = sorted([chain_id for chain_id in all_chain_ids if chain_id != binder_chain])

    if not target_chains_list:
        raise ValueError(f"No target chains found in {first_pdb}. All chains are binder chain '{binder_chain}'.")

    print(f"Auto-detected target chains: {target_chains_list}")
    print(f"Binder chain: {binder_chain}")

    results = []
    for pdb_path in all_pdbs:
        name = os.path.basename(pdb_path).removesuffix(".pdb")
        boltz_cif_path = os.path.join(boltz_pubdir, name, name + "_model_0.cif")
        boltz_str = cif_to_pdb_str(boltz_cif_path)

        with open(pdb_path) as f:
            input_pdb_str = f.read()

        # Build chain residue mappings for all target chains
        target_chain_mappings = [(chain_id, None) for chain_id in target_chains_list]

        aligned_pdbs, full_rmsd = align_multiple_proteins_pdb(
            [input_pdb_str, boltz_str],
            chain_residue_mappings=[
                target_chain_mappings,
                target_chain_mappings,
            ],
            all_atom=True,
        )

        mpnn_binder_str = trim_pdb_str(input_pdb_str, binder_chain)
        aligned_binder_str = trim_pdb_str(aligned_pdbs[1], binder_chain)

        mpnn_coords = get_ca_coords(mpnn_binder_str, binder_chain)
        aligned_coords = get_ca_coords(aligned_binder_str, binder_chain)
        diff = mpnn_coords - aligned_coords
        binder_rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1))).item()

        # Extract binder pLDDT from the Boltz prediction CIF file
        binder_plddt = get_chain_plddt(boltz_cif_path, binder_chain)

        with open(
            os.path.join(boltz_pubdir, name, "confidence_" + name + "_model_0.json"),
            "r",
        ) as f:
            metrics = json.load(f)

        results.append(
            {
                "id": name,
                "complex_rmsd": full_rmsd,
                "binder_rmsd": binder_rmsd,
                "binder_plddt": binder_plddt / 100,  # convert to 0-1 range for consistency with Boltz JSON
                **metrics,
            }
        )

    with open(output_metrics_path, "w") as f:
        for result in results:
            json.dump(result, f)
            f.write("\n")


def compute_rmsd_scaffold(
    input_dir: str, boltz_pubdir: str, chain: str, output_metrics_path: str, native_pdb_path: str | None = None
) -> None:
    assert len(chain) == 1, f'Expected a single chain ID for scaffold design, got "{chain}", {len(chain)=}.'

    # Load native PDB if provided
    native_pdb_str = None
    if native_pdb_path:
        with open(native_pdb_path, "r") as f:
            native_pdb_str = f.read()
        print(f"Loaded native PDB from: {native_pdb_path}")

    results = []
    for pdb_input_file_path in glob.glob(os.path.join(input_dir, "*.pdb")):
        name = os.path.basename(pdb_input_file_path).removesuffix(".pdb")
        boltz_cif_path = os.path.join(boltz_pubdir, name, name + "_model_0.cif")
        boltz_str = cif_to_pdb_str(boltz_cif_path)

        with open(pdb_input_file_path) as f:
            input_pdb_str = f.read()

        aligned_pdbs, full_rmsd = align_multiple_proteins_pdb(
            [input_pdb_str, boltz_str],
            chain_residue_mappings=[
                [(chain, None)],
                [(chain, None)],
            ],
            all_atom=True,
        )

        with open(
            os.path.join(boltz_pubdir, name, "confidence_" + name + "_model_0.json"),
            "r",
        ) as f:
            metrics = json.load(f)

        result = {
            "id": name,
            "design_rmsd": full_rmsd,
            **metrics,
        }

        # Calculate native motif RMSD if native PDB is provided
        if native_pdb_str:
            remark_lines = get_remark_header(input_pdb_str)
            if remark_lines:
                remark_dict = parse_remark_lines(remark_lines)
                input_motif_residues, output_motif_residues = get_motif_residues(remark_dict)
                print(f"  Computing native motif RMSD for {name}")
                print(f"    Native motif mapping: {input_motif_residues}")
                print(f"    Predicted motif mapping: {output_motif_residues}")
                _, native_motif_rmsd = align_multiple_proteins_pdb(
                    [native_pdb_str, boltz_str],
                    chain_residue_mappings=[input_motif_residues, output_motif_residues],
                    all_atom=True,
                )
                result["native_motif_rmsd"] = native_motif_rmsd
            else:
                print(f"  Warning: No REMARK header found in {name}, skipping native motif RMSD")

        results.append(result)

    with open(output_metrics_path, "w") as f:
        for result in results:
            json.dump(result, f)
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to directory containing [Protein/Ligand]MPNN structure files.",
    )
    parser.add_argument(
        "--boltz_pubdir",
        type=str,
        required=True,
        help="Path to the directory containing Boltz prediction MMCIF files.",
    )
    parser.add_argument(
        "--design_type",
        type=str,
        choices=["scaffold", "binder"],
        required=True,
        help="Type of design to determine which chain to analyze for RMSD calculation.",
    )
    parser.add_argument(
        "--cyclic",
        action="store_true",
        help="Not used, for compatibility with run_parameters from perpare_inputs.py, which is used in both scaffold and binder contexts. Ignored in compute_rmsd.",
    )
    parser.add_argument(
        "--chains",
        "--designed_chains",
        type=str,
        default="A",
        help="Chain ID for the binder/designed chain, e.g. 'A'. For scaffold design, can be comma-separated list. Default: 'A'.",
    )
    parser.add_argument(
        "--boltz_version",
        type=str,
        default="boltz2",
        choices=["boltz1", "boltz2"],
        help="Version of Boltz used, e.g. 'boltz1' or 'boltz2'. Default: 'boltz2'. Used to determine expected file naming conventions in Boltz output directory.",
    )
    parser.add_argument(
        "--no-template",
        action="store_true",
        default=False,
        help="Not used, for compatibility with run_parameters from perpare_inputs.py.",
    )
    parser.add_argument(
        "--output_metrics_path",
        type=str,
        required=True,
        help="Path to the output metrics file (JSONL format).",
    )
    parser.add_argument(
        "--output_pdb_dir",
        type=str,
        required=True,
        help="Path to the output directory for PDB files.",
    )
    parser.add_argument(
        "--native_pdb",
        type=str,
        required=False,
        help="Path to native PDB structure for computing native motif RMSD (scaffold design only).",
    )
    args = parser.parse_args()

    os.makedirs(args.output_pdb_dir, exist_ok=True)
    if args.design_type == "scaffold":
        compute_rmsd_scaffold(
            input_dir=args.input_dir,
            boltz_pubdir=args.boltz_pubdir,
            chain=args.chains,
            output_metrics_path=args.output_metrics_path,
            native_pdb_path=args.native_pdb,
        )
    elif args.design_type == "binder":
        compute_rmsd_binder(
            input_dir=args.input_dir,
            boltz_pubdir=args.boltz_pubdir,
            binder_chain=args.chains,
            output_metrics_path=args.output_metrics_path,
        )
    else:
        raise ValueError(f"Unsupported design type: {args.design_type}")

    # convert cif to pdb and move to batch_dir/test_name/design_id_test_name.pdb
    convert_predicted_cifs_to_pdbs(args.boltz_pubdir, args.output_pdb_dir)
