import itertools
import os
from typing import Callable

import pandas as pd
import streamlit as st

from ovo import db, storage, DesignJob, Pool
from ovo import viz
from ovo.app.components.navigation import get_jobs_url
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_rounds,
)
from ovo.core.database import (
    Design,
    WorkflowTypes,
    descriptors_rfdiffusion,
    descriptors_refolding,
)
from ovo.core.database.models_bindcraft import BindCraftBinderDesignWorkflow
from ovo.core.database.models_rfdiffusion import RFdiffusionWorkflow
from ovo.core.utils.pdb import filter_pdb_str
from ovo.core.utils.residue_selection import (
    parse_contig_for_input_structure,
    from_hotspots_to_segments,
    ContigSegment,
)


# Set once the user asks to see the whole summary, see iterate_shown_items
SHOW_ALL_SUMMARY_KEY = "show_all_workflow_summary"


def show_workflow_summary(jobs: list[DesignJob]):
    """Show the summary of each workflow type among the given jobs, grouped by their inputs.

    The jobs do not have to be submitted yet: an unsaved job has no pool, so the summary of a
    submission that is still being reviewed leaves out the design counts and the job links, see
    :func:`get_subjob_table`.

    Only the first workflow type is shown, and within it only its first group of jobs, until the
    user asks for all of them - see :func:`iterate_shown_items`.
    """
    workflow_names = sorted(set(job.workflow.name for job in jobs if job.workflow))
    for _, workflow_name in iterate_shown_items(workflow_names, noun="workflow", button_key="workflows"):
        WorkflowType = WorkflowTypes.get(workflow_name)
        st.write(f"#### {workflow_name}")

        try:
            WorkflowType.visualize_summary(
                jobs=[job for job in jobs if job.workflow and job.workflow.name == workflow_name]
            )
        except NotImplementedError as e:
            st.error(e)


@st.fragment
def rfdiffusion_scaffold_workflow_summary(jobs: list[DesignJob]):
    if len(jobs) > 1:
        st.write(
            "This section shows jobs in groups. Each group uses the same input structure "
            "and fixed motif residues (and their ordering)."
        )

    def groupby(subjob):
        job, pool, contig_index = subjob
        input_path = job.workflow.get_input_pdb_path(contig_index=contig_index)
        contig = job.workflow.get_contig(contig_index=contig_index)
        contig_segments = parse_contig_for_input_structure(contig)
        fixed_segments = "/".join([f"{s.chain}{s.start}-{s.end}" for s in contig_segments if s.chain])
        unfixed_segments = "/".join((job.workflow.rfdiffusion_params.rfd3_unindex or "").split(","))
        segments = f"{fixed_segments}/{unfixed_segments}".strip("/")

        # this is checked in parameter validation
        assert segments, (
            f"Expected at least one fixed contig segment or unindexed residue, got: {contig=}, {job.workflow.rfdiffusion_params.rfd3_unindex=}"
        )

        return (
            input_path if not job.workflow.rfdiffusion_params.partial_diffusion else "partial",
            segments,
        )

    accepted_designs_by_pool, total_designs_by_pool = get_cached_pool_stats(
        pools=get_cached_pools(design_job_id__in=[job.id for job in jobs])
    )
    key = "_".join([job.id for job in jobs])

    groups = group_subjobs_by_key(jobs, groupby)
    shown_groups = iterate_shown_items(groups, noun="group", button_key=f"groups_{key}")
    for i, ((input_or_partial, fixed_segments), group_subjobs) in shown_groups:
        if input_or_partial == "partial":
            title = "Partial diffusion"
        else:
            title = os.path.basename(input_or_partial)
        title += f", fixed segments: {fixed_segments}"

        st.write(f"##### {title}")
        show_subjob_table(group_subjobs, accepted_designs_by_pool, total_designs_by_pool)

        target_chains = [s[0] for s in fixed_segments.split("/") if s]
        left, right = st.columns(2)
        with left:
            input_path = subjob_input_selectbox(
                all_input_paths=[j.workflow.get_input_pdb_path(contig_index) for j, p, contig_index in group_subjobs],
                key_suffix=str(i),
            )
            viz.molstar(
                viz.StructureVisualization(
                    data=filter_pdb_str(storage.read_file_str(input_path), target_chains),
                    representation="cartoon+ball-and-stick",
                    contigs=parse_contig_for_input_structure(fixed_segments),
                ),
                key=f"input_structure_{key}_{i}",
                height=450,
            )
        with right:
            st.write("###### Input motif")
            viz.molstar(
                viz.StructureVisualization(
                    data=filter_pdb_str(storage.read_file_str(input_path), fixed_segments.split("/"), add_ter=True),
                    representation="cartoon+ball-and-stick",
                    contigs=parse_contig_for_input_structure(fixed_segments),
                ),
                key=f"structure_motif_{key}_{i}",
                height=450,
            )
        if i < len(groups) - 1:
            st.divider()


