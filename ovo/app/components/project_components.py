import humanize
import streamlit as st

from ovo import db, get_username, config
from ovo.app.components.custom_elements import highlight_query
from ovo.app.pages import project_page
from ovo.app.utils.cached_db import get_cached_project_ids_and_names
from ovo.app.utils.cached_db import (
    get_cached_projects,
    get_cached_rounds,
    get_cached_pools,
)
from ovo.core.database.models import Design
from ovo.core.database.models import Project
from ovo.core.logic.project_logic import get_or_create_personal_project
from ovo.core.logic.user_settings_logic import get_or_create_user_settings, update_last_project_id


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
    cursor: pointer !important;
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
        update_last_project_id(selected_project_id)
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


@st.fragment()
@st.dialog("Create new project")
def create_project_dialog():
    username = get_username()

    project_name = st.text_input("Project name", placeholder="My Project")
    public = _render_public_toggle_with_caption(default_value=True)

    if _render_submit_button("Create project"):
        if project_name == "":
            st.error("Please provide a project name.")
            return

        if not _validate_project_name_uniqueness(project_name, username):
            return

        new_project = Project(
            name=project_name,
            author=username,
            public=public,
        )
        db.save(new_project)
        st.session_state.flash_project = f'Project "**{project_name.strip()}**" created'
        st.session_state.project = new_project

        st.switch_page(project_page)
        return


@st.fragment()
@st.dialog("Project Settings", width="large")
def edit_project_dialog(project_id: str):
    username = get_username()

    existing_project = db.get(Project, id=project_id)
    if not existing_project:
        st.error(f"Project with ID {project_id} not found.")
        return

    project_name = st.text_input("Project name", value=existing_project.name, placeholder="My Project")
    public = _render_public_toggle_with_caption(default_value=existing_project.public)
    help_text = (
        "Supports markdown formatting:\n**bold**\n*italic*\n#### Heading\n##### Subheading\n- List items\n[links](url)"
    )
    description = st.text_area(
        "Description",
        value=existing_project.description or "",
        height=300,
        placeholder=f"Optional project description\n\n{help_text}",
        help=f"```\n{help_text}\n```",
    )

    if _render_submit_button("Save changes"):
        if project_name == "":
            st.error("Please provide a project name.")
            return

        if not _validate_project_name_uniqueness(project_name, username, existing_project_name=existing_project.name):
            return

        existing_project.name = project_name
        existing_project.description = description if description else None
        existing_project.public = public
        db.save(existing_project)
        st.session_state.project = existing_project

        st.rerun()
        return


@st.fragment()
@st.dialog("Manage Projects", width="medium")
def project_list_dialog(limit=100):
    username = get_username()

    # Get all accessible projects
    project_ids_and_names = get_cached_project_ids_and_names(username=username)

    if not project_ids_and_names:
        st.info("No projects found.")
        return

    # Load full project objects
    with st.spinner("Loading projects..."):
        projects = get_cached_projects(sorted(project_ids_and_names.keys()))
        projects_by_id = {p.id: p for p in projects}
        rounds = get_cached_rounds(project_ids=sorted(project_ids_and_names.keys()))
        pools = get_cached_pools(round_id__in=[r.id for r in rounds])

    with st.container(horizontal=True, vertical_alignment="bottom"):
        search = st.text_input(
            "Search projects",
            placeholder="Search projects by name, author, recent pools...",
            key="project_search",
            width=360,
        )
        st.button("Search")

        if not config.props.read_only:
            with st.container(horizontal=True, horizontal_alignment="right"):
                if st.button(":material/add: New project", type="primary"):
                    # handled in project_sidebar_component (we cannot open dialog from another dialog)
                    st.session_state["open_create_project_dialog"] = True
                    st.rerun()

    # Display recent projects
    user_settings = get_or_create_user_settings()
    recent_project_ids = user_settings.props.get("ovo.recent_project_ids", [])
    recent_projects = [projects_by_id[project_id] for project_id in recent_project_ids if project_id in projects_by_id]
    if recent_projects:
        header_container = st.container()
        num_found = 0
        for project in recent_projects:
            if _show_project_card(project, rounds, pools, search, key_suffix="recent"):
                num_found += 1
        if num_found:
            header_container.write("#### Recent projects")

    # Display all projects
    st.write("#### All projects")
    num_found = 0
    for project in projects:
        if _show_project_card(project, rounds, pools, search, key_suffix="all"):
            num_found += 1
        if num_found >= limit:
            st.write("...")
            break
    if not num_found:
        st.markdown(f'No projects found matching query **"{search}"**')


