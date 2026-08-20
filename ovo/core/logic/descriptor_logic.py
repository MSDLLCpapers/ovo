import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from io import StringIO, BytesIO
from typing import List, Collection, Callable

import pandas as pd

from sqlalchemy.orm.attributes import flag_modified

from ovo import db, storage, get_scheduler, config
from ovo.core.auth import get_username
from ovo.core.database.descriptors_proteinqc import PROTEINQC_MAIN_DESCRIPTORS
from ovo.core.database.descriptors_rfdiffusion import PYDSSP_STRING
from ovo.core.database.models_clustering import BaseHierarchicalClusteringWorkflow, FoldseekClusteringWorkflow
from ovo.core.database.models_refolding import RefoldingWorkflow, RefoldingSupportedDesignWorkflow
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY, ALL_DESCRIPTOR_KEYS_SET
from ovo.core.database.models import (
    DescriptorValue,
    Descriptor,
    Design,
    DescriptorJob,
    DescriptorWorkflow,
    DesignJob,
    DesignDescriptorWorkflow,
    Pool,
)
from ovo.core.logic.job_logic import update_job_status
from ovo.core.logic.proteinqc_logic import get_descriptor_cmap, get_descriptor_comment
from ovo.core.utils.export import write_sheet
from ovo.core.database.models_clustering import ProteinClusteringTool
from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.pdb import NoStructuresFound


def get_available_descriptors(design_ids: list[str], exclude_required_jobs: bool = True) -> dict[str, Descriptor]:
    """
    Return all descriptor keys found in DB for the given design ids.
    If exclude_required_jobs is True, only return descriptors that don't depend on a descriptor job (ambiguous values without it)
    """
    design_ids = list(set(design_ids))
    if not design_ids:
        return {}
    descriptor_keys = db.select_unique_values(DescriptorValue, "descriptor_key", design_id__in=design_ids)
    return {
        descriptor_key: ALL_DESCRIPTORS_BY_KEY[descriptor_key]
        for descriptor_key in ALL_DESCRIPTORS_BY_KEY
        if descriptor_key in descriptor_keys
        and not (
            exclude_required_jobs and getattr(ALL_DESCRIPTORS_BY_KEY[descriptor_key], "required_descriptor_job", False)
        )
    }


def get_available_descriptors_per_job(design_ids: list[str], descriptor_job_id: str) -> dict[str, Descriptor]:
    """
    Return all descriptor keys found in DB for the given design ids and the specified descriptor job.
    """
    design_ids = list(set(design_ids))
    if not design_ids:
        return {}
    descriptor_keys = db.select_unique_values(
        DescriptorValue, "descriptor_key", design_id__in=design_ids, descriptor_job_id=descriptor_job_id
    )
    return {
        descriptor_key: ALL_DESCRIPTORS_BY_KEY[descriptor_key]
        for descriptor_key in ALL_DESCRIPTORS_BY_KEY
        if descriptor_key in descriptor_keys
    }


