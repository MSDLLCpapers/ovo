import os
import shutil
import tempfile
import zipfile

import streamlit as st
from humanize import naturalsize
from streamlit import session_state

from ovo import db
from ovo.app.utils.page_init import initialize_page
from ovo.core.database.models import Project
from ovo.core.logic.import_export_logic import export_project, import_project, export_import_project
from ovo import storage
from ovo.core.utils.formatting import safe_filename


EXPORT_DESIGNS_LIMIT = 20_000  # TODO should this be configured in config?


def show_counts(counts: dict[str, int]):
    # Display summary in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Projects", counts.get("project"))
        st.metric("Rounds", counts.get("round"))
        st.metric("Pools", counts.get("pool"))

    with col2:
        st.metric("Total Designs", counts.get("design"))
        st.metric("Storage Files", counts.get("storage_file"))
        st.metric("Artifacts", counts.get("project_artifact"))

    with col3:
        st.metric("Descriptor Jobs", counts.get("descriptor_job"))
        st.metric("Descriptor Values", counts.get("descriptor_value"))


def export_tab():
    st.subheader("Export Project Data")
    st.markdown("""
    Export a complete project including all associated data to a ZIP file containing
    an SQLite database and all associated storage files.
    """)

    # Get all projects for the current user
    projects = db.select(Project, order_by="-created_date_utc")

    if not projects:
        st.warning("No projects found. Create a project first to export data.")
        return

    # Project selection
    st.subheader("Select Project to Export")
    projects_by_id = {project.id: project for project in projects}
    project_ids = sorted(projects_by_id.keys(), key=lambda p: projects_by_id[p].created_date_utc, reverse=True)
    project_id = st.selectbox(
        "Choose a project:",
        options=project_ids,
        index=project_ids.index(session_state.project.id)
        if session_state.project and session_state.project.id in project_ids
        else None,
        key=f"export_project_selector_{session_state.project.id}",
        format_func=lambda project_id: f"{projects_by_id[project_id].name} - {projects_by_id[project_id].author}",
    )

    if not project_id:
        return

    project = projects_by_id[project_id]

    # Show project information
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Project Name", project.name)
        st.metric("Author", project.author)

    with col2:
        st.metric("Created", project.created_date_utc.strftime("%Y-%m-%d %H:%M UTC"))
        st.metric("Visibility", "Public" if project.public else "Private")

    selection_options = {
        "accepted": "Accepted designs",
        "all": "All designs",
    }
    selection = st.radio(
        "Select designs to export:",
        options=selection_options.keys(),
        format_func=selection_options.get,
        key=f"export_selection_{session_state.project.id}",
        index=None,
    )
    if not selection:
        return
    accepted_only = selection == "accepted"

    # Get export summary
    st.subheader("Export Summary")
    with st.spinner("Preparing export..."):
        counts = export_import_project(
            source_db=db,
            source_storage=storage,
            dest_db=None,
            dest_dir=None,
            project_id=project_id,
            count_only=True,
            accepted_only=accepted_only,
        )

    st.markdown("The following data will be exported:")

    show_counts(counts)

    if counts["design"] > EXPORT_DESIGNS_LIMIT:
        # Do not allow exporting big projects for now due to memory limits
        if not accepted_only:
            st.error(
                f"Cannot export more than {EXPORT_DESIGNS_LIMIT} designs in the UI, "
                f'please select "Accepted designs" only, or use the commandline to export all designs.'
            )
        else:
            st.error(
                f"Cannot export more than {EXPORT_DESIGNS_LIMIT} designs in the UI, please use the commandline instead"
            )
        return

    # Export button
    if st.button("🚀 Start Export", type="primary", key="export_btn"):
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Preparing export...")
        progress_bar.progress(10)

        # Perform the export
        status_text.text("Exporting project data...")
        progress_bar.progress(30)
        # TODO show actual progress

        zip_path = export_project(project_id, accepted_only=accepted_only)

        # Read the zip archive
        progress_bar.progress(80)
        status_text.text("Preparing download...")
        with open(zip_path, "rb") as f:
            zip_data = f.read()

        # Clean up temp file
        os.remove(zip_path)

        # Prepare download buttons
        progress_bar.progress(100)
        # clear status
        progress_bar.empty()
        status_text.empty()

        st.success("✅ Export completed successfully!")

        # Download section
        st.subheader("Download Export")

        st.download_button(
            label=f"📦 Download Project Export ({naturalsize(len(zip_data))} ZIP)",
            data=zip_data,
            file_name=f"{safe_filename(project.name)}_ovo_export.zip",
            mime="application/zip",
            help="Contains ovo.db database, storage files with relative paths, and config.yml template",
        )

        st.info(f"ZIP file size: {len(zip_data) / (1024 * 1024):.1f} MB")


