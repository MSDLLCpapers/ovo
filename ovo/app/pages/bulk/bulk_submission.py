import io
import itertools
import json
import os
import zipfile
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urljoin

import pandas as pd
import streamlit as st
import timeago

from ovo.app.components.navigation import (
    SUBMISSION_QUERY_PARAM,
    get_jobs_url,
    open_first_section,
    open_section,
    show_prev_next_sections,
)
from ovo.app.components.submission_components import (
    format_param_table,
    get_cached_param_values,
    get_pool_inputs,
    pool_submission_inputs,
)
from ovo.app.utils.cached_db import get_cached_round, get_cached_pools
from ovo.app.utils.page_init import initialize_page
from ovo.app.utils.testing import is_test_dialog_shown
from ovo.core.utils.bulk_submission_utils import (
    dump_bulk_config_yaml,
    get_storage_path_values,
    match_uploaded_file,
    parse_bulk_config_yaml,
    replace_storage_paths,
)
from ovo.app.components.workflow_summary import show_workflow_summary
from ovo.core.database.models import (
    BulkSubmissionDraftArtifact,
    DesignJob,
    DesignWorkflow,
    ProjectArtifact,
    UnknownArtifact,
    WorkflowTypes,
)
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
    prepare_input_files,
    resolve_input_paths,
    save_bulk_submission_draft,
    save_bulk_submission_note,
    save_bulk_submission_results,
)
from ovo.app.components.history_components import format_label
from ovo.app.utils.cached_db import (
    get_cached_bulk_submission_drafts,
    get_cached_project,
    get_cached_project_ids_and_names,
    get_cached_workflow_pools_and_jobs,
)
from ovo import config, db, schedulers


_YAML_EXTENSIONS = {".yaml", ".yml", ".json"}

_REVIEW_SECTION_INDEX = 2

# Presets of the config step that are not an uploaded file or a workflow type, see bulk_input_step
_CUSTOM = "Custom"
_PREVIOUSLY_SUBMITTED = "Previously submitted"
_SUBMISSION_DRAFTS = "Submission drafts"


@dataclass
class BulkSubmissionUIState:
    """Session state of this page, kept in ``st.session_state.workflows``."""

    preset: str = None
    preset_project_id: str | None = None
    preset_pool_ids: list[str] | None = None
    preset_draft_id: str | None = None  # draft selected in the "Submission drafts" preset
    bulk_text: str = ""
    uploaded_files: dict = field(default_factory=dict)  # filename -> bytes
    submissions: list[BulkSubmission] = field(default_factory=list)  # parsed from bulk_text
    parse_error: str | None = None
    storage_verified_paths: set = field(default_factory=set)  # paths confirmed to exist in storage
    reset_counter: int = 0  # incremented each time the state is reset, to force updating components
    # The draft this state was loaded from, if any - submitting records the jobs back on it
    saved_submission: ProjectArtifact | None = None
    loaded_submission_id: str | None = None  # ID of the draft already loaded into this state
    saved_link_url: str | None = None  # link to show after the Save link button was clicked


def _get_state() -> BulkSubmissionUIState:
    if __file__ not in st.session_state.workflows:
        st.session_state.workflows[__file__] = BulkSubmissionUIState()
    return st.session_state.workflows[__file__]