@st.fragment
def rfdiffusion_binder_design_workflow_summary(jobs: list[DesignJob]):
    if len(jobs) > 1:
        st.write(
            "This section shows jobs in groups. Each group uses the same input structure, "
            "target chain, trim region, and hotspot."
        )

    def groupby(subjob):
        job, pool, contig_index = subjob
        input_path = job.workflow.get_input_pdb_path(contig_index=contig_index)
        target_contig = job.workflow.get_target_contig(contig_index=contig_index)
        hotspots = job.workflow.rfdiffusion_params.hotspots
        return (
            input_path if not job.workflow.rfdiffusion_params.partial_diffusion else "partial",
            target_contig,
            hotspots,
        )

    accepted_designs_by_pool, total_designs_by_pool = get_cached_pool_stats(
        pools=get_cached_pools(design_job_id__in=[job.id for job in jobs])
    )
    key = "_".join([job.id for job in jobs])

    groups = group_subjobs_by_key(jobs, groupby)
    shown_groups = iterate_shown_items(groups, noun="group", button_key=f"groups_{key}")
    for i, ((input_or_partial, target_contig, hotspots), group_subjobs) in shown_groups:
        if input_or_partial == "partial":
            title = "Partial diffusion"
        else:
            title = os.path.basename(input_or_partial)

        title += f", region: {target_contig}, hotspots: {hotspots}"

        st.write(f"##### {title}")
        show_subjob_table(group_subjobs, accepted_designs_by_pool, total_designs_by_pool)

        input_path = subjob_input_selectbox(
            all_input_paths=[j.workflow.get_input_pdb_path(contig_index) for j, p, contig_index in group_subjobs],
            key_suffix=str(i),
        )
        input_pdb_full = storage.read_file_str(input_path)
        input_pdb_target_region = filter_pdb_str(input_pdb_full, target_contig.split("/"))
        viz.molstar(
            viz.StructureVisualization(
                data=input_pdb_target_region,
                representation="cartoon+ball-and-stick",
                color="hydrophobicity",
                selection=hotspots.split(",") if hotspots else None,
            ),
            key=f"structure_{key}_{i}",
            height=450,
            width=700,
        )
        if not any(j.job_result for j, _, _ in group_subjobs):
            # A job without a pool is not submitted yet (see show_workflow_summary), so saying that
            # it has no results would only be confusing while its submission is being reviewed
            if any(pool is not None for _, pool, _ in group_subjobs):
                st.write("No results yet.")
            if i < len(groups) - 1:
                st.divider()
            continue

        for method, color, descriptor in [
            ["Designed", "green", descriptors_rfdiffusion.INTERFACE_TARGET_RESIDUES],
            ["AlphaFold2 refolding predicted", "red", descriptors_refolding.AF2_PRIMARY_INTERFACE_TARGET_RESIDUES],
            # TODO include Boltz-2 once the descriptor is available for Boltz-2 results
        ]:
            st.write(f"##### {method} binding sites")
            st.write(f"Most common binding sites shown in :{color}[{color}] - {descriptor.description}")
            target_chain_ids = sorted(set(s[0] for s in target_contig.split("/")))
            assert len(target_chain_ids) == 1, (
                f"Expected exactly one target chain ID, got multiple in contig: {target_contig}"
            )
            for accepted, col in zip([None, True], st.columns(2, gap="medium")):
                with col:
                    st.write("###### Accepted designs" if accepted else "###### All designs")
                    interface_residue_stats = get_cached_interface_residue_stats(
                        group_subjobs=group_subjobs,
                        accepted=accepted,
                        target_chain_id=target_chain_ids[0],
                        descriptor_key=descriptor.key,
                    )
                    if interface_residue_stats is None:
                        st.write("No designs found")
                        continue
                    mean_count = (
                        sum(interface_residue_stats.values()) / len(interface_residue_stats)
                        if interface_residue_stats
                        else 0
                    )
                    # TODO use a color gradient instead of a hard cutoff
                    binding_residues = [
                        residue for residue, count in interface_residue_stats.items() if count >= mean_count
                    ]
                    if not binding_residues:
                        st.write("No binding residues found")
                        continue
                    binding_segments = from_hotspots_to_segments(",".join(binding_residues))
                    viz.molstar(
                        viz.StructureVisualization(
                            data=input_pdb_full,
                            representation="cartoon",
                            selection=hotspots.split(",") if hotspots else None,
                            contigs=[
                                ContigSegment(
                                    chain=segment[0],
                                    start=int(segment[1:].split("-")[0]),
                                    end=int(segment[1:].split("-")[1]),
                                    color="#00cc00" if color == "green" else "#ff0000",
                                )
                                for segment in binding_segments
                            ],
                        ),
                        key=f"structure_{method}_{key}_{accepted}_{i}",
                        height=400,
                    )
                    if binding_residues:
                        # TODO include the amino acid: E24 (Tyr)
                        st.write(
                            f"Found {len(binding_residues)} most frequent "
                            f"binding residues: :{color}-badge[{f'] :{color}-badge['.join(binding_residues)}]"
                        )
        if i < len(groups) - 1:
            st.divider()


