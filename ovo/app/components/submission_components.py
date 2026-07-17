import json
import os
import traceback

import pandas as pd
import streamlit as st

from ovo import config, db, schedulers
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionWorkflow,
    ProteinMPNNParams,
    MODEL_WEIGHTS_SCAFFOLD,
    MODEL_WEIGHTS_BINDER,
)
from ovo.app.components.acceptance_thresholds_components import thresholds_input_component
from ovo.app.components.navigation import open_first_section
from ovo.core.utils.advanced_parameters import load_json_from_file, get_dict_diff, merge_dictionaries
from ovo.app.utils.cached_db import get_cached_round, get_cached_common_chain_ids
from ovo.app.utils.testing import is_test_dialog_shown
from ovo.core.auth import get_username
from ovo.core.database import (
    descriptors_rfdiffusion,
)
from ovo.core.database.descriptors_refolding import REFOLDING_TESTS_BY_TYPE
from ovo.core.database.models_rfdiffusion import RFdiffusionBinderDesignWorkflow, RFdiffusionScaffoldDesignWorkflow
from ovo.core.database.models_refolding import RefoldingWorkflow
from ovo.core.database.models import Pool, Round, Workflow
from ovo.core.logic.design_logic import submit_design_workflow
from ovo.core.logic.round_logic import get_or_create_project_rounds
from ovo.core.utils.formatting import truncate_middle


def pool_submission_inputs(page_key: str):
    rounds_by_id = get_or_create_project_rounds(project_id=st.session_state.project.id)
    round_ids = list(rounds_by_id.keys())

    if st.session_state.pool_inputs.get(page_key):
        round_id, pool_name, pool_description = st.session_state.pool_inputs[page_key]
        if round_id is None:
            round_id = round_ids[-1]
    else:
        round_id, pool_name, pool_description = round_ids[-1], "", ""

    if st.session_state.get("new_round_id"):
        # When a new round is created, select it by default
        round_id = st.session_state["new_round_id"]
        del st.session_state["new_round_id"]

    left, right, _ = st.columns([1, 1, 2], vertical_alignment="bottom")
    with left:
        round_id = st.selectbox(
            "Project Round",
            format_func=lambda i: rounds_by_id[i].name,
            options=round_ids,
            index=round_ids.index(round_id) if round_id in round_ids else len(round_ids) - 1,
            key=f"selected_round_{'_'.join(round_ids)}",
        )

    with right:
        if st.button("Create new Round") or is_test_dialog_shown("create_round"):
            create_new_round_dialog()

    with st.columns([2, 1])[0]:
        pool_name = st.text_input(
            "Pool name",
            placeholder="Name your submission",
            value=pool_name,
            key="input_pool_name",
        )
        previous_pools = db.select(Pool, round_id=round_id, limit=3, order_by="-created_date_utc")
        if previous_pools:
            st.write(f"*Previous pool names: {', '.join([p.name for p in previous_pools if p.name])}*")
        if db.count(Pool, round_id=round_id, name=pool_name):
            st.error(f"Pool '{pool_name}' already exists in this round, please choose a different name.")

    pool_description = st.text_area(
        "Pool description (optional)",
        placeholder="Describe your submission here",
        key="input_pool_description",
        value=pool_description,
    )

    st.session_state.pool_inputs[page_key] = round_id, pool_name, pool_description


def get_pool_inputs(page_key: str) -> tuple[str, str, str]:
    if not st.session_state.pool_inputs.get(page_key):
        # This should never happen since pool_submission_inputs() should be called before
        st.error("Pool inputs not found.")
        st.stop()

    round_id, pool_name, pool_description = st.session_state.pool_inputs[page_key]
    return round_id, pool_name, pool_description


def shorten_absolute_file_paths(v, max_length=40):
    if not isinstance(v, str) or not v.startswith("/") or len(v) < max_length:
        return v
    return truncate_middle(v, max_length)


def format_param_table(
    project_name: str,
    round_name: str,
    pool_name: str,
    pool_description: str | None,
    values: pd.Series,
):
    # concatenate list values into comma-separated strings
    values = values.apply(lambda v: ", ".join(map(str, v)) if isinstance(v, list) else v)
    # shorten long file paths to /path/to/.../filename.ext
    values = values.apply(shorten_absolute_file_paths)
    # remove empty values
    values = values[~values.isnull() & (values != "")]
    # add index names
    values.index.names = ("Category", "Parameter")

    return pd.concat(
        [
            pd.Series(
                {
                    ("Project", "Name"): project_name,
                    ("Round", "Name"): round_name,
                    ("Pool", "Name"): pool_name,
                    ("Pool", "Description"): pool_description or "",
                },
                name="Value",
            ),
            values,
        ]
    )


