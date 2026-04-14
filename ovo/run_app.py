#
# Run everything including imports only in __main__ block
# This is done to avoid subprocesses initializing streamlit
#
import os

from ovo.app.utils.page_init import show_login_dialog
from ovo.core.logic.user_settings_logic import get_or_create_user_settings

ASSETS_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app", "assets")

CSS = None


def read_css():
    """Cache CSS contents to speed up page load"""
    global CSS
    if CSS is None:
        with open(os.path.join(ASSETS_PATH, "styles.css"), "r") as f:
            CSS = f.read()
    return CSS


if __name__ == "__main__":
    import streamlit as st
    from ovo import config
    from ovo.app.pages import get_pages, workflow_page_tuples

    st.markdown(f"<style>{read_css()}</style>", unsafe_allow_html=True)

    # Create navigation manually for selected pages
    main_pages, hidden_pages = get_pages()
    for group, group_pages in main_pages.items():
        for page in group_pages:
            st.sidebar.page_link(page)

    if config.auth.streamlit_auth:
        if not st.user.get("is_logged_in"):
            show_login_dialog()
            st.stop()

    if "pinned_workflow_pages" not in st.session_state:
        user_settings = get_or_create_user_settings()
        st.session_state["pinned_workflow_pages"] = user_settings.props.get("ovo.pinned_workflow_pages", [])
    pages_by_path = {workflow_page.path: (workflow_page, st_page) for workflow_page, st_page in workflow_page_tuples}
    pinned_pages = [pages_by_path[path] for path in st.session_state["pinned_workflow_pages"] if path in pages_by_path]
    if pinned_pages:
        st.sidebar.caption("Pinned workflows")
        for _, st_page in pinned_pages[:5]:
            st.sidebar.page_link(st_page)

    st.sidebar.divider()

    # HIDDEN navigation (only used to enable programmatic page switching)
    # Actual navigation is created manually above
    pg = st.navigation(
        pages={
            **main_pages,
            **hidden_pages,
            "Workflows": [page for _, page in workflow_page_tuples],
        },
        position="hidden",
    )

    if login_token := os.environ.get("OVO_LOGIN_TOKEN"):
        if st.session_state.get("login_token") != login_token:
            show_login_dialog(token=login_token)
            st.stop()

    pg.run()
