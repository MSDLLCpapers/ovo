import importlib
import os

import pandas as pd
import streamlit as st
import base64

from ovo.app.components.custom_elements import highlight_query
from ovo.app.pages import workflow_page_tuples
from ovo.app.utils.page_init import initialize_page
from ovo.core.logic.user_settings_logic import get_or_create_user_settings, set_user_setting
from ovo.core.plugins import WorkflowPage


def main():
    user_settings = get_or_create_user_settings()
    st.html(
        """
        <style type="text/css">
        /* style only child buttons */
        .stMain button[kind="pills"]:only-child {
            border-color: transparent !important;
            color: #888888 !important;
        }
        </style>
        """
    )
    left, right = st.columns([0.4, 0.6])
    with left:
        st.title("▶️ Workflows")
        with st.container(horizontal=True):
            if st.session_state.get("clear_search"):
                st.session_state["quick_search"] = ""
                st.session_state.pop("clear_search")
            quick_search = st.text_input(
                "Filter",
                placeholder="Search...",
                icon=":material/search:",
                label_visibility="collapsed",
                width=320,
                key="quick_search",
            ).strip()
            if quick_search:
                if st.button(":material/close:", key="clear_search"):
                    st.session_state["clear_search"] = True
                    st.rerun()

    with right:
        with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="right"):
            st.caption("Filter by label", text_alignment="right", width=80)
            all_labels = (
                pd.Series(label for workflow_page, _ in workflow_page_tuples for label in workflow_page.labels)
                .value_counts()
                .index
            )
            filter_label = st.pills(
                "Labels",
                options=all_labels,
                label_visibility="collapsed",
            )

    filtered_workflow_page_tuples = []
    # primary hits
    for workflow_page, st_page in workflow_page_tuples:
        if filter_label and not filter_label in workflow_page.labels:
            continue
        fields = (workflow_page.title.lower(), (" ".join(workflow_page.labels)).lower())
        if any(quick_search.lower() in field for field in fields):
            filtered_workflow_page_tuples.append((workflow_page, st_page))
    # secondary hits
    for workflow_page, st_page in workflow_page_tuples:
        if (workflow_page, st_page) in filtered_workflow_page_tuples:
            continue
        if filter_label and not filter_label in workflow_page.labels:
            continue
        fields = (workflow_page.short_description.lower() if workflow_page.short_description else "",)
        if any(quick_search.lower() in field for field in fields):
            filtered_workflow_page_tuples.append((workflow_page, st_page))

    if not filtered_workflow_page_tuples:
        if filter_label and quick_search:
            st.write(f"No workflows found with label **{filter_label}** and matching query **{quick_search}**")
        elif filter_label:
            st.write(f"No workflows found with label **{filter_label}**")
        else:
            st.write(f"No workflows found matching query **{quick_search}**")
        st.stop()

    filtered_pages_by_path = {
        workflow_page.path: (workflow_page, st_page) for workflow_page, st_page in filtered_workflow_page_tuples
    }
    pinned_paths = user_settings.props.get("ovo.pinned_workflow_pages", [])
    pinned_pages = [filtered_pages_by_path[path] for path in pinned_paths if path in filtered_pages_by_path]

    left, right = st.columns([0.38, 0.62], gap="medium")

    with left:
        st.subheader("Search results" if quick_search or filter_label else "All workflows")

        if pinned_pages:
            st.caption("Pinned workflows")
            for workflow_page, st_page in pinned_pages:
                workflow_link(workflow_page, st_page, user_settings, "recent_list")

        unique_categories = pd.Series(
            workflow_page.category for workflow_page, _ in filtered_workflow_page_tuples
        ).unique()
        for category in unique_categories:
            st.caption(category)
            for workflow_page, st_page in filtered_workflow_page_tuples:
                if workflow_page.category != category:
                    continue
                workflow_link(workflow_page, st_page, user_settings, "all_list")

    with right:
        st.subheader("Workflow cards")

        for workflow_page, st_page in sorted(
            filtered_workflow_page_tuples, key=lambda x: x[0].path not in pinned_paths
        ):
            workflow_card(workflow_page, st_page, user_settings, quick_search=quick_search, filter_label=filter_label)


