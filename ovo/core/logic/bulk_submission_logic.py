"""Bulk design workflow submission: parse a config, expand its grids, resolve inputs, submit.

Front-end agnostic — the Bulk Submission page (``ovo/app/pages/bulk/bulk_submission.py``) and
``ovo workflow submit`` (``ovo/cli/workflow_cli.py``) both drive the same sequence from here:

1. :func:`import_bulk_config` — config dict to a list of expanded :class:`BulkSubmission` records
2. :func:`find_list_on_scalar_fields` — warn about a plain list where a grid was probably meant
3. :func:`check_workflows_limit` — refuse a grid larger than the server allows
4. :func:`resolve_input_paths` — get every referenced input file into storage
5. :func:`validate_submissions` — check the pool names and workflows of the whole batch
6. :func:`bulk_submit` — submit each workflow, collecting per-workflow errors

The config format is a list of submissions, each pairing the pool to create with the workflow to
run in it::

    submissions:
      - pool_name: My binders
        pool_description: first attempt
        workflow:
          name: RFdiffusion scaffold design
          rfdiffusion_params:
            timesteps: {grid: [20, 50]}   # expands this submission into 2 workflows

The two front-ends differ only in where input files come from (uploaded bytes vs. local paths
relative to the config file) and in how progress is reported — hence
:func:`resolve_input_paths`'s two keyword arguments and :func:`bulk_submit`'s ``callback``.
The web app also lets the user type a pool name and description prefix in the UI, which it passes as
:func:`bulk_submit`'s ``pool_name_prefix`` and ``pool_description_prefix`` — they name and describe
the pools of the submissions that the config did not, and prefix those that it did.

:func:`export_bulk_config` is the inverse of step 1, used to re-export previously submitted
workflows as a config dict — as YAML text via
:func:`~ovo.core.utils.bulk_submission_utils.dump_bulk_config_yaml`, or as a ZIP with the input
files via :func:`export_bulk_config_zip`.
"""

import io
import json
import os
import traceback
import typing
import zipfile
from dataclasses import dataclass, field
from dataclasses import fields as dataclass_fields

from ovo import config, db, storage
from ovo.core.database.models import DesignJob, DesignWorkflow, Pool, UnknownWorkflow, Workflow, WorkflowTypes
from ovo.core.logic.design_logic import submit_design_workflow
from ovo.core.logic.import_export_logic import can_export_bulk_config, get_pools_filename_prefix
from ovo.core.utils.bulk_submission_utils import (
    count_grid_combos,
    dump_bulk_config_yaml,
    expand_grid_configs,
    format_combo_string,
    get_storage_path_values,
    get_unique_storage_path_values,
    get_workflow_configs,
    match_uploaded_file,
    replace_storage_paths,
)
from ovo.core.utils.formatting import get_hashed_path_for_bytes