def load_saved_submission() -> None:
    """Replace the page state with the submission draft named by the ``submission`` query parameter.

    This is how an agent hands a prepared submission over to a user: the link restores the config,
    the input files (already in storage), the round and the prefixes, and opens the review step, so
    all that is left is to confirm it. See
    :func:`~ovo.core.logic.bulk_submission_logic.save_bulk_submission_draft`.

    A draft is loaded once per link: its ID is kept on the state, so the user can keep editing the
    loaded config without it being replaced on every rerun, while a different ID in the URL (or a
    draft picked in the config step) replaces the state again.
    """
    submission_id = st.query_params.get(SUBMISSION_QUERY_PARAM)
    if submission_id == _get_state().loaded_submission_id:
        return
    if not submission_id:
        # The draft was loaded earlier in this session and the query parameter has since been removed
        _get_state().loaded_submission_id = None
        return

    # Read from the DB and not from the cached draft list: submitting the draft saves this same row
    saved_submissions = db.select(
        ProjectArtifact, id=submission_id, artifact_type=BulkSubmissionDraftArtifact.artifact_type
    )
    if not saved_submissions:
        st.error(f"Submission draft not found: {submission_id}")
        st.stop()
    saved_submission = saved_submissions[0]
    if isinstance(saved_submission.artifact, UnknownArtifact):
        st.error(f"Cannot load submission draft {submission_id}: {saved_submission.artifact.error}")
        st.stop()

    switches_project = saved_submission.project_id != st.session_state.project.id
    if switches_project:
        accessible_project_ids = get_cached_project_ids_and_names(username=get_username())
        if (
            saved_submission.project_id not in accessible_project_ids
            and not config.auth.allow_private_project_link_access
        ):
            st.error(f"Submission draft {submission_id} belongs to a project you cannot access.")
            st.stop()
        st.session_state.project = get_cached_project(id=saved_submission.project_id)

    set_state_from_saved_submission(saved_submission)

    if switches_project:
        # The sidebar of this run still shows the previous project, rerun to draw it for the new one
        st.rerun()


def detach_foreign_draft() -> None:
    """Detach the attached submission draft once the active project is not the one it belongs to.

    Submitting records the jobs it created back on the attached draft (see
    :func:`~ovo.core.logic.bulk_submission_logic.save_bulk_submission_results`), which only makes
    sense while the submission goes to the project of that draft - the pools and jobs are created in
    the project selected now. The config stays, so it can still be submitted here, just not as the
    draft it was opened from, which is left unsubmitted in its own project.
    """
    state = _get_state()
    if not state.saved_submission or state.saved_submission.project_id == st.session_state.project.id:
        return

    state.saved_submission = None
    # Dropped as well, so that opening the link of the draft again loads and attaches it anew
    state.loaded_submission_id = None
    state.saved_link_url = None
    st.query_params.pop(SUBMISSION_QUERY_PARAM, None)
    st.info(
        f"Switched project, so this is no longer submitted as the draft it was opened from. "
        f"Submitting it creates a new submission in {st.session_state.project.name}."
    )


def set_state_from_saved_submission(saved_submission: ProjectArtifact) -> None:
    """Replace the page state with the config, round and prefixes of a submission draft.

    Opens the review step, as the point of a draft is to be reviewed and confirmed rather than
    edited - the user can still go back to the config step and change it, which leaves the draft
    attached, so submitting the edited config still records the jobs on it.
    """
    artifact: BulkSubmissionDraftArtifact = saved_submission.artifact
    st.session_state.workflows[__file__] = BulkSubmissionUIState(
        bulk_text=dump_bulk_config_yaml(artifact.config),
        # Parsed here rather than by the config step, which is skipped when opening a draft
        submissions=import_bulk_config(artifact.config),
        # Selects this draft in the config step, so going back to it does not load another preset
        # over the config that was just loaded
        preset=_SUBMISSION_DRAFTS,
        preset_project_id=saved_submission.project_id,
        preset_draft_id=saved_submission.id,
        saved_submission=saved_submission,
        loaded_submission_id=saved_submission.id,
    )
    st.session_state.pool_inputs[__file__] = (
        artifact.round_id,
        artifact.pool_name_prefix,
        artifact.pool_description_prefix,
    )
    if artifact.scheduler_key in schedulers:
        st.session_state["bulk_scheduler"] = artifact.scheduler_key
    open_section(__file__, _REVIEW_SECTION_INDEX)


def format_submission_url(saved_submission: ProjectArtifact) -> str:
    """Return the link that opens a submission draft on this page, absolute if the host is known.

    The draft ID is the whole link: the project is resolved from the draft itself, see
    :func:`~ovo.app.components.project_components.get_submission_query_arg_project_id`.
    """
    query = f"?{SUBMISSION_QUERY_PARAM}={saved_submission.id}"
    page_url = st.context.url.split("?")[0] if st.context.url else None
    return f"{urljoin(page_url, 'bulk_submission')}{query}" if page_url else f"./bulk_submission{query}"


