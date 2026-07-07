import os
from collections import defaultdict
from typing import Optional

import pandas as pd
import streamlit as st

from ovo import storage, Pool
from ovo.app.components.custom_elements import confirm_download_button
from ovo.app.utils.cached_db import (
    get_cached_design_jobs,
    get_cached_available_descriptors,
    get_cached_descriptor_values,
)
from ovo.core.database import DesignWorkflow, WorkflowTypes, Base, FileDescriptor, DescriptorValue
from ovo.core.database.descriptors import ALL_DESCRIPTORS, ALL_DESCRIPTORS_BY_KEY
from ovo.core.database.descriptors_clustering import PROTEIN_CLUSTERING_DESCRIPTORS_BY_KEY
from ovo.core.logic.descriptor_logic import export_design_descriptors_excel, get_wide_descriptor_table
from ovo.core.logic.design_logic import collect_storage_paths
from ovo.core.utils.formatting import get_hash_of_bytes


@st.fragment
def download_job_designs_component(
    design_ids: list[str],
    pools: list[Pool],
    descriptor_job_id: dict[str, list[str]] = None,
    key: str = "default",
    single_line: bool = True,
    group_by: str = None,
    group_by_fmt: str = "{}",
    group_by_flatten: bool = False,
):
    """Download design files for the specified workflow.

    :param design_ids: List of design IDs to download files for
    :param pools: List of Pool objects corresponding to the designs
    :param descriptor_job_id: Optional dict mapping job ID to list of its descriptor keys that should be included (used for descriptors that require a job id)
    :param key: Streamlit component key prefix
    :param single_line: Whether to display the download buttons in a single line (True) or in separate containers (False)
    :param group_by: Optional descriptor key to group the downloaded design files by.
    :param group_by_fmt: Optional format string for the group_by values in the zip file names. Default is "{}" (no formatting).
    :param group_by_flatten: If True, flatten the group_by values in the zip file names (e.g. "group1 filename.ext" instead of "group1/filename.ext"). Only applicable if group_by is specified.
    """

    # label -> (Model, field_name)
    # for example: {"pdb files": (Design, "structure_path")}
    download_fields = {}
    if any(not pool.design_job_id for pool in pools):
        # Some pools don't have a design job (e.g. uploaded designs), so we need to include the basic fields
        download_fields.update(DesignWorkflow.get_download_fields())
    design_jobs = get_cached_design_jobs([pool.design_job_id for pool in pools if pool.design_job_id])
    for design_job in design_jobs:
        WorkflowType = (
            WorkflowTypes.get(design_job.workflow.name) if design_job and design_job.workflow else DesignWorkflow
        )
        for label, v in WorkflowType.get_download_fields().items():
            if label in download_fields:
                assert download_fields[label] == v, (
                    f"Conflicting download field for key '{label}': {download_fields[label]} != {v}"
                )

        download_fields.update(WorkflowType.get_download_fields())
    # Add available file descriptor paths
    available_descriptors = get_cached_available_descriptors(design_ids)
    if descriptor_job_id:
        assert isinstance(descriptor_job_id, dict), (
            f"Expected descriptor_job_id to be a dict, got {type(descriptor_job_id)}"
        )
        available_descriptors = {
            **{k: ALL_DESCRIPTORS_BY_KEY[k] for job_id, keys in descriptor_job_id.items() for k in keys},
            **available_descriptors,
        }

    file_descriptors = [d for d in available_descriptors.values() if isinstance(d, FileDescriptor)]
    for file_descriptor in file_descriptors:
        download_fields[file_descriptor.name] = (DescriptorValue, file_descriptor.key)

    if single_line:
        first, second, third, _ = st.columns([1, 1, 1, 1])
    else:
        first = st.container()
        second = st.container()
        third = st.container()
    # for example ovo_xyv_avg_123_designs
    if len(design_ids) <= 3:
        filename_prefix = "_".join(design_ids)
    elif len(pools) < 10:
        filename_prefix = "ovo_" + "_".join(p.id for p in pools)
    else:
        filename_prefix = f"ovo_{len(pools)}_pools"
    filename = filename_prefix + f"_{len(design_ids)}_designs"
    key = key + "_" + get_hash_of_bytes(",".join(design_ids).encode())

    # Descriptor table
    with first:
        download_descriptor_table(
            filename,
            design_ids,
            descriptor_keys=available_descriptors,
            sort_by=group_by,
            descriptor_job_id=descriptor_job_id,
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
            descriptor_job_id=descriptor_job_id,
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
                descriptor_job_id=descriptor_job_id,
                key=key,
            )


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
            # Get raw dataframe with single header, columns named with descriptor keys ("pipeline|tool_key|descriptor")
            df = get_wide_descriptor_table(
                design_ids=design_ids,
                descriptor_keys=descriptor_keys,
                nested=False,
                human_readable=False,
                descriptor_job_id=descriptor_job_id,
            )
            if sort_by is not None and not df.empty:
                ascending = True
                if sort_by.startswith("-"):
                    sort_by = sort_by[1:]
                    ascending = False
                df = df.sort_values(by=sort_by, ascending=ascending)
            excel_bytes = export_design_descriptors_excel(df)
        confirm_download_button(
            data=excel_bytes.getvalue(),
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
        if download_field:
            # Only download the selected field
            download_fields = {download_field: download_fields[download_field]}
    else:
        button = st.button(label, key=f"prepare_{filename}_{key}", width="stretch")
    if button:
        with st.spinner("Loading files..."):
            # Get list of storage paths from Design or DesignWorkflow objects
            storage_paths_by_design = collect_storage_paths(
                download_fields, design_ids, descriptor_job_id=descriptor_job_id
            )

        if not storage_paths_by_design:
            st.error(f"No files found")
            return
        num_paths = sum(len(paths) for paths in storage_paths_by_design.values())
        if num_paths == 1:
            # Single file, download directly
            first_path = next(iter(storage_paths_by_design.values()))[0]
            filename = os.path.basename(first_path)
            with st.spinner(f"Downloading file..."):
                data = storage.read_file_bytes(first_path)
            st.write(f"Prepared file *{filename}*")
            confirm_download_button(data=data, file_name=filename, key=f"download_{filename}_{key}")
        else:
            # Multiple files, prepare zip
            with st.spinner(f"Preparing zip file with {num_paths:,} results..."):
                if group_by is not None:
                    if isinstance(descriptor_job_id, dict):
                        group_by_job_id = next(
                            (job_id for job_id, keys in descriptor_job_id.items() if group_by in keys), None
                        )
                    elif isinstance(descriptor_job_id, str):
                        group_by_job_id = descriptor_job_id
                    else:
                        group_by_job_id = None
                    group_by_values = (
                        get_cached_descriptor_values(group_by, design_ids, descriptor_job_id=group_by_job_id)
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
                else:
                    storage_paths_by_group = {
                        filename: sorted(set([path for paths in storage_paths_by_design.values() for path in paths]))
                    }
                data = storage.create_zip(storage_paths_by_group, flatten=group_by_flatten)

            st.write(
                f"Prepared zip with {num_paths:,} files for {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}."
            )
            confirm_download_button(
                data=data, file_name=filename + ".zip", mime="application/zip", key=f"download_{filename}_{key}"
            )