def review_workflow_submission(page_key: str):
    """Show a summary of the workflow settings and submission modal button."""
    workflow = st.session_state.workflows[page_key]

    round_id, pool_name, pool_description = get_pool_inputs(page_key)

    if not pool_name:
        st.error("Please provide a pool name in the submission tab.")
        return

    # Validate workflow parameters
    try:
        workflow.validate()
    except ValueError as e:
        st.write("Errors found in workflow parameters:")
        st.error(e)
        return

    project_round = get_cached_round(round_id)

    if db.count(Pool, round_id=round_id, name=pool_name):
        st.error(f"Pool '{pool_name}' already exists in this round, please choose a different name.")

    # Workflow parameters
    st.table(
        format_param_table(
            project_name=st.session_state.project.name,
            round_name=project_round.name,
            pool_name=pool_name,
            pool_description=pool_description,
            values=workflow.get_table_row(name="Value"),
        ),
        width="content",
    )

    if st.button("Continue to submission :material/arrow_forward_ios:", key="continue") or is_test_dialog_shown(
        "submission_dialog"
    ):
        submit_workflow_dialog(
            page_key=page_key,
            workflow=workflow,
            round_id=round_id,
            pool_name=pool_name,
            pool_description=pool_description,
        )


@st.dialog("Submit workflow", width="large")
def submit_workflow_dialog(page_key: str, workflow: Workflow, round_id: str, pool_name: str, pool_description: str):
    # Create "empty" element to enable clearing the contents after submitting
    content = st.empty()
    with content.container():
        # Get pipeline name from workflow
        try:
            pipeline_name = workflow.get_pipeline_name()
        except Exception:
            traceback.print_exc()
            st.error("Unable to determine pipeline name for this workflow.")
            return

        # Filter schedulers to only those that support this pipeline
        compatible_scheduler_keys = [
            key for key, scheduler in schedulers.items() if scheduler.supports_pipeline_name(pipeline_name)
        ]

        if not compatible_scheduler_keys:
            st.error("No compatible schedulers found for this workflow type.")
            return

        # Scheduler dropdown
        with st.columns(2)[0]:
            scheduler_key = st.selectbox(
                "Scheduler",
                options=compatible_scheduler_keys,
                format_func=lambda k: schedulers[k].name,
            )

        # Time estimate
        st.write(workflow.get_time_estimate(schedulers[scheduler_key]))

        # Submit button
        with st.columns([2, 1])[-1]:
            submitted = st.button("Submit", type="primary", width="stretch", key="submit_run")

    if submitted:
        # Clear dialog window contents
        content.empty()

        # Validate workflow parameters
        try:
            workflow.validate()
        except ValueError as e:
            st.error(e)
            return

        st.write("Submitting job... 🚀")
        submit_design_workflow(
            workflow,
            scheduler_key,
            round_id=round_id,
            pool_name=pool_name,
            pool_description=pool_description,
            return_existing=False,
        )

        st.session_state.flash_success = "Job submitted successfully"
        open_first_section(page_key)
        # Switch to jobs page and clear session state
        st.session_state.workflows.pop(page_key, None)
        st.session_state.pool_inputs.pop(page_key, None)
        st.switch_page("app/pages/jobs/jobs.py")


@st.dialog("Create new round of designs")
def create_new_round_dialog():
    project_id = st.session_state.project.id
    last_round_name = list(get_or_create_project_rounds(project_id=project_id).values())[-1].name
    next_name = get_next_round_name(last_round_name)
    round_name = st.text_input("Round name", value=next_name, key="round_name")

    if st.button("Create round", disabled=not round_name, key="create_round"):
        project_round = Round(project_id=project_id, name=round_name, author=get_username())
        db.save(project_round)
        st.session_state.new_round_id = project_round.id
        st.rerun()


def get_next_round_name(last_round_name: str) -> str | None:
    next_name = None
    parts = last_round_name.rsplit(maxsplit=1)
    if len(parts) == 2 and parts[-1].isnumeric():
        next_name = f"{parts[0]} {int(parts[-1]) + 1}"
    return next_name


