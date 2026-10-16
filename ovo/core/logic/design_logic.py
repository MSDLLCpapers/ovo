import os
import sys
import traceback
import warnings
import zipfile
from collections import defaultdict

from copy import deepcopy
from datetime import datetime, timezone
from typing import Callable, Collection

import pandas as pd
from humanize import naturaltime
from sqlalchemy.orm.attributes import flag_modified

from ovo import db, config, storage
from ovo import get_scheduler
from ovo.core.auth import get_username
from ovo.core.database.models import (
    Design,
    Threshold,
    DescriptorValue,
    Round,
    DesignJob,
    Base,
    DesignWorkflow,
    DesignSpec,
    DesignChain,
    ProjectArtifact,
    JobReportArtifact,
)
from ovo.core.database.models import Pool, Workflow
from ovo.core.logic.filtering_logic import filter_designs_by_thresholds
from ovo.core.logic.job_logic import (
    update_job_status,
    format_job_duration,
    create_job_report_artifact,
    delete_job_artifacts,
)
from ovo.core.utils.pdb import filter_and_relabel_chains_pdb_str, mmcif_to_pdb
from ovo.core.utils.residue_selection import get_chains_and_contigs

# note: bulk submission config import/export lives in ovo.core.logic.bulk_submission_logic


def get_pool_jobs(
    project_id: str = None,
    round_ids: list[str] = None,
    job_filters: dict = None,
    **pool_filters,
) -> tuple[list[DesignJob], dict[str, Pool]]:
    """Select the design jobs of the pools matching the given filters.

    Args:
        job_filters: Extra db.select filters for the DesignJobs, e.g. {"job_result": False} for the
                     failed ones (None=in-progress, True=completed) or
                     {"job_started_date_utc__gte": datetime} for the recently started ones.
        pool_filters: db.select filters for the Pools, on top of project_id and round_ids.

    Returns:
        The jobs, newest first, and the pool of each of them by job ID. Pools without a job are
        left out, as are the jobs filtered out by job_filters.
    """
    id_filters = {}
    if project_id is not None:
        project_round_ids = db.select_unique_values(Round, "id", project_id=project_id)
        if round_ids is not None:
            round_ids = set(round_ids).intersection(set(project_round_ids))
        else:
            round_ids = project_round_ids
    if round_ids is not None:
        if isinstance(round_ids, str):
            round_ids = [round_ids]
        id_filters["round_id__in"] = round_ids

    pools = db.select(Pool, **id_filters, **pool_filters)
    pools_by_job_id = {p.design_job_id: p for p in pools if p.design_job_id is not None}
    jobs = db.select(DesignJob, order_by="-created_date_utc", id__in=pools_by_job_id.keys(), **(job_filters or {}))
    return jobs, pools_by_job_id


def count_designs_by_pool(pool_ids: Collection[str]) -> tuple[dict[str, int], dict[str, int]]:
    """Count the accepted designs and all the designs of each of the given pools, by pool ID."""
    accepted_by_pool = db.count_distinct(Design, group_by="pool_id", pool_id__in=pool_ids, accepted=True)
    total_by_pool = db.count_distinct(Design, group_by="pool_id", pool_id__in=pool_ids)
    return accepted_by_pool, total_by_pool


def update_job_statuses(jobs: list[DesignJob], callback: Callable[[DesignJob], None] = None) -> None:
    """Poll the scheduler for the result of each job that is still in progress.

    If a job failed, it will be saved to the DB. If a job was successful, it's only updated in the
    job object, we will save it to DB later (after the designs have been processed).

    Args:
        callback: Called with each job that was polled, to report the progress.
    """
    for job in jobs:
        if job.job_result is None:
            update_job_status(job)
            if callback:
                callback(job)


