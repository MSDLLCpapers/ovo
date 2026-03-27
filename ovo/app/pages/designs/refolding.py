from collections import defaultdict

import streamlit as st

from ovo import db, schedulers
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import descriptor_table
from ovo.app.components.download_component import download_descriptor_table
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design_ids,
    get_cached_available_descriptors,
)
from ovo.core.database import Pool, Design, DesignJob
from ovo.core.database.descriptors_refolding import REFOLDING_DESCRIPTORS
from ovo.core.database.models_refolding import (
    REFOLDING_TESTS_BY_TYPE,
    RefoldingSupportedDesignWorkflow,
    RefoldingWorkflow,
)
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow, get_wide_descriptor_table


@st.fragment
def refolding_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    pools = get_cached_pools(pool_ids)

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

    st.header(f"🔁 Refolding | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    if st.button(
        "Submit Refolding",
        type="primary",
        key="submit_refolding_btn",
    ):
        submit_refolding_dialog(pool_ids, design_ids)

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

    descriptors_df = get_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=[d.key for d in descriptors], nested=True
    )
    descriptor_table(design_ids, descriptors_df, descriptors)

    download_descriptor_table(
        f"Refolding_test_{'_'.join(pool_ids)}_{len(design_ids)}_designs",
        design_ids,
        descriptor_keys=[d.key for d in descriptors],
    )


@st.fragment
@st.dialog("Refolding submission", width="medium")
def submit_refolding_dialog(pool_ids: list[str], design_ids: list[str]):
    # Create "empty" element to enable clearing the contents after submitting
    content = st.empty()
    with content.container():
        num_designs = len(design_ids)
        st.write(f"""Submit refolding evaluation for {num_designs:,} {"design" if num_designs == 1 else "designs"}""")

        pools = db.select(Pool, id__in=pool_ids)
        design_workflows_by_pool_id = {
            p.id: db.get(DesignJob, id=p.design_job_id).workflow for p in pools if p.design_job_id
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

        scheduler_key = st.selectbox(
            "Scheduler",
            options=list(schedulers.keys()),
            format_func=lambda x: schedulers[x].name,
            key="scheduler_selectbox",
        )

        submit = st.button("Submit", disabled=not tests, type="primary")

    if submit:
        content.empty()
        if not tests:
            st.warning("Please select at least one test.")
            return

        # collect designs by their native PDB path (each workflow job only supports a single native structure)
        st.write("Preparing workflow inputs...")
        groups = defaultdict(list)
        for pool in pools:
            index_by_id = db.select_dict(Design, "id", "contig_index", id__in=design_ids, pool_id=pool.id)
            if not pool.design_job_id:
                # Assume chain A is designed if no design workflow associated with the pool, and no native structure (e.g. for custom PDB uploads)
                default_designed_chains = ["A"]
                groups[(None, tuple(default_designed_chains))] += list(index_by_id.keys())
                continue
            design_workflow = design_workflows_by_pool_id[pool.id]
            ids_by_index = defaultdict(list)
            for design_id, contig_index in index_by_id.items():
                ids_by_index[contig_index].append(design_id)
            for contig_index, ids in ids_by_index.items():
                native_pdb_path = design_workflow.get_refolding_native_pdb_path(contig_index)
                designed_chains = design_workflow.get_refolding_designed_chains()
                groups[(native_pdb_path, tuple(designed_chains))] += ids

        for (native_pdb_path, designed_chains), group_design_ids in groups.items():
            workflow = RefoldingWorkflow(
                design_type=design_type,
                tests=tests,
                design_ids=group_design_ids,
                native_pdb_path=native_pdb_path,
                chains=list(designed_chains),
            )
            submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
        st.rerun()