def show_rfdiffusion_binder_seq_design_inputs(workflow: RFdiffusionWorkflow):
    seq_design_options = {
        "ligandmpnn": "LigandMPNN (ProteinMPNN weights)",
        "fastrelax": "ProteinMPNN-FastRelax",
    }
    captions = {
        "ligandmpnn": "Sequence design with ProteinMPNN model through its LigandMPNN re-implementation. "
        "Designs will not be relaxed as part of sequence design, only repacked with LigandMPNN OpenMM logic. "
        "Designs that pass refolding criteria will be relaxed during ddG scoring.",
        "fastrelax": "Cycles of ProteinMPNN design followed by Rosetta FastRelax relaxation "
        "based on Bennet et al. 2023 'Improving de novo protein binder design with deep learning'. "
        "Sequences from all cycles are kept.",
    }
    if workflow.protein_mpnn_params.fastrelax_cycles:
        seq_design_method = "fastrelax"
    else:
        seq_design_method = "ligandmpnn"
    options = list(seq_design_options)
    seq_design_method = st.radio(
        "Sequence design method",
        options=options,
        format_func=seq_design_options.get,
        index=options.index(seq_design_method) if seq_design_method in options else None,
        captions=[captions[o] for o in options],
        key="seq_design_method",
    )
    if seq_design_method == "fastrelax":
        if not config.props.pyrosetta_license:
            st.error(
                "Use of the PyRosetta license is disabled in this instance of OVO. "
                "If you want to use PyRosetta FastRelax for interface side-chains relaxation and "
                "you have a license (or in case of non-commercial use), "
                "enable props.pyrosetta_license in your config.yml"
            )
            st.stop()
        if workflow.protein_mpnn_params.fastrelax_cycles == 0:
            # Initialize at 3 cycles
            workflow.protein_mpnn_params.fastrelax_cycles = 3
        workflow.protein_mpnn_params.num_sequences = 1
        with st.columns([1, 2])[0]:
            workflow.protein_mpnn_params.fastrelax_cycles = st.number_input(
                "Number of FastRelax cycles (ProteinMPNN design followed by FastRelax relaxation)",
                min_value=1,
                max_value=5,
                value=workflow.protein_mpnn_params.fastrelax_cycles,
                key="fastrelax_cycles",
            )
        st.caption(
            "Note: Compared to Bennet et al. 2023, we skip the last ProteinMPNN design step "
            "so that all designs have undergone relaxation consistently. For example, with 2 cycles, "
            "the workflow actually performs (Design + Relax) * 2 instead of (Design + Relax) * 2 + Design."
        )
    else:
        if workflow.protein_mpnn_params.fastrelax_cycles:
            # Re-initialize to default number of sequences when switching back from FastRelax
            workflow.protein_mpnn_params.num_sequences = ProteinMPNNParams().num_sequences
            workflow.protein_mpnn_params.fastrelax_cycles = 0
        with st.columns([1, 2])[0]:
            workflow.protein_mpnn_params.num_sequences = st.number_input(
                f"Number of sequence designs per backbone",
                min_value=1,
                max_value=config.props.mpnn_sequences_limit,
                value=workflow.protein_mpnn_params.num_sequences,
                key="num_sequences",
            )


TIMESTEPS_INPUT_KEY = "timesteps"