@dataclass
class BulkSubmission:
    """One workflow of a bulk submission, together with the pool it will be submitted to.

    Produced by :func:`import_bulk_config` (one per expanded workflow) and consumed by
    :func:`bulk_submit`, which reports one :class:`BulkSubmissionResult` per submission.

    ``pool_name`` and ``pool_description`` hold what the config gave, under the same names as the
    config keys (``None`` when it did not set them). The name and description actually submitted
    under are derived on demand by :meth:`get_pool_name` and :meth:`get_pool_description`, so a
    front-end can render them on every rerun without mutating anything.

    ``combo_index`` and ``num_combos`` describe the position within the config entry this workflow was
    expanded from, **not** within the whole submission, so the second entry of a config starts
    counting its combos at 1 again.
    """

    workflow: DesignWorkflow
    pool_name: str | None = None  # pool name from the config, None if it did not name a pool
    pool_description: str | None = None
    combo: dict = field(default_factory=dict)  # {dotted param path: grid value}, empty without a grid
    combo_index: int = 0  # index of this combo within the config entry it was expanded from
    num_combos: int = 1  # number of combos that config entry expanded into

    def get_pool_name(self, prefix: str = "") -> str:
        """Return the pool name to submit under, built from prefix and the name from the config.

        A prefix (the web app's "Pool name prefix" input, nothing in the CLI) is joined to the
        config's pool name with a space, and names the pool on its own if the config did not.
        A config entry expanded into a grid gets "Combo N" appended, so its pools stay
        distinguishable in the round.

        Returns "" if neither side named the pool, so a grid does not end up with pools named after
        nothing but their combo number.
        """
        name = " ".join(part for part in (prefix, self.pool_name) if part)
        if not name:
            return ""
        if self.num_combos > 1:
            name = f"{name} Combo {self.combo_index + 1}"
        return name

    def get_pool_description(self, prefix: str = "") -> str:
        """Return the pool description, built from prefix and the description from the config.

        Like :meth:`get_pool_name`, the prefix (the web app's description input) is joined to the
        config's description with a space, and describes the pool on its own if the config did not.
        The grid combo values are appended, so each pool of a grid says which values it used.
        """
        description = " ".join(part for part in (prefix, self.pool_description) if part)
        return (description + format_combo_string(self.combo)).strip()

    @classmethod
    def get_pool_names(cls, submissions: list["BulkSubmission"], pool_name_prefix: str = "") -> list[str]:
        """Return the pool name of each submission, validating that they can all be created.

        :param pool_name_prefix: Prefixed to the pool name of every submission, see
            :meth:`get_pool_name`
        :raises ValueError: if a submission ends up without a pool name, or if two submissions would
            submit into the same pool — pool names are unique within a round, so this would otherwise
            fail halfway through :func:`bulk_submit`, after the earlier workflows were already
            submitted
        """
        pool_names = [submission.get_pool_name(pool_name_prefix) for submission in submissions]

        if unnamed := [i + 1 for i, pool_name in enumerate(pool_names) if not pool_name]:
            raise ValueError(f"Missing pool name for submission(s): {', '.join(str(i) for i in unnamed)}")

        if duplicates := sorted({name for name in pool_names if pool_names.count(name) > 1}):
            raise ValueError(
                f"Duplicate pool name(s): {', '.join(duplicates)} - each submission needs its own pool, "
                f"as pool names are unique within a round."
            )

        return pool_names


@dataclass
class BulkSubmissionResult:
    """Outcome of submitting one workflow of a bulk submission (error is None on success)."""

    pool_name: str
    pool_description: str
    design_job_id: str = None
    pool_id: str = None
    error: str = None

    @property
    def success(self) -> bool:
        return self.error is None


def import_bulk_config(config_dict: dict) -> list[BulkSubmission]:
    """Parse a bulk submission config dict into BulkSubmission records, one per expanded workflow.

    Expects top-level key 'submissions', each entry pairing 'pool_name'/'pool_description' with the
    'workflow' to run (see the module docstring). Grid parameters (values of the form
    {grid: [v1, v2, ...]}) are expanded via Cartesian product across all grid fields of a workflow,
    and the resulting pools are named "<pool_name> Combo N" (see
    :meth:`BulkSubmission.get_pool_name`). A submission that
    does not name its pool leaves that to the caller of :func:`bulk_submit`.

    Uses Workflow.from_dict for deserialization — no custom subtype logic needed.

    Raises ValueError for malformed configs: a missing or unregistered workflow name, a workflow
    that cannot be deserialized, or a grid larger than the configured workflows limit.
    """
    workflow_configs = get_workflow_configs(config_dict)

    for wf_config in workflow_configs:
        if not wf_config.get("name"):
            raise ValueError("Each workflow needs a 'name' with the workflow type, see 'ovo workflow names'")
        # Raises ValueError listing the available types if the name is not a registered workflow type
        WorkflowTypes.get(wf_config["name"])

    # Check the limit before expanding, a large grid would take a long time and a lot of memory to expand
    check_workflows_limit(sum(count_grid_combos(wf_config) for wf_config in workflow_configs))

    submissions = []
    for submission_config, wf_config in zip(config_dict["submissions"], workflow_configs):
        expanded_configs, combos = expand_grid_configs(wf_config)
        for combo_index, (cfg, combo) in enumerate(zip(expanded_configs, combos)):
            workflow = Workflow.from_dict(cfg)
            if workflow.is_instance(UnknownWorkflow):
                raise ValueError(f"Invalid config for workflow '{cfg['name']}': {workflow.error}")
            submissions.append(
                BulkSubmission(
                    workflow=workflow,
                    pool_name=submission_config.get("pool_name") or None,
                    pool_description=submission_config.get("pool_description") or None,
                    combo=combo,
                    combo_index=combo_index,
                    num_combos=len(expanded_configs),
                )
            )

    return submissions