def get_design_jobs_table(
    project_id: str = None,
    round_ids: list[str] = None,
    update=True,
    job_filters: dict = None,
    **pool_filters,
) -> pd.DataFrame:
    """Get pandas DataFrame with job and pool metadata and workflow parameter information.

    Args:
        update: Whether to poll the scheduler for the status of the jobs that are still in progress.
        job_filters: See :func:`get_pool_jobs`.
        pool_filters: See :func:`get_pool_jobs`.
    """
    jobs, pools_by_job_id = get_pool_jobs(
        project_id=project_id, round_ids=round_ids, job_filters=job_filters, **pool_filters
    )
    if update:
        update_job_statuses(jobs)

    accepted_by_pool, total_by_pool = count_designs_by_pool([p.id for p in pools_by_job_id.values()])

    # Load job report artifacts for all jobs at once
    job_ids = [job.id for job in jobs]
    query_params = {
        "design_job_id__in": job_ids,
        "artifact_type": JobReportArtifact.artifact_type,
    }
    if project_id is not None:
        query_params["project_id"] = project_id

    all_artifacts = db.select(ProjectArtifact, **query_params)
    artifacts_by_job_id = {artifact.design_job_id: artifact for artifact in all_artifacts}

    rows = []
    for job in jobs:
        pool = pools_by_job_id.get(job.id)
        artifact = artifacts_by_job_id.get(job.id)
        total_compute_hours = artifact.artifact.total_compute_hours if artifact else None

        rows.append(
            {
                ("Pool", "id"): pool.id,
                ("Pool", "name"): pool.name,
                ("Pool", "description"): pool.description,
                ("Job", "status"): format_pool_status(job, pool.processed, update_status=update),
                ("Job", "duration"): format_job_duration(job),
                ("Job", "created"): naturaltime(
                    job.created_date_utc, when=datetime.now(timezone.utc).replace(tzinfo=None)
                ),
                ("Job", "compute hours"): format_total_compute_hours(total_compute_hours),
                ("Designs", "accepted"): accepted_by_pool.get(pool.id, 0) if pool.processed else None,
                ("Designs", "total"): total_by_pool.get(pool.id, 0) if pool.processed else None,
            }
        )

    if not rows:
        return pd.DataFrame()

    pools_table = pd.DataFrame(rows)
    pools_table.columns = pd.MultiIndex.from_tuples([c for c in pools_table.columns])

    workflows_table = get_workflows_table(jobs=jobs)

    pools_table = pd.concat([pools_table, workflows_table], axis=1)

    return pools_table.set_index([("Pool", "id")])


def format_total_compute_hours(total_compute_hours: float | None) -> str | None:
    if total_compute_hours is None:
        return None
    if total_compute_hours >= 1:
        return f"{int(total_compute_hours)}h"
    return f"{total_compute_hours:.2f}"


def get_pools_table(project_id: str = None, round_ids: list[str] = None):
    id_filters = {}
    if project_id is not None:
        project_round_ids = db.select_unique_values(Round, "id", project_id=project_id)
        if round_ids is not None:
            round_ids = set(round_ids).intersection(set(project_round_ids))
        else:
            round_ids = project_round_ids
    if round_ids is not None:
        if isinstance(round_ids, str):
            round_ids = [round_ids]
        id_filters["round_id__in"] = round_ids

    pools = db.select(Pool, **id_filters, order_by="-created_date_utc")

    accepted_by_pool, total_by_pool = count_designs_by_pool([p.id for p in pools])
    failed_job_ids = db.select_unique_values(
        DesignJob, "id", job_result=False, id__in=[p.design_job_id for p in pools if p.design_job_id]
    )

    filtered_pools = [pool for pool in pools if not pool.design_job_id or pool.design_job_id not in failed_job_ids]

    df = pd.DataFrame(
        [
            {
                "ID": pool.id,
                "Name": pool.name,
                "Description": pool.description,
                "Created": naturaltime(pool.created_date_utc, when=datetime.now(timezone.utc).replace(tzinfo=None)),
                "Accepted Designs": accepted_by_pool.get(pool.id, 0) if pool.processed else "Not processed yet",
                "Total Designs": total_by_pool.get(pool.id, 0) if pool.processed else None,
                "Job ID": pool.design_job_id,
            }
            for pool in filtered_pools
        ]
    )
    if len(round_ids) > 1:
        round_names = db.select_dict(Round, "id", "name", id__in=round_ids)
        df.insert(0, "Round", [round_names.get(pool.round_id) for pool in filtered_pools])

    return df


# Status labels of format_pool_status that callers match on, e.g. to offer the results of a job that
# has finished but whose designs have not been opened yet (READY_STATUS)
READY_STATUS = "✅ Ready"
DONE_STATUS = "Done"
FAILED_STATUS = "Failed"