@st.fragment
def bindcraft_workflow_summary(jobs: list[DesignJob]):
    if len(jobs) > 1:
        st.write(
            "This section shows jobs in groups. Each group uses the same input structure, target chain, and hotspot."
        )

    def groupby(subjob):
        job, pool, contig_index = subjob
        workflow: BindCraftBinderDesignWorkflow = job.workflow
        return (
            # TODO pass contig_index when BindCraft supports multiple inputs per job
            workflow.get_input_pdb_path(),
            workflow.bindcraft_params.target_chains,
            workflow.bindcraft_params.hotspots,
        )

    accepted_designs_by_pool, total_designs_by_pool = get_cached_pool_stats(
        pools=get_cached_pools(design_job_id__in=[job.id for job in jobs])
    )
    key = "_".join([job.id for job in jobs])

    groups = group_subjobs_by_key(jobs, groupby)
    shown_groups = iterate_shown_items(groups, noun="group", button_key=f"groups_{key}")
    for i, ((input_path, target_chains, hotspots), group_subjobs) in shown_groups:
        title = f"{os.path.basename(input_path)} chain {target_chains}, hotspots: {hotspots}"

        st.write(f"##### {title}")
        show_subjob_table(group_subjobs, accepted_designs_by_pool, total_designs_by_pool)
        viz.molstar(
            viz.StructureVisualization(
                data=filter_pdb_str(storage.read_file_str(input_path), target_chains.split(",")),
                representation="cartoon+ball-and-stick",
                color="hydrophobicity",
                selection=hotspots.split(",") if hotspots else None,
            ),
            key=f"structure_{key}_{i}",
            height=450,
            width=700,
        )
        # TODO visualize interface residues - these are not produced by BindCraft currently
        if i < len(groups) - 1:
            st.divider()


