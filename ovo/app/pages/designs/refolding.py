import streamlit as st

from ovo import db, schedulers, Design
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.download_component import download_descriptor_table
from ovo.app.components.submission_components import scheduler_selectbox
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design_ids,
    get_cached_available_descriptors,
    get_cached_num_cyclic,
    get_cached_wide_descriptor_table,
)
from ovo.core.database import Pool, DesignJob
from ovo.core.database.descriptors_refolding import REFOLDING_DESCRIPTORS
from ovo.app.pages.designs.explorer import design_visualization_fragment
from ovo.core.database.models_refolding import (
    REFOLDING_TESTS_BY_TYPE,
    RefoldingSupportedDesignWorkflow,
    RefoldingWorkflow,
)
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow


@st.fragment
def refolding_fragment(pool_ids: list[str], design_ids: list[str] | None = None, max_preview_designs: int = 500):
    pools = get_cached_pools(pool_ids)

    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = get_cached_design_ids(pool_ids=pool_ids, accepted=True)
        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". All generated designs can be explored in the **Jobs** page."
            )
            return
    else:
        if not design_ids:
            # Empty list explicitly passed to design_ids
            st.write("No designs selected")
            return

    st.header(f"🔁 Refolding | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    if st.button(
        "Submit Refolding",
        type="primary",
        key="submit_refolding_btn",
    ):
        submit_refolding_dialog(design_ids)

    refresh_descriptors(
        design_ids=design_ids,
        workflow_names=[RefoldingWorkflow.name],
    )

    st.subheader("Results")

    available_descriptor_keys = set(get_cached_available_descriptors(design_ids))
    descriptors = [d for d in REFOLDING_DESCRIPTORS if d.key in available_descriptor_keys]

    if not descriptors:
        st.write("No results yet")
        return

    descriptors_df = get_cached_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=[d.key for d in descriptors], nested=True
    )

    if len(design_ids) > max_preview_designs:
        # Filter the displayed table rows for UI performance
        # NOTE that we are not filtering the ids passed to get_cached_wide_descriptor_table since
        # we don't know if all descriptors are available for all designs, so filtering too early could result in an empty table.
        # This would need to be solved by adding a limit to get_wide_descriptor_table itself.
        descriptors_df = descriptors_df[:max_preview_designs]
        st.warning(
            f"Showing only first {max_preview_designs}/{len(design_ids)} designs in the table. "
            f"Download the full table below to see all results."
        )

    descriptor_table(design_ids, descriptors_df, descriptors)

    download_descriptor_table(
        f"Refolding_test_{'_'.join(pool_ids)}_{len(design_ids)}_designs",
        design_ids,
        descriptor_keys=[d.key for d in descriptors],
    )

    st.subheader("Designs")
    design_visualization_fragment(design_ids)


@st.fragment
@st.dialog("Refolding submission", width="medium")
def submit_refolding_dialog(design_ids: list[str]):
    # Get actual pool ids from the selected designs
    pool_ids = sorted(set(Design.design_id_to_pool_id(design_id) for design_id in design_ids))
    # Create "empty" element to enable clearing the contents after submitting
    content = st.empty()
    with content.container():
        num_designs = len(design_ids)

        pools = get_cached_pools(pool_ids)
        design_workflows_by_job_id = db.select_dict(
            DesignJob, "id", "workflow", id__in=[p.design_job_id for p in pools if p.design_job_id]
        )
        design_workflows_by_pool_id = {
            p.id: design_workflows_by_job_id[p.design_job_id] for p in pools if p.design_job_id
        }
        if any(not p.design_job_id for p in pools):
            st.warning(
                """
                Running refolding on custom PDB files requires:
                
                - Designed chain should be chain A
                - The uploaded structure should be the designed structure, not a predicted structure, 
                  since the goal of the refolding workflow is to compare the design to the prediction.
                - In case of AlphaFold2 evaluation of scaffold designs, the PDB file needs to be standardized in OVO format, 
                  containing a REMARK header with the contig string

                More advanced support for custom files will be implemented in the future.
                """
            )
            if not st.checkbox("Acknowledge"):
                return
            design_type = st.selectbox("Select design type", options=REFOLDING_TESTS_BY_TYPE.keys(), key="design_type")
            if not design_type:
                return
        else:
            design_type = None
            for pool in pools:
                design_workflow = design_workflows_by_pool_id[pool.id]
                if not isinstance(design_workflow, RefoldingSupportedDesignWorkflow):
                    st.error(
                        f"Design workflow '{design_workflow.name}' for pool '{pool.name}' does not support refolding evaluation."
                    )
                    return
                workflow_design_type = design_workflow.get_refolding_design_type()
                if design_type is None:
                    design_type = workflow_design_type
                elif design_type != workflow_design_type:
                    st.error(
                        "Selected pools contain different design types "
                        f"('{design_type}' and '{workflow_design_type}'). Please select pools with the same design type."
                    )
                    return

        st.write(f"Select one or more refolding tests supported for **{design_type}** design:")

        tests = []
        for test, (label, description) in REFOLDING_TESTS_BY_TYPE[design_type].items():
            if st.checkbox(f"**{label}** {description}", key=test):
                tests.append(test)

        num_cyclic = get_cached_num_cyclic(design_ids)
        if num_cyclic:
            if num_cyclic != len(design_ids):
                st.error(
                    "Cannot submit cyclic and non-cyclic designs together "
                    f"({num_cyclic}/{len(design_ids)} designs are cyclic in this selection)"
                )
                return
            st.write(":material/info: Workflow will predict macrocyclic designs")

        workflows = RefoldingWorkflow.from_designs(
            pool_ids=pool_ids,
            design_ids=design_ids,
            tests=tests,
            design_type=design_type,
            cyclic=bool(num_cyclic),
        )

        scheduler_key = scheduler_selectbox(workflows)

        submit = st.button("Submit", disabled=not tests, type="primary")

    if submit:
        content.empty()
        if not tests:
            st.warning("Please select at least one test.")
            return

        # collect designs by their native PDB path (each workflow job only supports a single native structure)
        st.write("Preparing workflow inputs...")
        for workflow in workflows:
            submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
        st.rerun()