def format_pool_status(job: DesignJob, processed: bool, update_status: bool = True):
    job_result = job.job_result
    if processed and job_result is None:
        return None
    if job_result is True:
        return READY_STATUS if not processed else DONE_STATUS
    elif job_result is False:
        return FAILED_STATUS
    if update_status:
        # Get status label from scheduler
        try:
            scheduler = get_scheduler(job.scheduler_key)
        except Exception:
            traceback.print_exc()
            return "Unknown Scheduler"
        try:
            return f"⏳{scheduler.get_status_label(job.job_id)}"
        except:
            traceback.print_exc()
            return "Unknown Status"
    return "In progress"


def get_workflows_table(jobs: list[DesignJob]):
    """Get pandas DataFrame with workflow parameter information for each pool."""
    table = pd.DataFrame([job.workflow.get_table_row() for job in jobs])
    # If there are no pools with a workflow, create empty multiindex manually
    if table.columns.empty and not table.empty:
        table.columns = pd.MultiIndex.from_tuples([])
    return table


def submit_design_workflow(
    workflow: Workflow,
    scheduler_key: str,
    round_id: str,
    pool_name: str,
    pool_description: str,
    return_existing: bool = True,
    pipeline_name: str = None,
    resume_failed: bool = False,
    submission_args: dict = None,
) -> tuple[DesignJob, Pool]:
    """Submit a design workflow to the scheduler and create a Pool and DesignJob in the DB.

    :param workflow: Workflow object to submit
    :param scheduler_key: Key of the scheduler to use
    :param round_id: ID of the Round to associate the Pool with
    :param pool_name: Name of the Pool to create
    :param pool_description: Description of the Pool to create
    :param return_existing: If a Pool with the same name and parameters already exists in this round, return it instead of raising an error. Only applies when its job has not failed, see resume_failed.
    :param pipeline_name: Override the pipeline name to submit, e.g. ovo.rfdiffusion-end-to-end or a github url with @version
    :param resume_failed: If a Pool with the same name already exists in this round but its job has failed, submit the job again. Raises an error if not enabled.
    :param submission_args: Extra submission arguments to override in the scheduler, e.g. {"profile": "conda"} or {"stub": True}
    :return: Tuple of (DesignJob, Pool)
    """
    scheduler = get_scheduler(scheduler_key)

    if existing_pools := db.select(Pool, name=pool_name, round_id=round_id):
        if not return_existing:
            raise ValueError(f"Pool with name '{pool_name}' already exists in this round")
        pool = existing_pools[0]
        if pool.design_job_id is None:
            # No design job associated with this pool, raise an error
            raise ValueError(f"Pool with name '{pool_name}' already exists in this round")
        design_job = db.get(DesignJob, id=pool.design_job_id)
        try:
            before = design_job.workflow.prepare_params(workdir=scheduler.workdir)
            after = workflow.prepare_params(workdir=scheduler.workdir)
        except Exception as e:
            traceback.print_exc()
            print(f"Error comparing existing pool workflow params: {e}")
            raise ValueError(
                f"Pool with name '{pool_name}' already exists in this round and could not compare parameters"
            )

        if before != after:
            print("Differences:")
            for k in set(before).union(after):
                if before.get(k) != after.get(k):
                    print(f"  {k}: {before.get(k)} -> {after.get(k)}")
            raise ValueError(
                f"Please choose a different pool name. Pool with name '{pool_name}' was already submitted in this round with different parameters."
            )
        if design_job.job_result is False:
            print(f"Pool with name '{pool_name}' already exists in this round but its job has FAILED")
            if resume_failed:
                print("Resuming job...")
                design_job.job_result = None
                design_job.job_finished_date_utc = None
                design_job.job_id = scheduler.resume(design_job.job_id)
                delete_job_artifacts(design_job)
                db.save(design_job)
            else:
                raise ValueError(
                    f"Pool with name '{pool_name}' already exists in this round but its job has FAILED. "
                    f"Use resume_failed=True (--resume-failed in the CLI) to resubmit the job, "
                    f"or choose a different pool name to submit a new job."
                )
        else:
            print("Pool with same name and params already exists in this round, returning existing pool")
        return design_job, pool

    if config.props.read_only:
        raise RuntimeError("Cannot submit design workflow: OVO server is in read-only mode")

    # Create a deep copy of the workflow object to avoid errors
    # when users modify workflow params in place and resubmit
    workflow = deepcopy(workflow)

    workflow.validate()

    username = get_username()

    job_id = scheduler.submit(
        pipeline_name=pipeline_name or workflow.get_pipeline_name(),
        params=workflow.prepare_params(workdir=scheduler.workdir),
        submission_args=submission_args,
    )

    try:
        design_job = DesignJob(
            workflow=workflow,
            job_id=job_id,
            scheduler_key=scheduler_key,
            author=username,
        )

        pool = Pool(
            id=Pool.generate_id(),
            author=username,
            round_id=round_id,
            name=pool_name,
            description=pool_description,
            design_job_id=design_job.id,
            processed=False,
        )

        db.save_all([design_job, pool])

    except Exception:
        traceback.print_exc()
        # If there was an error saving to the DB, try to cancel the job in the scheduler to avoid orphaned jobs
        try:
            scheduler.cancel(job_id)
        except Exception as cancel_exception:
            traceback.print_exc()
            print(f"Error cancelling job {job_id} after DB save failure: {cancel_exception}")
        raise

    return design_job, pool