def get_wide_descriptor_table(
    *,  # disallow positional arguments
    pool_ids: Collection[str] = None,
    design_ids: Collection[str] = None,
    descriptor_keys: Collection[str] = None,
    human_readable=True,
    nested=False,
    descriptor_job_id: str | dict[str, list[str]] | None = None,
    **filters,
) -> pd.DataFrame:
    """
    Return a wide descriptor table for the given design ids.
    The table will have design ids as index and human-readable descriptor names (or keys if human_readable=False) as columns.

    :param pool_ids: Optional list of pool ids to filter designs by. If provided, design_ids will be ignored.
    :param design_ids: Optional list of design ids to filter by. If not provided, will be inferred from pool_ids.
    :param descriptor_keys: Optional list of descriptor keys to include. If not provided, all possible descriptors will be included (including those not available for any of the selected designs!)
    :param human_readable: If True, use human-readable descriptor names as columns. If False, use descriptor keys.
    :param nested: If True, use a MultiIndex for columns with (tool, name) tuples. If False, use flat column names.
    :param descriptor_job_id: Optional descriptor job ID to filter by, or a dict mapping job ID to list of its descriptor keys that should be filtered by that job (if present in descriptor_keys).

    """
    if design_ids is None:
        if pool_ids is None:
            raise ValueError("Either pool_ids or design_ids must be provided")
        design_ids = db.select_values(Design, "id", pool_id__in=pool_ids, **filters)
    elif filters:
        raise ValueError(
            "Can only use use additional keyword filters when pool_ids are used, not when design_ids are used"
        )
    df = db.select_wide_descriptor_table(
        design_ids=design_ids,
        descriptor_keys=list(ALL_DESCRIPTORS_BY_KEY.keys()) if descriptor_keys is None else list(descriptor_keys),
        descriptor_job_id=descriptor_job_id,
    )
    if df.empty:
        return df

    # Reformat columns
    if human_readable:
        descriptors = [ALL_DESCRIPTORS_BY_KEY[descriptor_key] for descriptor_key in df.columns]
        if nested:
            df.columns = pd.MultiIndex.from_tuples((d.tool, d.name) for d in descriptors)
        else:
            df.columns = [d.name for d in descriptors]
    else:
        # avoid complicating the format combinations too much
        assert not nested, "nested=True is not supported when human_readable=False"

    # Get sequences from design spec
    # chain id -> design id -> sequence
    sequences_by_chain_and_design_id = {}
    for design_id, spec in db.select_dict(Design, "id", "spec", id__in=design_ids).items():
        for chain in spec.chains:
            chain_ids = ",".join(chain.chain_ids)
            if chain_ids not in sequences_by_chain_and_design_id:
                sequences_by_chain_and_design_id[chain_ids] = {}
            sequences_by_chain_and_design_id[chain_ids][design_id] = chain.sequence

    # Add sequence columns as (Sequence, A), (Sequence, B) etc
    for chain_ids, sequences_by_design_id in sequences_by_chain_and_design_id.items():
        if human_readable:
            seq_column = ("Sequence", chain_ids) if nested else f"Sequence {chain_ids}"
        else:
            assert not nested, "nested=True is not supported when human_readable=False"
            seq_column = f"sequence_{chain_ids}"
        df.insert(0, seq_column, pd.Series(sequences_by_design_id))

    # Add design labels (comma separated) as a column
    design_labels_dict = {}
    for design_id in design_ids:
        labelings = db.get_labelings_for_design(design_id)
        labels = [labeling.label for labeling in labelings]
        design_labels_dict[design_id] = ",".join(labels) if labels else None
    design_labels_series = pd.Series(design_labels_dict)

    if not design_labels_series.isna().all():
        if human_readable:
            labels_column = ("Labels", "") if nested else "Labels"
        else:
            assert not nested, "nested=True is not supported when human_readable=False"
            labels_column = "labels"
        df.insert(0, labels_column, design_labels_series)

    return df


def submit_descriptor_workflow(
    workflow: DescriptorWorkflow,
    scheduler_key: str,
    project_id: str,
    pipeline_name: str = None,
    submission_args: dict = None,
):
    """Submit a descriptor workflow to the scheduler and create a DescriptorJob in the DB.

    :param workflow: DescriptorWorkflow object to submit
    :param scheduler_key: Key of the scheduler to use
    :param project_id: ID of the Project to associate the DescriptorJob with
    :param pipeline_name: Override the pipeline name to submit, e.g. ovo.proteinqc or a github url with @version
    :param submission_args: Extra submission arguments to override in the scheduler, e.g. {"profile": "conda"} or {"stub": True}
    :return: DescriptorJob
    """

    if config.props.read_only:
        raise RuntimeError("Cannot submit design workflow: OVO server is in read-only mode")

    workflow.validate()

    username = get_username()

    scheduler = get_scheduler(scheduler_key)

    # Submit the workflow
    job_id = scheduler.submit(
        pipeline_name=pipeline_name or workflow.get_pipeline_name(),
        params=workflow.prepare_params(workdir=scheduler.workdir),
        submission_args=submission_args,
    )

    # Create descriptor job
    descriptor_job = DescriptorJob(
        id=DescriptorJob.generate_id(),
        author=username,
        project_id=project_id,
        job_id=job_id,
        scheduler_key=scheduler_key,
        workflow=workflow,
    )

    # Save the descriptor job
    db.save(descriptor_job)
    return descriptor_job


def prepare_design_structures(designs: list[Design], workdir: str):
    """Prepare a txt file (or single pdb file if single design) with PDB file paths, all stored in a provided workdir"""
    storage_paths = []
    design_ids = []
    for design in designs:
        if not design.structure_path:
            print(f"Design {design.id} has no pdb path. Skipping...")
            continue
        storage_paths.append(design.structure_path)
        design_ids.append(design.id)

    if not storage_paths:
        raise NoStructuresFound("No structures found for the selected designs.")

    # Prepare a txt file with workflow input paths, each file renamed to design_id.pdb
    return storage.prepare_workflow_inputs(storage_paths, workdir, names=design_ids)


def prepare_design_sequences(designs: list[Design], workdir: str):
    """Prepare a csv file with a design_id column and a sequence column for each chain and store it in a provided workdir"""
    sequences = []
    design_ids = []
    for design in designs:
        if not design.spec or not design.spec.chains:
            print(f"Design {design.id} has no spec chains. Skipping...")
            continue
        sequences.append({chain_id: chain.sequence for chain in design.spec.chains for chain_id in chain.chain_ids})
        design_ids.append(design.id)

    if not sequences:
        raise ValueError("No sequences found for the selected designs.")

    df = pd.DataFrame(sequences, index=design_ids)
    df.index.name = "design_id"

    return storage.prepare_workflow_input(storage_path="designs.csv", input_bytes=df.to_csv().encode(), workdir=workdir)


