import streamlit as st

from ovo import db
from ovo.app.components.custom_elements import confirm_download_button
from ovo.app.components.descriptor_explorer import descriptor_explorer
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.descriptor_tiles import descriptor_overview_tiles
from ovo.app.components.navigation import design_navigation_selector
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design_ids,
    get_cached_available_descriptors,
)
from ovo.app.utils.protein_qc_plots import source_selectbox
from ovo.core.database import Pool, Design, NumericGlobalDescriptor
from ovo.core.database.descriptors_proteinqc import PROTEINQC_MAIN_DESCRIPTORS
from ovo.core.database.models_proteinqc import ProteinQCWorkflow, PROTEINQC_TOOLS
from ovo.core.logic.descriptor_logic import (
    submit_descriptor_workflow,
    get_wide_descriptor_table,
    export_proteinqc_excel,
)
from ovo.core.logic.proteinqc_logic import get_available_schedulers


@st.fragment
def proteinqc_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = get_cached_design_ids(pool_ids=pool_ids, accepted=True)
        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". Please mark some designs as accepted in the **Jobs** page."
            )
            return
    else:
        if not design_ids:
            # Empty list explicitly passed to design_ids
            st.write("No designs selected")
            return

    st.header(f"🔎 ProteinQC | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    if st.button(
        "Submit ProteinQC",
        type="primary",
        key="submit_full_proteinqc_btn",
        help="Submit full ProteinQC for all designs",
    ):
        submit_proteinqc_dialog(pool_ids, design_ids)

    refresh_descriptors(
        design_ids=design_ids,
        workflow_names=[ProteinQCWorkflow.name],
    )

    st.subheader("Descriptors table")
    descriptors_by_key = get_cached_available_descriptors(design_ids)
    numeric_descriptors_by_key = {
        d_key: d for d_key, d in descriptors_by_key.items() if type(d) is NumericGlobalDescriptor
    }
    descriptors_df = get_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=descriptors_by_key.keys(), nested=True
    )

    descriptors = [d for d in PROTEINQC_MAIN_DESCRIPTORS if d.key in descriptors_by_key]

    descriptor_table(design_ids, descriptors_df, descriptors)

    if st.button("Download ProteinQC table", key="prepare_proteinqc"):
        with st.spinner("Preparing descriptor table..."):
            excel_bytes = export_proteinqc_excel(design_ids)
        confirm_download_button(
            data=excel_bytes.getvalue(),
            file_name=f"ProteinQC_{'_'.join(pool_ids)}_{len(design_ids)}_designs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_proteinqc",
        )

    st.subheader("Results")

    # TODO rank by number of flags, pass fmt to navigation selector
    ranked_ids = descriptors_df.index.tolist()
    left, right = st.columns([3, 1], vertical_alignment="bottom")
    with left:
        design_id = design_navigation_selector(ranked_ids, allow_all=True)
    with right:
        histogram_source = source_selectbox(st.query_params.get("ref"), key_prefix="proteinqc_reference")
        st.query_params["ref"] = histogram_source
    descriptor_overview_tiles(
        descriptors_df, descriptors_by_key, design_id=design_id, histogram_source=histogram_source
    )

    st.subheader("Descriptor explorer")
    descriptor_explorer(descriptors_df, numeric_descriptors_by_key, single_design=False)


@st.fragment
@st.dialog("ProteinQC submission", width="large")
def submit_proteinqc_dialog(pool_ids: list[str], design_ids: list[str]):
    num_designs = len(design_ids)
    st.write(f"""Submit ProteinQC for {num_designs:,} {"design" if num_designs == 1 else "designs"}""")
    tools = st.multiselect(
        "Select ProteinQC tools",
        options=PROTEINQC_TOOLS,
        default=PROTEINQC_TOOLS,
        format_func=lambda x: x.name,
        key="proteinqc_tools_selectbox",
    )
    tool_keys = [tool.tool_key for tool in tools]
    chains = st.text_input(
        "Chain(s) to analyze",
        value="A",
        key="proteinqc_chains_input",
    )
    chains = chains.replace(" ", "").replace(",", "")

    schedulers = get_available_schedulers(tools)

    if not schedulers:
        st.warning("No schedulers available for the selected tools.")
        return

    scheduler_key = st.selectbox(
        "Scheduler",
        options=list(schedulers.keys()),
        format_func=lambda x: schedulers[x].name,
        key="proteinqc_scheduler_selectbox",
    )

    if st.button("Submit", key="submit_proteinqc_btn", type="primary"):
        st.write("Submitting job... 🚀")

        workflow = ProteinQCWorkflow(tools=tool_keys, chains=list(chains), design_ids=design_ids)
        submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
        st.rerun()