def get_log(design_job: DesignJob, task_id: str = None, preview: bool = False, tail: int = None) -> str:
    """Get the log of a design job from the scheduler."""
    assert isinstance(design_job, DesignJob), f"Expected DesignJob, got {type(design_job).__name__}"
    scheduler = get_scheduler(design_job.scheduler_key)
    log = scheduler.get_log(design_job.job_id, task_id=task_id, preview=preview)
    if tail is not None and log is not None:
        log_lines = log.splitlines()
        log = "\n".join(log_lines[-tail:])
    return log


def get_tasks(design_job: DesignJob) -> pd.DataFrame:
    """Get design job tasks table from the scheduler."""
    assert isinstance(design_job, DesignJob), f"Expected DesignJob, got {type(design_job).__name__}"
    scheduler = get_scheduler(design_job.scheduler_key)
    return scheduler.get_tasks(design_job.job_id)


def process_results(design_job: DesignJob, callback: Callable = None, wait=True) -> Pool:
    """Process the results of a design job and return the pool object.

    This downloads/copies the workflow results into Storage
    and saves the Design and DescriptorValue objects to the database."""
    assert isinstance(design_job, DesignJob), f"Expected DesignJob, got {type(design_job).__name__}"

    pool = db.get(Pool, design_job_id=design_job.id)
    if pool.processed:
        # Pool already processed
        print("Pool already processed, returning existing pool")
        return pool
    scheduler = get_scheduler(design_job.scheduler_key)
    if scheduler.get_result(design_job.job_id) is None:
        # Job is still running
        if wait:
            print(f"Waiting for job {design_job.job_id} to finish...")
            scheduler.wait(design_job.job_id)
        else:
            raise ValueError(
                f"Job {design_job.job_id} has not finished yet, try again later or use scheduler.wait(design_job.job_id)"
            )
    # Job should be successful or failed now, update job status
    update_job_status(design_job)
    if design_job.job_result is False:
        print(scheduler.get_log(design_job.job_id))
        print(scheduler.get_failed_message(design_job.job_id), file=sys.stderr)
        print()
        raise ValueError(f"Job {design_job.job_id} has failed")
    # Create artifact for successful job
    artifact = create_job_report_artifact(design_job, scheduler)
    # Process results
    print("Job finished, processing pool results...")
    objects = design_job.workflow.process_results(design_job, callback=callback)
    assert isinstance(objects, list), f"Expected list from process_results(), got {type(objects).__name__}"
    # Mark pool as processed
    pool.processed = True
    flag_modified(design_job, "workflow")
    flag_modified(design_job, "warnings")
    if artifact:
        objects.append(artifact)
    # Atomically save all objects
    db.save_all(objects + [pool, design_job])
    return pool


