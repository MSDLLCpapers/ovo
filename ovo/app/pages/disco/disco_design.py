import json
import os

import streamlit as st

from ovo import storage
from ovo.app.components.acceptance_thresholds_components import thresholds_input_component
from ovo.app.components.input_components import initialize_workflow
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.submission_components import pool_submission_inputs, review_workflow_submission
from ovo.app.utils.page_init import initialize_page
from ovo.core.database.models_disco import DiscoWorkflow
from ovo.core.logic.design_logic_disco import build_disco_input_json
from ovo.core.utils.formatting import get_hashed_path_for_bytes, safe_filename

LIGAND_MODE_CCD = "CCD code"
LIGAND_MODE_SMILES = "SMILES"
LIGAND_MODE_FILE = "File"
LIGAND_MODE_NONE = "No ligand (unconditional)"
LIGAND_MODES = [LIGAND_MODE_CCD, LIGAND_MODE_SMILES, LIGAND_MODE_FILE, LIGAND_MODE_NONE]


@st.fragment
def intro_step():
    initialize_workflow(__file__, DiscoWorkflow.name)

    with st.container(width=850):
        st.markdown(
            """
Ligand-conditioned protein design using DISCO.<sup>[1]</sup> DISCO (DIffusion for Sequence-structure CO-design)
is a multimodal generative model that **jointly co-designs a protein sequence and 3D structure** around a target ligand,
without requiring a template structure or seed sequence. LigandMPNN then packs the side chains, and the design is
validated by Boltz refolding.

Use case: Designing a new protein binding pocket around a small-molecule ligand (cofactor, drug, substrate, ...).

- **Input**
    - A ligand, specified as a CCD code, a SMILES string, or an uploaded structure file (SDF/MOL/MOL2/PDB)
    - The desired protein length
- **Main parameters**
    - Experiment preset (designable / diverse) and compute effort (fast / max)
    - Number of designs to generate
- **Output**
    - Designs — co-designed sequences and structures, side chains packed with LigandMPNN
    - Descriptors — LigandMPNN confidence and Boltz refolding metrics

### References
1. DISCO paper – [https://arxiv.org/abs/2604.05181/](https://arxiv.org/abs/2604.05181/)
2. Project website – [https://disco-design.github.io/](https://disco-design.github.io/)
3. Code – [https://github.com/DISCO-design/DISCO/](https://github.com/DISCO-design/DISCO/)
4. Forked version – [https://github.com/hugohrban/DISCO/](https://github.com/hugohrban/DISCO/)
""",
            unsafe_allow_html=True,
        )


# Warning shown when a ligand mode is selected but left empty (i.e. would run unconditionally by accident)
EMPTY_LIGAND_WARNING = (
    "No ligand provided — this will run **unconditional** generation (protein only). "
    "Did you mean to specify a ligand? Select 'No ligand (unconditional)' to suppress this warning."
)
# Session-state flag: set once the user interacts with any ligand input, so we don't warn on first load
LIGAND_TOUCHED_KEY = "disco_ligand_touched"
# Session-state copy of the selected ligand mode. Streamlit drops widget keys when the widget is not rendered
# (e.g. on the review step), and the mode can't be derived from the workflow when the ligand is empty.
LIGAND_MODE_KEY = "disco_selected_ligand_mode"


def _mark_ligand_touched():
    st.session_state[LIGAND_TOUCHED_KEY] = True


def _ligand_is_missing(workflow: DiscoWorkflow) -> bool:
    """True when a ligand mode is selected but no ligand was provided (would silently run unconditionally)."""
    if workflow.disco_params.custom_input_json:
        # In custom JSON mode the ligand fields don't drive the submission, so there's nothing to warn about
        return False
    mode = st.session_state.get(LIGAND_MODE_KEY, LIGAND_MODE_CCD)
    return mode != LIGAND_MODE_NONE and not workflow.disco_params.ligand


