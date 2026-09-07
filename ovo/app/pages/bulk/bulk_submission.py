import io
import itertools
import json
import os
import zipfile
from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.submission_components import (
    format_param_table,
    format_param_values,
    get_pool_inputs,
    pool_submission_inputs,
)
from ovo.app.utils.cached_db import get_cached_round, get_cached_pools
from ovo.app.utils.page_init import initialize_page
from ovo.core.utils.bulk_submission_utils import (
    dump_bulk_config_yaml,
    get_storage_path_values,
    match_uploaded_file,
    parse_bulk_config_yaml,
)
from ovo.core.database.models import WorkflowTypes
from ovo.core.utils.formatting import get_hash_of_bytes
from ovo.core.auth import get_username
from ovo.core.logic.bulk_submission_logic import (
    BulkSubmission,
    bulk_submit,
    export_bulk_config,
    find_list_on_scalar_fields,
    get_submissions_for_pools,
    get_unresolved_input_paths,
    get_bulk_config_template,
    import_bulk_config,
    resolve_input_paths,
)
from ovo.app.components.history_components import format_label
from ovo.app.utils.cached_db import get_cached_project_ids_and_names, get_cached_workflow_pools_and_jobs
from ovo import schedulers


_YAML_EXTENSIONS = {".yaml", ".yml", ".json"}


@dataclass
class BulkSubmissionUIState:
    """Session state of this page, kept in ``st.session_state.workflows``."""

    preset: str = None
    preset_project_id: str | None = None
    preset_pool_ids: list[str] | None = None
    bulk_text: str = ""
    uploaded_files: dict = field(default_factory=dict)  # filename -> bytes
    submissions: list[BulkSubmission] = field(default_factory=list)  # parsed from bulk_text
    cached_param_columns: list = field(default_factory=list)  # see _get_cached_param_columns
    parse_error: str | None = None
    storage_verified_paths: set = field(default_factory=set)  # paths confirmed to exist in storage
    reset_counter: int = 0  # incremented each time the state is reset, to force updating components


def _get_state() -> BulkSubmissionUIState:
    if __file__ not in st.session_state.workflows:
        st.session_state.workflows[__file__] = BulkSubmissionUIState()
    return st.session_state.workflows[__file__]


def _clear_parsed_workflows(state: BulkSubmissionUIState, parse_error: str = None) -> None:
    """Drop the submissions parsed from a previous config version, so they cannot be submitted."""
    state.submissions = []
    state.cached_param_columns = []
    state.parse_error = parse_error


def _get_cached_param_columns(state: BulkSubmissionUIState) -> list[pd.Series]:
    """Return the formatted review table column of each submission's workflow, one per submission.

    Formatted once per parsed config and kept on the state: the review step is a fragment that reruns
    on every keystroke in the pool name prefix, where formatting a large grid again would take
    hundreds of milliseconds. The pool name and description are not included here, as those do change
    on every rerun.
    """
    if not state.cached_param_columns:
        num_workflows = len(state.submissions)
        state.cached_param_columns = [
            format_param_values(
                # The combo values are not in the header, they show up among the differing parameters
                submission.workflow.get_table_row(name="Pool" if num_workflows == 1 else f"Pool {i + 1}")
            )
            for i, submission in enumerate(state.submissions)
        ]
    return state.cached_param_columns


def _get_uploaded_config_files(uploaded_files: dict) -> dict[str, str]:
    """Return {filename: text} for uploaded YAML/JSON files that can be decoded."""
    result = {}
    for name, file_bytes in uploaded_files.items():
        if os.path.splitext(name)[1].lower() in _YAML_EXTENSIONS:
            try:
                result[name] = file_bytes.decode("utf-8")
            except Exception:
                pass
    return result


def _get_uploaded_data_files(uploaded_files: dict) -> list[str]:
    """Return keys of uploaded files that are NOT YAML/JSON (i.e. PDB, etc.).

    Keys of directory and ZIP uploads keep their directory prefix, e.g. "inputs/target.pdb".
    """
    return sorted(name for name in uploaded_files if os.path.splitext(name)[1].lower() not in _YAML_EXTENSIONS)