def prepare_refolding_params(workflow: RefoldingWorkflow, workdir: str) -> dict:
    workflow.validate()

    designs = db.select(Design, id__in=workflow.design_ids)
    pools = db.select(Pool, id__in=set(d.pool_id for d in designs))
    design_workflows_by_pool_id = {
        p.id: db.get(DesignJob, id=p.design_job_id).workflow for p in pools if p.design_job_id
    }
    design_paths = {}
    for pool in pools:
        if not pool.design_job_id:
            # In case of custom designs, use design.structure_path as design input
            # TODO add warning if column seems to contain pLDDT - we don't want predicted structures as input!
            design_paths.update({d.id: d.structure_path for d in designs if d.pool_id == pool.id})
            continue
        design_workflow = design_workflows_by_pool_id[pool.id]
        if not isinstance(design_workflow, RefoldingSupportedDesignWorkflow):
            raise NotImplementedError(f"Workflow does not support refolding evaluation: {design_workflow.name}")
        pool_design_ids = [d.id for d in designs if d.pool_id == pool.id]
        design_paths.update(design_workflow.get_refolding_design_paths(pool_design_ids))

    if not design_paths:
        raise ValueError("No refolding structure paths available for the selected designs")

    # Prepare a txt file with workflow input paths, each file renamed to design_id.pdb
    input_designs_txt = storage.prepare_workflow_inputs(design_paths.values(), workdir, names=design_paths.keys())

    # Prepare native structure path (if specified)
    native_pdb_path = (
        storage.prepare_workflow_input(workflow.native_pdb_path, workdir) if workflow.native_pdb_path else None
    )

    # Prepare a single directory with reference files (requires filenames to be unique)
    return {
        "design_type": workflow.design_type,
        "input_designs": input_designs_txt,
        "native_pdb": native_pdb_path,
        "tests": ",".join(workflow.tests),
        "designed_chains": ",".join(list(workflow.chains)),
    }


def prepare_foldseek_clustering_workflow_params(workflow: FoldseekClusteringWorkflow, workdir: str) -> dict:
    workflow.validate()

    designs = db.select(Design, id__in=workflow.design_ids)

    designs_query = designs
    designs_target = workflow.designs_target
    chains = list(workflow.chains)
    n_neighbors = workflow.n_neighbors

    # Use prepare_design_structures helper for better error handling
    input_query_path = prepare_design_structures(designs_query, workdir=workdir)

    # Prepare target structures if provided
    input_target_path = None
    if designs_target:
        input_target_path = prepare_design_structures(designs_target, workdir=workdir)

    optional_params = workflow.params.to_dict()
    # Add "foldseek_" prefix to optional parameters
    optional_params = {f"foldseek_{k}": v for k, v in optional_params.items()}

    return {
        "query_pdb": input_query_path,
        "target_pdb": input_target_path,
        "n_neighbors": ",".join(map(str, n_neighbors)),
        "chains": ",".join(chains),
        "workflow_name": "foldseek",
        **optional_params,
    }


def prepare_hierarchical_clustering_workflow_params(workflow: BaseHierarchicalClusteringWorkflow, workdir: str) -> dict:
    workflow.validate()

    designs = db.select(Design, id__in=workflow.design_ids)

    chains = list(workflow.chains)
    n_neighbors = workflow.n_neighbors

    # Determine if we need structures or can use sequences
    if workflow.requires_structures:
        input_query_path = prepare_design_structures(designs, workdir=workdir)
    else:
        # For sequence/descriptor-based clustering, use sequences CSV (provides design IDs)
        # Try sequences first, fall back to structures if needed
        input_query_path = prepare_design_sequences(designs, workdir=workdir)

    optional_params = workflow.params.to_dict()

    # Also add the pydssp df as a csv file to the input directory and pass the path as a parameter
    if workflow.tool_key == "secondary_structure_hierarchical_clustering":
        descriptors_df = get_wide_descriptor_table(
            design_ids=workflow.design_ids, descriptor_keys=[PYDSSP_STRING.key], nested=False, human_readable=False
        )
        csv_bytes = descriptors_df.to_csv().encode("utf-8")
        pydssp_csv_path = storage.prepare_workflow_input("pydssp_descriptors.csv", workdir, input_bytes=csv_bytes)
        optional_params["dssp_csv"] = pydssp_csv_path

    if workflow.tool_key == "interface_residues_hierarchical_clustering":
        descriptor_values = db.select_descriptor_values(workflow.input_descriptor_key, design_ids=workflow.design_ids)
        descriptor_values_by_design_series = pd.Series(descriptor_values, index=workflow.design_ids)
        interface_residues_table = get_interface_residues_by_design_table(descriptor_values_by_design_series)
        csv_bytes = interface_residues_table.to_csv().encode("utf-8")
        interface_residues_table_path = storage.prepare_workflow_input(
            "interface_residues.csv", workdir, input_bytes=csv_bytes
        )
        optional_params["interface_residues_csv"] = interface_residues_table_path

    # Add "hierarchical_" prefix to optional parameters
    optional_params = {f"hierarchical_{k}": v for k, v in optional_params.items()}

    return {
        "query_pdb": input_query_path,
        "n_neighbors": ",".join(map(str, n_neighbors)),
        "chains": ",".join(chains),
        "workflow_name": "hierarchical",
        **optional_params,
    }