def show_backbone_generation_settings(workflow: RFdiffusionWorkflow):
    def _on_backbone_generator_change():
        new_gen = st.session_state["backbone_generator"]
        # Clear previous preview (only compatible with RFdiffusion v1)
        workflow.preview_job_id = None
        default_timesteps = 200 if new_gen == "rfdiffusion3" else 50
        workflow.rfdiffusion_params.timesteps = default_timesteps
        st.session_state[TIMESTEPS_INPUT_KEY] = default_timesteps

    generator_options = ["rfdiffusion", "rfdiffusion3"]
    workflow.rfdiffusion_params.backbone_generator = st.selectbox(
        "Backbone generator",
        options=generator_options,
        format_func=lambda x: "RFdiffusion (RFD1)" if x == "rfdiffusion" else "RFdiffusion3 (RFD3)",
        index=generator_options.index(workflow.rfdiffusion_params.backbone_generator),
        key="backbone_generator",
        on_change=_on_backbone_generator_change,
    )

    if workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3":
        show_rfdiffusion3_params(workflow)
    elif workflow.rfdiffusion_params.backbone_generator == "rfdiffusion":
        if workflow.is_instance(RFdiffusionBinderDesignWorkflow):
            workflow.rfdiffusion_params.model_weights = st.radio(
                "Model weights",
                help="Use 'beta' model weights to generate a greater diversity of topologies.",
                index=MODEL_WEIGHTS_BINDER.index(workflow.rfdiffusion_params.model_weights)
                if workflow.rfdiffusion_params.model_weights
                else 0,
                key="active_site",
                options=MODEL_WEIGHTS_BINDER,
            )
        else:
            workflow.rfdiffusion_params.model_weights = st.radio(
                "Model weights",
                help="Use 'active site' model weights to hold better selected residues specified in the contig.",
                index=MODEL_WEIGHTS_SCAFFOLD.index(workflow.rfdiffusion_params.model_weights)
                if workflow.rfdiffusion_params.model_weights
                else 0,
                key="active_site",
                options=MODEL_WEIGHTS_SCAFFOLD,
            )
        st.caption(":material/info: Reference: https://github.com/RosettaCommons/RFdiffusion#binder-design")


def show_rfdiffusion3_params(workflow: RFdiffusionWorkflow):
    """Show RFdiffusion3-specific InputSpec parameters, filtered by design type.
    Only renders when backbone_generator is 'rfdiffusion3'.

    Scaffold: unindex, ligand, select_fixed_atoms (enzyme/scaffolding use case)
    Binder: select_fixed_atoms (hotspots handled by existing UI field)
    """
    if workflow.rfdiffusion_params.backbone_generator != "rfdiffusion3":
        return

    design_type = workflow.get_refolding_design_type()

    assert design_type in REFOLDING_TESTS_BY_TYPE, (
        f"Unknown design type '{design_type}' for RFdiffusion3 parameters. Expected one of: {', '.join(REFOLDING_TESTS_BY_TYPE.keys())}"
    )

    st.write("#### RFdiffusion3 parameters")

    if design_type == "scaffold":
        workflow.rfdiffusion_params.rfd3_unindex = (
            st.text_input(
                "Unindexed motif (unindex)",
                value=workflow.rfdiffusion_params.rfd3_unindex,
                placeholder="e.g. A244,A274,A320",
                key="rfd3_unindex",
                help="Residues whose relative position in the sequence is unknown to the model. Useful for scaffolding around active sites.",
            )
            or None
        )
        workflow.rfdiffusion_params.rfd3_ligand = (
            st.text_input(
                "Ligand (ligand)",
                value=workflow.rfdiffusion_params.rfd3_ligand,
                placeholder="e.g. HAX,OAA",
                key="rfd3_ligand",
                help="Ligand CCD names from RCSB PDB to include in the design.",
            )
            or None
        )

    if design_type == "binder":
        workflow.rfdiffusion_params.rfd3_select_hotspots = (
            st.text_area(
                "Atom-level hotspots (select_hotspots)",
                value=workflow.rfdiffusion_params.rfd3_select_hotspots,
                placeholder='e.g. {"E64": "CD2,CZ", "E88": "CG,CZ"}',
                key="rfd3_select_hotspots",
                help="Dict of residue → atom names for atom-level hotspot control. "
                "Overrides residue-level hotspots above when set. "
                "Hotspots will typically be at most 4.5Å to any heavy atom in the designed structure.",
            )
            or None
        )
        if workflow.rfdiffusion_params.rfd3_select_hotspots:
            try:
                parsed_hs = json.loads(workflow.rfdiffusion_params.rfd3_select_hotspots)
                if not isinstance(parsed_hs, dict):
                    st.error('Atom-level hotspots must be a JSON dict, e.g. {"E64": "CD2,CZ"}')
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")

    workflow.rfdiffusion_params.rfd3_select_fixed_atoms = (
        st.text_area(
            "Fixed atoms (select_fixed_atoms)",
            value=workflow.rfdiffusion_params.rfd3_select_fixed_atoms,
            placeholder='e.g. A123,A234 or {"A123": "CA,CB,C,N"}',
            key="rfd3_select_fixed_atoms",
            help='Override which atoms are fixed in 3D space. Contig string or dict syntax (e.g. "A244":"TIP","A274":"BKBN").',
        )
        or None
    )

    # is_non_loopy: default True for binder (RFD3 docs recommend it for PPI), Auto (None) for scaffold
    is_non_loopy_options = ["Auto", "True", "False"]
    is_non_loopy_default = "True" if design_type == "binder" else "Auto"
    current = workflow.rfdiffusion_params.rfd3_is_non_loopy
    if current is None:
        current_label = is_non_loopy_default
    else:
        current_label = str(current)
    is_non_loopy_selected = st.selectbox(
        "Fewer loops (is_non_loopy)",
        options=is_non_loopy_options,
        index=is_non_loopy_options.index(current_label),
        key="rfd3_is_non_loopy",
        help="True = fewer loops, more helices/sheets (recommended for binder). False = more loops. Auto = no bias (RFD3 default).",
    )
    workflow.rfdiffusion_params.rfd3_is_non_loopy = {"Auto": None, "True": True, "False": False}[is_non_loopy_selected]


