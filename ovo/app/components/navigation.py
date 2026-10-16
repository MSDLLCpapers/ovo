from contextlib import nullcontext
from typing import Callable

import pandas as pd
import streamlit as st

from ovo import db
from ovo.core.database import Round, Design, Pool, Project
from ovo.core.utils.formatting import get_hash_of_bytes
from ovo.app.utils.cached_db import get_cached_project_ids_and_names
from ovo.core.auth import get_username

CURRENT_SECTION_PREFIX = "current_section_"
ROUND_IDS_QUERY_PARAM = "rounds"
DESIGN_IDS_QUERY_PARAM = "designs"
# ID of the bulk submission draft to review, see bulk_submission.load_saved_submission
SUBMISSION_QUERY_PARAM = "submission"


def show_prev_next_sections(key: str, title: str, sections: dict[str, callable]):
    session_key = CURRENT_SECTION_PREFIX + key
    current_index = st.session_state.get(session_key, 0)
    section_labels = list(sections.keys())

    top_buttons_container = st.empty()
    with top_buttons_container:
        # Empty spacer for loading state
        st.write("&nbsp;")

    # Section content
    current_section_fragment = list(sections.values())[current_index]
    current_section_fragment()

    # Top buttons with title
    # NOTE: we run this code below the content fragment to avoid ignoring user's last input on next button click
    with top_buttons_container:
        show_buttons(
            session_key,
            current_index,
            section_labels,
            key_suffix="top",
            title=title,
            show_title=True,
            glow=current_index == 0,
        )

    # Bottom buttons
    st.markdown("#")  # Empty spacer
    show_buttons(session_key, current_index, section_labels, key_suffix="bottom")


def open_first_section(key: str):
    open_section(key, 0)


def open_section(key: str, section_index: int):
    """Open the section of the given page at the given index, as if the user had navigated to it."""
    st.session_state[CURRENT_SECTION_PREFIX + key] = section_index


def show_buttons(
    session_key: str,
    current_index: int,
    section_labels: list[str],
    key_suffix: str = "",
    title: str = "",
    show_title: bool = False,
    glow: bool = False,
):
    with st.container(key="navigation_buttons_" + key_suffix):
        left, middle, right = st.columns([6, 1, 2] if current_index == 0 else [2, 3, 2], vertical_alignment="top")
        with left:
            if current_index > 0:
                # Show back button on all but first section
                if st.button(
                    f"Back to {section_labels[current_index - 1]}",
                    icon=":material/arrow_back_ios:",
                    key="back_button_" + key_suffix,
                ):
                    st.session_state[session_key] = st.session_state.get(session_key, 0) - 1
                    st.rerun(scope="app")
            elif show_title:
                # Show title instead of back button on first section
                st.title(title)

        if show_title and 0 < current_index < len(section_labels):
            with middle:
                # Title in the middle when not on first or last section
                st.html(
                    f'<div style="text-align: center; font-size: 23px; font-weight: 600; padding-top: 5px;">'
                    f"{title} ({current_index}/{len(section_labels) - 1})"
                    f"</div>"
                )

        with right:
            with st.container(key="glow" if glow else None, horizontal=True, horizontal_alignment="right"):
                if current_index < len(section_labels) - 1:
                    # Show next button on all but last section
                    if st.button(
                        f"Next to {section_labels[current_index + 1]}",
                        icon=":material/arrow_forward_ios:",
                        key="next_button_" + key_suffix,
                    ):
                        st.session_state[session_key] = st.session_state.get(session_key, 0) + 1
                        st.rerun(scope="app")
                else:
                    # Empty space to align back button to the left
                    st.markdown(" ")

        st.markdown(
            """
        <style>
        .st-key-navigation_buttons_SUFFIX {
            /* Hack to reduce the whitespace at the top of the page */
            margin-top: -20px;
            margin-bottom: 20px;
        }
        .st-key-navigation_buttons_SUFFIX button {
            padding: 10px 25px;
            min-width: 200px;
        }
        </style>
        """.replace("SUFFIX", key_suffix),
            unsafe_allow_html=True,
        )
        if glow:
            # Glow effect for next button (to emphasize you can continue)
            st.markdown(
                """
            <style>
            .st-key-glow button {
                animation: glowfade 2.7s ease-out forwards;
                box-shadow: 0 0 25px rgba(91, 163, 15, 0.5);
            }
            @keyframes glowfade {
                0%   { box-shadow: 0 0 25px rgba(91, 163, 15, 0.5); }
                100% { box-shadow: 0 0 0rem rgba(91, 163, 15, 0.0); }
            }
            </style>
            """,
                unsafe_allow_html=True,
            )


