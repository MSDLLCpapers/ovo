import streamlit as st

from ovo import db, config
from ovo.app.components.navigation import project_round_selector, pool_selector_table
from ovo.app.utils.page_init import initialize_page
from ovo.app.components.create_new_pool import create_new_pool
from ovo.core.database import Design
from ovo.core.plugins import load_variable, plugin_design_views
from ovo.app.utils.cached_db import get_cached_pools_table, get_cached_rounds

initialize_page(page_title="Designs")

st.title("🐣 Designs")
project = st.session_state.project

st.write(f"Showing all design pools in project **{project.name}**")

rounds = get_cached_rounds(project_id=project.id)
rounds_by_id = {r.id: r for r in rounds}
if not rounds:
    st.write("*No designs available in this project. Upload a pool or submit a workflow in the left panel.*")
    if st.button(":material/upload: Upload designs", key="empty_upload"):
        create_new_pool()
    st.stop()


selected_round_ids, selected_design_ids = project_round_selector(rounds, allow_design_input=True)

if selected_design_ids is not None:
    selected_pool_ids = sorted(db.select_unique_values(Design, "pool_id", id__in=selected_design_ids))
else:
    st.subheader("Pools")

    if st.button(
        ":material/upload: Upload designs",
        disabled=config.props.read_only,
        help="Ovo is running in read-only mode, design upload is disabled" if config.props.read_only else None,
    ):
        create_new_pool()

    with st.spinner("Loading pools..."):
        pools_table = get_cached_pools_table(round_ids=selected_round_ids)

        if pools_table.empty:
            st.write("No pools created yet in this round")
            st.stop()

    selected_pool_ids = pool_selector_table(pools_table, st.session_state.project.id)

views = {
    "🔵 Explorer": "ovo.app.pages.designs.explorer:explorer_fragment",
    "🔎 ProteinQC": "ovo.app.pages.designs.proteinqc:proteinqc_fragment",
    "🎯 Interface analyzer": "ovo.app.pages.designs.interface:interface_fragment",
    "🔁 Refolding": "ovo.app.pages.designs.refolding:refolding_fragment",
    "🫧 Clustering": "ovo.app.pages.designs.clustering:clustering_fragment",
    # "🧬 Structure prediction": "TODO",
    # "🧩 Plugins": "TODO",
}

# Update functions with
views.update(plugin_design_views)

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