def update_acceptance_thresholds(pools: list[Pool], acceptance_thresholds: dict[str, Threshold]):
    """Update the accepted designs in a pool based on the given acceptance thresholds.

    Save the Design objects and the DesignJob.workflow.acceptance_thresholds to the DB.
    """
    for pool in pools:
        assert isinstance(pool, Pool), f"Expected collection of Pool objects, got {pool} ({type(pool).__name__})"
        assert pool.design_job_id is not None, f"Pool must have a design job to update acceptance thresholds: {pool.id}"
    all_design_ids = db.select_values(Design, "id", pool_id__in=[p.id for p in pools])
    design_jobs = db.select(DesignJob, id__in=[p.design_job_id for p in pools])
    new_accepted_design_ids, num_accepted_by_descriptor = filter_designs_by_thresholds(
        all_design_ids=all_design_ids,
        thresholds=acceptance_thresholds,
        values={
            descriptor_key: db.select_descriptor_values(descriptor_key, design_ids=all_design_ids).to_dict()
            for descriptor_key, threshold in acceptance_thresholds.items()
            if threshold.enabled
        },
    )
    # Save the acceptance thresholds to the DesignJob
    for job in design_jobs:
        job.workflow.acceptance_thresholds = acceptance_thresholds
        # tell sqlalchemy that we modified the workflow object - with dataclasses this is not auto-detected
        flag_modified(job, "workflow")
    db.save_all(design_jobs)
    # Save accepted field of Design objects
    update_accepted_design_ids(pool_ids=[p.id for p in pools], accepted_design_ids=new_accepted_design_ids)


def update_accepted_design_ids(pool_ids: list[str], accepted_design_ids: list[str]):
    db.save_value(Design, "accepted", False, pool_id__in=pool_ids)
    db.save_value(Design, "accepted", True, id__in=accepted_design_ids)
    saved_ids = set(db.select_values(Design, "id", pool_id__in=pool_ids, accepted=True))
    assert saved_ids == set(accepted_design_ids), (
        f"Unexpected error marking designs as accepted "
        f"({saved_ids.difference(accepted_design_ids)} extra, "
        f"{set(accepted_design_ids).difference(saved_ids)} missing)"
    )


def set_designs_accepted(
    designs: list[Design],
    descriptor_values: list[DescriptorValue],
    job: DesignJob,
    skipped_keys: Collection[str] | None = None,
):
    """Update the accepted field of designs based on the given thresholds (does not save to DB)

    Makes the following modifications IN PLACE:
    - If a threshold is enabled but its descriptor values are missing:
      - set threshold.enabled to False
      - add a warning in the DesignJob job.warnings
    - Update the accepted field of each design based on whether it passes the thresholds or not.

    :param designs: List of Design objects to update
    :param descriptor_values: List of DescriptorValue objects to use for checking thresholds
    :param job: DesignJob object
    :param skipped_keys: Do not apply these descriptor keys (used for descriptors that are not computed)
    """

    if isinstance(job, dict):
        warnings.warn(
            "set_designs_accepted should be called with the DesignJob instead of acceptance thresholds",
            DeprecationWarning,
            stacklevel=2,
        )
        thresholds = job
        job = None
    else:
        assert isinstance(job, DesignJob), f"Expected DesignJob, got {type(job).__name__}"
        thresholds = job.workflow.acceptance_thresholds

    available_descriptor_keys = set(dv.descriptor_key for dv in descriptor_values)
    warn_missing_descriptor_keys = []
    for descriptor_key, threshold in thresholds.items():
        if skipped_keys and descriptor_key in skipped_keys:
            threshold.enabled = False
            continue
        if descriptor_key not in available_descriptor_keys and threshold.enabled:
            threshold.enabled = False
            warn_missing_descriptor_keys.append(descriptor_key)

    if warn_missing_descriptor_keys and job is not None:
        job.warnings.append(
            f"Some descriptors were not computed, their acceptance threshold was not applied: {', '.join(warn_missing_descriptor_keys)}"
        )

    # initialize dict of dicts (descriptor_key -> design_id -> value)
    values = {}
    for descriptor_value in descriptor_values:
        if descriptor_value.descriptor_key not in thresholds:
            continue
        if descriptor_value.descriptor_key not in values:
            values[descriptor_value.descriptor_key] = {}
        values[descriptor_value.descriptor_key][descriptor_value.design_id] = (
            float(descriptor_value.value) if descriptor_value.value is not None else None
        )
    # get list of accepted design ids based on thresholds
    accepted_design_ids, _ = filter_designs_by_thresholds(
        all_design_ids=[d.id for d in designs],
        thresholds=thresholds,
        values=values,
    )
    # update the accepted field of designs
    accepted_design_ids = set(accepted_design_ids)
    for design in designs:
        design.accepted = design.id in accepted_design_ids