def project_round_selector(
    rounds: list[Round], key_prefix="round_pills", allow_design_input=False
) -> list[str] | tuple[list[str], list[str] | None]:
    rounds_by_id = {r.id: r for r in rounds}
    key_suffix = "_".join(rounds_by_id)
    design_ids_key = f"{key_prefix}_design_ids_{key_suffix}"
    single_key = f"{key_prefix}_single_{key_suffix}"
    multi_key = f"{key_prefix}_multi_{key_suffix}"
    single_default = [rounds[0].id]
    multi_default = rounds_by_id.keys()

    if design_ids_key not in st.session_state:
        # First time loading the page, get design IDs in query arg input
        if st.query_params.get(DESIGN_IDS_QUERY_PARAM) and allow_design_input:
            st.session_state[design_ids_key] = st.query_params[DESIGN_IDS_QUERY_PARAM].replace(",", "\n")
            single_default = ["designs"]

    if single_key not in st.session_state and st.query_params.get(ROUND_IDS_QUERY_PARAM):
        # Page loaded for first time, initialize the defaults
        query_round_ids = st.query_params[ROUND_IDS_QUERY_PARAM].split(",")
        # only use the round ids if they belong to current project (ignore when switching to different project)
        if all(round_id in rounds_by_id for round_id in query_round_ids):
            single_default = "all" if len(query_round_ids) > 1 else query_round_ids[0]
            multi_default = query_round_ids

    options = list(rounds_by_id.keys())
    if len(rounds) > 1:
        options.append("all")
    if allow_design_input:
        options.append("designs")
    round_id = st.segmented_control(
        label="Select round",
        options=options,
        key=single_key,
        selection_mode="single",
        format_func=lambda round_id: "Multiple rounds"
        if round_id == "all"
        else ("Specific designs" if round_id == "designs" else rounds_by_id[round_id].name),
        default=single_default,  # Using the most recent round as default
        label_visibility="collapsed",
    )

    if not round_id:
        st.error("Please select a round above.")
        return ([], None) if allow_design_input else []

    if round_id == "designs":
        design_ids_input = st.text_area(
            "Design IDs",
            placeholder="Paste design IDs here, separated by commas, spaces, or new lines",
            key=design_ids_key,
        )
        input_design_ids = design_ids_input.replace(",", " ").strip().split()
        # validate design IDs
        found_design_ids = set(db.select_values(Design, "id", id__in=input_design_ids))
        if found_design_ids != set(input_design_ids):
            missing_ids = sorted(set(input_design_ids) - found_design_ids)
            st.warning(f"{len(missing_ids):,} design IDs were not found: {', '.join(missing_ids)}")
            if not found_design_ids:
                st.stop()
            st.warning(f"Showing designs for {len(found_design_ids):,} valid design IDs.")
        elif found_design_ids:
            st.success(f"Showing {len(found_design_ids):,} " + ("design" if len(found_design_ids) == 1 else "designs"))
        else:
            return [], []

        # remove duplicates and missing ids while preserving input order
        design_ids = [design_id for design_id in dict.fromkeys(input_design_ids) if design_id in found_design_ids]

        # check if the designs belong to the current project, and warn if not
        pool_ids = set(Design.design_id_to_pool_id(design_id) for design_id in design_ids)
        round_ids = db.select_unique_values(Pool, "round_id", id__in=pool_ids)
        project_ids = sorted(db.select_unique_values(Round, "project_id", id__in=round_ids))
        if len(project_ids) > 1:
            st.info(
                "Showing designs from multiple projects. Any submitted descriptor jobs will be accessible only from the current project."
            )
        elif project_ids[0] != st.session_state.project.id:
            if project_ids[0] not in get_cached_project_ids_and_names(username=get_username()):
                st.error("Designs from this project are not accessible to your account")
                st.stop()
            expected_project = db.get(Project, id=project_ids[0])
            st.warning(f"These designs originate from a different project: {expected_project.name}")
            if st.button(f"Switch to project: {expected_project.name}"):
                st.session_state.project = expected_project
                st.rerun()
            st.stop()

        if len(design_ids) <= 100:
            # Save design IDs to query params but avoid too long URLs
            st.query_params[DESIGN_IDS_QUERY_PARAM] = ",".join(design_ids)
            if ROUND_IDS_QUERY_PARAM in st.query_params:
                del st.query_params[ROUND_IDS_QUERY_PARAM]

        return [], design_ids

    if round_id == "all":
        # Select multiple rounds
        selected_round_ids = st.segmented_control(
            label="Select rounds",
            options=rounds_by_id.keys(),
            key=multi_key,
            selection_mode="multi",
            format_func=lambda round_id: rounds_by_id[round_id].name,
            default=multi_default,
        )

        if not selected_round_ids:
            st.error("No rounds selected. Please select at least one round above.")
            return ([], None) if allow_design_input else []
    else:
        selected_round_ids = [round_id]

    st.query_params[ROUND_IDS_QUERY_PARAM] = ",".join(selected_round_ids)
    if DESIGN_IDS_QUERY_PARAM in st.query_params:
        del st.query_params[DESIGN_IDS_QUERY_PARAM]
    return (selected_round_ids, None) if allow_design_input else selected_round_ids


