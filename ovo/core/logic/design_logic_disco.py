import json
import os
import re
from io import StringIO
from typing import Callable

import pandas as pd

from ovo import storage, Pool, Round, db, get_scheduler
from ovo.core.database import DesignJob, DesignSpec, Design, Base, DescriptorValue
from ovo.core.database.models_disco import DiscoWorkflow
from ovo.core.database.models_refolding import RefoldingWorkflow
from ovo.core.database import descriptors_disco
from ovo.core.logic.descriptor_logic import read_descriptor_file_values, save_descriptor_job_for_design_job
from ovo.core.logic.design_logic import set_designs_accepted
from ovo.core.utils.formatting import safe_filename


def _ligand_slug(ligand: str) -> str:
    """Derive a short, filesystem-safe slug from a ligand string for use as the DISCO job name."""
    if ligand.startswith("CCD_"):
        return safe_filename(ligand[len("CCD_") :]) or "ligand"
    if ligand.startswith("FILE_"):
        # Use the file's base name without extension
        base = os.path.splitext(os.path.basename(ligand[len("FILE_") :]))[0]
        return safe_filename(base) or "ligand"
    # SMILES or other: not filename-safe, use a generic slug
    return "smiles"


def build_disco_input_json(workflow: DiscoWorkflow, ligand_value: str | None = None) -> list[dict]:
    """Build the DISCO input JSON (a list with a single job) from the workflow params.

    :param workflow: the DISCO workflow
    :param ligand_value: override for the ligand string written into the JSON (e.g. a staged "FILE_<path>");
        defaults to workflow.disco_params.ligand
    """
    params = workflow.disco_params
    ligand = ligand_value if ligand_value is not None else params.ligand
    sequence_length = params.sequence_length

    sequences = [{"proteinChain": {"sequence": "-" * sequence_length, "count": 1}}]
    if ligand:
        sequences.append({"ligand": {"ligand": ligand, "count": 1}})

    name = f"length_{sequence_length}"
    if ligand:
        name += f"_{_ligand_slug(ligand)}"

    return [{"sequences": sequences, "name": name}]


def prepare_disco_params(workflow: DiscoWorkflow, workdir: str) -> dict:
    params = workflow.disco_params

    # Staged ligand file path passed to the pipeline; left unset (the pipeline falls back to its NO_FILE
    # sentinel) unless an uploaded ligand file is used.
    ligand_file = None

    if params.custom_input_json:
        # Advanced mode: the user supplied the full DISCO input JSON verbatim.
        input_json = storage.prepare_workflow_input(
            "input.json",
            workdir=workdir,
            input_bytes=params.custom_input_json.encode("utf-8"),
        )
    elif params.input_json_path:
        # Escape hatch / existing tests: a pre-made input JSON was provided.
        input_json = storage.prepare_workflow_input(params.input_json_path, workdir=workdir)
    else:
        # Build the input JSON from structured fields at submit time.
        # When no ligand is set, this produces an unconditional generation job (protein chain only).
        ligand_value = params.ligand
        if params.ligand and params.ligand_file_path:
            # Stage the uploaded ligand file and reference it in the JSON by basename. The pipeline symlinks
            # the file into the task working directory, where DISCO resolves the "FILE_<basename>" path.
            ligand_file = storage.prepare_workflow_input(params.ligand_file_path, workdir=workdir)
            ligand_value = f"FILE_{os.path.basename(ligand_file)}"
        input_dict = build_disco_input_json(workflow, ligand_value=ligand_value)
        input_json = storage.prepare_workflow_input(
            "input.json",
            workdir=workdir,
            input_bytes=json.dumps(input_dict).encode("utf-8"),
        )

    result = {
        "input_json": input_json,
        "experiment": params.experiment,
        "effort": params.effort,
        "num_designs": str(params.num_designs),
    }

    if ligand_file:
        result["ligand_file"] = ligand_file

    if params.ligandmpnn_run_parameters:
        result["ligandmpnn_run_parameters"] = params.ligandmpnn_run_parameters

    return result