def import_tab():
    st.subheader("Import Project Data")
    st.markdown("""
        Import project data from a ZIP file containing ovo.db and storage files.
        The ZIP file should be in the format created by the Export function.
        """)

    # Step 1: File uploader
    uploaded_file = st.file_uploader(
        "Choose a ZIP file to import",
        type="zip",
        help="Upload a ZIP file exported from OVO containing ovo.db and storage files",
        key="import_file_uploader",
    )

    if uploaded_file:
        with st.spinner("Importing ZIP file..."):
            temp_root = tempfile.mkdtemp(prefix="ovo")
            with zipfile.ZipFile(uploaded_file, "r") as zipf:
                zipf.extractall(temp_root)
            paths = os.listdir(temp_root)
            if not len(paths) == 1 or not os.path.isdir(os.path.join(temp_root, paths[0])):
                raise ValueError(f"Invalid ZIP file structure: expected a single root directory, got: {paths}")
            st.session_state.import_temp_dir = os.path.join(temp_root, paths[0])
            st.session_state.import_counts = import_project(
                st.session_state.import_temp_dir, count_only=True, init_and_migrate=True
            )
            st.session_state.import_done = False

    if not st.session_state.get("import_counts"):
        # Instructions
        st.subheader("Import Instructions")
        st.markdown("""
            **Import Requirements:**

            1. ZIP file must contain `ovo.db` (SQLite database file)
            2. ZIP file may contain `storage/` directory with data files (relative paths)
            3. ZIP file may contain `config.yml` (configuration template)
            4. ZIP file should be created using OVO's Export function

            **Import Process:**

            1. **Upload**: Choose a ZIP file to upload
            2. **Preview**: Click "Preview Project" to analyze the file and show project details
            3. **Customize**: Modify project name, author, and visibility settings
            4. **Import**: Click "Start Import" to import with your custom settings

            **Notes:**

            - Data is imported additively (existing data is preserved)
            - Duplicate IDs are skipped with warnings
            - Storage files are added with relative paths (no migration needed)
            - Configuration file is included as reference but not applied
            """)
        return

    st.subheader("Step 2: Project Details & Import Options")

    # Show original project information
    st.markdown("**Import Statistics:**")
    show_counts(st.session_state.import_counts)

    if st.button("Import data", type="primary", key="import_btn"):
        # Import the project
        with st.spinner("Importing..."):
            # TODO show progress
            import_project(st.session_state.import_temp_dir)

        st.session_state.import_done = True
        # Rerun to refresh projects list in sidebar, session will be cleared using logic below
        st.rerun()
    else:
        # Warning about import
        st.warning("""
        ⚠️ **Import Warning**

        - Importing will add new data to your current database
        - Storage files will be added to your storage system
        - This operation cannot be easily undone
        """)


initialize_page(page_title="Import & Export")

st.title("📦 Import & Export Project Data")

if st.session_state.get("import_done"):
    # Success message
    st.success("✅ Import completed successfully!")

    # Show import summary
    st.subheader("Import Summary")
    show_counts(st.session_state.import_counts)

    # Clear temp directory and session state
    shutil.rmtree(st.session_state.import_temp_dir)
    del st.session_state.import_temp_dir
    del st.session_state.import_counts
    del st.session_state.import_done

    st.stop()

# Create tabs for Import and Export
tab1, tab2 = st.tabs(["📤 Export", "📥 Import"])

with tab1:
    export_tab()

with tab2:
    import_tab()
