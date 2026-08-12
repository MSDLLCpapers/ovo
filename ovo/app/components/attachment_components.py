import os

import humanize
import streamlit as st
from ovo import storage, get_username, config, db
from ovo.core.database.models import (
    Project,
    ProjectArtifact,
    AttachmentArtifact,
    UnknownArtifact,
    DistanceMatrixArtifact,
    DescriptorJob,
)
from ovo.core.utils.formatting import safe_filename
from ovo.app.components.download_component import get_download_filename_prefix


def add_project_attachments(project: Project):
    st.write(
        "You can use this area to upload any project-related files. "
        "Tabular files indexed by design_id will be available for correlation analysis "
        "in the Regression tab on the Designs page."
    )

    if config.props.read_only:
        return

    if "uploader_reset" not in st.session_state:
        st.session_state.uploader_reset = 0
    uploaded_files = st.file_uploader(
        "Upload attachment (CSV, Excel, or other files)",
        type=config.props.allowed_attachment_types,
        accept_multiple_files=True,
        key=f"attachment_uploader_{st.session_state.uploader_reset}",
    )
    if uploaded_files:
        attachment_paths = []
        conflicts = False
        for uploaded_file in uploaded_files:
            sanitized_filename = safe_filename(uploaded_file.name)
            attachment_dir = os.path.join(storage.get_project_path(project.id), "attachments")
            attachment_path = os.path.join(attachment_dir, sanitized_filename)
            if attachment_path in attachment_paths:
                st.error(f"Duplicate filename '{sanitized_filename}' in uploaded files.")
                st.stop()
            if storage.file_exists(attachment_path):
                if uploaded_file.read() == storage.read_file_bytes(attachment_path):
                    st.error(f"File '{uploaded_file.name}' was already uploaded and is up to date.")
                    return
                st.error(f"File '{sanitized_filename}' already exists.")
                conflicts = True
                basename, extension = os.path.splitext(sanitized_filename)
                n = 1
                while storage.file_exists(attachment_path):
                    attachment_path = os.path.join(attachment_dir, f"{basename}_copy_{n}{extension}")
                    n += 1
            attachment_paths.append(attachment_path)
        if conflicts:
            upload_text = "Upload new version"
        elif len(uploaded_files) == 1:
            upload_text = "Upload file"
        else:
            upload_text = f"Upload {len(uploaded_files)} files"
        with st.container(horizontal=True):
            upload_button = st.button(
                upload_text,
                type="primary",
                disabled=not uploaded_files,
            )
            if conflicts:
                if st.button("Cancel"):
                    st.session_state.uploader_reset += 1
                    st.rerun()
        if upload_button:
            assert len(uploaded_files) == len(attachment_paths)
            for uploaded_file, attachment_path in zip(uploaded_files, attachment_paths):
                file_bytes = uploaded_file.read()
                # Upload file to Storage
                storage.store_file_bytes(file_bytes, attachment_path)
                # Create artifact entry in the DB
                try:
                    project_artifact = ProjectArtifact(
                        project_id=project.id,
                        artifact_type=AttachmentArtifact.artifact_type,
                        artifact=AttachmentArtifact(
                            file_path=attachment_path,
                            original_filename=uploaded_file.name,
                            size_bytes=len(file_bytes),
                        ),
                        author=get_username(),
                    )
                    db.save(project_artifact)
                except:
                    # If DB save fails, remove the uploaded file to avoid orphaned files
                    storage.remove(attachment_path)
                    raise
            st.session_state.flash_num_uploaded_attachments = len(uploaded_files)
            st.session_state.uploader_reset += 1
            st.rerun()

    if "flash_num_uploaded_attachments" in st.session_state:
        num_uploaded = st.session_state.flash_num_uploaded_attachments
        st.success(f"Successfully uploaded {num_uploaded} attachment{'s' if num_uploaded > 1 else ''}!")
        del st.session_state.flash_num_uploaded_attachments


