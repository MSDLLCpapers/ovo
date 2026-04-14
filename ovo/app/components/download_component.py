import os

import streamlit as st

from ovo import storage, Pool
from ovo.app.components.custom_elements import confirm_download_button
from ovo.app.utils.cached_db import get_cached_design_jobs, get_cached_available_descriptors
from ovo.core.database import DesignWorkflow, WorkflowTypes, Base, FileDescriptor, DescriptorValue
from ovo.core.database.descriptors import ALL_DESCRIPTORS
from ovo.core.database.descriptors_clustering import PROTEIN_CLUSTERING_DESCRIPTORS_BY_KEY
from ovo.core.logic.descriptor_logic import export_design_descriptors_excel, get_wide_descriptor_table
from ovo.core.logic.design_logic import collect_storage_paths
from ovo.core.utils.formatting import get_hash_of_bytes


@st.fragment
def download_job_designs_component(
    design_ids: list[str], pools: list[Pool], key: str = "default", single_line: bool = True
):
    """
    Download design files for the specified workflow.
    Args:
        design_ids (list[str]): A list of design IDs to be displayed.
        pools (list[Pool]): A list of pools associated with the designs.
        key (str): Streamlit component key prefix
        single_line: Whether to display the download options in a single line
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
    # Dont consider descriptors that depend on descriptor job (ambiguous values without it)
    file_descriptors = [
        d
        for d in ALL_DESCRIPTORS
        if isinstance(d, FileDescriptor) and not d.required_descriptor_job and d.key in available_descriptors
    ]
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
        download_descriptor_table(filename, design_ids, descriptor_keys=available_descriptors, key=key, width="stretch")

    # All files in one zip
    with second:
        download_design_files(
            label="design files",
            download_fields=download_fields,
            filename=filename,
            design_ids=design_ids,
            key=key,
        )

    # Individual file types in separate zips
    if len(download_fields) > 1:
        with third:
            with st.popover("Download by type", width="stretch"):
                for label, (Model, field) in download_fields.items():
                    download_design_files(
                        label=label,
                        download_fields={label: (Model, field)},
                        filename=f"{filename}_{label.lower().replace(' ', '_')}",
                        design_ids=design_ids,
                        key=key,
                    )


@st.fragment
def download_descriptor_table(
    filename, design_ids, descriptor_keys=None, key="default", width="content", descriptor_job_id=None
):
    if st.button(
        "Download full descriptor table" if len(design_ids) > 1 else "Download descriptors",
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
            excel_bytes = export_design_descriptors_excel(df)
        confirm_download_button(
            data=excel_bytes.getvalue(),
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_descriptors_{key}",
        )


@st.fragment
def download_design_files(
    label: str, download_fields: dict[str, tuple[Base, str]], filename: str, design_ids: list, key="default"
):
    if st.button(f"Download {label}", key=f"prepare_{filename}_{key}", width="stretch"):
        with st.spinner("Loading files..."):
            # Get list of storage paths from Design or DesignWorkflow objects
            storage_paths = collect_storage_paths(download_fields, design_ids)
            # Make sure the paths are unique
            storage_paths = sorted(set(storage_paths))

        if not storage_paths:
            st.error(f"No files found")
            return
        elif len(storage_paths) == 1:
            # Single file, download directly
            filename = os.path.basename(storage_paths[0])
            with st.spinner(f"Downloading file..."):
                data = storage.read_file_bytes(storage_paths[0])
            st.write(f"Prepared file *{filename}*")
            confirm_download_button(data=data, file_name=filename, key=f"download_{filename}_{key}")
        else:
            # Multiple files, prepare zip
            with st.spinner(f"Preparing zip file with {len(storage_paths):,} results..."):
                data = storage.create_zip({filename: storage_paths})

            st.write(
                f"Prepared zip with {len(storage_paths):,} files for {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}."
            )
            confirm_download_button(
                data=data, file_name=filename + ".zip", mime="application/zip", key=f"download_{filename}_{key}"
            )