@st.cache_data(max_entries=10)
def get_cached_pool_stats(pools: list[Pool]):
    with st.spinner("Getting statistics..."):
        accepted_designs_by_pool = db.count_distinct(
            Design, group_by=("pool_id", "contig_index"), pool_id__in=[p.id for p in pools], accepted=True
        )
        total_designs_by_pool = db.count_distinct(
            Design, group_by=("pool_id", "contig_index"), pool_id__in=[p.id for p in pools]
        )
    return accepted_designs_by_pool, total_designs_by_pool


@st.cache_data(max_entries=10)
def get_cached_interface_residue_stats(
    group_subjobs, accepted: bool | None, target_chain_id: str, descriptor_key: str
) -> dict | None:
    with st.spinner("Loading descriptors..."):
        all_contig_indexes = sorted(set(contig_index for j, p, contig_index in group_subjobs))
        accepted_filter = {"accepted": accepted} if accepted is not None else {}
        if len(all_contig_indexes) == 1:
            design_ids = db.select_values(
                Design,
                "id",
                pool_id__in=[pool.id for job, pool, contig_index in group_subjobs],
                contig_index=all_contig_indexes[0],
                **accepted_filter,
            )
        else:
            design_ids = []
            for job, pool, contig_index in group_subjobs:
                design_ids.extend(
                    db.select_values(
                        Design,
                        "id",
                        pool_id=pool.id,
                        contig_index=contig_index,
                        **accepted_filter,
                    )
                )
        if not design_ids:
            # We return None to flag that there are no designs
            return None

        interface_residues = db.select_descriptor_values(descriptor_key=descriptor_key, design_ids=design_ids)
    interface_residue_stats = {}
    for design_id, residues in interface_residues.dropna().items():
        for residue in residues.split(","):
            if not residue:
                continue
            assert residue[0] == "B", f"Expected target to be B, got: {residue[0]} in {design_id}"
            input_residue = f"{target_chain_id}{residue[1:]}"
            interface_residue_stats[input_residue] = interface_residue_stats.get(input_residue, 0) + 1
    return interface_residue_stats


def group_subjobs_by_key(jobs: list[DesignJob], key: Callable):
    pools = get_cached_pools(design_job_id__in=[job.id for job in jobs])
    pools_by_job_id = {pool.design_job_id: pool for pool in pools}

    # we split a job into multiple subjobs in case it has multiple PDB inputs or multiple contigs
    subjobs: list[tuple[DesignJob, Pool | None, int]] = []
    for job in jobs:
        for contig_index in job.workflow.get_contig_indexes():
            # The pool is None for a job that is not submitted yet, see show_workflow_summary
            subjobs.append((job, pools_by_job_id.get(job.id), contig_index))

    group_sizes = pd.Series(key(subjob) for subjob in subjobs).value_counts().to_dict()
    # sort subjobs by their group size (largest first), then by the key (to group them consecutively)
    subjobs = sorted(subjobs, key=lambda subjob: (group_sizes[key(subjob)], key(subjob)), reverse=True)

    # Materialized rather than returned as the groupby iterator, so that the caller knows how many
    # groups there are - e.g. to leave out the divider after the last one
    return [(group_key, list(group_subjobs)) for group_key, group_subjobs in itertools.groupby(subjobs, key=key)]


def iterate_shown_items(items: list, noun: str, button_key: str, limit: int = 10):
    """Yield the items of one summary section to show, hiding the rest behind a "Show all" button.

    Only the very first item is shown until the user asks for all of them, the same way the job
    detail page shows only the first job - the hidden items are not rendered at all, so their input
    structures are not read from storage until they are asked for. Even then at most ``limit`` of
    them are shown, as a large grid of workflows would take very long to visualize.

    All the sections share one state, so a single "Show all" reveals the remaining workflow types as
    well as the remaining groups within each of them.

    :param noun: What the items are called in the messages about the ones that are not shown
    :param button_key: Distinguishes this button from the "Show all" of another section
    :param limit: How many items to show at most once the user asked for all of them
    """
    show_all = st.session_state.get(SHOW_ALL_SUMMARY_KEY)
    num_shown = limit if show_all else 1

    for i, item in enumerate(items[:num_shown]):
        yield i, item

    num_hidden = len(items) - num_shown
    if num_hidden <= 0:
        return

    if show_all:
        st.warning(f"Showing the first {num_shown} {noun}s, {num_hidden} remaining {noun}s not shown.")
        return

    with st.container(horizontal=True, vertical_alignment="center"):
        if st.button(":material/unfold_more: Show all", key=f"show_all_summary_{button_key}"):
            st.session_state[SHOW_ALL_SUMMARY_KEY] = True
            # The hidden items of the other sections are rendered outside of this fragment
            st.rerun(scope="app")
        st.write(f"1 more {noun} not shown" if num_hidden == 1 else f"{num_hidden} more {noun}s not shown")


