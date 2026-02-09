import streamlit as st

from ovo import schedulers
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.download_component import download_descriptor_table
from ovo.app.utils.cached_db import get_cached_design_ids, get_cached_available_descriptors
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow, get_wide_descriptor_table
from __MODULE_NAME__.models___MODULE_SUFFIX__ import __WORKFLOW_CLASS_NAME__
from __MODULE_NAME__ import descriptors___MODULE_SUFFIX__


@st.fragment
def __MODULE_NAME___fragment(pool_ids: list[str], design_ids: list[str] | None = None):
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
    elif not design_ids:
        # Empty list explicitly passed to design_ids
        st.write("No designs selected")
        return

    st.header(f"💥 My Method | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    st.write("This is a template for a custom descriptor workflow. You can modify this code to create your own view.")

    if st.button(
        "Submit My Method",
        type="primary",
        key="submit_btn",
    ):
        __MODULE_NAME___submit_dialog(design_ids=design_ids)

    refresh_descriptors(
        design_ids=design_ids,
        workflow_names=[__WORKFLOW_CLASS_NAME__.name],
    )

    st.subheader("Results")

    available_descriptor_keys = set(get_cached_available_descriptors(design_ids))
    descriptors = [d for d in descriptors___MODULE_SUFFIX__.DESCRIPTORS if d.key in available_descriptor_keys]

    if not descriptors:
        st.write("No results yet")
        return

    descriptors_df = get_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=[d.key for d in descriptors], nested=True
    )

    descriptor_table(design_ids, descriptors_df, descriptors)

    download_descriptor_table(
        f"__MODULE_SUFFIX___{'_'.join(pool_ids[:5])}_{len(design_ids)}_designs",
        design_ids,
        descriptor_keys=[d.key for d in descriptors],
    )


@st.fragment
@st.dialog("Submit", width="large")
def __MODULE_NAME___submit_dialog(design_ids: list[str]):
    content = st.empty()
    with content.container():
        chains = st.text_input(
            "Chain(s) to analyze",
            value="A",
            key="chains_input",
        )
        chains = chains.replace(" ", "").replace(",", "")

        params = {}

        scheduler_key = st.selectbox(
            "Scheduler",
            options=list(schedulers.keys()),
            format_func=lambda x: schedulers[x].name,
            key="submit_scheduler",
        )
        with st.columns(2)[-1]:
            submit = st.button("Submit", key="confirm_btn", type="primary", width="stretch")

    if submit:
        content.empty()
        st.write(f"Submitting job... 🚀")
        workflow = __WORKFLOW_CLASS_NAME__(chains=list(chains), design_ids=design_ids, params=params)
        submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
        st.rerun()