def get_descriptor_job_id_for_key(descriptor_job_id: str | dict | None, descriptor_key: str) -> str | None:
    """Return the descriptor job to read a descriptor key from, out of the caller's descriptor_job_id.

    ``descriptor_job_id`` is either one job ID for all keys, or {job ID: keys of that job} as the
    descriptor selection produces it, or None to read the key from any job.
    """
    if isinstance(descriptor_job_id, dict):
        return next((job_id for job_id, keys in descriptor_job_id.items() if descriptor_key in keys), None)
    return descriptor_job_id


def collect_storage_paths(
    download_fields: dict[str, tuple[Base, str]],
    design_ids: list,
    descriptor_job_id: str | dict[str, list[str]] | None = None,
) -> dict[str | None, list[str]]:
    """Collect storage paths from designs based on fields returned by DesignWorkflow.get_download_fields().

    :param download_fields: Fields returned by DesignWorkflow.get_download_fields()
    :param design_ids: List of design IDs to collect storage paths for
    :param descriptor_job_id: Optional dict mapping job ID to list of its descriptor keys that should be included (used for descriptors that require a job id)
    :return: Dict of {design_id (or None if input): list of storage paths}
    """
    storage_paths = defaultdict(list)
    for label, (Model, field_name) in download_fields.items():
        if "." in field_name:
            # Allow nesting like rfdiffusion_params.input_pdb_path
            assert field_name.count(".") == 1, f"Only single-level relationships supported, got: {field_name}"
            field_name, subfield_name = field_name.split(".")
        else:
            # Regular field like structure_path
            subfield_name = None

        field_job_id = get_descriptor_job_id_for_key(descriptor_job_id, field_name)
        descriptor_job_filter = {"descriptor_job_id": field_job_id} if field_job_id else {}

        if issubclass(Model, Design):
            # Get field values from Design objects
            paths_and_ids = db.select_dict(Model, field_name, "id", id__in=design_ids)
        elif issubclass(Model, DesignWorkflow):
            # Get field values from DesignWorkflow objects via the DesignJob associated with each Pool
            pool_ids = db.select_unique_values(Design, "pool_id", id__in=design_ids)
            pools = db.select(Pool, id__in=pool_ids)
            design_job_ids = [pool.design_job_id for pool in pools if pool.design_job_id]
            paths_and_ids = {}
            for workflow in db.select_values(DesignJob, "workflow", id__in=design_job_ids):
                if isinstance(workflow, Model):
                    value = getattr(workflow, field_name)
                    path = value if subfield_name is None else getattr(value, subfield_name)
                    if isinstance(path, list):
                        path = tuple(path)
                    paths_and_ids[path] = None
        elif issubclass(Model, DescriptorValue):
            paths_and_ids = db.select_dict(
                Model,
                "value",
                "design_id",
                descriptor_key=field_name,
                design_id__in=design_ids,
                **descriptor_job_filter,
            )
        else:
            raise ValueError(
                f"Unsupported model {Model.__name__} for download, use a subclass of Design or DesignWorkflow"
            )

        for path, design_id in paths_and_ids.items():
            if not path:
                continue
            elif isinstance(path, str):
                storage_paths[design_id].append(path)
            elif isinstance(path, list) or isinstance(path, tuple):
                storage_paths[design_id].extend(path)
            else:
                raise ValueError(
                    f"Unexpected field type {type(path)} for {field_name}.{subfield_name}, expected str or list"
                )

    # make sure paths are unique
    for design_id in storage_paths:
        storage_paths[design_id] = list(set(storage_paths[design_id]))

    return storage_paths