def export_bulk_config(submissions: list[BulkSubmission]) -> dict:
    """Return the bulk submission config dict of the submissions, the inverse of :func:`import_bulk_config`.

    The pool name and description of each submission are exported alongside its workflow, which is
    serialized with :meth:`Workflow.to_dict` (clean=True, so UI state fields are left out).
    Serialize it with :func:`~ovo.core.utils.bulk_submission_utils.dump_bulk_config_yaml`, or use
    :func:`export_bulk_config_zip` to export the input files along with it.
    """
    return {
        "submissions": [
            {
                # The names as configured, without the grid combo suffix that submission adds
                "pool_name": s.pool_name or "",
                "pool_description": s.pool_description or "",
                "workflow": s.workflow.to_dict(clean=True),
            }
            for s in submissions
        ]
    }


def find_list_on_scalar_fields(config_dict: dict) -> list[str]:
    """Return warning strings for any field that has a plain list value but is typed as a scalar.

    A likely mistake: `timesteps: [20, 50]` on a scalar field is passed through as a list and fails
    validation later, where `timesteps: {grid: [20, 50]}` would have expanded into two workflows.
    Advisory only — nothing here blocks submission, and a config that is not valid yet (the user is
    still typing) simply produces no warnings.
    """
    try:
        workflow_configs = get_workflow_configs(config_dict)
    except ValueError:
        return []

    warnings = []
    for wf_config in workflow_configs:
        wf_name = wf_config.get("name", "")
        try:
            wf_cls = WorkflowTypes.get(wf_name)
        except Exception:
            continue
        instance = wf_cls()
        for param_field_name, param_instance in instance.get_param_fields().items():
            param_dict = wf_config.get(param_field_name)
            if not isinstance(param_dict, dict):
                continue
            for f in dataclass_fields(param_instance):
                value = param_dict.get(f.name)
                if not isinstance(value, list):
                    continue
                # Skip grid dicts — those are intentional
                if len(value) > 0 and isinstance(value[0], dict) and "grid" in value[0]:
                    continue
                origin = typing.get_origin(f.type)
                if origin is not list:
                    warnings.append(
                        f"`{param_field_name}.{f.name}` is typed as `{getattr(f.type, '__name__', str(f.type))}`, not a list.\n\n"
                        f"If you meant to submit a grid of values, please use the following format:\n\n"
                        f"```yaml\n    {f.name}:\n      grid: {json.dumps(value)}\n```"
                    )
    return warnings


def check_workflows_limit(num_workflows: int) -> None:
    """Raise ValueError if a grid of num_workflows exceeds props.bulk_submission_workflows_limit."""
    limit = config.props.bulk_submission_workflows_limit
    if num_workflows > limit:
        raise ValueError(
            f"Cannot submit {num_workflows} workflows - this OVO server is configured "
            f"to only allow submitting up to {limit} workflows at once."
        )