def show_rfdiffusion_advanced_settings(workflow: RFdiffusionWorkflow):
    st.markdown("Advanced settings")

    with st.expander(label="Show advanced settings"):
        if get_username() in config.auth.admin_users:
            st.markdown("#### Admin settings")

            workflow.rfdiffusion_params.batch_size = st.number_input(
                "Batch size",
                min_value=1,
                max_value=200,
                value=workflow.rfdiffusion_params.batch_size,
                key="batch_size",
            )

        st.markdown("#### RFdiffusion")

        is_rfd3 = workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3"

        if is_rfd3:
            timestep_label = "Number of timesteps (inference_sampler.num_timesteps)"
            timestep_help = "Number of diffusion steps. Default is 200; use 10–50 for fast testing."
        else:
            timestep_label = "Num RFdiffusion timesteps (T)"
            timestep_help = "Number of diffusion steps. Default is 50; use 10–20 for fast testing."

        if TIMESTEPS_INPUT_KEY not in st.session_state:
            st.session_state[TIMESTEPS_INPUT_KEY] = workflow.rfdiffusion_params.timesteps

        workflow.rfdiffusion_params.timesteps = st.number_input(
            timestep_label,
            min_value=1,
            key=TIMESTEPS_INPUT_KEY,
            help=timestep_help,
        )
        st.caption(
            ":material/info: Number of denoising diffusion steps determines the granularity of the diffusion process. "
            "Higher values lead to better quality structures but also longer runtime."
        )

        workflow.rfdiffusion_params.contigmap_length = (
            st.text_input(
                "Sequence length limit" + (" (contigmap.length)" if not is_rfd3 else ""),
                placeholder="For example 123 or 123-456",
                value=workflow.rfdiffusion_params.contigmap_length,
                key="contigmap_length",
            )
            or None
        )
        st.caption(
            ":material/info: When using multiple generated segments with random length range (for example 10-100), "
            "make sure that randomly sampling those lengths will produce contigs within the total length range."
        )

        if not is_rfd3 and workflow.is_instance(RFdiffusionScaffoldDesignWorkflow):
            workflow.rfdiffusion_params.inpaint_seq = (
                st.text_input(
                    "Sequence inpainting regions (contigmap.inpaint_seq)",
                    placeholder="For example A12-34/A45-67/B89-90",
                    value=workflow.rfdiffusion_params.inpaint_seq,
                    key="inpaint_seq",
                )
                or None
            )
            st.caption(
                ":material/info: Input structure regions present in the contig but to be redesigned with ProteinMPNN. "
                "This argument tells RFdiffusion that the sequence will be redesigned "
                "so it can better pack against those regions."
            )

        workflow.rfdiffusion_params.backbone_filters = (
            st.text_input(
                "Hard filters for backbone designs",
                placeholder="For example pydssp_helix_percent<50,N_contact_hotspots>=5",
                value=workflow.rfdiffusion_params.backbone_filters,
                key="backbone_filters",
            )
            or None
        )
        st.caption(
            "This filter can be used to completely discard undesirable backbone designs "
            "and avoid wasting compute resources on their sequence design and structure prediction."
        )
        st.caption(f"Supported filtering metrics: {', '.join(descriptors_rfdiffusion.BACKBONE_METRIC_FIELD_NAMES)}")

        run_params_placeholder = (
            "e.g. inference_sampler.step_scale=0.5" if is_rfd3 else "e.g. contigmap.inpaint_str=[123-456]"
        )
        workflow.rfdiffusion_params.run_parameters = st.text_input(
            "Additional run parameters",
            placeholder=run_params_placeholder,
            value=workflow.rfdiffusion_params.run_parameters,
            key="rfdiff_run_parameters",
        )
        if is_rfd3:
            st.caption(
                ":material/info: Hydra overrides passed directly to rfd3 design (e.g. inference_sampler.step_scale=0.5). Reference: https://rosettacommons.github.io/foundry/models/rfd3/input.html"
            )
        else:
            st.caption(":material/info: Reference: https://github.com/RosettaCommons/RFdiffusion.")
        if workflow.rfdiffusion_params.run_parameters:
            st.warning("Additional parameters can override previously selected parameters.")

        if is_rfd3:
            st.markdown("**InputSpec overrides (RFdiffusion3)**")
            col1, col2 = st.columns(2)
            with col1:
                infer_ori_options = ["", "hotspots", "com"]
                workflow.rfdiffusion_params.rfd3_infer_ori_strategy = (
                    st.selectbox(
                        "Origin strategy (infer_ori_strategy)",
                        options=infer_ori_options,
                        format_func=lambda x: "Auto-detect" if x == "" else x,
                        index=infer_ori_options.index(workflow.rfdiffusion_params.rfd3_infer_ori_strategy or ""),
                        key="rfd3_infer_ori_strategy",
                        help="Controls placement of the ORI token. 'hotspots' places it near hotspot COM, 'com' uses input structure COM. Auto-detect sets 'hotspots' when hotspots are provided, 'com' otherwise.",
                    )
                    or None
                )
            with col2:
                workflow.rfdiffusion_params.rfd3_ori_token = (
                    st.text_input(
                        "ORI token (ori_token)",
                        value=workflow.rfdiffusion_params.rfd3_ori_token,
                        placeholder="e.g. 10.5,20.3,15.1",
                        key="rfd3_ori_token",
                        help="Explicit [x,y,z] origin override to control center of mass placement of the designed structure. Overrides infer_ori_strategy.",
                    )
                    or None
                )

            # workflow.rfdiffusion_params.rfd3_length = (
            #     st.text_input(
            #         "Total length constraint (length)",
            #         value=workflow.rfdiffusion_params.rfd3_length,
            #         placeholder="e.g. 100-150 or 120",
            #         key="rfd3_length",
            #         help="Constrain the total design length. Useful when contig alone does not fix the total length.",
            #     )
            #     or None
            # )

            workflow.rfdiffusion_params.rfd3_spec_overrides = (
                st.text_area(
                    "Additional InputSpec overrides (JSON)",
                    value=workflow.rfdiffusion_params.rfd3_spec_overrides,
                    placeholder='e.g. {"select_unfixed_sequence": "A20-35", "redesign_motif_sidechains": true}',
                    key="rfd3_spec_overrides",
                    help="JSON dict of additional InputSpec fields. These are applied on top of the parameters above and will override them on conflict.",
                    height=80,
                )
                or None
            )
            st.caption(
                ":material/info: JSON dict of additional InputSpec fields. These are applied on top of the parameters above and will override them on conflict. Reference: https://rosettacommons.github.io/foundry/models/rfd3/input.html"
            )
            if workflow.rfdiffusion_params.rfd3_spec_overrides:
                try:
                    parsed = json.loads(workflow.rfdiffusion_params.rfd3_spec_overrides)
                    if not isinstance(parsed, dict):
                        st.error("Spec overrides must be a JSON object (dict)")
                    else:
                        from ovo.core.database.models_rfdiffusion import RFD3_SPEC_FIELDS

                        unknown = set(parsed.keys()) - RFD3_SPEC_FIELDS
                        if unknown:
                            st.error(f"Unknown InputSpec keys: {', '.join(sorted(unknown))}")
                        # Warn about keys that overlap with dedicated UI fields
                        named_param_keys = {
                            "unindex",
                            "select_fixed_atoms",
                            "select_hotspots",
                            "ligand",
                            "length",
                            "infer_ori_strategy",
                            "is_non_loopy",
                            "ori_token",
                        }
                        overlapping = set(parsed.keys()) & named_param_keys
                        if overlapping:
                            st.warning(
                                f"Keys [{', '.join(sorted(overlapping))}] overlap with dedicated parameters above. "
                                f"The values from this field will take precedence."
                            )
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")

        st.markdown("#### Protein MPNN ")

        workflow.protein_mpnn_params.sampling_temp = st.number_input(
            "Sampling temperature protein MPNN",
            format="%g",
            value=workflow.protein_mpnn_params.sampling_temp
            or (0.0001 if workflow.is_instance(RFdiffusionBinderDesignWorkflow) else 0.1),
            key="sampling_temp",
        )
        st.caption(
            ":material/info: ProteinMPNN is a deterministic neural network, outputting residue probabilities. "
            "The temperature parameter is used to select less probable residues during sequence sampling. "
            "Higher temperature leads to higher diversity, temperature closer to 0 leads to less diversity and higher ProteinMPNN score. "
            "Suggested values 0.0001, 0.1, 0.15, 0.2, 0.25, 0.3. "
        )

        workflow.protein_mpnn_params.omit_aa = st.text_input(
            "Omitted residue types from sequence design",
            value=workflow.protein_mpnn_params.omit_aa,
            key="omit_aa",
        )

        workflow.protein_mpnn_params.bias_aa = st.text_input(
            "Amino acid bias for ProteinMPNN",
            placeholder="For example F:1.5,K-1.2",
            value=workflow.protein_mpnn_params.bias_aa,
            key="mpnn_bias",
        )
        st.caption(
            ":material/info: Negative values reduce the probability of sampling given amino acid, positive values increase it, zero is neutral (default)."
        )

        st.markdown("#### Refolding tests")

        # For example 'scaffold' or 'binder'
        supported_refolding_tests = REFOLDING_TESTS_BY_TYPE[workflow.get_refolding_design_type()]
        test_options = list(supported_refolding_tests.keys())

        workflow.refolding_params.primary_test = st.radio(
            "Refolding test (Structure prediction method used to compare designed and predicted structure)",
            options=test_options,
            format_func=lambda k: f"**{supported_refolding_tests[k][0]}** {supported_refolding_tests[k][1]}",
            key="refolding_test",
            index=test_options.index(workflow.refolding_params.primary_test)
            if workflow.refolding_params.primary_test in test_options
            else None,
        )

        if workflow.refolding_params.primary_test == "esmfold":
            workflow.refolding_params.esmfold_fp16 = st.checkbox(
                "Use fp16 mode in ESMFold",
                help="Use half-precision mode in ESMFold to reduce memory consumption and speed up predictions. This may lead to slightly less accurate predictions.",
                value=workflow.refolding_params.esmfold_fp16,
                key="esmfold_fp16",
            )

        new_thresholds = thresholds_input_component(
            selected_thresholds=workflow.acceptance_thresholds,
            skipped_threshold_keys=workflow.get_skipped_threshold_keys(),
        )

        if new_thresholds != workflow.acceptance_thresholds:
            workflow.acceptance_thresholds = new_thresholds
            st.rerun()
            return