def _parse_ligandmpnn_fa(fa_content: str) -> dict:
    """Parse LigandMPNN .fa file header to extract confidence metrics.

    Expected format (second header line):
    >name, id=1, T=0.1, seed=87905, overall_confidence=1.0000, ligand_confidence=1.0000, seq_rec=nan
    """
    metrics = {}
    for line in fa_content.splitlines():
        if not line.startswith(">"):
            continue
        if "overall_confidence=" in line:
            for match in re.finditer(r"(\w+)=([\d.]+|nan)", line):
                key, value = match.groups()
                if key in ("overall_confidence", "ligand_confidence"):
                    if value != "nan":
                        metrics[key] = float(value)
                    else:
                        metrics[key] = None
            break
    return metrics


def process_workflow_results(job: DesignJob, callback: Callable = None) -> list[Base]:
    """Process DISCO workflow results: discover designs, store files, create Design and DescriptorValue objects."""
    pool = db.get(Pool, design_job_id=job.id)
    project_round = db.get(Round, id=pool.round_id)
    scheduler = get_scheduler(job.scheduler_key)
    workflow: DiscoWorkflow = job.workflow

    source_dir = scheduler.get_output_dir(job.job_id)
    destination_dir = storage.get_project_path(project_round.project_id, pool.id)

    # Collect the "[Warning] ..." lines the pipeline printed (e.g. a ligand left out of refolding by
    # disco/bin/add_ligand_remarks.py) from the main log and the task logs, so the app shows them.
    warning_regex = r"\[Warning\]\s+(.+?)(?=\n|$)"
    logs = [("", scheduler.get_log(job.job_id))]
    tasks = scheduler.get_tasks(job.job_id)
    if tasks is not None and not tasks.empty:
        logs += [
            (f"{task['name']}: ", scheduler.get_log(job.job_id, task_id=task["task_id"]))
            for _, task in tasks.iterrows()
        ]
    for task_prefix, log in logs:
        for warning in re.findall(warning_regex, log or "", re.IGNORECASE):
            if f"{task_prefix}{warning}" not in job.warnings:
                job.warnings.append(f"{task_prefix}{warning}")

    refolding_test = "boltz2_scaffold_nt"

    # Discover designs: iterate over batches
    designs = []
    design_id_mapping = {}
    descriptor_values = []
    ligandmpnn_rows = []
    sequence_rows = []

    batch_number = 1
    design_number = 0
    while True:
        batch_name = f"batch{batch_number}"
        packed_dir = os.path.join(source_dir, batch_name, "disco_packed")
        packed_files = [f for f in storage.list_dir(packed_dir) if f.endswith("_packed.pdb")]
        if not packed_files:
            break

        for packed_filename in sorted(packed_files):
            design_number += 1
            # Derive base name: "length_100_ADP_sample_0_packed.pdb" -> "length_100_ADP_sample_0"
            base_name = packed_filename.removesuffix("_packed.pdb")

            design_id = f"ovo_{pool.id}_{str(design_number).zfill(max(2, len(str(workflow.disco_params.num_designs))))}"

            # Store packed PDB (main design structure)
            packed_source = os.path.join(packed_dir, packed_filename)
            packed_stored_path = storage.store_file_path(
                source_abs_path=packed_source,
                storage_rel_path=os.path.join(destination_dir, "disco_packed", f"{design_id}.pdb"),
                overwrite=False,
            )

            # Store backbone PDB
            backbone_source = os.path.join(source_dir, batch_name, "disco_raw", "pdbs", f"{base_name}.pdb")
            backbone_stored_path = storage.store_file_path(
                source_abs_path=backbone_source,
                storage_rel_path=os.path.join(destination_dir, "disco_backbone", f"{design_id}_backbone.pdb"),
                overwrite=False,
            )

            # Create Design object
            design = Design(
                id=design_id,
                pool_id=pool.id,
                accepted=False,
                structure_path=packed_stored_path,
                structure_descriptor_key=descriptors_disco.DISCO_PACKED_STRUCTURE_PATH.key,
            )
            design.spec = DesignSpec.from_pdb_str(
                pdb_data=storage.read_file_str(packed_source),
                chains=["A"],
            )

            chains_str = ",".join(chain_id for c in design.spec.chains for chain_id in c.chain_ids)
            shared_args = dict(
                design_id=design_id,
                descriptor_job_id=None,
                chains=chains_str,
            )

            # Descriptor values for structure paths
            descriptor_values.extend(
                [
                    DescriptorValue(
                        descriptor_key=descriptors_disco.DISCO_BACKBONE_STRUCTURE_PATH.key,
                        value=backbone_stored_path,
                        **shared_args,
                    ),
                    DescriptorValue(
                        descriptor_key=descriptors_disco.DISCO_PACKED_STRUCTURE_PATH.key,
                        value=packed_stored_path,
                        **shared_args,
                    ),
                ]
            )

            # Store boltz refolding structure
            refolding_structure_path = os.path.join(
                source_dir,
                batch_name,
                refolding_test,
                f"{base_name}_packed_{refolding_test}.pdb",
            )

            descriptor_values += RefoldingWorkflow.store_output(
                test=refolding_test,
                destination_dir=destination_dir,
                batch_output_path=None,
                source_structure_path=refolding_structure_path,
                primary=True,
                **shared_args,
            )

            # Parse LigandMPNN confidence from .fa file
            fa_path = os.path.join(source_dir, batch_name, "ligandmpnn_out", "seqs", f"{base_name}.fa")
            # if storage.file_exists(fa_path):
            fa_content = storage.read_file_str(fa_path)
            metrics = _parse_ligandmpnn_fa(fa_content)
            ligandmpnn_rows.append({"ID": design_id, **metrics})

            # Sequence length
            sequence_length = len(design.spec.chains[0].sequence) if design.spec.chains else None
            sequence_rows.append({"ID": design_id, "length": sequence_length})

            design_id_mapping[design_id] = (design_id, f"{base_name}_packed")
            designs.append(design)

            if callback:
                callback(
                    value=design_number / max(workflow.disco_params.num_designs, design_number),
                    text=f"Processing design {base_name}",
                )

        batch_number += 1

    if not designs:
        job.job_result = False
        job.warnings.append(f"No designs found in output directory: {source_dir}")
        return []

    # Create descriptor job
    descriptor_job = save_descriptor_job_for_design_job(
        design_job=job,
        project_id=project_round.project_id,
        chains=["A"],
        design_ids=list(design_id_mapping.keys()),
    )
    for value in descriptor_values:
        value.descriptor_job_id = descriptor_job.id

    # Build descriptor tables
    descriptor_tables = {}
    if ligandmpnn_rows:
        ligandmpnn_df = pd.DataFrame(ligandmpnn_rows).set_index("ID")
        descriptor_tables["disco|ligandmpnn"] = ligandmpnn_df
    if sequence_rows:
        sequence_df = pd.DataFrame(sequence_rows).set_index("ID")
        descriptor_tables["disco|sequence"] = sequence_df

    # Read refolding metrics from JSONL (batch{N}/ directories, not contig{N}_batch{M}/)
    refolding_dfs = []
    for bn in range(1, batch_number):
        jsonl_path = os.path.join(source_dir, f"batch{bn}", f"{refolding_test}.jsonl")
        if storage.file_exists(jsonl_path):
            df = pd.read_json(StringIO(storage.read_file_str(jsonl_path)), lines=True)
            if not df.empty:
                refolding_dfs.append(df)
    if refolding_dfs:
        refolding_df = pd.concat(refolding_dfs)
        refolding_df = refolding_df.set_index("id")
        descriptor_tables["refolding|boltz_primary"] = refolding_df

    descriptor_values.extend(
        read_descriptor_file_values(
            descriptor_job=descriptor_job,
            design_id_mapping=design_id_mapping,
            descriptor_tables=descriptor_tables,
        )
    )

    # Apply acceptance thresholds
    set_designs_accepted(
        designs,
        descriptor_values,
        job,
        skipped_keys=workflow.get_skipped_threshold_keys(),
    )

    return designs + descriptor_values