def subjob_input_selectbox(all_input_paths: list[str], key_suffix: str):
    # get filename -> full path mapping, ensuring unique names by adding suffix if needed
    input_paths_by_name = {}
    for path in pd.Series(all_input_paths).value_counts().index:
        name = os.path.basename(path)
        if name in input_paths_by_name:
            # if duplicate names, add suffix to make them unique
            suffix = 1
            while f"{name} ({suffix})" in input_paths_by_name:
                suffix += 1
            name = f"{name} ({suffix})"
        input_paths_by_name[name] = path

    if len(input_paths_by_name) > 1:
        input_name = st.selectbox(
            "Input structure",
            options=input_paths_by_name.keys(),
            key=f"input_path_{key_suffix}",
            width=400,
        )
    else:
        input_name = list(input_paths_by_name.keys())[0]
        st.write(f"###### Input structure: {input_name}")
    return input_paths_by_name[input_name]


def get_subjob_table(
    group_subjobs: list[tuple[DesignJob, Pool | None, int]],
    accepted_designs_by_pool,
    total_designs_by_pool,
):
    """Return the table of the subjobs of one group, one row per subjob.

    Subjobs whose pool does not exist yet (a draft submission that is still being reviewed, see
    :func:`show_workflow_summary`) only get the columns that come from the workflow - their design
    counts are all zero and their job link would lead nowhere.
    """
    is_draft = any(pool is None for job, pool, contig_index in group_subjobs)
    project_rounds_by_id = (
        {}
        if is_draft
        else {r.id: r for r in get_cached_rounds(id__in=[pool.round_id for job, pool, _ in group_subjobs])}
    )
    rows = []
    for job, pool, contig_index in group_subjobs:
        row = {}
        if isinstance(job.workflow, RFdiffusionWorkflow):
            if len(job.workflow.rfdiffusion_params.input_pdb_paths) > 1:
                row["Input"] = os.path.basename(job.workflow.get_input_pdb_path(contig_index))
            elif len(job.workflow.rfdiffusion_params.contigs) > 1:
                row["Contig"] = job.workflow.get_contig(contig_index)
        if is_draft:
            rows.append(row)
            continue
        accepted_designs = accepted_designs_by_pool.get((pool.id, contig_index), 0)
        total_designs = total_designs_by_pool.get((pool.id, contig_index), 0)
        rows.append(
            {
                **row,
                "Accepted": accepted_designs,
                "Total": total_designs,
                "% Accepted": f"{accepted_designs / total_designs if total_designs else 0:.2%}",
                "Pool name": pool.name,
                "Link": f"[Job ↑]({get_jobs_url(project_rounds_by_id[pool.round_id].project_id, pool.id)})",
            }
        )

    table = pd.DataFrame(rows)
    if not is_draft:
        table.index = [pool.id for job, pool, contig_index in group_subjobs]
        table.index.name = "Pool ID"

    return table


def show_subjob_table(group_subjobs: list, accepted_designs_by_pool: dict, total_designs_by_pool: dict):
    table = get_subjob_table(group_subjobs, accepted_designs_by_pool, total_designs_by_pool)
    if table.empty:
        # A draft submission whose workflows have a single input and contig, nothing to show
        return
    st.table(table, width="content")