def get_jobs_url(project_id: str, pool_id: str) -> str:
    return f"./jobs?pool_ids={pool_id}&project_id={project_id}"


def pool_selector_table(pools_table: pd.DataFrame, project_id: str) -> list[str]:
    key = "_".join(pools_table["ID"])

    # Prepare table for data editor
    data_columns = pools_table.columns.tolist()

    # Initialize default selection state
    # We use table contents to define the key
    # TODO we could use {key} instead when Streamlit persists selection across table changes
    # So when table content changes, this will remember the previous selection across reruns.
    # Note that this does not solve saving user's new selection - it still gets discarded
    # because the block below doesn't even return the new selection state because streamlit resets the component.
    # User needs to click twice to select a new item in case they clicked after the table has changed.
    default_selection_key = f"pool_default_selection_{get_hash_of_bytes(pools_table.to_csv().encode())}"
    if default_selection_key in st.session_state:
        # Page is already loaded, use previous default state
        default_selection = st.session_state[default_selection_key]
    else:
        # First page load, initialize selection based on query params
        default_selection = st.query_params.get("pool_ids").split(",") if st.query_params.get("pool_ids") else []
        st.session_state[default_selection_key] = default_selection
    pools_table.insert(0, "Selected", [pool_id in default_selection for pool_id in pools_table["ID"]])
    pools_table["Job ID"] = [
        get_jobs_url(project_id, pool_id) if not pd.isna(job_id) else None
        for pool_id, job_id in pools_table.set_index("ID")["Job ID"].items()
    ]

    edited = st.data_editor(
        pools_table,
        key=f"pools_{key}",
        hide_index=True,
        width="content",
        disabled=data_columns,
        column_config={
            "Selected": "",
            "Job ID": st.column_config.LinkColumn(display_text=r"Job ↑", disabled=True),
        },
    )

    if edited["Selected"].any():
        selected_pools_table = pools_table[edited["Selected"]]
        st.caption(
            f"Showing designs from {len(selected_pools_table)} selected "
            f"{'pool' if len(selected_pools_table) == 1 else 'pools'}."
        )
        st.query_params["pool_ids"] = ",".join(selected_pools_table["ID"].astype(str).tolist())
    else:
        selected_pools_table = pools_table
        st.caption("Showing designs from all pools. Use checkboxes above to select specific pools.")
        if "pool_ids" in st.query_params:
            del st.query_params["pool_ids"]

    selected_pool_ids = list(selected_pools_table["ID"])
    return selected_pool_ids


def previous_design_idx(idx):
    if idx > 0:
        idx -= 1
    return idx


def next_design_idx(idx, n):
    if idx < n:
        idx += 1
    return idx


DEFAULT_SELECTED_DESIGN_KEY = "selected_design"


