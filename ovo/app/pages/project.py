import humanize
import streamlit as st

from ovo import storage, get_username, config
from ovo.app.components.attachment_components import add_project_attachments, list_project_attachments
from ovo.app.components.project_components import edit_project_dialog, project_stats_fragment
from ovo.app.pages import import_export_page
from ovo.app.utils.page_init import initialize_page

initialize_page(f"{st.session_state.project.name} - Project" if st.session_state.get("project") else "Project")

project = st.session_state.project

# Add Settings button in top right corner

with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
    st.title(f"💼 {project.name}")
    if st.button(":material/settings: Project settings"):
        edit_project_dialog(project_id=project.id)

st.write(
    f"Created {humanize.naturaldate(project.created_date_utc)} by {project.author}"
    + (" | Public" if project.public else " | Private")
)

if get_username() in config.auth.admin_users:
    st.write(f"Storage path: `{storage.get_project_path(project.id, absolute=True)}`")

with st.container(horizontal=True):
    if st.button(import_export_page.title):
        st.switch_page(import_export_page)

if project.description:
    st.write(project.description)
else:
    st.write("*No project description added.*")

if st.button(":material/edit: " + ("Edit description" if project.description else "Add description")):
    edit_project_dialog(project_id=project.id)

project_stats_fragment(project.id)

st.markdown("#### Project attachments")

add_project_attachments(project)

list_project_attachments(project)