def pin_button(workflow_page: WorkflowPage, st_page, user_settings, key_suffix: str):
    pinned_workflow_pages = user_settings.props.get("ovo.pinned_workflow_pages", [])
    saved_pin_state = workflow_page.path in pinned_workflow_pages
    new_pin_state = (
        st.pills(
            "Pin",
            options=[":material/keep:"],
            default=":material/keep:" if saved_pin_state else None,
            label_visibility="collapsed",
            key=f"pin_{st_page.url_path}_{saved_pin_state}_{key_suffix}",
        )
        is not None
    )
    if saved_pin_state != new_pin_state:
        if new_pin_state:
            if workflow_page.path not in pinned_workflow_pages:
                pinned_workflow_pages = [workflow_page.path] + pinned_workflow_pages
        else:
            if workflow_page.path in pinned_workflow_pages:
                pinned_workflow_pages.remove(workflow_page.path)
        set_user_setting("ovo.pinned_workflow_pages", pinned_workflow_pages)
        st.session_state["pinned_workflow_pages"] = pinned_workflow_pages
        st.rerun()


def workflow_link(workflow_page: WorkflowPage, st_page, user_settings, key_suffix):
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.page_link(st_page)
        pin_button(workflow_page, st_page, user_settings, key_suffix)


@st.fragment
def workflow_card(
    workflow_page: WorkflowPage, st_page, user_settings, quick_search: str = None, filter_label: str = None
):
    with st.container(border=True):
        with st.container(horizontal=True, horizontal_alignment="distribute"):
            st.markdown(f"#### {workflow_page.title}")
            pin_button(workflow_page, st_page, user_settings, "card")

        if workflow_page.labels:
            labels = []
            for label in workflow_page.labels:
                if filter_label == label or (quick_search and quick_search.lower() in label.lower()):
                    labels.append(f":primary-badge[{label}]")
                else:
                    labels.append(f":grey-badge[{label}]")
            st.markdown(" ".join(labels))
        with st.container(horizontal=True):
            if workflow_page.thumbnail:
                encoded_image = get_thumbnail_image(workflow_page.module_name, workflow_page.thumbnail)
                st.markdown(
                    f'<img src="{encoded_image}" width="200" height="200" style="margin-bottom: 10px;" />',
                    unsafe_allow_html=True,
                    width=200,
                )
            with st.container():
                if workflow_page.short_description:
                    short_description = workflow_page.short_description
                    if quick_search:
                        # wrap matching terms in short description with **highlight**
                        short_description = highlight_query(short_description, quick_search)
                    st.markdown(short_description)

                with st.container(horizontal=True, horizontal_alignment="right"):
                    if st.button("Select workflow", key=f"view_{st_page.url_path}"):
                        st.switch_page(st_page)


def get_thumbnail_image(module_name: str, thumbnail_str: str):
    assert isinstance(thumbnail_str, str), (
        f"Expected thumbnail path as string, got {type(thumbnail_str).__name__}: {thumbnail_str}"
    )
    if thumbnail_str.startswith("http://") or thumbnail_str.startswith("https://"):
        raise ValueError(f"External URLs not allowed for thumbnails, got: {thumbnail_str}")
    module = importlib.import_module(module_name)
    module_path = os.path.dirname(module.__file__)
    thumbnail_path = os.path.join(module_path, thumbnail_str)
    if not os.path.isfile(thumbnail_path):
        raise FileNotFoundError(f"Thumbnail file not found: {thumbnail_path}")
    # base64 encode the image to embed it in markdown
    with open(thumbnail_path, "rb") as f:
        encoded_image = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    return encoded_image


if __name__ == "__main__":
    initialize_page("Workflows")

    main()
