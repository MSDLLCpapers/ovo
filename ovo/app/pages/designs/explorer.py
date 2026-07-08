import itertools

import streamlit as st

from ovo import db
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.descriptor_scatterplot import (
    descriptor_scatterplot_component,
    descriptor_scatterplot_input_component,
)
from ovo.app.components.navigation import design_navigation_selector, get_jobs_url
from ovo.app.utils.cached_db import (
    get_cached_design,
    get_cached_pool,
    get_cached_design_job,
    get_cached_wide_descriptor_table,
)
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.database.models import Design, DesignWorkflow, UnknownWorkflow
from ovo.app.utils.cached_db import get_cached_pools, get_cached_design_jobs
from ovo.app.components.design_labeling import design_labeling_fragment
import traceback


def explorer_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    pools = get_cached_pools(pool_ids)

    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = sorted(db.select_values(Design, "id", pool_id__in=pool_ids, accepted=True))

        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". All generated designs can be explored in the **Jobs** page."
            )
            return

    elif not design_ids:
        # Empty list explicitly passed to design_ids
        st.write("No designs selected")
        return

    st.header(f"Explorer | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    badges = [f":grey-badge[{pool.name}]" for pool in pools]
    st.write("Selected pools: " + " ".join(badges))

    refresh_descriptors(
        design_ids=design_ids,
    )

    scatterplot_settings = descriptor_scatterplot_input_component(design_ids)
    if not scatterplot_settings:
        st.write("No descriptors available for the selected designs.")
        st.stop()

    selected_design_ids = descriptor_scatterplot_component(settings=scatterplot_settings, design_ids=design_ids)

    if len(selected_design_ids) > 1:
        design_labeling_fragment(selected_design_ids, key_suffix="explorer_bulk")

    st.subheader("Descriptors")

    design_jobs = get_cached_design_jobs(design_job_ids=[p.design_job_id for p in pools if p.design_job_id])
    # get unique descriptor keys in original order from all design jobs' workflows
    descriptor_keys = list(
        dict.fromkeys(
            itertools.chain(
                scatterplot_settings.get_keys(),
                (k for job in design_jobs for k in job.workflow.get_relevant_descriptor_keys()),
            )
        )
    )

    if not descriptor_keys:
        st.warning(
            "No descriptors selected. Select X and Y descriptors above, or download the full descriptor table below."
        )
    else:
        st.caption(
            "Showing selected X and Y descriptors plus descriptors most relevant to the workflow. "
            "Use the download button below to get a table with all descriptors."
        )

        df = get_cached_wide_descriptor_table(
            pool_ids=pool_ids,
            design_ids=selected_design_ids,
            descriptor_keys=descriptor_keys,
            human_readable=True,
            nested=True,
        )

        descriptor_table(selected_design_ids, df, [ALL_DESCRIPTORS_BY_KEY[k] for k in descriptor_keys], height=300)

    st.subheader(f"Download {len(selected_design_ids):,} " + ("design" if len(selected_design_ids) == 1 else "designs"))
    download_job_designs_component(selected_design_ids, pools)

    st.subheader("Designs")
    design_visualization_fragment(selected_design_ids)


@st.fragment
def design_visualization_fragment(selected_design_ids: list[str]):
    # Use the navigation selector component
    design_id = design_navigation_selector(selected_design_ids, key="selected_design")

    design_labeling_fragment(design_id, key_suffix=f"explorer_{design_id}")

    design = get_cached_design(design_id)
    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id) if pool.design_job_id else None
    WorkflowType = type(design_job.workflow) if design_job and design_job.workflow else DesignWorkflow

    if design_job and design_job.workflow.is_instance(UnknownWorkflow):
        st.warning(
            f"Falling back to basic structure and sequence visualization, "
            f"failed to load workflow information: {design_job.workflow.error}"
        )

    st.markdown(
        f'**Pool:** {pool.name} <a href="{get_jobs_url(st.session_state.project.id, pool.id)}">↑ Show job</a>',
        unsafe_allow_html=True,
    )
    if pool.description:
        st.write(f"**Pool description:** {pool.description}")

    try:
        WorkflowType.visualize_single_design_structures(design_id)
    except Exception as e:
        traceback.print_exc()
        st.error(e)

    st.markdown("### Sequence")

    WorkflowType.visualize_single_design_sequences(design_id)

    st.markdown(f"### Download single design: {design_id}")

    download_job_designs_component(design_ids=[design_id], pools=[pool], key="single")
