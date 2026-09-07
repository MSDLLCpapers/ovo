import os

import streamlit as st

from ovo import Design, Pool
from ovo.app.components.custom_elements import confirm_download_button
from ovo.app.utils.cached_db import (
    get_cached_design_jobs,
    get_cached_available_descriptors,
    get_cached_descriptor_values,
)
from ovo.core.database import Base
from ovo.core.logic.bulk_submission_logic import export_bulk_config_for_pools, get_bulk_config_filename
from ovo.core.logic.descriptor_logic import export_design_descriptors_excel
from ovo.core.logic.design_logic import collect_storage_paths_by_group, get_descriptor_job_id_for_key
from ovo.core.logic.import_export_logic import (
    BULK_CONFIG_DOWNLOAD_LABEL,
    get_download_filename_prefix,
    merge_job_descriptors,
    resolve_download_fields,
)
from ovo.core.utils.formatting import get_hash_of_bytes
from ovo import storage


@st.fragment
def download_bulk_config_button(pool_ids: list[str], key: str):
    """Download button that serializes the workflows of the given pools to a bulk config ZIP."""
    # What the export reported, kept in the session state so the rerun after the download can show it,
    # as the ZIP is only built inside the download button callback
    export_report_key = f"{key}_export_report"

    def build_zip() -> bytes:
        # Only called when the button is clicked, the ZIP is not built on every rerun
        zip_bytes, unreadable_paths = export_bulk_config_for_pools(pool_ids)
        st.session_state[export_report_key] = (not zip_bytes, unreadable_paths)
        return zip_bytes

    st.download_button(
        "Download bulk submission config",
        icon=":material/download:",
        icon_position="right",
        data=build_zip,
        file_name=get_bulk_config_filename(pool_ids),
        mime="application/zip",
        key=key,
        # Rerun the fragment after the download to report the inputs that could not be included
        on_click="rerun",
    )

    export_error, unreadable_paths = st.session_state.get(export_report_key, (False, []))
    if export_error:
        # A download button cannot abort once clicked, so an empty ZIP is reported after the rerun
        st.error("None of the selected pools has a design workflow to export as a bulk submission config.")
    if unreadable_paths:
        st.warning(
            "Some input files could not be read and were not included in the ZIP, "
            "the config still refers to them by their original storage path:\n\n"
            + "\n".join(f"- {path}" for path in unreadable_paths)
        )


@st.fragment
def download_job_designs_component(
    design_ids: list[str],
    pools: list[Pool],
    descriptor_keys_by_job_id: dict[str, list[str]] = None,
    key: str = "default",
    single_line: bool = True,
    group_by: str = None,
    group_by_fmt: str = "{}",
    group_by_flatten: bool = False,
):
    """Download design files for the specified workflow.

    :param design_ids: List of design IDs to download files for
    :param pools: List of Pool objects corresponding to the designs
    :param descriptor_keys_by_job_id: Optional dict mapping job ID to list of its descriptor keys that should be included (used for descriptors that require a job id)
    :param key: Streamlit component key prefix
    :param single_line: Whether to display the download buttons in a single line (True) or in separate containers (False)
    :param group_by: Optional descriptor key to group the downloaded design files by.
    :param group_by_fmt: Optional format string for the group_by values in the zip file names. Default is "{}" (no formatting).
    :param group_by_flatten: If True, flatten the group_by values in the zip file names (e.g. "group1 filename.ext" instead of "group1/filename.ext"). Only applicable if group_by is specified.
    """

    # label -> (Model, field_name)
    # for example: {"pdb files": (Design, "structure_path")}
    # DB reads are passed in from the cached app versions, so core does not repeat them.
    # The job descriptors are merged in here because the descriptor table below needs them too.
    available_descriptors = merge_job_descriptors(
        get_cached_available_descriptors(design_ids), descriptor_keys_by_job_id
    )
    download_fields = resolve_download_fields(
        pools=pools,
        design_ids=design_ids,
        design_jobs=get_cached_design_jobs([pool.design_job_id for pool in pools if pool.design_job_id]),
        available_descriptors=available_descriptors,
    )

    if single_line:
        first, second, third, extra = st.columns([1, 1, 1, 1])
    else:
        first = st.container()
        second = st.container()
        third = st.container()
        extra = st.container()
    # for example ovo_xyv_avg_123_designs
    filename_prefix = get_download_filename_prefix([p.id for p in pools], design_ids)
    filename = filename_prefix + f"_{len(design_ids)}_designs"
    key = key + "_" + get_hash_of_bytes(",".join(design_ids).encode())

    # Descriptor table
    with first:
        download_descriptor_table(
            filename,
            design_ids,
            descriptor_keys=available_descriptors,
            sort_by=group_by,
            descriptor_job_id=descriptor_keys_by_job_id,
            key=key,
            width="stretch",
        )

    # All files in one zip
    with second:
        download_design_files(
            label="Download design files",
            download_fields=download_fields,
            filename=filename,
            design_ids=design_ids,
            group_by=group_by,
            group_by_fmt=group_by_fmt,
            group_by_flatten=group_by_flatten,
            descriptor_job_id=descriptor_keys_by_job_id,
            key=key,
        )

    # Individual file types in separate zips
    if len(download_fields) > 1:
        with third:
            download_design_files(
                label="Download by type",
                download_fields=download_fields,
                menu_by_type=True,
                filename=filename,
                design_ids=design_ids,
                group_by=group_by,
                group_by_fmt=group_by_fmt,
                group_by_flatten=group_by_flatten,
                descriptor_job_id=descriptor_keys_by_job_id,
                key=key,
            )

    return extra