def _ligand_input(workflow: DiscoWorkflow, disabled: bool = False):
    """Collect the ligand using one of three modes and store it on the workflow in DISCO format.

    :param disabled: when True (custom JSON mode), the inputs are shown disabled and no warning is emitted.
    """
    st.subheader("Ligand")

    # Widget values are initialized from the workflow so they survive navigating to the review step and back
    ligand = workflow.disco_params.ligand or ""
    mode = st.radio(
        "Ligand input mode",
        options=LIGAND_MODES,
        index=LIGAND_MODES.index(st.session_state.get(LIGAND_MODE_KEY, LIGAND_MODE_CCD)),
        horizontal=True,
        key="disco_ligand_mode",
        on_change=_mark_ligand_touched,
        disabled=disabled,
        help=(
            "CCD code: a PDB Chemical Component Dictionary code (e.g. ATP). "
            "SMILES: a SMILES string, a 3D conformer is generated automatically. "
            "File: upload a 3D conformer (SDF/MOL/MOL2/PDB)."
        ),
    )
    st.session_state[LIGAND_MODE_KEY] = mode

    if mode == LIGAND_MODE_CCD:
        code = st.text_input(
            "CCD code",
            placeholder="e.g. ATP",
            value=ligand.removeprefix("CCD_") if ligand.startswith("CCD_") else "",
            key="disco_ccd_code",
            on_change=_mark_ligand_touched,
            disabled=disabled,
            help="For multi-component ligands (e.g. glycans), concatenate codes with underscores, e.g. NAG_BMA_BGC.",
        )
        workflow.disco_params.ligand_file_path = None
        workflow.disco_params.ligand = f"CCD_{code.strip().upper()}" if code.strip() else None

    elif mode == LIGAND_MODE_SMILES:
        smiles = st.text_input(
            "SMILES string",
            placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O",
            value=ligand if not ligand.startswith(("CCD_", "FILE_")) else "",
            key="disco_smiles",
            on_change=_mark_ligand_touched,
            disabled=disabled,
        )
        workflow.disco_params.ligand_file_path = None
        workflow.disco_params.ligand = smiles.strip() or None

    elif mode == LIGAND_MODE_FILE:
        st.caption("Help: https://github.com/DISCO-design/DISCO#custom-ligand-conditioned-design")
        uploaded_file = st.file_uploader(
            "Ligand structure file (must contain a 3D conformer)",
            type=["sdf", "mol", "mol2", "pdb"],
            key="disco_ligand_file",
            on_change=_mark_ligand_touched,
            disabled=disabled,
        )
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            filename = safe_filename(uploaded_file.name)
            stored_path = storage.store_file_bytes(
                file_bytes,
                f"project/{st.session_state.project.id}/inputs/{get_hashed_path_for_bytes(file_bytes)}/{filename}",
                overwrite=False,
            )
            workflow.disco_params.ligand_file_path = stored_path
            workflow.disco_params.ligand = f"FILE_{os.path.basename(stored_path)}"
            st.success(f"Uploaded ligand file: {uploaded_file.name}")
        elif workflow.disco_params.ligand_file_path:
            st.success(f"Using uploaded ligand file: {workflow.disco_params.ligand_file_path}")

    elif mode == LIGAND_MODE_NONE:
        # Unconditional generation: protein chain only, no ligand. No warning.
        workflow.disco_params.ligand_file_path = None
        workflow.disco_params.ligand = None

    # Only warn once the user has interacted with the ligand inputs and still left it empty
    # (suppressed in custom JSON mode, where the ligand fields don't drive the submission)
    if not disabled and st.session_state.get(LIGAND_TOUCHED_KEY) and _ligand_is_missing(workflow):
        st.warning(EMPTY_LIGAND_WARNING)