def get_interface_residues_by_design_table(descriptor_values: pd.Series) -> pd.DataFrame:
    unique_residues = set()
    design_to_residues = {}

    # Build mapping from design to set of residues, and collect all unique residues
    for design_id, val in descriptor_values.items():
        if pd.isna(val):
            residues = set()
        else:
            residues = {r.strip() for r in str(val).split(",") if r.strip()}
        design_to_residues[design_id] = residues
        unique_residues.update(residues)
    # Remove "None" if present
    if "None" in unique_residues:
        unique_residues.remove("None")
    unique_residues = sorted(unique_residues, key=lambda x: (x[0], int(x[1:])))  # sort by chain and residue number
    bool_data = []

    # For each design, create a boolean row for presence of each residue
    for design_id in descriptor_values.index:
        row = [res in design_to_residues[design_id] for res in unique_residues]
        bool_data.append(row)
    bool_df = pd.DataFrame(bool_data, index=descriptor_values.index, columns=unique_residues)
    return bool_df


def get_log(descriptor_job: DescriptorJob, tail: int = None) -> str:
    """Get the log of a descriptor job from the scheduler."""
    assert isinstance(descriptor_job, DescriptorJob), f"Expected DescriptorJob, got {type(descriptor_job).__name__}"
    scheduler = get_scheduler(descriptor_job.scheduler_key)
    log = scheduler.get_log(descriptor_job.job_id)
    if tail is not None:
        log_lines = log.splitlines()
        log = "\n".join(log_lines[-tail:])
    return log


def process_results(descriptor_job: DescriptorJob, callback: Callable = None, wait: bool = True):
    """Process results of a successful workflow - save DescriptorValues to database"""
    assert isinstance(descriptor_job, DescriptorJob), f"Expected DescriptorJob, got {type(descriptor_job).__name__}"
    if descriptor_job.processed:
        print("Job already processed")
        return
    scheduler = get_scheduler(descriptor_job.scheduler_key)
    if scheduler.get_result(descriptor_job.job_id) is None:
        # Job is still running
        if wait:
            print(f"Waiting for job {descriptor_job.job_id} to finish...")
            scheduler.wait(descriptor_job.job_id)
        else:
            raise ValueError(
                f"Job {descriptor_job.job_id} has not finished yet, try again later or use scheduler.wait(design_job.job_id)"
            )
    # Job should be successful or failed now, update job status
    update_job_status(descriptor_job)
    if descriptor_job.job_result is False:
        # Print job log and raise error
        print(scheduler.get_log(descriptor_job.job_id))
        raise ValueError(f"Job {descriptor_job.job_id} has failed")
    # Process and save descriptor values
    objects = descriptor_job.workflow.process_results(descriptor_job, callback=callback)
    assert isinstance(objects, list), f"Expected list from process_results(), got {type(objects).__name__}: {objects}"
    # Update processed flag
    descriptor_job.processed = True
    flag_modified(descriptor_job, "workflow")
    flag_modified(descriptor_job, "warnings")
    # Save all atomically in one commit
    db.save_all(objects + [descriptor_job])


