import streamlit as st

from ovo import db
from ovo.app.components.custom_elements import refresh_button
from ovo.app.components.navigation import project_round_selector
from ovo.app.pages.jobs.design_job_detail import design_job_detail
from ovo.app.utils.page_init import initialize_page
from ovo.core.database.models import Pool, Round
from ovo.app.utils.cached_db import get_cached_design_jobs_table


@st.fragment
def overview():
    st.title("⏳️ Jobs")
    project = st.session_state.project

    st.write(f"Showing all jobs in project **{project.name}**")

    rounds = db.select(Round, project_id=project.id, order_by="-created_date_utc")
    if not rounds:
        st.write("*No design jobs yet in this project. Submit a workflow in the left panel.*")
        return

    selected_round_ids = project_round_selector(rounds)
    key = "_".join(sorted(selected_round_ids))

    st.subheader("Design jobs")

    refresh_button(key="jobs")

    with st.spinner("Checking workflow status..."):
        table = get_cached_design_jobs_table(round_ids=selected_round_ids)
        table = table.reset_index()

    if table.empty:
        st.write("No jobs submitted yet in this round")
        return

    table.insert(
        0, ("Pool", "actions"), [f"?pool_ids={pool_id}&project_id={project.id}" for pool_id in table[("Pool", "id")]]
    )

    selection = st.dataframe(
        table,
        hide_index=True,
        key=f"pools_round_{key}",
        column_config={
            "actions": st.column_config.LinkColumn(display_text=r"Results ↑"),
        },
        on_select="rerun",
    )

    selected_ids = table[("Pool", "id")].iloc[selection["selection"]["rows"]].tolist()
    label = "All job" if not selected_ids else "Selected job"
    if st.button(f"{label} results :material/arrow_forward_ios:", key=f"open_round_{key}"):
        st.query_params["pool_ids"] = ",".join(selected_ids if selected_ids else table[("Pool", "id")])
        st.rerun()


if "pool_ids" in st.query_params:
    assert "project_id" in st.query_params, "Invalid URL, project ID expected"
    # Get the pool(s)
    pool_ids = st.query_params.get("pool_ids").split(",")
    project_id = st.query_params.get("project_id")
    pools = db.select(Pool, id__in=pool_ids)
    if not pools:
        raise ValueError("Pool not found")

    # check the project ID for security reasons, to avoid users guessing the short pool ID
    for round_id in set([p.round_id for p in pools]):
        project_round = db.get(Round, round_id)
        assert project_round.project_id == project_id, f"Pool does not belong to project {project_id}"

    name = f"{len(pools)} pools" if len(pools) > 1 else pools[0].name
    initialize_page(f"{name} - Jobs")
    if st.button(":material/arrow_back_ios: Back to jobs"):
        del st.query_params["pool_ids"]
        st.rerun()
    design_job_detail([pool.id for pool in pools])

# Overview page
else:
    initialize_page("Jobs")
    overview()