def _show_project_card(project, rounds, pools, search, key_suffix):
    project_round_ids = set(r.id for r in rounds if r.project_id == project.id)
    project_pools = [p for p in pools if p.round_id in project_round_ids]
    last_pool_names = ", ".join([p.name for p in project_pools])

    if (
        search
        and search.lower() not in project.name.lower()
        and search.lower() not in project.author.lower()
        and (search.lower() not in project.description.lower() if project.description else True)
        and (search.lower() not in last_pool_names.lower() if last_pool_names else True)
    ):
        # not matching search, skip
        return False

    with st.container(border=True):
        left, right = st.columns([5, 1])

        with left:
            st.markdown(f"**{project.name}**")
            st.caption(
                highlight_query(
                    f"Created: {humanize.naturaldate(project.created_date_utc)} by {project.author}",
                    search,
                )
            )

        with right:
            with st.container(horizontal=True, horizontal_alignment="right", gap="xsmall"):
                if st.button("Open", key=f"open_{project.id}_{key_suffix}"):
                    st.session_state.project = project
                    update_last_project_id(project.id)
                    st.switch_page(project_page)

        if project_pools:
            pool_names_truncated = last_pool_names[:150] + ("..." if len(last_pool_names) > 150 else "")
            pool_names_truncated = highlight_query(pool_names_truncated, search)
            st.caption(f"{len(project_pools)} pools: " + pool_names_truncated)
        else:
            st.caption("No pools yet in this project")
    return True


def _render_public_toggle_with_caption(default_value: bool = True) -> bool:
    """Render the public/private toggle with explanatory caption."""
    public = st.toggle(label="Public", value=default_value)

    st.caption(
        "Public projects are visible to all users with access to this app. "
        "Private projects are only visible to you"
        + (
            ", but are accessible by other users when shared via a link."
            if config.auth.allow_private_project_link_access
            else "."
        )
    )

    return public


def _render_submit_button(label: str) -> bool:
    """Render a submit button aligned to the right."""
    with st.container(horizontal=True, horizontal_alignment="right"):
        return st.button(label, type="primary")


def _validate_project_name_uniqueness(
    project_name: str, username: str, existing_project_name: str | None = None
) -> bool:
    """
    Validate that project name doesn't conflict with existing projects.
    Returns True if valid, False otherwise (and displays error).
    """
    # Skip check if editing and name unchanged
    if existing_project_name and existing_project_name == project_name:
        return True

    if db.count(Project, name=project_name, public=True):
        st.error(f'Public project "{project_name}" already exists. Please choose another name.')
        return False
    elif db.count(Project, name=project_name, author=username):
        st.error(f'You already have a private project named "{project_name}". Please choose another name.')
        return False

    return True


@st.fragment
def project_stats_fragment(project_id):
    st.write("#### Project statistics")
    with st.spinner("Loading project stats..."):
        rounds = get_cached_rounds(project_id=project_id)
        pools = get_cached_pools(round_id__in=[r.id for r in rounds])

        accepted_designs_by_pool = db.count(Design, pool_id__in=[p.id for p in pools], accepted=True)
        total_designs_by_pool = db.count(Design, pool_id__in=[p.id for p in pools])

    with st.container(horizontal=True, gap="large"):
        st.metric("Pools", value=f"{len(pools):,}", width="content")
        st.metric(label="Total designs", value=f"{total_designs_by_pool:,}", width="content")
        st.metric(label="Accepted designs", value=f"{accepted_designs_by_pool:,}", width="content")