def resolve_input_paths(
    workflows: list[DesignWorkflow],
    project_id: str,
    uploaded_files: dict[str, bytes] = None,
    base_dir: str = None,
) -> None:
    """Get every input file referenced by the workflows into storage, rewriting the paths in place.

    Each storage_path value found on the workflows is resolved in this order:

    1. present in ``uploaded_files`` (filename -> bytes, matched by :func:`match_uploaded_file`) —
       stored from those bytes
    2. already a valid storage path — left alone
    3. ``base_dir`` given — resolved as a local file relative to it (absolute paths as-is) and uploaded

    :param workflows: Expanded workflows, **mutated in place** to point at the resolved storage paths
    :param project_id: Project whose storage the inputs are stored under
    :param uploaded_files: Optional {filename: bytes} of files supplied by the caller (the web app)
    :param base_dir: Optional directory to resolve relative local paths against (the CLI's config dir)
    :raises FileNotFoundError: if a referenced path matches none of the three cases
    """
    all_paths = {path for paths in get_storage_path_values(workflows).values() for path in paths}

    path_mapping = {}
    for path in sorted(all_paths):
        if uploaded_key := match_uploaded_file(path, uploaded_files):
            path_mapping[path] = storage.store_input(
                project_id=project_id,
                file_bytes=uploaded_files[uploaded_key],
                filename=os.path.basename(uploaded_key),
            )
        elif storage.file_exists(path, storage_only=True):
            # Already in storage, no need to upload — leave the path untouched
            continue
        elif base_dir is not None:
            local_path = path if os.path.isabs(path) else os.path.join(base_dir, path)
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Input file not found: {path} (resolved to {local_path})")
            path_mapping[path] = storage.store_input(
                project_id=project_id,
                file_path=local_path,
                filename=os.path.basename(local_path),
            )
        else:
            raise FileNotFoundError(f"Input file not found in storage or among the provided files: {path}")

    if path_mapping:
        print(f"Uploaded {len(path_mapping)} input file(s) to storage")
    # replace storage paths in-place
    replace_storage_paths(workflows, path_mapping)


def get_unresolved_input_paths(
    workflows: list[DesignWorkflow], uploaded_files: dict[str, bytes] = None, verified_paths: set[str] = None
) -> dict[str, list[str]]:
    """Return {dotted field path: [unresolvable path, ...]} for inputs neither uploaded nor in storage.

    Read-only counterpart to :func:`resolve_input_paths`, so a front-end can report what is missing
    before anything is uploaded or submitted. ``verified_paths`` is an optional set of paths already
    known to exist in storage, to save repeated existence checks.
    """
    unresolved = {}
    for field_path, paths in get_storage_path_values(workflows).items():
        for path in sorted(paths):
            if match_uploaded_file(path, uploaded_files):
                continue
            if verified_paths is not None and path in verified_paths:
                continue
            if storage.file_exists(path, storage_only=True):
                if verified_paths is not None:
                    verified_paths.add(path)
                continue
            unresolved.setdefault(field_path, []).append(path)
    return unresolved


def validate_submissions(
    submissions: list[BulkSubmission],
    round_id: str,
    pool_name_prefix: str = "",
    return_existing: bool = True,
) -> list[str]:
    """Check everything that must hold before any of the submissions is submitted, returning their pool names.

    Called by :func:`bulk_submit` so a batch that cannot be submitted fails as a whole, instead of
    submitting workflows until it reaches the bad one. A front-end can also call it earlier (the CLI
    does, before uploading input files) to report the problem before anything happens.

    :param round_id: Round the pools would be created in, to check the names it already contains
    :param pool_name_prefix: Prefixed to every pool name, see :meth:`BulkSubmission.get_pool_name`
    :param return_existing: Skip the check for names already used in the round, as submitting into an
        existing identical pool is then intentional (see submit_design_workflow)
    :raises ValueError: if the pool names are not all present and unique, if one of them is already
        used in the round, or if a workflow is not valid
    """
    pool_names = BulkSubmission.get_pool_names(submissions, pool_name_prefix)

    if not return_existing:
        existing_names = {pool.name for pool in db.select(Pool, round_id=round_id)}
        if taken := sorted(existing_names.intersection(pool_names)):
            raise ValueError(
                f"Pool name(s) already used in this round: {', '.join(taken)} - "
                f"please choose a different pool name, or submit into a new round."
            )

    for pool_name, submission in zip(pool_names, submissions):
        try:
            submission.workflow.validate()
        except Exception as e:
            raise ValueError(f"Invalid workflow of pool '{pool_name}': {e}") from e

    return pool_names


