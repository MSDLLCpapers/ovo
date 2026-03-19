import streamlit as st
import os

ASSETS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "assets")


@st.dialog("Welcome to OVO!")
def show_login_dialog(token: str = None):
    st.write("This OVO server requires login")
    if token:
        # Token-based login flow
        if st.query_params.get("login_token") == token:
            # Auto-login via URL param
            st.session_state.login_token = token
            st.rerun()
        # Manual token entry
        with st.form(border=False, key="login"):
            st.write("Please enter the login token to continue")
            token_input = st.text_input("Login Token", width="stretch")
            if st.form_submit_button("Continue", width="stretch", type="primary"):
                if token_input == token:
                    st.session_state.login_token = token
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid token, please try again.")
                    st.stop()
    else:
        # Streamlit login flow
        if st.button("Continue", width="stretch"):
            st.login()


def initialize_page(page_title=None):
    if st.session_state.get("project"):
        page_title += f" - {st.session_state.project.name}"
    st.set_page_config(
        layout="wide",
        page_title=page_title if "OVO" in page_title else page_title + " - OVO",
        page_icon=os.path.join(ASSETS_PATH, "ovo-favicons32x32.png"),
    )

    from ovo.app.components.sidebar import project_sidebar_component

    if st.session_state.get("flash_success"):
        st.success(st.session_state.pop("flash_success"))

    with st.spinner("Setting things up for you..."):
        if "workflows" not in st.session_state:
            st.session_state.workflows = {}

        if "initial_workflows" not in st.session_state:
            st.session_state.initial_workflows = {}

        if "pool_inputs" not in st.session_state:
            st.session_state.pool_inputs = {}

        if "flash_project" not in st.session_state:
            st.session_state.flash_project = None

        if "project" not in st.session_state:
            st.session_state.project = None  # filled in project_sidebar() below

        if "selection_history" not in st.session_state:
            st.session_state["selection_history"] = {}

        if "user_df" not in st.session_state:
            st.session_state["user_df"] = None
        if "clustering_tool_instances" not in st.session_state:
            st.session_state.clustering_tool_instances = []

        # Select project
        project_sidebar_component()