@st.fragment
def download_descriptor_table(
    filename,
    design_ids,
    descriptor_keys=None,
    sort_by: str = None,
    descriptor_job_id: str | dict[str, list[str]] = None,
    label: str = None,
    key="default",
    width="content",
):
    """Show download button for descriptor table of the specified designs and descriptors.

    :param filename: The base filename to use for the downloaded file (without extension)
    :param design_ids: List of design IDs to include in the descriptor table
    :param descriptor_keys: List of descriptor keys to include in the table. If None, all available descriptors will be included (excluding those that require a descriptor job id).
    :param sort_by: Optional descriptor key to sort the table by
    :param descriptor_job_id: Optional descriptor job ID to filter by, or a dict mapping job ID to list of its descriptor keys that should be filtered by that job (if present in descriptor_keys).
    :param key: Streamlit component key prefix
    :param width: Width of the download button ("content" or "stretch")
    """
    if label is None:
        label = "Download full descriptor table" if len(design_ids) > 1 else "Download descriptors"
    if st.button(
        label,
        key=f"prepare_descriptors_{key}",
        width=width,
    ):
        with st.spinner("Preparing descriptor table..."):
            excel_bytes = export_design_descriptors_excel(
                design_ids=design_ids,
                descriptor_keys=descriptor_keys,
                sort_by=sort_by,
                descriptor_job_id=descriptor_job_id,
            ).getvalue()
        confirm_download_button(
            data=excel_bytes,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_descriptors_{key}",
        )


@st.fragment
def download_design_files(
    label: str,
    download_fields: dict[str, tuple[Base, str]],
    filename: str,
    design_ids: list,
    menu_by_type: bool = False,
    group_by: str = None,
    group_by_fmt: str = "{}",
    group_by_flatten: bool = False,
    descriptor_job_id: str | dict[str, list[str]] | None = None,
    key="default",
):
    """Show download button for design files of the specified designs and fields.

    :param label: Label for the download button
    :param download_fields: Dict mapping label to (Model, field_name) for the files to download
    :param filename: The base filename to use for the downloaded file (without extension)
    :param design_ids: List of design IDs to include in the download
    :param menu_by_type: If True, show a streamlit menu to choose the file type to download. If False, download all files in one zip.
    :param group_by: Optional descriptor key to group the downloaded files by
    :param group_by_fmt: Optional format string for the group_by values in the zip file names. Default is "{}" (no formatting).
    :param group_by_flatten: If True, flatten the group_by values in the zip file names (e.g. "group1 filename.ext" instead of "group1/filename.ext"). Only applicable if group_by is specified.
    :param descriptor_job_id: Optional descriptor job ID to filter by, or a dict mapping job ID to list of its descriptor keys that should be filtered by that job (if present in download_fields).
    :param key: Streamlit component key prefix
    """
    if menu_by_type:
        options = list(download_fields.keys())
        button = st.menu_button(label, options=options, key=f"prepare_{filename}_menu_{key}", width="stretch")
        download_field = button
        if download_field == BULK_CONFIG_DOWNLOAD_LABEL:
            # Generated from the pools' workflows, not read from storage like the other fields
            pool_ids = list({Design.design_id_to_pool_id(design_id) for design_id in design_ids})
            download_bulk_config_button(pool_ids, key=f"download_bulk_{key}")
            return
        if download_field:
            # Only download the selected field
            download_fields = {download_field: download_fields[download_field]}
    else:
        # The bulk config is not a design file, it is only offered as its own download
        download_fields = {k: v for k, v in download_fields.items() if k != BULK_CONFIG_DOWNLOAD_LABEL}
        button = st.button(label, key=f"prepare_{filename}_{key}", width="stretch")
    if button:
        with st.spinner("Loading files..."):
            group_by_values = None
            if group_by is not None:
                # Read the group_by descriptor values here, to use the app's cached read of them
                group_by_job_id = get_descriptor_job_id_for_key(descriptor_job_id, group_by)
                group_by_values = (
                    get_cached_descriptor_values(group_by, design_ids, descriptor_job_id=group_by_job_id)
                    .dropna()
                    .to_dict()
                )
            storage_paths_by_group = collect_storage_paths_by_group(
                download_fields,
                design_ids,
                default_group=filename,
                group_by=group_by,
                group_by_fmt=group_by_fmt,
                group_by_values=group_by_values,
                descriptor_job_id=descriptor_job_id,
            )
            num_paths = sum(len(paths) for paths in storage_paths_by_group.values())

        if not num_paths:
            st.error("No files found")
            return
        if num_paths == 1:
            # Single file, download it directly instead of a zip holding one entry
            storage_path = next(path for paths in storage_paths_by_group.values() for path in paths)
            filename = os.path.basename(storage_path)
            with st.spinner("Downloading file..."):
                data = storage.read_file_bytes(storage_path)
            st.write(f"Prepared file *{filename}*")
            confirm_download_button(data=data, file_name=filename, key=f"download_{filename}_{key}")
        else:
            # Multiple files, prepare zip
            with st.spinner(f"Preparing zip file with {num_paths:,} results..."):
                data = storage.create_zip(storage_paths_by_group, flatten=group_by_flatten)

            st.write(
                f"Prepared zip with {num_paths:,} files for {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}."
            )
            confirm_download_button(
                data=data, file_name=filename + ".zip", mime="application/zip", key=f"download_{filename}_{key}"
            )