def bulk_submit(
    submissions: list[BulkSubmission],
    scheduler_key: str,
    round_id: str,
    pool_name_prefix: str = "",
    pool_description_prefix: str = "",
    return_existing: bool = True,
    resume_failed: bool = False,
    callback: typing.Callable[[BulkSubmissionResult], None] = None,
) -> list[BulkSubmissionResult]:
    """Submit each of the expanded submissions, returning one result record per submission.

    Pool names come from the submissions as prepared by :func:`import_bulk_config`, prefixed with
    ``pool_name_prefix``, which also names the pools of the submissions whose config did not.

    A failure to submit one workflow does not abort the rest — it is recorded on that workflow's
    result, so the caller decides how to report a partial failure. ``callback`` is invoked with each
    result as it completes, for a progress bar or a line of CLI output.

    :param submissions: Expanded submissions, with input paths already resolved by :func:`resolve_input_paths`
    :param pool_name_prefix: Prefixed to every pool name, e.g. entered in the web app
    :param pool_description_prefix: Prefixed to every pool description, e.g. entered in the web app
    :param return_existing: Return an existing identical pool instead of raising (see submit_design_workflow)
    :param resume_failed: Resubmit if a pool of the same name exists in this round and its job failed
    :raises ValueError: if the submissions cannot all be submitted, see :func:`validate_submissions`
    """
    # Validated up front, so a bad batch does not submit half of the workflows before it is noticed
    pool_names = validate_submissions(
        submissions, round_id=round_id, pool_name_prefix=pool_name_prefix, return_existing=return_existing
    )

    results = []
    for i, submission in enumerate(submissions):
        result = BulkSubmissionResult(
            pool_name=pool_names[i],
            pool_description=submission.get_pool_description(pool_description_prefix),
        )
        try:
            design_job, pool = submit_design_workflow(
                workflow=submission.workflow,
                scheduler_key=scheduler_key,
                round_id=round_id,
                pool_name=result.pool_name,
                pool_description=result.pool_description,
                return_existing=return_existing,
                resume_failed=resume_failed,
            )
            result.design_job_id = design_job.id
            result.pool_id = pool.id
        except Exception as e:
            traceback.print_exc()
            result.error = str(e)
        results.append(result)
        if callback is not None:
            callback(result)

    return results


def get_bulk_config_template(name: str) -> str:
    """Return a bulk submission config template for a workflow type, with all defaults filled in.

    This is the starting point for a submission: read the template, fill in the pool name, edit the
    values and submit it back through :func:`import_bulk_config`. Only param fields are included.
    """
    return dump_bulk_config_yaml(export_bulk_config([BulkSubmission(workflow=WorkflowTypes.get(name)())]))


