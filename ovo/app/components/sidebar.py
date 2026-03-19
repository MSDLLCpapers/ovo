import streamlit as st

from ovo.app.components.project_components import create_project_dialog, project_list_dialog
from ovo.app.utils.cached_db import get_cached_project_ids_and_names
from ovo.core.logic.project_logic import get_or_create_personal_project
from ovo.core.logic.user_settings_logic import get_or_create_user_settings, set_user_setting
from ovo import db, get_username, config
from ovo.core.database.models import Project


def get_query_arg_project() -> Project | None:
    if project_id := st.query_params.get("project_id"):
        if not config.auth.allow_private_project_link_access and project_id not in get_cached_project_ids_and_names(
            username=get_username()
        ):
            st.error(f"Project URL **{project_id}** not accessible, redirecting to last project.")
            del st.query_params["project_id"]
            return None
        else:
            return db.get(Project, id=project_id)
    return None


def project_sidebar_component():
    success_message = None

    if st.session_state.project is None:
        if project := get_query_arg_project():
            # Load project from URL query parameter
            success_message = f"Opened project from URL"
            st.session_state.project = project
        elif config.props.read_only:
            # In read-only mode, just select the first available project
            project_ids_and_names = get_cached_project_ids_and_names(username=get_username())
            if not project_ids_and_names:
                st.error(f"No projects available to user {get_username()} in read-only mode.")
                st.stop()
            st.session_state.project = db.get(Project, id=list(project_ids_and_names.keys())[0])
        else:
            # Restore last selected project or select personal project
            user_settings = get_or_create_user_settings()
            last_project_id = user_settings.props.get("ovo.last_project_id")
            if last_project_id and (project := db.get(Project, last_project_id)):
                success_message = f"Resuming in project **{project.name}**"
                st.session_state.project = project
            else:
                st.session_state.project = get_or_create_personal_project()

    project_ids_and_names = get_cached_project_ids_and_names(
        username=get_username(), extra_project_ids=[st.session_state.project.id]
    )
    project_ids = sorted(project_ids_and_names.keys(), key=lambda x: project_ids_and_names[x].lower())

    left, right = st.sidebar.columns([5, 1], vertical_alignment="bottom", gap="xsmall")
    with left:
        selected_project_id = st.selectbox(
            "**Project**",
            format_func=project_ids_and_names.get,
            # Change key when number of projects changes to reset dropdown state
            key=f"project_dropdown_{st.session_state.project.id}_{len(project_ids)}",
            options=project_ids,
            # Do not select any project if the currently selected project is not in the list
            # (should only happen if the project was deleted)
            index=project_ids.index(st.session_state.project.id)
            if st.session_state.project.id in project_ids
            else None,
            width="stretch",
        )
        if not selected_project_id:
            # This should only happen if the currently selected project is deleted
            st.error("Please select a project")
            st.stop()
    with right:
        if st.button(":material/more_horiz:"):
            project_list_dialog()

    # Hack needed to hide tooltips because they disrupt clicking on the dropdown item (as of Dec 2024)
    dropdown_style = """
    <style>
    .stTooltipContent {
    pointer-events: none;
    }
    </style>
    """
    st.markdown(dropdown_style, unsafe_allow_html=True)

    if st.session_state.flash_project:
        # Notify that a new project was selected or created
        st.sidebar.success(st.session_state.flash_project)
        st.session_state.flash_project = None

    if selected_project_id != st.session_state.project.id:
        # Update selected project when changed
        selected_project = db.get(Project, id=selected_project_id)
        st.session_state.project = selected_project
        st.session_state.flash_project = f"Selected project **{selected_project.name}**"
        if not config.props.read_only:
            user_settings = get_or_create_user_settings()
            recent_project_ids = user_settings.props.get("ovo.recent_project_ids", []).copy()
            if selected_project.id in recent_project_ids:
                recent_project_ids.remove(selected_project.id)
            recent_project_ids = [selected_project.id] + recent_project_ids
            set_user_setting("ovo.last_project_id", selected_project.id)
            set_user_setting("ovo.recent_project_ids", recent_project_ids[:10])
        # the additional rerun is required to ensure that the dropdown key has settled to the new key
        # without this rerun, changing project multiple times is ignored because the dropdown key changes in meantime,
        # so user's selection is discarded because that dropdown doesn't exist anymore
        st.rerun()

    if selected_project_id != st.query_params.get("project_id"):
        st.query_params["project_id"] = selected_project_id

    if config.props.read_only:
        st.sidebar.info("Read-only mode")

    if st.session_state.get("open_create_project_dialog"):
        st.session_state.pop("open_create_project_dialog")
        create_project_dialog()

    if success_message:
        st.sidebar.success(success_message)