def customize_json_settings_component(diff: dict | None, default: dict, key_suffix: str):
    """
    Allows to modify default advanced an filter setting in a text field and returns only the differences between custom and default.

    Args:
        diff: A dictionary with previously saaved customizations. (Differences from the default)
        default: The base dictionary with default settings.
        key_suffix: Unique string used to crate keys for Streamlit components.

    Returns:
        Newly calculated differences and boolean indicating whether the component is in edit mode or not.
    """
    merged_settings = merge_dictionaries(default, diff)
    new_diff = get_dict_diff(default, merged_settings)
    merged_json = json.dumps(merged_settings, indent=4)

    if new_diff:
        st.warning(f"You have customized the '{key_suffix}' settings. See changes below:")
        st.json(new_diff, expanded=False)

    col1, info_col = st.columns([0.2, 0.8])
    with col1:
        edit_mode = st.toggle("Edit", key=f"edit_toggle_{key_suffix}")

    with st.columns([1.2, 1])[0]:
        if edit_mode:
            with info_col:
                st.info(
                    "You are in edit mode. Changes are processed live. Toggle 'Edit' off to see the changes.",
                    icon="✍️",
                )

            editor_key = f"editor_text_{key_suffix}"
            response_text = st.text_area(
                "Edit JSON settings",
                height=400,
                value=merged_json,
                key=editor_key,
                label_visibility="collapsed",
            )

            try:
                response_dict = json.loads(response_text)
                new_diff = get_dict_diff(default, response_dict)
                if not new_diff:
                    new_diff = None
            except json.JSONDecodeError:
                st.error("The text is not valid JSON. Please correct it.", icon="🚨")
                pass  # Keep the last valid diff

        else:
            st.code(merged_json, language="json", line_numbers=True, height=400)

        return new_diff, edit_mode