def export_bulk_config_zip(submissions: list[BulkSubmission]) -> tuple[bytes, list[str]]:
    """Export the submissions as a ZIP of their bulk submission config and the input files it references.

    The ZIP holds bulk_config.yaml (see :func:`export_bulk_config`) with the input paths rewritten to
    inputs/<basename> (or inputs/<hash_subdir>/<basename> on basename collision), plus the actual
    files at those paths. Workflows are mutated in-place to reflect the rewritten paths.

    :return: (ZIP bytes, storage paths that could not be read and were left out).
        An input that could not be read keeps its original storage path in the config, so the export
        is still usable on this OVO server — report the paths so the user knows what is missing.
    """
    workflows = [submission.workflow for submission in submissions]
    # Collect files, assign zip paths: inputs/<basename>, with hash subdir on collision
    storage_paths = get_unique_storage_path_values(workflows)
    files: list[tuple[str, bytes]] = []  # (zip_path, file_bytes)
    used_basenames: set[str] = set()
    path_mapping: dict[str, str] = {}  # storage_path -> zip_path
    unreadable_paths: list[str] = []
    for path in storage_paths:
        try:
            file_bytes = storage.read_file_bytes(path)
        except Exception as e:
            print(f"Could not read input file, leaving it out of the bulk config export: {path} ({e})")
            unreadable_paths.append(path)
            continue
        basename = os.path.basename(path)
        if basename not in used_basenames:
            used_basenames.add(basename)
            zip_path = f"inputs/{basename}"
        else:
            zip_path = f"inputs/{get_hashed_path_for_bytes(file_bytes)}/{basename}"
        path_mapping[path] = zip_path
        files.append((zip_path, file_bytes))

    # Rewrite storage paths in workflows to match zip paths, then build YAML
    replace_storage_paths(workflows, path_mapping)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("bulk_config.yaml", dump_bulk_config_yaml(export_bulk_config(submissions)))
        for zip_path, file_bytes in files:
            zf.writestr(zip_path, file_bytes)
    zip_buffer.seek(0)
    return zip_buffer.read(), unreadable_paths


def get_bulk_config_filename(pool_ids: list[str]) -> str:
    """Return the ZIP filename for the bulk config of the given pools, e.g. ``ovo_abc_def_bulk_config.zip``."""
    return f"{get_pools_filename_prefix(pool_ids)}_bulk_config.zip"


def get_submissions_for_pools(pools: list[Pool], jobs_by_id: dict[str, DesignJob]) -> list[BulkSubmission]:
    """Return one BulkSubmission per pool, so previously submitted pools can be exported or resubmitted.

    Pools without a design job (e.g. uploaded design pools) and pools whose job runs a non-design
    workflow are skipped, see :func:`~ovo.core.logic.import_export_logic.can_export_bulk_config`.

    :param pools: Pools to convert, in the order they should appear in the config
    :param jobs_by_id: Design jobs of those pools, by job ID
    """
    submissions = []
    for pool in pools:
        job = jobs_by_id.get(pool.design_job_id)
        if job is None or not can_export_bulk_config(job.workflow):
            continue
        submissions.append(
            BulkSubmission(
                workflow=job.workflow,
                pool_name=pool.name,
                pool_description=pool.description,
            )
        )
    return submissions


def export_bulk_config_for_pools(pool_ids: list[str]) -> tuple[bytes, list[str]]:
    """Export the design workflows of the given pools as a bulk submission config ZIP.

    Pools that cannot be resubmitted are skipped (see :func:`get_submissions_for_pools`).
    Returns b"" when none of the pools has an exportable workflow.

    :return: (ZIP bytes, storage paths that could not be read and were left out),
        see :func:`export_bulk_config_zip`
    """
    pools = db.select(Pool, id__in=pool_ids)
    design_job_ids = [pool.design_job_id for pool in pools if pool.design_job_id]
    if not design_job_ids:
        return b"", []
    jobs = db.select(DesignJob, id__in=design_job_ids, order_by="-created_date_utc")
    jobs_by_id = {job.id: job for job in jobs}
    # Export in the order the jobs were submitted, newest first
    pools_by_job_id = {pool.design_job_id: pool for pool in pools}
    submissions = get_submissions_for_pools([pools_by_job_id[job.id] for job in jobs], jobs_by_id)
    if not submissions:
        return b"", []
    return export_bulk_config_zip(submissions)