def read_descriptor_file_values(
    descriptor_job: DescriptorJob,
    design_id_mapping: dict[str, str | tuple],
    filenames: dict[str, str] = None,
    descriptor_tables: dict[str, pd.DataFrame] = None,
) -> list[DescriptorValue]:
    """Process CSV/JSONL files containing descriptor values (one file per batch, one row per design), return list of DescriptorValues to be inserted into DB.

    :param descriptor_job: DescriptorJob object
    :param design_id_mapping: Mapping from design.id to table_id (basename of PDB file = id column in descriptor output file)
    :param filenames: Dict of "pipeline_name|tool_key" -> filename in output directory (with or without file extension - will look for .csv or .jsonl)
    :param descriptor_tables: Optional dictionary of pre-loaded descriptor tables (tool_key -> pd.DataFrame).

    :return: List of DescriptorValue objects to be saved to DB
    """
    assert len(design_id_mapping) == len(set(design_id_mapping.values())), (
        f"Duplicate ids in design_id_mapping: {design_id_mapping}"
    )

    if descriptor_tables is None:
        descriptor_tables = {}

    # source path -> (design_id, storage subdir, storage suffix, descriptor_key),
    # e.g. path/to/contig1_batch1/pssm/first.csv -> (descriptors, ovo_xyz_01, _pssm.csv, some|descriptor|key)
    design_file_paths = {}

    if filenames:
        scheduler = get_scheduler(descriptor_job.scheduler_key)
        source_output_path = scheduler.get_output_dir(descriptor_job.job_id)

        batch_descriptors = {descriptor_key_prefix: [] for descriptor_key_prefix in filenames}
        contig_number = 1
        # Iterate over contigs until no more files are found
        while True:
            any_files_in_contig = False
            batch_number = 1
            # Iterate over batches until no more files are found
            while True:
                batch_name = f"contig{contig_number}_batch{batch_number}"
                any_files_in_batch = False
                for descriptor_key_prefix, filename in filenames.items():
                    df = None
                    filename_wo_extension, extension = os.path.splitext(filename)
                    if not extension or extension == ".jsonl":
                        jsonl_path = os.path.join(source_output_path, batch_name, f"{filename_wo_extension}.jsonl")
                        if storage.file_exists(jsonl_path):
                            try:
                                df = pd.read_json(StringIO(storage.read_file_str(jsonl_path)), lines=True)
                            except Exception as e:
                                raise ValueError(f"Failed to read {jsonl_path}: {e}")
                    if not extension or extension == ".csv":
                        csv_path = os.path.join(source_output_path, batch_name, f"{filename_wo_extension}.csv")
                        if storage.file_exists(csv_path):
                            df = pd.read_csv(StringIO(storage.read_file_str(csv_path)))
                    if df is not None:
                        if not df.empty:
                            id_column = find_id_column(df, descriptor_key_prefix)
                            batch_descriptors[descriptor_key_prefix].append((batch_name, df.set_index(id_column)))
                        any_files_in_batch = True
                        any_files_in_contig = True
                if not any_files_in_batch:
                    break
                batch_number += 1

            if not any_files_in_contig:
                break

            contig_number += 1

        if contig_number == 1 and batch_number == 1:
            raise ValueError(
                f"No suitable descriptor files found in {source_output_path}, "
                f"expected at least one of: {', '.join(filenames.values())}."
            )

        # Concatenate dataframes from all batches for each tool
        for key, batch_dfs in batch_descriptors.items():
            if batch_dfs:
                descriptor_tables[key] = _concat_batch_descriptor_tables(key, batch_dfs)

    descriptor_values = []
    for design_id, table_ids in design_id_mapping.items():
        descriptor_values.extend(
            generate_descriptor_values_for_design(
                design_id=design_id,
                table_ids=table_ids,
                descriptor_job_id=descriptor_job.id,
                descriptor_tables=descriptor_tables,
                chains=descriptor_job.workflow.chains,
            )
        )

    return descriptor_values


