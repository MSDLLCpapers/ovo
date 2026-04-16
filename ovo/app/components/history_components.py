from copy import deepcopy
from typing import Callable

import streamlit as st

from ovo.app.utils.cached_db import get_cached_workflow_pools_and_jobs
from datetime import datetime, timezone
import timeago
from ovo.core.database import Pool, WorkflowTypes


def history_dropdown_component(
    page_key: str, workflow_name: str, filter_func: Callable = None, include_subclasses: bool = True
):
    if page_key not in st.session_state.initial_workflows:
        raise ValueError(
            "history_dropdown_component should be called after initialize_workflow() so that st.session_state.initial_workflows is set"
        )

    # Get list of workflow names including subclasses
    if include_subclasses:
        workflow_names = WorkflowTypes.get_subclass_names(workflow_name)
    else:
        workflow_names = [workflow_name]

    pools_by_id, jobs_by_id = get_cached_workflow_pools_and_jobs(st.session_state.project.id, workflow_names)
    if filter_func:
        pools_by_id = {
            pool_id: pool
            for pool_id, pool in pools_by_id.items()
            if filter_func(jobs_by_id[pool.design_job_id].workflow)
        }
    num_options = len(pools_by_id)

    previous_pool_id = st.session_state.get("history_pool_id")
    pool_ids_by_date = [p.id for p in sorted(pools_by_id.values(), key=lambda p: p.created_date_utc, reverse=True)]
    pool_id: str = st.selectbox(
        "Re-use previous run:",
        options=pool_ids_by_date,
        format_func=lambda pool_id: format_label(pool_id, pools_by_id),
        index=None,
        key="history_dropdown",
        placeholder=("1 run available" if num_options == 1 else f"{num_options} runs available")
        if num_options
        else "No runs in this project",
        help="Select a previous run to load its parameters. "
        "If you clear the selection, the parameters will be cleared and history reloaded.",
    )

    if pool_id:
        pool = pools_by_id[pool_id]
        workflow = jobs_by_id[pool.design_job_id].workflow

    if pool_id != previous_pool_id:
        if pool_id:
            workflow.preview_job_id = None
            st.session_state.workflows[page_key] = workflow
            st.session_state.pool_inputs[page_key] = None, pool.name, pool.description
        else:
            # Reset to initial workflow when selection is cleared
            st.session_state.workflows[page_key] = deepcopy(st.session_state.initial_workflows[page_key])

        st.session_state["history_pool_id"] = pool_id
        st.rerun()


def format_label(pool_id: str, pools_by_id: dict[str, Pool]):
    delta = datetime.now(timezone.utc).replace(tzinfo=None) - pools_by_id[pool_id].created_date_utc
    return "{id} | {name} | {when_created}".format(
        id=pool_id,
        name=pools_by_id[pool_id].name,
        # NOTE: we need to use "a moment ago" for times less than 1 hour
        # to avoid the streamlit selectbox being re-created and discarding user's selection
        when_created=timeago.format(delta) if delta.total_seconds() > 3600 else "a moment ago",
    )