def format_draft_label(saved_submission: ProjectArtifact) -> str:
    """Return the dropdown label of a submission draft, naming the pools it would submit."""
    artifact: BulkSubmissionDraftArtifact = saved_submission.artifact
    if isinstance(artifact, UnknownArtifact):
        return f"{saved_submission.id} | cannot be loaded: {artifact.error}"
    pool_names = [submission.get("pool_name") for submission in artifact.config.get("submissions", [])]
    named = [name for name in pool_names if name]
    summary = ", ".join(named[:3]) + (", ..." if len(named) > 3 else "") if named else "unnamed"
    label = f"{summary} | {len(pool_names)} submission(s) | {format_draft_created(saved_submission)}"
    return f"{label} | submitted by {artifact.submitted_by}" if artifact.is_submitted() else label


def format_draft_created(saved_submission: ProjectArtifact) -> str:
    """Return when a submission draft was created and by whom, e.g. "Created 2 hours ago by jane"."""
    delta = datetime.now(timezone.utc).replace(tzinfo=None) - saved_submission.created_date_utc.replace(tzinfo=None)
    return f"created {timeago.format(delta)} by {saved_submission.author}"


def _clear_parsed_workflows(state: BulkSubmissionUIState, parse_error: str = None) -> None:
    """Drop the submissions parsed from a previous config version, so they cannot be submitted."""
    state.submissions = []
    state.parse_error = parse_error


@st.cache_data(max_entries=1000, show_spinner=False)
def get_cached_job_for_summary(workflow: DesignWorkflow, path_mapping: dict, index: int) -> DesignJob:
    """Return an unsaved DesignJob, to show the summary of a workflow before it is submitted.

    The job is never saved - it only carries the workflow, which is all the summary needs. The pool it
    would create does not exist yet, so the summary leaves out everything pool-specific, see
    :func:`~ovo.app.components.workflow_summary.get_subjob_table`. Its ID is positional rather than
    random, so the summary keeps the same widget keys across reruns.

    The paths of the input files, which the summary reads from storage, are rewritten on a copy of the
    workflow - the submission itself keeps the paths the user wrote, as shown in the review table and
    saved in a draft. Cached, so the copying happens once per config version rather than on every
    keystroke in the pool name prefix, which reruns the review step.

    :param path_mapping: Where the workflow's input files are stored, from
        :func:`~ovo.core.logic.bulk_submission_logic.prepare_input_files` - which stores them and is
        deliberately not cached
    """
    workflow = deepcopy(workflow)
    replace_storage_paths([workflow], path_mapping)
    return DesignJob(id=f"summary-{index}", workflow=workflow)


def _show_saved_submission(artifact: BulkSubmissionDraftArtifact) -> bool:
    """Show the draft being reviewed and return whether it can still be submitted."""
    if artifact.note:
        st.info(artifact.note)

    if not artifact.is_submitted():
        return True

    st.warning(
        f":material/check: This draft was already submitted by {artifact.submitted_by} "
        f"as {len(artifact.design_job_ids)} job(s)."
    )
    for error in artifact.submission_errors:
        st.error(error)

    # The draft only records the jobs it submitted, the pools they created are looked up from those
    pool_ids = [pool.id for pool in get_cached_pools(design_job_id__in=artifact.design_job_ids)]
    if pool_ids:
        st.link_button(
            ":material/open_in_new: Show the submitted jobs",
            get_jobs_url(st.session_state.project.id, ",".join(pool_ids)),
        )
    return st.checkbox("Submit this draft again anyway", key="bulk_resubmit")