def collect_storage_paths_by_group(
    download_fields: dict[str, tuple[Base, str]],
    design_ids: list[str],
    default_group: str = "",
    group_by: str = None,
    group_by_fmt: str = "{}",
    group_by_values: dict[str, object] = None,
    descriptor_job_id: str | dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    """Collect the storage paths to export and arrange them into zip directories.

    Without ``group_by`` everything lands in one directory (``default_group``). With it, each
    design's files land in a directory named after that design's value of the ``group_by``
    descriptor — designs missing the descriptor go to "other", and files that belong to the workflow
    input rather than a design go to "inputs".

    :param download_fields: Fields to export, from
                            ``ovo.core.logic.import_export_logic.resolve_download_fields``
    :param design_ids: Designs to export files for
    :param default_group: Zip directory to use when not grouping ("" for the zip root)
    :param group_by: Optional descriptor key to group the files by
    :param group_by_fmt: Format string applied to each group_by value to make the directory name
    :param group_by_values: Optional pre-loaded {design_id: value} for group_by (the web app passes cached)
    :param descriptor_job_id: Optional descriptor job ID to filter by, or {job id: [descriptor keys]}
    :return: {zip directory: [storage path, ...]}
    """
    storage_paths_by_design = collect_storage_paths(download_fields, design_ids, descriptor_job_id=descriptor_job_id)
    if not storage_paths_by_design:
        return {}

    if group_by is None:
        return {default_group: sorted({path for paths in storage_paths_by_design.values() for path in paths})}

    if group_by_values is None:
        group_by_job_id = get_descriptor_job_id_for_key(descriptor_job_id, group_by)
        group_by_values = (
            db.select_descriptor_values(group_by, design_ids=design_ids, descriptor_job_id=group_by_job_id)
            .dropna()
            .to_dict()
        )

    storage_paths_by_group = defaultdict(list)
    for design_id, paths in storage_paths_by_design.items():
        if design_id is None:
            group_value = "inputs"
        elif design_id not in group_by_values:
            group_value = "other"
        else:
            group_value = group_by_fmt.format(group_by_values[design_id])
        storage_paths_by_group[group_value].extend(paths)
    return dict(storage_paths_by_group)


def create_designs_from_dataframe(
    df: pd.DataFrame,
    id_column: str,
    column_chains: dict[str, str],
    pool_id: str,
) -> list[Design]:
    """
    Create Design objects from a DataFrame.

    Args:
        df: pandas DataFrame with design data
        id_column: column name to use as design ID
        column_chains: mapping of column names to chain IDs (e.g., {"seq_A": "A", "seq_B": "B"})
        pool_id: pool ID for the designs

    Returns:
        list of Design objects
    """
    designs = []
    for idx, row in df.iterrows():
        # Ensure design_id starts with "ovo_" prefix and contains pool_id
        design_id = f"ovo_{pool_id}_{row[id_column]}"

        # Create design chains from selected sequence columns
        chains = []
        for seq_col, chain_ids_str in column_chains.items():
            if pd.isna(row[seq_col]):
                continue
            # Split chain IDs by comma or space, then clean up
            chain_ids = [cid.strip() for cid in chain_ids_str.replace(",", " ").split() if cid.strip()]
            chains.append(
                DesignChain(
                    type="protein",
                    chain_ids=chain_ids,
                    sequence=str(row[seq_col]),
                )
            )

        if not chains:
            # No sequence columns with valid data for this design, skip it
            continue

        designs.append(
            Design(
                id=design_id,
                pool_id=pool_id,
                spec=DesignSpec(chains=chains),
                structure_path=None,  # No structure file for sequence-only designs
            )
        )

    return designs


def create_designs_from_structure_files(
    structure_files: list, chains: list[str], pool: Pool, project_id: str
) -> tuple[list[Design], list[str]]:
    shared_args = dict(
        storage=storage,
        chains=chains,
        project_id=project_id,
        pool_id=pool.id,
    )
    designs = []
    conversion_warnings = []
    for file in structure_files:
        if file.name.lower().endswith(".pdb"):
            designs.append(Design.from_pdb_file(filename=file.name, pdb_str=file.read().decode(), **shared_args))
        elif file.name.lower().endswith((".cif", ".mmcif")):
            pdb_filename = os.path.splitext(file.name)[0] + ".pdb"
            result = mmcif_to_pdb(file.read().decode())
            conversion_warnings.extend(result.warnings)
            designs.append(Design.from_pdb_file(filename=pdb_filename, pdb_str=result.pdb_string, **shared_args))
        elif file.name.lower().endswith(".zip"):
            found = False
            with zipfile.ZipFile(file) as z:
                for zip_info in z.infolist():
                    if zip_info.filename.startswith("__MACOSX/"):
                        continue
                    filename = os.path.basename(zip_info.filename)
                    if filename.startswith("."):
                        continue
                    if filename.lower().endswith(".pdb"):
                        found = True
                        print("Reading", zip_info.filename)
                        pdb_str = z.read(zip_info.filename).decode()
                        designs.append(
                            Design.from_pdb_file(
                                filename=filename,
                                pdb_str=pdb_str,
                                **shared_args,
                            )
                        )
                    elif filename.lower().endswith((".cif", ".mmcif")):
                        found = True
                        print("Reading and converting", zip_info.filename)
                        pdb_filename = os.path.splitext(filename)[0] + ".pdb"
                        result = mmcif_to_pdb(z.read(zip_info.filename).decode())
                        conversion_warnings.extend(result.warnings)
                        designs.append(
                            Design.from_pdb_file(
                                filename=pdb_filename,
                                pdb_str=result.pdb_string,
                                **shared_args,
                            )
                        )
            if not found:
                raise ValueError(f"No PDB or CIF files found in zip archive '{file.name}'")
    return designs, conversion_warnings


def get_common_chain_ids(design_ids: list[str]) -> tuple[list[str], list[str]]:
    """Get chain IDs that exist across all provided designs' specs"""
    specs = db.select_values(Design, "spec", id__in=design_ids)
    chain_id_counts = {}
    for spec in specs:
        if not spec:
            continue
        for chain in spec.chains:
            for chain_id in chain.chain_ids:
                if chain_id not in chain_id_counts:
                    chain_id_counts[chain_id] = 0
                chain_id_counts[chain_id] += 1
    common_chain_ids = sorted([chain_id for chain_id, count in chain_id_counts.items() if count == len(specs)])
    available_chain_ids = sorted(chain_id_counts.keys())
    return common_chain_ids, available_chain_ids


def get_designed_chain_ids_by_design_id(design_ids: list[str]) -> dict[str, list[str]]:
    """Get the designed chain IDs of each design, based on its spec (which only contains the designed chains)"""
    designs = db.select(Design, id__in=design_ids)
    designed_chain_ids_by_design_id = {}
    for design in designs:
        if not design.spec or not design.spec.chains:
            raise ValueError(f"Design {design.id} has no chains in its spec, cannot determine the designed chains")
        designed_chain_ids_by_design_id[design.id] = design.spec.get_designed_chain_ids()
    return designed_chain_ids_by_design_id


def store_structures_with_binder_as_chain_a(designs: list[Design], project_id: str) -> list[str]:
    """Store a copy of the structure of each design with its binder chain labelled A and its target B.

    The RFdiffusion binder workflows assume the binder is chain A - see
    :meth:`~ovo.core.database.models_rfdiffusion.RFdiffusionBinderDesignWorkflow.get_refolding_designed_chains`
    and the partial diffusion contig, which puts the diffused binder first - while a design can label
    it differently (BindCraft labels the binder B). Designs are therefore relabelled before they are
    diversified, the same way designs with differently labelled chains are relabelled for a
    clustering job, see
    :func:`~ovo.core.logic.descriptor_logic.prepare_design_structures`.

    A design that already has the binder as chain A and the target as chain B is used as it is, so
    the common case keeps pointing at the design's own structure rather than at a copy of it.

    :return: One storage path per design, in the given order
    :raises ValueError: if a design does not have exactly one designed and one target chain
    """
    designed_chains_by_design_id = get_designed_chain_ids_by_design_id([design.id for design in designs])

    storage_paths = []
    with storage.bulk_read_context():
        for design in designs:
            designed_chains = list(designed_chains_by_design_id[design.id])
            pdb_str = storage.read_file_str(design.structure_path)
            all_chains = sorted(get_chains_and_contigs(pdb_str))
            target_chains = [chain_id for chain_id in all_chains if chain_id not in designed_chains]
            if len(designed_chains) != 1 or len(target_chains) != 1:
                raise ValueError(
                    f"Design {design.id} has chains {', '.join(all_chains)} of which "
                    f"{', '.join(designed_chains)} designed - expected one binder and one target chain"
                )
            if designed_chains + target_chains == ["A", "B"]:
                storage_paths.append(design.structure_path)
                continue
            storage_paths.append(
                storage.store_input(
                    project_id=project_id,
                    file_str=filter_and_relabel_chains_pdb_str(pdb_str, designed_chains + target_chains),
                    filename=f"{design.id}.pdb",
                )
            )
    return storage_paths