def read_per_design_files(
    descriptor_job: DescriptorJob,
    design_id_mapping: dict[str, str | tuple],
    design_files: dict[str, tuple[str, str, str]],
    callback: Callable = None,
) -> list[DescriptorValue]:
    """Process per-design output files such as predicted PDB structures, return DescriptorValues (containing the stored file path as DescriptorValue.value) to be inserted into DB.

    :param descriptor_job: DescriptorJob object
    :param design_id_mapping: Mapping from design.id to table_id (basename of PDB file = id column in descriptor output file)
    :param design_files: Optional dict of filename produced by pipeline -> (subdir in storage, file suffix in storage, descriptor_key), for individual design files
                         (e.g. per-design PDB output files or CSV files with more detailed descriptors, to be stored as storage path descriptors).
                         For example pssm/{}.csv (with {} replaced by value of design_id_mapping) -> (descriptors, _pssm.csv, some|descriptor|key)
                         Will store the descriptor files under pool/{pool_id}/descriptors/{descriptor_job_id}/{design_id}{file_suffix}.
    :param callback: Optional callback function for reporting progress, will be called with value between 0 and 1 and text description of the current step

    :return: List of DescriptorValue objects to be saved to DB
    """
    assert len(design_id_mapping) == len(set(design_id_mapping.values())), (
        f"Duplicate ids in design_id_mapping: {design_id_mapping}"
    )

    # source path -> (design_id, storage subdir, storage suffix, descriptor_key),
    # e.g. path/to/contig1_batch1/pssm/first.csv -> (descriptors, ovo_xyz_01, _pssm.csv, some|descriptor|key)
    design_file_paths = {}

    scheduler = get_scheduler(descriptor_job.scheduler_key)
    source_output_path = scheduler.get_output_dir(descriptor_job.job_id)

    contig_number = 1
    # Iterate over contigs until no more files are found
    while True:
        any_files_in_contig = False
        batch_number = 1
        # Iterate over batches until no more files are found
        while True:
            batch_name = f"contig{contig_number}_batch{batch_number}"
            any_files_in_batch = False
            for design_file_template, (storage_subdir, storage_suffix, descriptor_key) in design_files.items():
                assert (
                    isinstance(storage_subdir, str)
                    and isinstance(storage_suffix, str)
                    and isinstance(descriptor_key, str)
                ), (
                    "Expected (storage_subdir string, storage_suffix string, descriptor_key string) tuple, "
                    f"got: {(storage_subdir, storage_suffix, descriptor_key)}"
                )
                for design_id, table_ids in design_id_mapping.items():
                    if isinstance(table_ids, str):
                        table_ids = (table_ids,)
                    for table_id in table_ids:
                        design_file_path = os.path.join(
                            source_output_path, batch_name, design_file_template.format(table_id)
                        )
                        if storage.file_exists(design_file_path):
                            any_files_in_batch = True
                            any_files_in_contig = True
                            design_file_paths[design_file_path] = (
                                design_id,
                                storage_subdir,
                                storage_suffix,
                                descriptor_key,
                            )
            if not any_files_in_batch:
                break
            batch_number += 1

        if not any_files_in_contig:
            break

        contig_number += 1

    if contig_number == 1 and batch_number == 1:
        raise ValueError(
            f"No suitable design files found in {source_output_path}, "
            f"expected at least one file matching template: {', '.join(design_files.keys())}."
        )

    descriptor_values = []
    with storage.archive_context(delete_if_exists=True):
        with ThreadPoolExecutor(config.storage.num_copy_threads) as executor:
            futures = [
                executor.submit(
                    _store_design_file_descriptor,
                    source_path,
                    # Storage path:
                    # project/[project_id]/pool/[pool_id]/descriptors/[descriptor_job_id]/[design_id]_suffix.ext
                    os.path.join(
                        storage.get_project_path(descriptor_job.project_id, Design.design_id_to_pool_id(design_id)),
                        storage_subdir,
                        descriptor_job.id,
                        f"{design_id}{storage_suffix}",
                    ),
                    descriptor_key,
                    descriptor_job.id,
                    design_id,
                    descriptor_job.workflow.chains,
                )
                for source_path, (
                    design_id,
                    storage_subdir,
                    storage_suffix,
                    descriptor_key,
                ) in design_file_paths.items()
            ]

            for i, future in enumerate(futures):
                descriptor_values.append(future.result())
                if callback:
                    callback(
                        value=(i + 1) / len(futures),
                        text=f"Storing file ({i + 1}/{len(futures)})",
                    )

    return descriptor_values


def _store_design_file_descriptor(
    source_path: str,
    storage_path: str,
    descriptor_key: str,
    descriptor_job_id: str,
    design_id: str,
    chains: list[str],
) -> DescriptorValue:
    return DescriptorValue(
        descriptor_key=descriptor_key,
        value=storage.store_file_path(
            source_abs_path=source_path,
            storage_rel_path=storage_path,
            overwrite=False,
        ),
        design_id=design_id,
        descriptor_job_id=descriptor_job_id,
        chains=",".join(chains),
    )


def save_descriptor_job_for_design_job(
    design_job: DesignJob, project_id: str, chains: list[str], design_ids: list[str]
) -> DescriptorJob:
    descriptor_job = DescriptorJob(
        id=DescriptorJob.generate_id(),
        scheduler_key=design_job.scheduler_key,
        job_id=design_job.job_id,
        author=design_job.author,
        project_id=project_id,
        job_result=True,
        workflow=DesignDescriptorWorkflow(
            design_job_id=design_job.id,
            chains=chains,
            design_ids=design_ids,
        ),
    )
    # We need to save the descriptor job to obtain its autoincrement ID
    db.save(descriptor_job)
    return descriptor_job