@st.fragment
def settings_step():
    st.subheader("Settings")

    workflow: DiscoWorkflow = st.session_state.workflows[__file__]

    pool_submission_inputs(__file__)

    # Advanced mode: let the user fully specify the DISCO input JSON (RNA/DNA, chain counts, explicit
    # residues, multiple jobs, etc.). When enabled, the structured input fields are disabled.
    custom_json_mode = st.toggle(
        "Specify custom input JSON",
        value=workflow.disco_params.custom_input_json is not None,
        key="disco_custom_json_mode",
        help=(
            "Edit the full DISCO input JSON directly to access options not exposed by the fields below "
            "(e.g. RNA/DNA conditioning, chain counts, explicit residues, multiple jobs)."
        ),
    )

    _ligand_input(workflow, disabled=custom_json_mode)

    st.subheader("Design parameters")
    with st.columns([1, 2])[0]:
        workflow.disco_params.sequence_length = st.number_input(
            "Protein length (residues)",
            value=workflow.disco_params.sequence_length,
            min_value=1,
            max_value=1000,
            key="disco_sequence_length",
            disabled=custom_json_mode,
            help="Number of residues in the designed protein chain.",
        )

        workflow.disco_params.num_designs = st.number_input(
            "Number of designs",
            value=workflow.disco_params.num_designs,
            min_value=1,
            key="disco_num_designs",
            help="Number of random seeds; each produces one design.",
        )

        experiment_options = ["designable", "diverse"]
        workflow.disco_params.experiment = st.selectbox(
            "Experiment preset",
            options=experiment_options,
            index=experiment_options.index(workflow.disco_params.experiment),
            key="disco_experiment",
            help="'designable' steers toward refoldable designs; 'diverse' samples more freely for greater variety.",
        )
        st.caption("Help: https://github.com/DISCO-design/DISCO#experiment-presets")

        effort_options = ["fast", "max"]
        workflow.disco_params.effort = st.selectbox(
            "Compute effort",
            options=effort_options,
            index=effort_options.index(workflow.disco_params.effort),
            key="disco_effort",
            help="'fast' (100 steps) for prototyping; 'max' (200 steps) recommended for ligand-conditioned design.",
        )
        st.caption("Help: https://github.com/DISCO-design/DISCO#trading-off-quality-for-speed")

    if custom_json_mode:
        st.subheader("Custom input JSON")
        st.caption(
            "Edit the DISCO input JSON directly. This overrides the fields above. Docs: https://github.com/DISCO-design/DISCO#-input-json-format"
        )
        # Seed the editor from the generated JSON the first time custom mode is enabled
        default_json = workflow.disco_params.custom_input_json or json.dumps(build_disco_input_json(workflow), indent=2)
        # Render the editor inside a keyed container so we can scope a monospace font to just this textarea
        st.markdown(
            "<style>.st-key-disco_custom_json_container textarea { font-family: monospace !important; }</style>",
            unsafe_allow_html=True,
        )
        with st.container(key="disco_custom_json_container"):
            custom_json = st.text_area(
                "DISCO input JSON",
                value=default_json,
                height=400,
                key="disco_custom_json",
                label_visibility="collapsed",
            )
        workflow.disco_params.custom_input_json = custom_json
        try:
            parsed = json.loads(custom_json)
            if not isinstance(parsed, list) or not parsed:
                st.error("Input JSON must be a non-empty list of DISCO jobs.")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
    else:
        # Structured mode: discard any previously entered custom JSON
        workflow.disco_params.custom_input_json = None
        st.subheader("Generated input JSON")
        st.caption("This is the DISCO input that will be submitted, generated from the fields above.")
        st.code(json.dumps(build_disco_input_json(workflow), indent=2), language="json")

    new_thresholds = thresholds_input_component(
        selected_thresholds=workflow.acceptance_thresholds,
        skipped_threshold_keys=workflow.get_skipped_threshold_keys(),
    )

    if new_thresholds != workflow.acceptance_thresholds:
        workflow.acceptance_thresholds = new_thresholds
        st.rerun()
        return


@st.fragment
def review_step():
    st.subheader("Review settings")

    workflow: DiscoWorkflow = st.session_state.workflows[__file__]
    # Reaching the review step is an explicit attempt to proceed, so warn here too if no ligand was set
    if _ligand_is_missing(workflow):
        st.warning(EMPTY_LIGAND_WARNING)

    review_workflow_submission(__file__)


if __name__ == "__main__":
    initialize_page(page_title="DISCO design")

    show_prev_next_sections(
        key=__file__,
        title="🪩 DISCO scaffold design",
        sections={
            "intro": intro_step,
            "settings": settings_step,
            "review": review_step,
        },
    )