@st.fragment
def file_upload_step():
    state = _get_state()

    with st.container(width=850):
        st.markdown("""
Upload files needed for your bulk submission (if any), such as: 

- Input structures (PDB, CIF)
- Parameter files (YAML)
- Bulk submission ZIP files (can be downloaded on Jobs page)
""")

        uploaded_single = st.file_uploader(
            "Upload files (PDB, CIF, YAML, ZIP, ...)",
            accept_multiple_files=True,
            key="bulk_upload_single",
            width=500,
        )

        st.write("Or upload an entire directory:")
        uploaded_dir = st.file_uploader(
            "Upload directory",
            accept_multiple_files="directory",
            key="bulk_upload_dir",
            width=400,
        )

        # Accumulated across reruns on purpose, so the user can come back to this step and add more
        # files to what a previous upload (or an extracted ZIP) already provided
        for f in (uploaded_single or []) + (uploaded_dir or []):
            file_bytes = f.getvalue()
            if os.path.splitext(f.name)[1].lower() == ".zip":
                try:
                    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                        for member in zf.infolist():
                            # Skip directories and the metadata files added by the macOS archiver
                            if member.is_dir() or member.filename.startswith("__MACOSX/"):
                                continue
                            if os.path.basename(member.filename).startswith("."):
                                continue
                            state.uploaded_files[member.filename] = zf.read(member)
                except zipfile.BadZipFile:
                    state.uploaded_files[f.name] = file_bytes
            else:
                state.uploaded_files[f.name] = file_bytes

        if state.uploaded_files:
            config_files = _get_uploaded_config_files(state.uploaded_files)
            data_files = _get_uploaded_data_files(state.uploaded_files)
            summary_parts = []
            if config_files:
                summary_parts.append(
                    f"{len(config_files)} config file(s): {', '.join(f'`{n}`' for n in sorted(config_files))}"
                )
            if data_files:
                summary_parts.append(f"{len(data_files)} data file(s): {', '.join(f'`{n}`' for n in data_files)}")
            st.success("Uploaded: " + " · ".join(summary_parts))