def _concat_batch_descriptor_tables(
    descriptor_key_prefix: str, batch_dfs: list[tuple[str, pd.DataFrame]]
) -> pd.DataFrame:
    """Concatenate per-batch descriptor tables into one table indexed by table_id.

    The same table_id can legitimately appear in multiple batches (e.g. two BindCraft batches
    independently sampling the same random seed, producing the same design name). Such rows are
    identical, so we keep the first occurrence. Duplicate IDs with *differing* values are a real
    problem and raise an error naming the IDs and batches involved.
    """
    df = pd.concat([df for _, df in batch_dfs]).sort_index()
    duplicated = df.index.duplicated(keep=False)
    if not duplicated.any():
        return df

    batch_of_row = pd.Series(
        [batch_name for batch_name, batch_df in batch_dfs for _ in range(len(batch_df))],
        index=pd.concat([batch_df for _, batch_df in batch_dfs]).index,
    ).sort_index()
    conflicting = {}
    for table_id in df.index[duplicated].unique():
        rows = df.loc[[table_id]]
        if len(rows.drop_duplicates()) > 1:
            conflicting[table_id] = sorted(set(batch_of_row.loc[[table_id]]))
    if conflicting:
        details = ", ".join(f"'{k}' in {'/'.join(v)}" for k, v in list(conflicting.items())[:10])
        raise ValueError(
            f"Found {len(conflicting)} duplicate ID(s) with conflicting values in descriptor table "
            f"'{descriptor_key_prefix}': {details}"
        )

    duplicate_ids = df.index[duplicated].unique()
    print(
        f"Warning: dropping {duplicated.sum() - len(duplicate_ids)} duplicate row(s) with identical "
        f"values in descriptor table '{descriptor_key_prefix}' for {len(duplicate_ids)} ID(s): "
        f"{', '.join(map(str, duplicate_ids[:10]))}" + (" ..." if len(duplicate_ids) > 10 else "")
    )
    return df[~df.index.duplicated(keep="first")]


def find_id_column(df: pd.DataFrame, df_name: str):
    for column in ["id", "ID", "Id"]:
        if column in df.columns:
            return column
    raise ValueError(f'Dataframe should contain an "ID" column, got: {df.columns} in {df_name}')


def generate_descriptor_values_for_design(
    design_id: str,
    table_ids: str | tuple,
    descriptor_job_id: str | None,
    descriptor_tables,
    chains: list[str],
) -> list[DescriptorValue]:
    """Generate DescriptorValue objects for a given design based on descriptor tables.

    Requirements (otherwise an error is raised, leading to interrupted processing of the job):
    - Each descriptor table must contain at least one recognized descriptor (defined by Descriptor objects)
    - One of the design's table_ids must be found in each descriptor table (each design should be present)
    - Descriptor table index must be unique

    :param design_id: ID of the design
    :param table_ids: ID(s) corresponding to the design in the dataframes (can be a single string or a tuple of strings)
    :param descriptor_job_id: ID of the DescriptorJob
    :param descriptor_tables: Dictionary of descriptor tables (tool_key -> pd.DataFrame, indexed by table_id)
    :param chains: List of chain IDs the descriptors apply to
    :return: List of DescriptorValue objects
    """
    if isinstance(table_ids, str):
        table_ids = (table_ids,)

    # Convert chains to comma-separated string
    if isinstance(chains, str):
        chains = list(chains.replace(",", ""))
    chains = ",".join(chains)

    descriptor_values = []
    for descriptor_key_prefix, descriptor_table in descriptor_tables.items():
        row = None
        for table_id in table_ids:
            if table_id in descriptor_table.index:
                row = descriptor_table.loc[table_id]
                if isinstance(row, pd.DataFrame):
                    raise ValueError(
                        f"Found {len(row)} rows with duplicate ID '{table_id}' in descriptor table "
                        f"'{descriptor_key_prefix}' (design {design_id}), "
                        f"{len(row.drop_duplicates())} of them with distinct values"
                    )
        if row is None:
            raise ValueError(
                f"ID {table_ids} ({design_id}) missing in {descriptor_key_prefix} descriptor table, found only: {descriptor_table.index.tolist()}"
            )
        recognized_fields = set()
        for field, value in row.items():
            if f"{descriptor_key_prefix}|{field}" not in ALL_DESCRIPTOR_KEYS_SET:
                continue
            recognized_fields.add(field)
            if pd.isna(value):
                continue
            descriptor_values.append(
                DescriptorValue(
                    design_id=design_id,
                    descriptor_key=f"{descriptor_key_prefix}|{field}",
                    descriptor_job_id=descriptor_job_id,
                    # TODO enable parsing row.chain(s) and store separate values for each chain or combination of chains
                    chains=chains,
                    value=str(value),
                )
            )
        if not recognized_fields:
            raise ValueError(
                f"No recognized descriptors found in table '{descriptor_key_prefix}', "
                f"found columns: {', '.join(map(str, row.keys()))}. "
                f"Please create Descriptor objects with keys starting with '{descriptor_key_prefix}|...' "
                f"to match the columns in the table."
            )
    return descriptor_values


def update_and_process_descriptors(descriptor_jobs: List[DescriptorJob], error_callback: Callable):
    """
    Update descriptor jobs and process finished descriptor jobs
    """
    processed_jobs = []
    for descriptor_job in descriptor_jobs:
        job_result = update_job_status(descriptor_job)

        if job_result is True and descriptor_job.workflow:
            workflow_name = descriptor_job.workflow.name or "workflow"
            try:
                process_results(descriptor_job, wait=False)
                processed_jobs.append(descriptor_job)
            except Exception as e:
                # Print exception and continue processing other jobs
                error_callback(
                    f"Unexpected error processing result of {workflow_name} (job {descriptor_job.job_id}): {e}"
                )
                traceback.print_exc()
    return processed_jobs