def list_project_attachments(project: Project):
    """List project attachments with download and delete options."""
    attachments = db.select(
        ProjectArtifact,
        project_id=project.id,
        artifact_type=AttachmentArtifact.artifact_type,
        order_by=ProjectArtifact.created_date_utc.desc(),
    )

    if not attachments:
        st.write("No attachments uploaded yet.")
        return

    for pa in attachments:
        attachment: AttachmentArtifact = pa.artifact
        if isinstance(attachment, UnknownArtifact):
            st.warning(f"Skipping outdated schema attachment: {attachment.error}")
            continue
        with st.container(horizontal=True, vertical_alignment="center"):
            st.download_button(
                label="",
                icon=":material/download:",
                data=lambda: storage.read_file_bytes(attachment.file_path),
                file_name=attachment.original_filename,
                key=f"download_{pa.id}",
            )
            with st.popover(
                icon=":material/more_horiz:",
                label="",
                key=f"delete_{pa.id}",
            ):
                if st.button(":material/delete: Delete", type="primary", key=f"delete_button_{pa.id}"):
                    storage.remove(attachment.file_path)
                    db.remove(ProjectArtifact, id=pa.id)
                    st.rerun()

            st.write(attachment.original_filename)
            st.write(f":grey[{humanize.naturalsize(attachment.size_bytes)}]")
            st.write(f":grey[uploaded {humanize.naturaldate(pa.created_date_utc)} by {pa.author}]")


def select_project_attachments(
    project: Project, extensions: tuple = None, missing_message: str = None
) -> list[AttachmentArtifact]:
    """Shows checkboxes with attachments and returns a list of selected project attachments."""

    all_attachments = db.select(
        ProjectArtifact,
        project_id=project.id,
        artifact_type=AttachmentArtifact.artifact_type,
        order_by=ProjectArtifact.created_date_utc.desc(),
    )

    if extensions:
        filtered_attachments = []
        for pa in all_attachments:
            attachment: AttachmentArtifact = pa.artifact
            if isinstance(attachment, UnknownArtifact):
                st.warning(f"Skipping outdated schema attachment: {attachment.error}")
                continue
            # Only show CSV and Excel files
            if attachment.original_filename.endswith(extensions):
                filtered_attachments.append(pa)
    else:
        filtered_attachments = all_attachments

    if not filtered_attachments:
        if missing_message:
            st.write(missing_message)
        return []

    st.write("Or select from project attachments:")
    selected_attachments = []
    for pa in filtered_attachments:
        attachment: AttachmentArtifact = pa.artifact
        with st.container(horizontal=True, vertical_alignment="center"):
            if st.checkbox(attachment.original_filename, key=f"attachment_{pa.id}", bind="query-params"):
                selected_attachments.append(attachment)
            st.write(f":grey[{humanize.naturalsize(attachment.size_bytes)}]")
            st.write(f":grey[uploaded {humanize.naturaldate(pa.created_date_utc)} by {pa.author}]")
    return selected_attachments


def download_distance_matrix_artifacts(
    artifact: DistanceMatrixArtifact, job: DescriptorJob, pools: list, design_ids: list[str]
):
    """Display distance matrix artifacts for a descriptor job with download button.

    :param job: DescriptorJob object
    :param pools: List of Pool objects corresponding to the designs
    :param design_ids: List of design IDs that were clustered
    """
    if not artifact:
        return

    clustering_method = job.workflow.params.similarity_method

    # Generate filename using same convention as descriptor table downloads
    filename_prefix = get_download_filename_prefix([p.id for p in pools], design_ids)
    filename = f"{filename_prefix}_distance_matrix_{clustering_method}.csv.gz"

    st.download_button(
        label=f"Download distance matrix",
        data=lambda path=artifact.file_path: storage.read_file_bytes(path),
        file_name=filename,
        key=f"download_distance_matrix_{job.id}",
        width="stretch",
    )
