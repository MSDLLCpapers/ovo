"""Prepend the ligand REMARK header to a DISCO packed PDB.

DISCO writes the ligand it was given to ``<design>_ligands.txt`` next to the raw PDB
(``ligand_smiles <value>`` lines, one per ligand). The packed PDB carries no bond orders, so
refolding would have to perceive the ligand from coordinates, which corrupts it (benzene
becomes cyclohexane, C=O becomes C-OH). Writing the ground-truth ligand into the PDB header
instead makes the packed PDB self-describing: refolding reads the header and never guesses.

DISCO accepts a ligand in three forms (see ``build_ligand`` in its ``json_parser``), each
mapped here to the Boltz ligand entity that refolding needs:

* a SMILES string -> ``REMARK   1 Ligand SMILES: "<SMILES>"``
* ``CCD_<CODE>`` (or ``CCD_<A>_<B>`` for multi-component ligands such as glycans)
  -> one ``REMARK   1 Ligand CCD: "<CODE>"`` per component code
* ``FILE_<path>`` (an uploaded mol/mol2/sdf/pdb) -> read with RDKit here, inside the DISCO
  container where the file exists, and written out as a SMILES remark

One remark per entity, in the order DISCO lists the ligands, quoted like the standardized
RFdiffusion remarks (neither SMILES nor CCD codes contain spaces, so they are never chunked).
"""

import argparse
import os
import pathlib

SMILES_REMARK = 'REMARK   1 Ligand SMILES: "{}"\n'
CCD_REMARK = 'REMARK   1 Ligand CCD: "{}"\n'


def format_ligand_remarks(ligands_txt: str) -> str:
    """Return the REMARK header for the ligands in a DISCO ``_ligands.txt``, "" if it lists none."""
    values = [
        line.removeprefix("ligand_smiles ").strip()
        for line in ligands_txt.splitlines()
        if line.startswith("ligand_smiles ")
    ]
    return "".join(format_ligand_remark(value) for value in values if value)


def format_ligand_remark(value: str) -> str:
    """Return the REMARK line(s) for a single DISCO ligand value, "" if it cannot be declared."""
    if value.startswith("CCD_"):
        # Multi-component ligands are underscore-joined CCD codes, each its own Boltz entity.
        return "".join(CCD_REMARK.format(code) for code in value.removeprefix("CCD_").split("_"))
    if value.startswith("FILE_"):
        smiles = read_file_smiles(value.removeprefix("FILE_"))
        return SMILES_REMARK.format(smiles) if smiles else ""
    return SMILES_REMARK.format(value)


def read_file_smiles(ligand_file: str) -> str:
    """Return the SMILES of an uploaded ligand file, "" if its chemistry cannot be recovered.

    Same suffixes and loaders as DISCO's own ``lig_file_to_atom_info``, so any file DISCO
    accepted as input can also be read back here.
    """
    from rdkit import Chem
    from rdkit.Chem import rdDetermineBonds

    # DISCO records the path it resolved the ligand to (relative paths against its own install
    # dir), while OVO stages uploads into the task working directory, so look there too.
    if not os.path.isfile(ligand_file) and os.path.isfile(os.path.basename(ligand_file)):
        ligand_file = os.path.basename(ligand_file)

    # Read without sanitizing: the bond orders are checked (and possibly repaired) first.
    if ligand_file.endswith(".mol"):
        mol = Chem.MolFromMolFile(ligand_file, sanitize=False, removeHs=False)
    elif ligand_file.endswith(".sdf"):
        mol = next(Chem.SDMolSupplier(ligand_file, sanitize=False, removeHs=False))
    elif ligand_file.endswith(".pdb"):
        mol = Chem.MolFromPDBFile(ligand_file, sanitize=False, removeHs=False)
    elif ligand_file.endswith(".mol2"):
        mol = Chem.MolFromMol2File(ligand_file, sanitize=False, removeHs=False)
    else:
        raise ValueError(f"Invalid ligand file type: {ligand_file}, expected one of [mol, mol2, sdf, pdb]")
    assert mol is not None, f"RDKit could not read the ligand file DISCO was given: {ligand_file}"

    bonds = list(mol.GetBonds())
    if bonds and all(bond.GetBondType() == Chem.BondType.SINGLE for bond in bonds):
        # A bare 3D geometry dump (every bond single, as PDB files and some SDF writers produce)
        # would serialize to nonsense: amides come out as C(N)O, phosphates as [PH](O)(O)O, aromatic
        # rings saturated. Infer the orders from the geometry instead. RDKit has no valence model
        # for metals, so this gives up on metal complexes - those need a CCD code or a SMILES.
        try:
            rdDetermineBonds.DetermineBondOrders(mol)
        except ValueError as error:
            # "[Warning]" is the prefix OVO collects into job.warnings to show in the app
            print(
                f"[Warning] The ligand file {os.path.basename(ligand_file)} carries no bond orders and "
                f"they cannot be inferred from its geometry ({error}), so the ligand is left out of the "
                f"design and refolding runs on the protein alone. Submit this ligand as 'CCD_<code>' or "
                f"as a SMILES string to refold the complex."
            )
            return ""

    Chem.SanitizeMol(mol)
    return Chem.MolToSmiles(Chem.RemoveHs(mol))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdb", required=True, help="Packed PDB to prepend the REMARK header to, in place")
    parser.add_argument("--ligands-txt", required=True, help="DISCO <design>_ligands.txt sidecar")
    args = parser.parse_args()

    remarks = format_ligand_remarks(pathlib.Path(args.ligands_txt).read_text())
    if remarks:
        pdb = pathlib.Path(args.pdb)
        pdb.write_text(remarks + pdb.read_text())