@st.fragment
def bulk_input_step():
    state = _get_state()

    uploaded_config_files = _get_uploaded_config_files(state.uploaded_files)
    data_files = _get_uploaded_data_files(state.uploaded_files)
    workflow_names = list(WorkflowTypes.get_design_workflow_types())

    _CUSTOM = "Custom"
    _PREVIOUSLY_SUBMITTED = "Previously submitted"

    # Preset options: uploaded config files first, then workflow defaults
    preset_options = list(uploaded_config_files.keys()) + [_CUSTOM, _PREVIOUSLY_SUBMITTED] + workflow_names
    prev_state_preset = state.preset

    with st.container(horizontal=True, vertical_alignment="bottom"):
        state.preset = st.selectbox(
            "Load preset",
            options=preset_options,
            index=preset_options.index(state.preset) if state.preset in preset_options else 0,
            key="bulk_preset_select",
        )

        _RESET = ":material/refresh: Reset"
        reset = st.menu_button("Options", options=[_RESET], key="bulk_options") == _RESET
        if reset:
            state.reset_counter += 1

    if reset or prev_state_preset != state.preset:
        if state.preset == _CUSTOM:
            state.bulk_text = ""
        elif state.preset == _PREVIOUSLY_SUBMITTED:
            state.bulk_text = ""
        elif state.preset in uploaded_config_files:
            state.bulk_text = uploaded_config_files[state.preset]
        else:
            # Only the selected workflow type's template is generated, not every type's
            state.bulk_text = get_bulk_config_template(state.preset)

    if state.preset == _PREVIOUSLY_SUBMITTED:
        project_ids_and_names = get_cached_project_ids_and_names(username=get_username())
        current_project_id = state.preset_project_id
        if not current_project_id and st.session_state.project:
            current_project_id = st.session_state.project.id

        project_ids = list(project_ids_and_names.keys())
        with st.container(horizontal=True):
            state.preset_project_id = st.selectbox(
                "Project",
                options=project_ids,
                index=project_ids.index(current_project_id) if current_project_id in project_ids else 0,
                format_func=lambda pid: project_ids_and_names[pid],
                key="bulk_prev_project_select",
                width=400,
            )
            if state.preset_project_id:
                # Only pools of a submittable design workflow can be turned back into a config
                pools_by_id, jobs_by_id = get_cached_workflow_pools_and_jobs(state.preset_project_id, workflow_names)
                pool_ids_by_date = [
                    p.id for p in sorted(pools_by_id.values(), key=lambda p: p.created_date_utc, reverse=True)
                ]
                prev_selected_pool_ids = state.preset_pool_ids
                new_preset_pool_ids = st.multiselect(
                    "Previously submitted workflows",
                    options=pool_ids_by_date,
                    default=prev_selected_pool_ids
                    if all(pool_id in pools_by_id for pool_id in (prev_selected_pool_ids or []))
                    else None,
                    format_func=lambda pid: format_label(pid, pools_by_id),
                    key="bulk_prev_pools_select",
                    placeholder=f"{len(pool_ids_by_date)} runs available"
                    if pool_ids_by_date
                    else "No runs in this project",
                )
                if reset or prev_state_preset != state.preset or prev_selected_pool_ids != new_preset_pool_ids:
                    # Export the selected pools as a config, keeping their pool names and descriptions
                    submissions_from_history = get_submissions_for_pools(
                        [pools_by_id[pid] for pid in new_preset_pool_ids], jobs_by_id
                    )
                    state.preset_pool_ids = new_preset_pool_ids
                    state.bulk_text = (
                        dump_bulk_config_yaml(export_bulk_config(submissions_from_history))
                        if submissions_from_history
                        else ""
                    )

    left, right = st.columns([1.5, 1])

    with left:
        st.markdown(
            """
        <style>
        textarea {
            font-family: monospace !important;
            font-size: 10pt !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
        bulk_text = st.text_area(
            "Bulk config (YAML or JSON)",
            value=state.bulk_text,
            height=480,
            key=f"bulk_text_input_{state.preset}_{get_hash_of_bytes(str(state.preset_pool_ids).encode())}_{state.reset_counter}",
            placeholder=(
                "submissions:\n"
                "  - pool_name: RFD motif 1 run 1\n"
                '    pool_description: ""\n'
                "    workflow:\n"
                '      name: "RFdiffusion scaffold design"\n'
                "      rfdiffusion_params:\n"
                "        input_pdb_paths: [target.pdb]\n"
                "        contigs: [A1-100/10/A200-300]\n"
                "        timesteps:\n"
                "          grid: [20, 50]\n"
                "        num_designs: 10"
            ),
        )
        state.bulk_text = bulk_text

        with st.expander("Format reference", expanded=True):
            st.markdown("""
**Top-level structure:**
```yaml
submissions:
  - pool_name: "<pool to create>"
    pool_description: "<optional>"
    workflow:
      name: "<registered workflow name>"
      <param_field_name>:
        <param_key>: <value>
        <param_key>:
          grid: [v1, v2, v3]   # expands this submission into 3 runs
  - pool_name: "<second pool>"
    pool_description: "<optional>"
    workflow:
      ...
```

**Grid expansion:** any scalar value can be replaced with `{grid: [...]}`.
Multiple grid fields produce a Cartesian product (e.g. 2 × 3 = 6 runs).
Each run gets its own pool, named `<pool_name> Combo N`.

**Pool names and descriptions** are optional here — the prefixes entered in the next step are
prepended to them, and name and describe the pools of the submissions that do not set them.

**File paths:** specify filenames matching what you uploaded (e.g. `target.pdb`).

**Partial configs:** omitted param fields fall back to workflow defaults.

**Multiple workflows** can be submitted by repeating the whole `- pool_name: ...` block.
Repeating just `workflow:` within one block is an error, as YAML would keep only the last one.

Bulk submission config for previously executed jobs can be exported on the Jobs page.
""")

    with right:
        st.write("&nbsp;")
        # Live parse + file match preview
        if not bulk_text or not bulk_text.strip():
            _clear_parsed_workflows(state)
            return
        try:
            config_dict = parse_bulk_config_yaml(bulk_text)
            if not isinstance(config_dict, dict):
                raise ValueError("Config must be a YAML/JSON object with a 'submissions' key")
            list_warnings = find_list_on_scalar_fields(config_dict)
            for w in list_warnings:
                st.warning(w)
            submissions = import_bulk_config(config_dict)
        except Exception as e:
            # Nothing can be submitted until the config parses again, drop the previously parsed workflows
            _clear_parsed_workflows(state, parse_error=str(e))
            st.error("Error in the configuration:")
            st.code(str(e))
            # Print available files also when user is typing and syntax is not valid yet
            st.caption("Available files:")
            for name in data_files:
                st.code(json.dumps(name), language=None, wrap_lines=True)
            return

        state.parse_error = None
        state.submissions = submissions
        state.cached_param_columns = []  # formatted lazily by the review step, from these submissions

        workflows = [submission.workflow for submission in submissions]
        num_workflows = len(workflows)
        st.write(":material/check: Parsed successfully")
        if num_workflows == 1:
            status = ":material/check: Workflow is ready to submit"
        else:
            status = f":material/check: Grid of {num_workflows} workflows ready to submit"
        for workflow in workflows:
            try:
                workflow.validate()
            except Exception as e:
                status = f":orange-background[:material/warning: {e}]"
                break
        st.write(status)

        storage_paths_by_field = get_storage_path_values(workflows)
        unresolved_by_field = get_unresolved_input_paths(
            workflows, uploaded_files=state.uploaded_files, verified_paths=state.storage_verified_paths
        )
        if any(storage_paths_by_field.values()):
            st.write("Referenced paths:")
            unresolved = []
            for field, paths in storage_paths_by_field.items():
                for path in paths:
                    if path in unresolved_by_field.get(field, []):
                        unresolved.append(f'{field}: "{path}"')
                    elif match_uploaded_file(path, state.uploaded_files):
                        st.markdown(f":material/check: {os.path.basename(path)}")
                    else:
                        st.markdown(f":material/check: {os.path.basename(path)} *(in storage)*")
            if unresolved:
                st.error(
                    f"Missing files: {', '.join(unresolved)}. Please fix the path or upload the file in the previous step."
                )

        all_storage_paths = set(path for paths in storage_paths_by_field.values() for path in paths)
        unused_paths = [path for path in data_files if path not in all_storage_paths]
        if unused_paths:
            st.caption("Available files:")
            for name in unused_paths:
                st.code(json.dumps(name), language=None, wrap_lines=True)


@st.fragment
def review_and_submit_step():
    state = _get_state()

    if not state.submissions:
        if state.parse_error:
            st.warning(f"Nothing to submit, the config could not be parsed: {state.parse_error}")
        else:
            st.warning("No workflows to submit. Please enter the submission config in the previous step.")
        return

    num_workflows = len(state.submissions)

    pool_submission_inputs(__file__, inputs_are_prefixes=True)
    round_id, pool_name_prefix, pool_description_prefix = get_pool_inputs(__file__)
    project_round = get_cached_round(round_id)

    if num_workflows > 1 and get_cached_pools(round_id=round_id):
        st.warning(
            f":material/info: Note: {project_round.name} already contains some pools. "
            f"Group your new pools together by clicking 'Create new Round' above."
        )

    # The prefix above is prepended to the pool names from the config, and names the pools that it did not
    try:
        pool_names = BulkSubmission.get_pool_names(state.submissions, pool_name_prefix)
    except ValueError as e:
        # Only a missing name can be fixed by the prefix input, a duplicate one needs editing the config
        missing_name = any(not s.get_pool_name(pool_name_prefix) for s in state.submissions)
        hint = "\n\nPlease provide a pool name prefix above, or a 'pool_name' per submission in the config."
        st.error(f"{e}{hint if missing_name else ''}")
        return

    # Checked here rather than in pool_submission_inputs, which only sees the prefix, not the final names
    if taken := sorted({pool.name for pool in get_cached_pools(round_id=round_id)}.intersection(pool_names)):
        st.error(
            f"Pool name(s) already used in {project_round.name}: {', '.join(taken)}\n\n"
            f"Please change the pool name prefix above, or click 'Create new Round' to submit into a new one."
        )
        return

    st.markdown(f"#### {num_workflows} workflow{'' if num_workflows == 1 else 's'} to submit")

    columns = [
        format_param_table(
            project_name=st.session_state.project.name,
            round_name=project_round.name,
            pool_name=pool_names[i],
            pool_description=submission.get_pool_description(pool_description_prefix),
            values=values,
            format_values=False,  # formatted once per parsed config, see _get_cached_param_columns
        )
        for i, (submission, values) in enumerate(zip(state.submissions, _get_cached_param_columns(state)))
    ]

    column_limit = 100
    table = pd.concat(columns, axis=1)

    if num_workflows <= 2:
        st.table(table, width="content")
    else:
        # With more workflows the table gets too wide to read, so the parameters that are the same
        # for all of them are listed once, leaving only the differing ones side by side
        is_shared = table.apply(lambda row: row.nunique(dropna=False) <= 1, axis=1)
        st.write("Shared parameters")
        st.table(table[is_shared].iloc[:, :1].set_axis(["All workflows"], axis=1), width="content")

        differing = table[~is_shared]
        if not differing.empty:
            if num_workflows > column_limit:
                st.write(f"Differing parameters (first {column_limit}/{num_workflows} workflows)")
            else:
                st.write("Differing parameters")
            st.table(differing.iloc[:, :column_limit], width="content")
    # Check that every referenced input file can be resolved before offering to submit
    workflows = [submission.workflow for submission in state.submissions]
    unresolved = sorted(
        {
            path
            for paths in get_unresolved_input_paths(
                workflows,
                uploaded_files=state.uploaded_files,
                verified_paths=state.storage_verified_paths,
            ).values()
            for path in paths
        }
    )
    if unresolved:
        st.error(f"Cannot submit: missing files: {', '.join(unresolved)}.")
        return

    with st.columns(2)[0]:
        scheduler_key = st.selectbox(
            "Scheduler",
            options=list(schedulers.keys()),
            format_func=lambda k: schedulers[k].name,
            key="bulk_scheduler",
        )

    if num_workflows == 1:
        st.write(workflows[0].get_time_estimate(schedulers[scheduler_key]))
        submit_label = "Submit"
    else:
        st.write(f"Will submit {num_workflows} workflows with scheduler **{schedulers[scheduler_key].name}**")
        with st.expander("Show time estimates for each workflow"):
            for pool_name, workflow in zip(pool_names, workflows):
                st.write(f"{pool_name}: {workflow.get_time_estimate(schedulers[scheduler_key])}")
        submit_label = f"Submit {num_workflows} workflows"

    if st.button(submit_label, type="primary", key="bulk_submit_all"):
        try:
            resolve_input_paths(
                workflows,
                project_id=st.session_state.project.id,
                uploaded_files=state.uploaded_files,
            )
        except FileNotFoundError as e:
            # The check above already reported missing files, so this means one disappeared since
            st.error(str(e))
            return

        progress = st.progress(0, text="Submitting...")
        # bulk_submit reports one result per submission, in order, so counting them tracks the progress
        num_submitted = itertools.count(1)

        def report(result) -> None:
            submitted = next(num_submitted)
            progress.progress(submitted / num_workflows, text=f"Submitted {submitted}/{num_workflows}")

        try:
            results = bulk_submit(
                submissions=state.submissions,
                scheduler_key=scheduler_key,
                round_id=round_id,
                pool_name_prefix=pool_name_prefix,
                pool_description_prefix=pool_description_prefix,
                return_existing=False,
                callback=report,
            )
        except ValueError as e:
            # Raised by the up-front validation of the whole batch, so nothing has been submitted -
            # e.g. a pool of that name was created in the round since the check above read them
            st.error(f"Cannot submit: {e}")
            return

        errors = [f"Pool '{result.pool_name}': {result.error}" for result in results if not result.success]
        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.flash_success = f"Submitted {len(state.submissions)} job(s) successfully"
            st.session_state.workflows.pop(__file__, None)
            st.session_state.pool_inputs.pop(__file__, None)
            st.switch_page("app/pages/jobs/jobs.py")


if __name__ == "__main__":
    initialize_page(page_title="Bulk submission")
    show_prev_next_sections(
        key=__file__,
        title="📦 Bulk submission",
        sections={
            "files": file_upload_step,
            "config": bulk_input_step,
            "review & submit": review_and_submit_step,
        },
    )