def design_navigation_selector(
    design_ids: list[str],
    key: str = DEFAULT_SELECTED_DESIGN_KEY,
    fmt: dict[str, str] | Callable | None = None,
    allow_all: bool = False,
    default_all: bool = True,
) -> str | None:
    """
    Display navigation controls (prev/next buttons and dropdown) for browsing designs.
    Updates query params and returns the currently selected design_id.

    Args:
        design_ids: List of design IDs to navigate through
        key: Query parameter key for storing selected design (default: "selected_design")
        fmt: Optional dict or function that maps design IDs to labels for display in the selectbox
        allow_all: If True, allows selecting all designs (returns None)
        default_all: If True and allow_all is True, "All" will be selected by default if there are any design_ids

    Returns:
        str: Currently selected design_id or None if all designs are selected
    """
    if not design_ids:
        return None
    if allow_all and len(design_ids) == 1:
        # simplify case when only one design is available - select the design directly
        allow_all = False
    num_designs = len(design_ids)
    if allow_all:
        design_ids = ["ALL"] + list(design_ids)
    ids_hash = get_hash_of_bytes(",".join(design_ids).encode())
    element_key_prefix = f"{key}_{ids_hash}_selectbox"

    # Try getting current value from session state (we need to find the key based on the prefix)
    idx = None
    prev_element_keys = [k for k in st.session_state if k and k.startswith(element_key_prefix)]
    if prev_element_keys:
        prev_element_key = prev_element_keys[0]
        design_id = st.session_state[prev_element_key]
        if design_id in design_ids:
            idx = design_ids.index(design_id)

    if idx is None:
        if key in st.query_params and st.query_params[key] in design_ids:
            # Get current index from query params
            idx = design_ids.index(st.query_params[key])
        elif allow_all:
            idx = 0 if default_all else 1
        else:
            idx = 0

    with st.container(horizontal=True, gap="small", vertical_alignment="center"):
        prev_button_key = f"previous_design_btn_{key}"
        next_button_key = f"next_design_btn_{key}"

        # Check if prev/next buttons were pressed through session state
        # so that we can set the current value and the button disabled state correctly
        pressed_prev = st.session_state.get(prev_button_key)
        pressed_next = st.session_state.get(next_button_key)
        if pressed_prev:
            idx = previous_design_idx(idx)
        if pressed_next:
            idx = next_design_idx(idx, len(design_ids) - 1)

        st.button(
            ":material/arrow_back_ios:",
            key=f"previous_design_btn_{key}",
            width="content",
            disabled=idx == 0,
        )

        with st.container(width=75, horizontal_alignment="center"):
            curr = "All" if design_ids[idx] == "ALL" else (idx if allow_all else idx + 1)
            st.html(
                f'<div style="text-align: center">{curr} / {num_designs:,}</div>',
            )

        st.button(
            ":material/arrow_forward_ios:",
            key=f"next_design_btn_{key}",
            width="content",
            disabled=idx == len(design_ids) - 1,
        )

        start_idx = 0 if allow_all else 1
        design_indexes = {design_id: i for i, design_id in enumerate(design_ids, start=start_idx)}

        def format_func(design_id):
            if design_id == "ALL":
                return f"All {num_designs:,} designs"
            if fmt:
                label = fmt.get(design_id, "") if isinstance(fmt, dict) else fmt(design_id)
            else:
                label = ""
            return f"{design_indexes[design_id]} | {design_id}" + (f" | {label}" if label else "")

        # force forgetting idx when design_ids change (since the idx doesn't make sense anymore)
        element_key = element_key_prefix + f"_{idx}"

        design_id = st.selectbox(
            "Select a design",
            options=design_ids,
            label_visibility="collapsed",
            key=element_key,  # we add idx to force re-creating the component when idx changes
            index=idx,
            format_func=format_func,
            width="stretch",
        )
        st.query_params[key] = design_id

        if design_id != "ALL":
            url = f"./designs?project_id={st.session_state.project.id}&design={design_id}"
            if design_view := st.query_params.get("design_view"):
                url += f"&design_view={design_view}"
            st.link_button(":material/open_in_new: Detail page", url)

    return None if design_id == "ALL" else design_id