def _select_preset_project(state: BulkSubmissionUIState, key: str) -> str:
    """Show the project selector of a preset that loads its config from the database.

    Shared by the presets that do, so they offer the same projects and remember the same selection
    when the user switches between them.
    """
    project_ids_and_names = get_cached_project_ids_and_names(username=get_username())
    current_project_id = state.preset_project_id
    if not current_project_id and st.session_state.project:
        current_project_id = st.session_state.project.id

    project_ids = list(project_ids_and_names.keys())
    return st.selectbox(
        "Project",
        options=project_ids,
        index=project_ids.index(current_project_id) if current_project_id in project_ids else 0,
        format_func=lambda pid: project_ids_and_names[pid],
        key=key,
        width=400,
    )


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
                # include zip file itself
                state.uploaded_files[f.name] = file_bytes
                try:
                    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                        for member in zf.infolist():
                            # Skip directories and the metadata files added by the macOS archiver
                            if member.is_dir() or member.filename.startswith("__MACOSX/"):
                                continue
                            if os.path.basename(member.filename).startswith("."):
                                continue
                            state.uploaded_files[member.filename] = zf.read(member)
                except zipfile.BadZipFile as e:
                    st.warning("Uploaded ZIP file could not be read: " + str(e))
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

    # Preset options: uploaded config files first, then workflow defaults
    preset_options = (
        list(uploaded_config_files.keys()) + [_CUSTOM, _PREVIOUSLY_SUBMITTED, _SUBMISSION_DRAFTS] + workflow_names
    )
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
        elif state.preset in (_PREVIOUSLY_SUBMITTED, _SUBMISSION_DRAFTS):
            state.bulk_text = ""
        elif state.preset in uploaded_config_files:
            state.bulk_text = uploaded_config_files[state.preset]
        else:
            # Only the selected workflow type's template is generated, not every type's
            state.bulk_text = get_bulk_config_template(state.preset)

    if state.preset == _SUBMISSION_DRAFTS:
        with st.container(horizontal=True):
            drafts_by_id = {draft.id: draft for draft in get_cached_bulk_submission_drafts(st.session_state.project.id)}
            draft_ids = list(drafts_by_id)
            selected_draft_id = st.selectbox(
                "Submission draft",
                options=draft_ids,
                index=draft_ids.index(state.preset_draft_id) if state.preset_draft_id in draft_ids else None,
                format_func=lambda draft_id: format_draft_label(drafts_by_id[draft_id]),
                key="bulk_draft_select",
                placeholder=f"{len(draft_ids)} draft(s) available" if draft_ids else "No drafts saved in this project",
            )
            if selected_draft_id and selected_draft_id != state.preset_draft_id:
                # Read with db.get and not from the cached list: submitting it saves this same row
                set_state_from_saved_submission(db.get(ProjectArtifact, id=selected_draft_id))
                st.query_params[SUBMISSION_QUERY_PARAM] = selected_draft_id
                st.rerun(scope="app")

    if state.preset == _PREVIOUSLY_SUBMITTED:
        with st.container(horizontal=True):
            state.preset_project_id = _select_preset_project(state, key="bulk_prev_project_select")
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
                    select_all=False,
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
            key=f"bulk_text_input_{state.preset}_{get_hash_of_bytes(str((state.preset_pool_ids, state.preset_draft_id)).encode())}_{state.reset_counter}",
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

    if state.saved_submission and not _show_saved_submission(state.saved_submission.artifact):
        return

    workflows = [submission.workflow for submission in state.submissions]
    num_workflows = len(workflows)

    st.markdown(f"## {num_workflows} workflow{'' if num_workflows == 1 else 's'} to submit")

    if state.saved_submission and not state.saved_submission.artifact.is_submitted():
        st.caption(f":material/link: Draft {format_draft_created(state.saved_submission)}")

    try:
        # Not cached, but cheap to repeat: the files that are already stored are not stored again
        path_mapping = prepare_input_files(
            workflows, project_id=st.session_state.project.id, uploaded_files=state.uploaded_files
        )
        show_workflow_summary(
            [
                get_cached_job_for_summary(submission.workflow, path_mapping, i)
                for i, submission in enumerate(state.submissions)
            ]
        )
    except Exception as e:
        st.warning(f"Error generating workflow summary: {e}")

    st.markdown("### Submission settings")

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

    columns = [
        format_param_table(
            project_name=st.session_state.project.name,
            round_name=project_round.name,
            pool_name=pool_names[i],
            pool_description=submission.get_pool_description(pool_description_prefix),
            # The combo values are not in the header, they show up among the differing parameters
            values=get_cached_param_values(submission.workflow, name="Pool" if num_workflows == 1 else f"Pool {i + 1}"),
        )
        for i, submission in enumerate(state.submissions)
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
        submit_label = "Submit 1 workflow"
    else:
        st.write(f"Will submit {num_workflows} workflows with scheduler **{schedulers[scheduler_key].name}**")
        with st.expander("Show time estimates for each workflow"):
            for pool_name, workflow in zip(pool_names, workflows):
                st.write(f"{pool_name}: {workflow.get_time_estimate(schedulers[scheduler_key])}")
        submit_label = f"Submit {num_workflows} workflows"

    with st.container(horizontal=True):
        submit = st.button(submit_label, type="primary", key="bulk_submit_all")
        save_link = st.button(
            ":material/link: Save link",
            key="bulk_save_link",
            help="Save this submission as a draft and get a link to review and submit it later",
        )

    if save_link:
        # A new draft is saved on every opening of the dialog, drop the previous one and its note
        state.saved_link_url = None
        st.session_state.pop("save_link_note", None)

    if save_link or is_test_dialog_shown("save_link"):
        save_link_dialog(
            state=state,
            round_id=round_id,
            pool_name_prefix=pool_name_prefix,
            pool_description_prefix=pool_description_prefix,
            scheduler_key=scheduler_key,
        )

    if submit:
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

        if state.saved_submission:
            # Not atomic with the submission above, see save_bulk_submission_results. The submissions
            # are passed as submitted - their input paths were resolved above - so that a draft whose
            # config was edited here records what was submitted rather than what it was saved with
            save_bulk_submission_results(
                state.saved_submission,
                results,
                submissions=state.submissions,
                round_id=round_id,
                pool_name_prefix=pool_name_prefix,
                pool_description_prefix=pool_description_prefix,
                scheduler_key=scheduler_key,
            )

        errors = [f"Pool '{result.pool_name}': {result.error}" for result in results if not result.success]
        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.flash_success = f"Submitted {len(state.submissions)} job(s) successfully"
            open_first_section(__file__)
            st.session_state.workflows.pop(__file__, None)
            st.session_state.pool_inputs.pop(__file__, None)
            st.switch_page("app/pages/jobs/jobs.py")


@st.dialog("Save a link to this submission", width="medium")
def save_link_dialog(
    state: BulkSubmissionUIState,
    round_id: str,
    pool_name_prefix: str,
    pool_description_prefix: str,
    scheduler_key: str,
) -> None:
    """Save the reviewed submission as a draft and show the link that opens it again.

    The draft is saved as soon as this dialog opens, so that its link can be copied right away -
    typing a note updates the draft that is already saved.

    The draft keeps the config, the input files, the round and the prefixes as they are now - editing
    the config afterwards does not change the draft, but submitting it does (see
    :func:`~ovo.core.logic.bulk_submission_logic.save_bulk_submission_results`).
    """
    if not state.saved_link_url:
        saved_submission = save_bulk_submission_draft(
            # The config text as written, so that the draft keeps its grids
            config_dict=parse_bulk_config_yaml(state.bulk_text),
            project_id=st.session_state.project.id,
            round_id=round_id,
            pool_name_prefix=pool_name_prefix,
            pool_description_prefix=pool_description_prefix,
            scheduler_key=scheduler_key,
            uploaded_files=state.uploaded_files,
        )
        # Attached to this page state, so submitting here records the jobs on the draft as its link would
        state.saved_submission = saved_submission
        state.preset_draft_id = saved_submission.id
        state.saved_link_url = format_submission_url(saved_submission)

    st.write("Anyone with the link can open this submission, review it and submit it. ")
    note = st.text_area(
        "Note (optional)",
        key="save_link_note",
        placeholder="Shown to whoever opens the link, e.g. why this submission is proposed",
        height=80,
    )
    if (note or None) != state.saved_submission.artifact.note:
        save_bulk_submission_note(state.saved_submission, note=note)

    st.html(
        """
        <style>
        div[data-testid="stCode"] > div {
          opacity: 1 !important;
          visibility: visible;
        }
        </style>
        """
    )

    with st.container(horizontal=True, horizontal_alignment="right"):
        st.markdown("Saved, click below to copy :material/south: &nbsp;&nbsp;&nbsp;&nbsp;", width="content")
    st.code(state.saved_link_url, language=None)


if __name__ == "__main__":
    initialize_page(page_title="Bulk submission")
    load_saved_submission()
    detach_foreign_draft()
    show_prev_next_sections(
        key=__file__,
        title="📦 Bulk submission",
        sections={
            "files": file_upload_step,
            "config": bulk_input_step,
            "review & submit": review_and_submit_step,
        },
    )
