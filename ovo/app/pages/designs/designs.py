import streamlit as st

from ovo import db, config
from ovo.app.components.custom_elements import refresh_button
from ovo.app.components.navigation import project_round_selector, pool_selector_table
from ovo.app.utils.page_init import initialize_page
from ovo.app.utils.testing import is_test_dialog_shown
from ovo.app.components.create_new_pool import create_new_pool
from ovo.core.database import Design
from ovo.core.plugins import load_variable, get_extension_points, DesignView
from ovo.app.utils.cached_db import (
    get_cached_pools_table,
    get_cached_rounds,
    get_cached_available_labels_for_design_ids,
    get_cached_design_ids,
    get_cached_design_ids_with_labels,
    get_cached_available_labels_for_pool_ids,
)

initialize_page(page_title="Designs")

st.title("🐣 Designs")
project = st.session_state.project

st.write(f"Showing all design pools in project **{project.name}**")

rounds = get_cached_rounds(project_id=project.id)
rounds_by_id = {r.id: r for r in rounds}
if not rounds:
    st.write("*No designs available in this project. Upload a pool or submit a workflow in the left panel.*")
    if st.button(":material/upload: Upload designs", key="empty_upload") or is_test_dialog_shown("create_new_pool"):
        create_new_pool()
    st.stop()


selected_round_ids, selected_design_ids = project_round_selector(rounds, allow_design_input=True)

clear_cache = False
if selected_design_ids is not None:
    selected_pool_ids = sorted(db.select_unique_values(Design, "pool_id", id__in=selected_design_ids))
else:
    st.subheader("Pools")

    with st.container(horizontal=True):
        if st.button(
            ":material/upload: Upload designs",
            disabled=config.props.read_only,
            help="Ovo is running in read-only mode, design upload is disabled" if config.props.read_only else None,
        ) or is_test_dialog_shown("create_new_pool"):
            create_new_pool()
        if refresh_button("refresh_pools"):
            clear_cache = True

    with st.spinner("Loading pools..."):
        pools_table = get_cached_pools_table(round_ids=selected_round_ids)

        if pools_table.empty:
            st.write("No pools created yet in this round")
            st.stop()

    selected_pool_ids = pool_selector_table(pools_table, st.session_state.project.id)

# Label filtering
# Get relevant labels based on current context
if selected_design_ids is not None:
    # If design IDs are explicitly provided, get labels for those designs
    if clear_cache:
        get_cached_available_labels_for_design_ids.clear(selected_design_ids)
    relevant_labels = get_cached_available_labels_for_design_ids(selected_design_ids)
else:
    if clear_cache:
        get_cached_available_labels_for_pool_ids.clear(selected_pool_ids, accepted=True)
    relevant_labels = get_cached_available_labels_for_pool_ids(selected_pool_ids, accepted=True)

# Display labels that are relevant to the currently selected designs/pools/rounds
if relevant_labels:
    with st.container(horizontal=True, vertical_alignment="center"):
        st.write("Filter by labels:")
        selected_labels = st.pills(
            "Select labels",
            options=relevant_labels,
            key="labels",
            selection_mode="multi",
            label_visibility="collapsed",
            bind="query-params",
        )

        union = False
        if len(selected_labels) > 1:
            st.write(":grey[Filter mode:]")
            union = (
                st.segmented_control(
                    label="Combine",
                    options=["Intersection", "Union"],
                    key="label_combine_mode",
                    label_visibility="collapsed",
                    default="Intersection",
                    bind="query-params",
                    help="Intersection selects designs that have all selected labels, Union selects designs with at least one of the selected label",
                )
                == "Union"
            )

    # Apply label filtering to design_ids
    if selected_labels:
        if selected_design_ids is None:
            selected_design_ids = get_cached_design_ids(selected_pool_ids)
        # Filter existing selected_design_ids
        args = (selected_labels, selected_design_ids, union)
        if clear_cache:
            get_cached_design_ids_with_labels.clear(*args)
        selected_design_ids = get_cached_design_ids_with_labels(*args)

    # Show filtering results
    if selected_labels:
        formatted_labels = [f":grey-background[&nbsp;{label}&nbsp;]" for label in selected_labels]
        sep = " :grey[ &nbsp;or&nbsp; ] " if union else " :grey[ &nbsp;and&nbsp; ] "
        if selected_design_ids:
            st.write(
                f":grey[Showing {len(selected_design_ids)} designs "
                f"with {'label' if len(selected_labels) == 1 else 'labels'}:]&nbsp; {sep.join(formatted_labels)}"
            )
        else:
            st.write(f":red[No designs found with:]&nbsp; {sep.join(formatted_labels)}")
            st.stop()


views = {
    "🔵 Explorer": "ovo.app.pages.designs.explorer:explorer_fragment",
    "🔎 ProteinQC": "ovo.app.pages.designs.proteinqc:proteinqc_fragment",
    "🎯 Interface analyzer": "ovo.app.pages.designs.interface:interface_fragment",
    "🔁 Refolding": "ovo.app.pages.designs.refolding:refolding_fragment",
    "📉 Regression": "ovo.app.pages.designs.regression:regression_fragment",
    "🫧 Clustering": "ovo.app.pages.designs.clustering:clustering_fragment",
}

# Update functions from plugins
views.update({view.title: view.path for view in get_extension_points("ovo.design_view", DesignView)})

if "design_view" not in st.session_state and "design_view" in st.query_params:
    st.session_state["design_view"] = st.query_params["design_view"]

view = st.segmented_control("Views", options=list(views), key="design_view")

if not view:
    if "design_view" in st.query_params:
        del st.query_params["design_view"]
    st.write(":material/arrow_upward: *Choose one of the view options to see your designs*")
    st.stop()

st.query_params["design_view"] = view

# Load function lazily to avoid importing all plugins when page is loaded
view_path = views[view]
assert isinstance(view_path, str), f"View function should be a string (module.submodule:func_name), got: {view_path}"
view_func = load_variable(view_path)

view_func(selected_pool_ids, design_ids=selected_design_ids)