@st.fragment()
def show_bindcraft_advanced_settings(workflow: "BindCraftBinderDesignWorkflow"):
    advanced_settings_path, filter_settings_path = workflow.get_settings_paths()
    advanced_default_dict = load_json_from_file(advanced_settings_path)
    filter_default_dict = load_json_from_file(filter_settings_path)

    if advanced_default_dict is None or filter_default_dict is None:
        st.error("Cannot display settings component because the default settings failed to load.")
        return

    with st.expander(label="Advanced settings and filter settings"):
        st.markdown("#### Advanced Settings")
        advanced_key = os.path.basename(advanced_settings_path).removesuffix(".json")

        st.write(
            f"""
            Settings reference: [github.com/martinpacesa/BindCraft](https://github.com/martinpacesa/BindCraft?tab=readme-ov-file#advanced-settings)
            
            The advanced settings json file **`{advanced_key}`** 
            was selected based on the design protocol choices above. 
            You can further customize the settings using the editor below.
            """
        )

        custom_advanced, advanced_edit_mode = customize_json_settings_component(
            diff=workflow.bindcraft_params.custom_advanced_settings,
            default=advanced_default_dict,
            key_suffix=advanced_key,
        )
        workflow.bindcraft_params.custom_advanced_settings = custom_advanced

        if workflow.bindcraft_params.custom_advanced_settings and not advanced_edit_mode:
            if st.button("Reset Advanced Settings to Default", key="reset_advanced", type="primary"):
                workflow.bindcraft_params.custom_advanced_settings = None
                # editor_key = f"editor_text_{advanced_key}"
                # if editor_key in st.session_state:
                #     del st.session_state[editor_key]
                st.rerun()

        st.divider()

        st.markdown("#### Filter Settings")

        filter_key = os.path.basename(filter_settings_path).removesuffix(".json")

        st.write(
            f"""
            Settings reference: [github.com/martinpacesa/BindCraft](https://github.com/martinpacesa/BindCraft?tab=readme-ov-file#advanced-settings)
            
            The filter settings json file **`{filter_key}`** 
            was selected based on the design protocol choices above. 
            You can further customize the settings using the editor below.
            """
        )

        custom_filter, filter_edit_mode = customize_json_settings_component(
            diff=workflow.bindcraft_params.custom_filter_settings, default=filter_default_dict, key_suffix=filter_key
        )
        workflow.bindcraft_params.custom_filter_settings = custom_filter

        if workflow.bindcraft_params.custom_filter_settings and not filter_edit_mode:
            if st.button("Reset Filter Settings to Default", key="reset_filter", type="primary"):
                workflow.bindcraft_params.custom_filter_settings = None
                # editor_key = f"editor_text_{filter_key}"
                # if editor_key in st.session_state:
                #     del st.session_state[editor_key]
                st.rerun()

        new_thresholds = thresholds_input_component(selected_thresholds=workflow.acceptance_thresholds)
        if new_thresholds != workflow.acceptance_thresholds:
            workflow.acceptance_thresholds = new_thresholds
            st.rerun()
            return


def chain_ids_input(design_ids: list[str]) -> list[str]:
    """Get user input for chain IDs to analyze, with pre-filled common chain IDs across the provided designs."""
    common_chain_ids, available_chain_ids = get_cached_common_chain_ids(design_ids)

    if not common_chain_ids:
        st.error("Designs have different chain IDs of the designed chains. Please submit these designs separately.")
        return []

    if common_chain_ids != available_chain_ids:
        st.warning(
            "Designs do not share the same set of chain IDs. "
            f"Using the common chain IDs for analysis: {', '.join(common_chain_ids)}. "
        )

    chains = st.multiselect(
        "Chain(s) to analyze", options=common_chain_ids, default=common_chain_ids, key="select_chain_ids"
    )
    if not chains:
        st.warning("Please specify at least one chain to analyze.")
    return chains
