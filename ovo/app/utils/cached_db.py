import pandas as pd
from typing import List, Collection

from ovo import db, config
from ovo.core.database.cache_clearing import clear_when_modified
from ovo.core.database.models import Project, DescriptorValue, Descriptor, Pool, Round, Design, DesignJob
import streamlit as st

from ovo.core.logic.descriptor_logic import get_available_descriptors
from ovo.core.logic.design_logic import get_design_jobs_table, get_pools_table


@clear_when_modified(Project)
@st.cache_data(ttl="1h")
def get_cached_project_ids_and_names(username: str, extra_project_ids: Collection[str] = None) -> dict[str, str]:
    """Return dict of project id -> name"""
    if username in config.auth.admin_users:
        projects = db.select(Project)
        return {
            project.id: project.name
            + (
                f" (private, only visible to {project.author} and admins)"
                if not project.public and project.author != username
                else ""
            )
            for project in projects
        }
    else:
        public_projects = db.select(Project, public=True)
        private_projects = db.select(Project, public=False, author=username)
        extra_projects = db.select(Project, id__in=extra_project_ids or [])
        projects = sorted(public_projects + private_projects + extra_projects, key=lambda project: project.name.lower())
        return {project.id: project.name for project in projects}


@clear_when_modified(DescriptorValue)
@st.cache_data(max_entries=100, ttl="1h")
def get_cached_available_descriptors(design_ids: Collection[str]) -> dict[str, Descriptor]:
    """
    Return all descriptor keys found in DB for the given design ids.
    """
    return get_available_descriptors(design_ids)


@clear_when_modified(DescriptorValue)
@st.cache_data(max_entries=100, ttl="1h")
def get_cached_descriptor_values(descriptor_key: str, design_ids: list[str]) -> pd.Series():
    return db.select_descriptor_values(descriptor_key, design_ids=design_ids)


@clear_when_modified(Design)
@st.cache_data(max_entries=100, ttl="10m")
def get_cached_design(design_id: str) -> Design:
    return db.get(Design, id=design_id)


@clear_when_modified(Design)
@st.cache_data(max_entries=10, ttl="1h")
def get_cached_designs(design_ids: Collection[str]) -> list[Design]:
    designs_by_id = {d.id: d for d in db.select(Design, id__in=design_ids)}
    return [designs_by_id[design_id] for design_id in design_ids if design_id in designs_by_id]


@clear_when_modified(Design)
@st.cache_data(max_entries=10, ttl="1h")
def get_cached_design_ids(pool_ids: list[str], **filters) -> list[str]:
    """Get design ids matching the given filters, sorted from most recently created."""
    ids = db.select_values(Design, "id", pool_id__in=pool_ids, **filters)
    order = dict(zip(pool_ids, range(len(pool_ids))))
    return sorted(ids, key=lambda design_id: order.get(Design.design_id_to_pool_id(design_id)))


@clear_when_modified(Round)
@st.cache_data(max_entries=100, ttl="10m")
def get_cached_round(round_id: str) -> Round:
    return db.get(Round, id=round_id)


@clear_when_modified(Round)
@st.cache_data(max_entries=100, ttl="10m")
def get_cached_rounds(project_id: str = None) -> list[Round]:
    return db.select(Round, project_id=project_id, order_by="-created_date_utc")


@clear_when_modified(Pool)
@st.cache_data(max_entries=100, ttl="10m")
def get_cached_pool(pool_id: str) -> Pool:
    return db.get(Pool, id=pool_id)


@clear_when_modified(Pool)
@st.cache_data(max_entries=100, ttl="1h")
def get_cached_pools(pool_ids: Collection[str]) -> list[Pool]:
    return db.select(Pool, id__in=pool_ids, order_by="-created_date_utc")


@clear_when_modified(DesignJob)
@st.cache_data(max_entries=100, ttl="1h")
def get_cached_design_jobs(design_job_ids: Collection[str]) -> list[DesignJob]:
    return db.select(DesignJob, id__in=design_job_ids, order_by="-created_date_utc")


@clear_when_modified(DesignJob)
@st.cache_data(max_entries=100, ttl="10m")
def get_cached_design_job(design_job_id: str) -> DesignJob:
    return db.get(DesignJob, id=design_job_id)


# note: caching is managed by nested function - only when no jobs are in progress
def get_cached_design_jobs_table(round_ids: list[str], **filters) -> pd.DataFrame:
    design_job_ids = [v for v in db.select_values(Pool, "design_job_id", round_id__in=round_ids) if v]
    if db.count(DesignJob, id__in=design_job_ids, job_result=None):
        # if any jobs are still running, do not use cache so that job status is updated
        _get_cached_design_jobs_table.clear(round_ids=round_ids, **filters)
    return _get_cached_design_jobs_table(round_ids=round_ids, **filters)


@clear_when_modified(DesignJob)
@st.cache_data(show_spinner=False, max_entries=100, ttl="1m")  # update every minute since the table contains datetimes
def _get_cached_design_jobs_table(
    project_id: str = None, round_ids: list[str] = None, update=True, **pool_filters
) -> pd.DataFrame:
    return get_design_jobs_table(project_id=project_id, round_ids=round_ids, update=update, **pool_filters)


@clear_when_modified(Pool, Design)
@st.cache_data(max_entries=100, ttl="1m")  # update every minute since the table contains datetimes
def get_cached_pools_table(project_id: str = None, round_ids: list[str] = None) -> pd.DataFrame:
    return get_pools_table(project_id=project_id, round_ids=round_ids)


@clear_when_modified(DescriptorValue)
@st.cache_data(max_entries=100, ttl="1h")
def get_cached_design_descriptors(design_id: str, descriptor_keys: list[str]) -> pd.Series():
    return db.select_design_descriptors(design_id=design_id, descriptor_keys=descriptor_keys)


@clear_when_modified(Design)
@st.cache_data()
def get_cached_designs_accept_field(design_ids: list[str]) -> List[bool]:
    return db.get_design_accepted_values(design_ids)


@clear_when_modified(Pool, DesignJob)
@st.cache_data(ttl="1h")
def get_cached_workflow_pools_and_jobs(project_id: str, workflow_names: Collection[str]):
    round_ids = db.select_unique_values(Round, "id", project_id=project_id)
    pools = [pool for pool in db.select(Pool, round_id__in=round_ids) if pool.design_job_id]
    all_jobs_by_id = {
        j.id: j for j in db.select(DesignJob, id__in=[p.design_job_id for p in pools], order_by="-created_date_utc")
    }
    pools_by_id = {}
    jobs_by_id = {}
    for pool in pools:
        job = all_jobs_by_id[pool.design_job_id]
        if job.workflow.name not in workflow_names:
            continue
        pools_by_id[pool.id] = pool
        jobs_by_id[job.id] = job
    return pools_by_id, jobs_by_id