def export_proteinqc_excel(design_ids: list[str], output_path: str = None):
    df = get_wide_descriptor_table(
        design_ids=design_ids,
        descriptor_keys=[d.key for d in PROTEINQC_MAIN_DESCRIPTORS],
        nested=False,
        human_readable=False,
    )
    # TODO add numbers of yellow and orange flags
    return export_design_descriptors_excel(df, output_path=output_path)


def export_design_descriptors_excel(df: pd.DataFrame, output_path=None) -> BytesIO | None:
    """Export Excel file with design descriptors for the given design ids.

    :param df: Dataframe with any values, descriptor columns should be descriptor keys
    :param output_path: If given, write the Excel file to this path. If None, return the bytes of the Excel file.
    """
    assert df.columns.nlevels == 1, "Expected nested=False dataframe with single-level columns"
    # Set index to include non-descriptor columns
    meta_cols = [col for col in df.columns if col not in ALL_DESCRIPTORS_BY_KEY]
    df = df.reset_index().set_index([df.index.name] + meta_cols)
    descriptors = [ALL_DESCRIPTORS_BY_KEY[c] for c in df.columns]

    # Rename columns to human-readable names
    if not df.empty:
        df.columns = pd.MultiIndex.from_tuples([(descriptor.tool, descriptor.name) for descriptor in descriptors])

    sheet_name = "Descriptors"
    buffer = BytesIO()
    writer = pd.ExcelWriter(buffer, engine="xlsxwriter")

    write_sheet(df, writer, sheet_name=sheet_name, index=True)

    workbook = writer.book
    sheet = writer.sheets[sheet_name]

    n_cols = sheet.dim_colmax + 1
    n_rows = sheet.dim_rowmax + 1

    row_offset = df.columns.nlevels
    column_offset = df.index.nlevels

    # Freeze panes
    sheet.freeze_panes(row_offset, column_offset)

    # Set column width
    index_width = 20
    sheet.set_column(0, 0, index_width)
    width = 10
    sheet.set_column(1, n_cols - 1, width)

    # Add filters
    sheet.autofilter(1, 0, n_rows - 1, n_cols - 1)

    # Add cell comments for labels column showing explanation for each label
    labels_level_index = None
    for i, level_name in enumerate(df.index.names):
        if level_name in ["Labels", "labels"] or (isinstance(level_name, tuple) and level_name[0] == "Labels"):
            labels_level_index = i
            break

    if labels_level_index is not None:
        labels_excel_col = labels_level_index
        design_ids = df.index.get_level_values(0).tolist()

        for row_idx, design_id in enumerate(design_ids, start=row_offset):
            labelings = db.get_labelings_for_design(design_id)
            if labelings:
                # Create comment text with label: explanation pairs
                comment_parts = []
                for labeling in labelings:
                    if labeling.explanation:
                        comment_parts.append(f"{labeling.label}: {labeling.explanation}")
                    else:
                        comment_parts.append(f"{labeling.label}: No explanation provided")

                if comment_parts:
                    comment_text = "\n".join(comment_parts)
                    sheet.write_comment(row_idx, labels_excel_col, comment_text, {"x_scale": 2, "y_scale": 1.5})

    # Apply background colors
    for i, (descriptor, col) in enumerate(zip(descriptors, df.columns), start=column_offset):
        cmap = get_descriptor_cmap(descriptor, min_val=df[col].dropna().min(), max_val=df[col].dropna().max())
        for row_idx, value in enumerate(df[col], start=row_offset):
            if pd.isna(value):
                sheet.write(row_idx, i, "")
            else:
                hex_color = cmap(value)
                cell_format = workbook.add_format({"bg_color": hex_color})
                sheet.write(row_idx, i, value, cell_format)

        # Write column description as a comment
        comment = get_descriptor_comment(descriptor)
        sheet.write_comment(1, i, comment, {"x_scale": 2})

    writer.close()
    if not output_path:
        buffer.seek(0)
        return buffer
    return None


def get_descriptor_metadata_table(descriptor_keys: Collection[str]) -> pd.DataFrame:
    """Get a table with metadata for the given descriptor keys."""
    descriptors = [ALL_DESCRIPTORS_BY_KEY[key] for key in descriptor_keys if key in ALL_DESCRIPTORS_BY_KEY]
    data = {
        "Key": [d.key for d in descriptors],
        "Name": [d.name for d in descriptors],
        "Tool": [d.tool for d in descriptors],
        "Description": [d.description for d in descriptors],
    }
    return pd.DataFrame(data).set_index("Key")
