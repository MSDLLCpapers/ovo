import os
import re
from collections import Counter
from copy import deepcopy

import pandas as pd
import streamlit as st

from ovo.app.components.history_components import history_dropdown_component
from ovo.app.components.input_components import sequence_selection_fragment, initialize_workflow
from ovo import viz
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.preview_components import visualize_rfdiffusion_preview, submit_rfdiffusion_preview_component
from ovo.app.components.scheduler_components import wait_with_statusbar
from ovo.app.components.submission_components import (
    pool_submission_inputs,
    show_mpnn_sequence_design_inputs,
    review_workflow_submission,
    show_rfdiffusion_binder_seq_design_inputs,
    show_rfdiffusion_backbone_design_inputs,
    show_rfdiffusion_timesteps_input,
)

from ovo.app.pages import jobs_page, designs_page
from ovo.app.utils.page_init import initialize_page
from ovo import (
    config,
    db,
    local_scheduler,
    storage,
    Design,
    get_username,
)
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionBinderDesignWorkflow,
    RFdiffusionWorkflow,
    MODEL_WEIGHTS_BINDER,
    RFdiffusionParams,
)
from ovo.app.components.submission_components import show_rfdiffusion_advanced_settings
from ovo.core.database import descriptors_rfdiffusion, descriptors_refolding
from ovo.core.database.models import WorkflowTypes, Pool, DesignJob
from ovo.core.utils.formatting import get_hashed_path_for_bytes, safe_filename, truncate_middle
from ovo.core.utils.pdb import (
    ChainNotFoundError,
    get_contact_residues,
    get_residue_b_factors,
    mmcif_to_pdb,
    pdb_chain_looks_cyclic,
    get_sequences_from_pdb_str,
    filter_and_relabel_chains_pdb_str,
)
from ovo.core.logic.design_logic import store_structures_with_binder_as_chain_a
from ovo.core.utils.residue_selection import (
    from_contig_to_residues,
    from_residues_to_segments,
    get_chains_and_contigs,
)
from ovo.app.utils.cached_db import get_cached_num_cyclic


# This workflow diffuses the binder as chain A, see store_structures_with_binder_as_chain_a
BINDER_CHAIN = "A"

# Residue sets offered in the selection step, applied by selection_action_dialog
ALL_RESIDUES = "All residues"
CONTACT_RESIDUES = "Residues in contact with target"
NON_CONTACT_RESIDUES = "Residues *not* in contact with target"
LOW_PLDDT_RESIDUES = "Regions with low pLDDT"
AMINO_ACID_RESIDUES = "Specific amino acid types"
SELECTION_ACTIONS = [
    ALL_RESIDUES,
    CONTACT_RESIDUES,
    NON_CONTACT_RESIDUES,
    LOW_PLDDT_RESIDUES,
    AMINO_ACID_RESIDUES,
]

# Shown in the dialog, telling the user what the set picked from the menu is, not what the menu says
SELECTION_ACTION_DESCRIPTIONS = {
    ALL_RESIDUES: "The whole binder is redesigned by default, so adding all residues restores that.",
    CONTACT_RESIDUES: "Contact is measured between Cα atoms, so side chains are ignored.",
    NON_CONTACT_RESIDUES: "Everything but the interface, measured between Cα atoms, so side chains are ignored.",
    LOW_PLDDT_RESIDUES: "pLDDT is read from the B-factor column, which only a predicted structure fills in.",
    AMINO_ACID_RESIDUES: "For example to redesign every cysteine, or to keep a disulfide bond fixed.",
}

# How the residues of the set are applied to the residues already selected in each input
SELECT = "Select"
ADD = "Add"
REMOVE = "Remove"
INTERSECT = "Intersect"
SELECTION_OPERATIONS = {
    SELECT: lambda selected, matched: matched,
    ADD: lambda selected, matched: selected | matched,
    REMOVE: lambda selected, matched: selected - matched,
    INTERSECT: lambda selected, matched: selected & matched,
}
SELECTION_OPERATION_HELP = {
    SELECT: "Redesign exactly these residues, replacing the current selection",
    ADD: "Redesign these residues on top of the ones already selected",
    REMOVE: "Keep these residues fixed, leaving the rest of the selection as it is",
    INTERSECT: "Narrow the selection down to these residues",
}

# Starting points for the amino acid types of the two actions above, the list stays editable
AMINO_ACID_PRESETS = {
    "Hydrophobic (AVILMFWC)": "AVILMFWC",
    "Aromatic (FWYH)": "FWYH",
    "Positively charged (KRH)": "KRH",
    "Negatively charged (DE)": "DE",
    "Polar uncharged (STNQY)": "STNQY",
    "Small (GAS)": "GAS",
    "Glycine and proline (GP)": "GP",
    "Cysteine (C)": "C",
    "Methionine (M)": "M",
    "Custom": "",
}


# Incremented when an action rewrites the selection, to re-create the molstar component with it
_SELECTION_RESET_KEY = "diversification_selection_reset"

# The uploaded files the binder chain dialog was cancelled for, see select_binder_chains_dialog
_CANCELLED_UPLOAD_KEY = "diversification_cancelled_upload"

# Protocols offered in the sequence design step, picked by whether the backbone of the selected
# residues is diffused or kept as it is - keeping it means submitting the input structures as custom
# backbones, which skips backbone design in the pipeline, see sequence_design_step
PARTIAL_DIFFUSION_PROTOCOL = "Partial diffusion + Sequence redesign"
SEQUENCE_REDESIGN_PROTOCOL = "Sequence redesign"
PROTOCOL_DESCRIPTIONS = {
    PARTIAL_DIFFUSION_PROTOCOL: "The backbone of the selected residues is redesigned by RFdiffusion partial diffusion, "
    'their sequence is then redesigned by ProteinMPNN.\n\n:material/info: Tip: Select "Sequence redesign" above for a faster workflow that redesigns only the sequence.',
    SEQUENCE_REDESIGN_PROTOCOL: "Only the sequence of the selected residues is redesigned by ProteinMPNN, keeping the "
    "backbone of the input structures as it is.",
}


@st.fragment
def intro_step():
    # Initialize the workflow object in session state
    initialize_workflow(
        page_key=__file__,
        workflow_name=RFdiffusionBinderDesignWorkflow.name,
        include_subclasses=True,
    )

    with st.container(width=850):
        st.markdown(
            f"""
This workflow enables starting from an existing binder-target complex, generating 
similar binder backbones and designing their sequences. It implements the end-to-end RFdiffusion partial diffusion
protocol,<sup>[2,3]</sup> where noise is added to the backbone of an existing binder chain.

Use cases:
- Generate binders with improved computational success rate, starting from a computationally successful design. <sup>[3]</sup>
- Generate binders with improved specificity and affinity for a target protein, using an existing binder as starting point. <sup>[2]</sup>
- Generate binders with altered specificity by starting from a binder–homolog complex (same family) with the target swapped for homolog. <sup>[2,3]</sup>
    <!--[2] also shows the success rate is better when altering the specificity than when starting de-novo. In [3] the starting design was not
                de novo from RFdiffusion but rather some modified structure using RF joint inpainting.  -->

This workflow noises and denoises the binder chain in the input structure for a specified number of timesteps (noising
strength) using RFdiffusion. This allows sampling backbones around the starting binder structure. The higher the number
of timesteps, the more the generated backbones will diverge from the original binder structure.

Partial diffusion can also be skipped, redesigning only the sequence of the selected binder residues and keeping the
backbone of the input structure as it is — pick the protocol in the sequence design step.

- **Input**
    - Protein structures — one or more PDB files with binder chain (A) and target chain (B), or OVO Design IDs
- **Main parameters**
    - Hotspot residues to select preferred binding site (optional, RFdiffusion may preserve the original binding site even without hotspots, but specifying hotspots explicitly enables computing hotspot-focused interface metrics) 
    - (Optional) Noising strength (num partial diffusion timesteps `partial_T`), the default is 20 out of 1-50
- **Output**
    - Designs — binder sequences and structures in complex with target protein
    - Design descriptors
        - Refolding metrics
        - Rosetta descriptors
        - Backbone metrics
        - Sequence composition

You can run this workflow as a next step after the RFdiffusion binder design workflow — besides partial diffusion, 
the methods and computed metrics are the same.

### Features

View and filter your designs based on descriptors at {jobs_page.title}. All designs and descriptors are also available
for download. Most relevant descriptors are listed below:

#### Backbone metrics

- Computed for the RFdiffusion backbone design
- **Secondary structure composition**:
    - Percentages of helix, sheet, loop (the remaining residues); computed using PyDSSP
- Backbone-backbone contacts (Cα atoms within 8&nbsp;Å):
    - **{descriptors_rfdiffusion.N_CONTACTS_TO_INTERFACE.name}** — Number of pairwise contacts between all residues of binder and target
    - **{descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS.name}** — Number of pairwise contacts between the binder backbone and hotspot residues
    - **{descriptors_rfdiffusion.N_HOTSPOTS_ON_INTERFACE.name}** — Number of hotspot residues in contact with the binder backbone

#### Sequence composition

- Percentage of individual amino acids
- Charge at pH 7.4 and 5.5, isoelectric point
- Aromaticity
- And more; computed using BioPython ProteinAnalysis <sup>[5]</sup>

#### Rosetta descriptors <sup>[6]</sup>

- **{descriptors_rfdiffusion.PYROSETTA_DDG.name}** — Rosetta binding energy of the complex (in Rosetta energy units). Lower (negative) values indicate better binding affinity.
- **{descriptors_rfdiffusion.PYROSETTA_CMS.name}** — Rosetta molecular surface area (in square angstroms).
- **{descriptors_rfdiffusion.PYROSETTA_SAP_SCORE.name}** — Evaluates hydrophobicity of surface exposed regions. Positive values indicate hydrophobic molecules.

#### AlphaFold2 initial guess refolding metrics

- **{descriptors_refolding.AF2_PRIMARY_IPAE.name}** — Binder–target pose error (predicted) in angstroms. Predicted Aligned Error (residue–residue 
    matrix) averaged over binder→target residue values.
- **{descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.name}** — Cα RMSD of the binder between RFdiffusion output and AF2 prediction (aligned on target)
- **{descriptors_refolding.AF2_PRIMARY_BINDER_PAE.name}** — Binder error (predicted) including the binder–target pose, in angstroms. Predicted Aligned Error 
    <sup>[4]</sup> (residue–residue matrix) averaged over binder→binder and binder→target residue values.

We also include AF2 binder pLDDT and pTM scores.

In RFdiffusion,<sup>[1]</sup> in silico success for binder design was defined as AF2&nbsp;Binder&nbsp;pLDDT >&nbsp;80,
AF2&nbsp;Interface&nbsp;PAE <&nbsp;10 and AF2&nbsp;monomer&nbsp;RMSD <&nbsp;1.0 (we do not include this metric with the
binder predicted in isolation, you could use AF2&nbsp;Binder&nbsp;RMSD which includes the pose RMSD in the complex).

These descriptors are computed for all designs. Additionally, you can run ProteinQC for the accepted designs at
{designs_page.title}, computing descriptors of predicted solubility, electrostatic and hydrophobic patch area, and more.


### Limitations
<!--Binder diversification is -->
- Only one target chain is supported. You may circumvent this by merging multiple chains into a single chain in your
input PDB file, adding residue index jumps (200) between the original chains, this influences both RFdiffusion and
AlphaFold2.
 <!---clipped to -32, 32 in alphafold2, colabdesign adds 50 between binder and target. How are inputs for proteinmpnn
 prepared? It could add 200 residues between the original chains and slow it down (a bit, is not quadratic..) --->

Request more features in our **TODO github issues link**!

### References
1. [RFdiffusion](https://www.nature.com/articles/s41586-023-06415-8) (and [Partial Diffusion GitHub guide](https://github.com/RosettaCommons/RFdiffusion?tab=readme-ov-file#partial-diffusion))
2. Partial diffusion, [Glögl et al. 2024](https://www.science.org/doi/full/10.1126/science.adp1779), Target-conditioned diffusion generates potent TNFR superfamily antagonists and agonists
3. Partial diffusion, [Vázquez Torres et al. 2023](https://www.nature.com/articles/s41586-023-06953-1), De novo design of high-affinity binders of bioactive helical peptides
4. [Predicted Aligned Error (PAE)](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/pae-a-measure-of-global-confidence-in-alphafold-predictions/)
5. [BioPython ProteinAnalysis](https://biopython.org/docs/latest/api/Bio.SeqUtils.ProtParam.html#Bio.SeqUtils.ProtParam.ProteinAnalysis)
6. [PyRosetta descriptors](https://www.science.org/doi/10.1126/science.abn2100#supplementary-materials)
""",
            unsafe_allow_html=True,
        )


@st.fragment
def input_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    left, _, right = st.columns([4, 1, 3])
    with left:
        st.subheader("Input structures")

        if not workflow.rfdiffusion_params.input_pdb_paths:
            st.markdown("##### Start from one or more previous designs")

            initialize_workflow_input()

        elif st.button("Change input"):
            workflow.input_name = None
            workflow.rfdiffusion_params.input_pdb_paths = []
            workflow.rfdiffusion_params.contigs = []
            workflow.rfdiffusion_params.custom_backbones = None
            st.rerun()

    with right:
        history_dropdown_component(
            page_key=__file__,
            workflow_name=RFdiffusionBinderDesignWorkflow.name,
            filter_func=lambda w: w.rfdiffusion_params.partial_diffusion,
        )

    # workflow instance may have been replaced in initialize_workflow(), read it again
    workflow = st.session_state.workflows[__file__]

    if not workflow.rfdiffusion_params.input_pdb:
        # No input structure provided yet, stop here
        return

    if not workflow.rfdiffusion_params.contigs:
        # Input structures were just provided, initialize the parameters derived from them
        try:
            contigs = get_contigs_for_input_structures(workflow.rfdiffusion_params.input_pdb_paths)
        except ValueError as e:
            st.error(e)
            workflow.input_name = None
            workflow.rfdiffusion_params.input_pdb_paths = []
            return
        workflow.preview_job_id = None
        workflow.rfdiffusion_params.partial_diffusion = True
        workflow.rfdiffusion_params.timesteps = 20
        workflow.rfdiffusion_params.num_designs = 10
        # TODO use presets to initialize this instead
        workflow.refolding_params.primary_test = "af2_model_1_multimer_tt_3rec"
        workflow.rfdiffusion_params.contigs = contigs
        st.rerun()

    if workflow.rfdiffusion_params.cyclic_offset:
        st.write(":material/info: Workflow will generate macrocyclic designs")

    st.subheader(workflow.input_name)

    if len(workflow.rfdiffusion_params.input_pdb_paths) > 1:
        indexes = {v: i for i, v in enumerate(workflow.rfdiffusion_params.input_pdb_paths, start=1)}
        page = st.pagination(
            num_pages=len(workflow.rfdiffusion_params.input_pdb_paths),
        )
        input_pdb_path = workflow.rfdiffusion_params.input_pdb_paths[page - 1]
        st.markdown(f"**{input_pdb_path.split('/')[-1]}**")
    else:
        input_pdb_path = workflow.rfdiffusion_params.input_pdb

    pdb_data = storage.read_file_str(input_pdb_path)

    if not workflow.design_ids and not workflow.rfdiffusion_params.cyclic_offset:
        # for user-provided files, show a warning if the input structure looks cyclic, but this workflow does not support it
        if pdb_chain_looks_cyclic(pdb_data, chain_id="A"):
            st.warning(
                "The input structure looks cyclic, but this workflow does not support macrocyclic peptide design. "
                "Please see other available variants of this workflow in the previous step."
            )

    st.markdown(":violet-background[Binder chain shown in pink]")

    viz.molstar(
        viz.StructureVisualization(
            data=pdb_data,
            representations=[
                viz.Representation("A", color="#ffccff"),  # binder chain should always be A at this stage
            ],
        ),
        height=500,
        key="diversification",
    )


def initialize_workflow_input():
    """Ask for the input structures, by design ID or by upload, and set them in the workflow."""
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    design_ids_raw = st.text_area(
        "Design IDs to be diversified",
        placeholder="Enter design IDs separated by spaces, commas, or lines",
        value="\n".join(workflow.design_ids),
        key="design_ids_input",
    )
    design_ids = [design_id.strip() for design_id in design_ids_raw.replace(",", " ").split()]
    # deduplicate but keep original order
    design_ids = list(dict.fromkeys(design_ids))

    if st.button("Confirm") or (design_ids and design_ids != workflow.design_ids):
        designs: list[Design] = db.select(Design, id__in=design_ids)
        if not designs:
            st.error("No designs found for the provided IDs.")
            return
        if missing_ids := (set(design_ids).difference([d.id for d in designs])):
            st.error(f"Designs not found for IDs: {', '.join(missing_ids)}")
            return
        pool_ids = sorted(set(design.pool_id for design in designs))

        workflow.design_ids = design_ids
        workflow.input_name = design_ids[0] if len(design_ids) == 1 else f"{len(design_ids)} designs"
        workflow.rfdiffusion_params.contigs = []

        # This workflow diffuses the binder as chain A, so designs that label it differently
        # (BindCraft labels the binder B) are relabelled
        try:
            workflow.rfdiffusion_params.input_pdb_paths = store_structures_with_binder_as_chain_a(
                designs,
                project_id=st.session_state.project.id,
            )
        except (ValueError, ChainNotFoundError) as e:
            st.error(e)
            return

    # ensure that cyclic input designs produce cyclic designs again
    num_cyclic = get_cached_num_cyclic(design_ids)
    if num_cyclic:
        if num_cyclic != len(design_ids):
            st.error(
                "Cannot submit cyclic and non-cyclic designs together "
                f"({num_cyclic}/{len(design_ids)} designs are cyclic in this selection)"
            )
            workflow.rfdiffusion_params.input_pdb_paths = []
            return
        if not workflow.rfdiffusion_params.cyclic_offset:
            # NOTE we could also set cyclic_offset=True here, but we actually
            # want to use a different implementation of the pipeline here, not the default binder design pipeline,
            # so we force the user to go back and select it
            st.error(
                "The selected designs are cyclic, but this workflow variant does not support cyclic design. "
                "Please select a cyclic workflow variant in the previous step."
            )
            workflow.rfdiffusion_params.input_pdb_paths = []
            return

    st.markdown("##### Or upload a custom structure")

    uploaded_files = st.file_uploader(
        "Upload a structure file with binder chain (A) and target chain (B)",
        type=["pdb", "pdb1", "cif", "mmcif"],
        key="input_pdb_file",
        accept_multiple_files=True,
    )
    if uploaded_files:
        # The binder chain has to be picked in every uploaded structure, which is asked for in a
        # dialog so that it cannot be missed - the structures are stored once it is confirmed
        upload_key = "|".join(uploaded_file.name for uploaded_file in uploaded_files)
        if st.session_state.get(_CANCELLED_UPLOAD_KEY) == upload_key:
            st.warning("No binder chain was selected, so the uploaded structures were not used.")
            if st.button("Select binder chain"):
                st.session_state[_CANCELLED_UPLOAD_KEY] = None
                st.rerun()
        else:
            select_binder_chains_dialog(uploaded_files, upload_key=upload_key)


@st.dialog("Select the binder chain", width="medium")
def select_binder_chains_dialog(uploaded_files: list, upload_key: str):
    """Let the user pick the binder chain of each uploaded structure, store them on confirmation.

    The structures are stored with the binder as chain A, which is the chain this workflow diffuses
    (see :func:`store_structures_with_binder_as_chain_a` for the structures of existing designs).

    :param uploaded_files: files of the st.file_uploader
    :param upload_key: identifier of this set of files, remembered when the dialog is cancelled
    """
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    filename_counts = Counter(
        os.path.splitext(safe_filename(uploaded_file.name))[0] for uploaded_file in uploaded_files
    )
    duplicate_filenames = sorted(filename for filename, count in filename_counts.items() if count > 1)
    if duplicate_filenames:
        st.error(
            f"Uploaded files have duplicate normalized names: {', '.join(duplicate_filenames)}. "
            "Please rename them to have unique names without extensions and upload them again."
        )
        return

    pdb_strs_by_filename = {}
    binder_chains_by_filename = {}
    for uploaded_file in uploaded_files:
        pdb_str = uploaded_file.getvalue().decode("utf-8")
        filename, ext = os.path.splitext(safe_filename(uploaded_file.name))

        if ext.lower() in (".cif", ".mmcif"):
            result = mmcif_to_pdb(pdb_str)
            pdb_str = result.pdb_string
            for warning in result.warnings:
                st.warning(warning)
            st.warning(f"The uploaded CIF file {filename} has been converted to PDB format.")

        seqs_by_chain = get_sequences_from_pdb_str(pdb_str)
        options = {
            chain: f"Chain {chain} ({len(seq)} residues: {truncate_middle(seq, 20)})"
            for chain, seq in seqs_by_chain.items()
        }
        pdb_strs_by_filename[filename] = pdb_str
        binder_chains_by_filename[filename] = st.segmented_control(
            f"Binder chain in {filename}",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            required=True,
            key=f"binder_chain_{filename}",
        )

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            st.session_state[_CANCELLED_UPLOAD_KEY] = upload_key
            st.rerun()
        if st.button("Confirm", type="primary", disabled=not all(binder_chains_by_filename.values())):
            filenames = list(binder_chains_by_filename)
            workflow.design_ids = []
            workflow.input_name = filenames[0] if len(filenames) == 1 else f"{len(filenames)} structures"
            workflow.rfdiffusion_params.contigs = []
            workflow.rfdiffusion_params.custom_backbones = None
            workflow.rfdiffusion_params.input_pdb_paths = [
                store_input_structure_with_binder_chain(
                    pdb_strs_by_filename[filename], binder_chain=binder_chain, filename=filename
                )
                for filename, binder_chain in binder_chains_by_filename.items()
            ]
            st.rerun()


def store_input_structure_with_binder_chain(pdb_str: str, binder_chain: str, filename: str) -> str:
    """Store an uploaded structure with its binder chain relabelled to chain A.

    :param pdb_str: structure in PDB format
    :param binder_chain: chain of the binder in the given structure
    :param filename: filename to store the structure under, without extension
    :return: storage path of the stored structure
    """
    if binder_chain != "A":
        chains = get_sequences_from_pdb_str(pdb_str)
        pdb_str = filter_and_relabel_chains_pdb_str(
            pdb_str, [binder_chain] + [chain for chain in chains if chain != binder_chain]
        )
    return storage.store_input(
        project_id=st.session_state.project.id,
        file_str=pdb_str,
        filename=f"{filename}.pdb",
    )


def get_contigs_for_input_structures(input_pdb_paths: list[str]) -> list[str]:
    """Get the contig of each input structure, with the whole binder redesigned.

    :param input_pdb_paths: storage paths of the input structures, binder as chain A
    :return: one contig per input structure, e.g. "100-100/0 B20-130"
    :raises ValueError: when a structure does not have a binder chain (A) and a target chain (B)
    """
    contigs = []
    for pdb_path in input_pdb_paths:
        chain_contigs = get_chains_and_contigs(storage.read_file_str(pdb_path))
        # read target length 100 from A1-100/0
        chain_ids = sorted(chain_contigs.keys())
        if chain_ids != ["A", "B"]:
            raise ValueError(f"This pipeline expects two chains - binder (A) and target (B), got: {chain_ids}")
        binder_contig = chain_contigs["A"].removeprefix("A").removesuffix("/0")
        if not binder_contig.startswith("1-"):
            raise ValueError(f"Expected binder chain to start with residue 1, got: {chain_contigs['A']}")
        if "/" in binder_contig:
            raise ValueError(f"Expected binder contig to be a single range, got: {binder_contig}")
        binder_length = int(binder_contig.removeprefix("1-"))
        # 100-100/0 B20-130
        contigs.append(f"{binder_length}-{binder_length}/0 {chain_contigs['B']}")
    return contigs


@st.cache_data(max_entries=200, show_spinner=False)
def get_cached_binder_residues(input_pdb_path: str) -> tuple[list[int], str]:
    """Get the residue numbers and the sequence of the binder chain of an input structure."""
    pdb_str = storage.read_file_str(input_pdb_path)
    residues = from_contig_to_residues(get_chains_and_contigs(pdb_str).get(BINDER_CHAIN)) or []
    return residues, get_sequences_from_pdb_str(pdb_str).get(BINDER_CHAIN, "")


@st.cache_data(max_entries=200, show_spinner=False)
def get_cached_contact_residues(input_pdb_path: str, distance_cutoff: float) -> list[int]:
    """Get the binder residues of an input structure that are in contact with the target."""
    return get_contact_residues(storage.read_file_str(input_pdb_path), BINDER_CHAIN, distance_cutoff=distance_cutoff)


@st.cache_data(max_entries=200, show_spinner=False)
def get_cached_binder_plddt(input_pdb_path: str) -> dict[int, float]:
    """Get the pLDDT of each binder residue of an input structure, empty if it has none.

    Read from the B-factor column, which only a predicted structure fills in - a structure where it
    is constant has no pLDDT. The values are returned as percentages, however the file scaled them.
    """
    plddt_by_residue = get_residue_b_factors(storage.read_file_str(input_pdb_path), BINDER_CHAIN)
    if len(set(plddt_by_residue.values())) <= 1:
        return {}
    if max(plddt_by_residue.values()) <= 1:
        return {residue: value * 100 for residue, value in plddt_by_residue.items()}
    return plddt_by_residue


@st.dialog("Modify selection", width="medium")
def selection_action_dialog(operation: str, action: str):
    """Let the user review the residues of a set before adding, removing or intersecting them.

    The set applies to all inputs at once - repeating an action per input would be the point of pain
    with a hundred of them - so it is worked out per input, from its own structure, and the preview
    reports what the operation would do to each of them.

    The selection is kept on the workflow as the designed segments of the binder contig, so applying
    the operation only has to write the new set of binder residues back. The molstar component of
    :func:`selection_step` is re-created to pick it up, see ``_SELECTION_RESET_KEY``.
    """
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]
    input_pdb_paths = workflow.rfdiffusion_params.input_pdb_paths

    st.write(f"**{operation} - {action.lower()}**")
    st.write(f"{SELECTION_OPERATION_HELP[operation]}. {SELECTION_ACTION_DESCRIPTIONS[action]}")
    if len(input_pdb_paths) > 1:
        st.caption(f"Applied to all {len(input_pdb_paths)} inputs.")

    # Parameters of the set, the same for every input - the residues they match are not
    distance_cutoff = None
    plddt_threshold = None
    amino_acids = []
    if action in (CONTACT_RESIDUES, NON_CONTACT_RESIDUES):
        distance_cutoff = st.number_input(
            "Cα contact distance (Å)",
            min_value=1.0,
            max_value=20.0,
            value=10.0,
            step=0.5,
            help="A residue is in contact when its Cα is within this distance of a Cα of the target, "
            "the same definition the backbone contact descriptors use.",
        )
    elif action == LOW_PLDDT_RESIDUES:
        inputs_without_plddt = [path for path in input_pdb_paths if not get_cached_binder_plddt(path)]
        if len(inputs_without_plddt) == len(input_pdb_paths):
            st.warning(
                "These inputs have no pLDDT values - they are read from the B-factor column, which "
                "only a predicted structure fills in."
            )
            return
        if inputs_without_plddt:
            st.warning(f"{len(inputs_without_plddt)} of the inputs have no pLDDT and match no residues.")
        plddt_threshold = st.slider("pLDDT below", min_value=0, max_value=100, value=70, step=5)
    elif action == AMINO_ACID_RESIDUES:
        amino_acid_counts = Counter(
            amino_acid for path in input_pdb_paths for amino_acid in get_cached_binder_residues(path)[1]
        )
        preset = st.selectbox("Preset", options=list(AMINO_ACID_PRESETS), index=None, key="aa_preset")
        if preset is None:
            # A preset has to be picked before there is anything to apply, "Custom" starts from nothing
            return
        amino_acids = st.multiselect(
            "Amino acids",
            options=sorted(amino_acid_counts),
            # A preset only fills in the default, the list stays editable - hence the key per preset
            default=[amino_acid for amino_acid in AMINO_ACID_PRESETS[preset] if amino_acid in amino_acid_counts],
            format_func=lambda amino_acid: f"{amino_acid} ({amino_acid_counts[amino_acid]}x)",
            key=f"aa_types_{preset}",
        )

    # What the operation would select in each input, evaluated against its own structure
    new_segments_by_index = {}
    rows = []
    for contig_index, input_pdb_path in enumerate(input_pdb_paths):
        binder_residues, sequence = get_cached_binder_residues(input_pdb_path)
        selected = set(
            from_contig_to_residues(
                "/".join(workflow.get_selected_segments(contig_index=contig_index, partial_diffusion=True))
            )
            or []
        )

        if action == ALL_RESIDUES:
            matched = set(binder_residues)
        elif action == CONTACT_RESIDUES:
            matched = set(get_cached_contact_residues(input_pdb_path, distance_cutoff))
        elif action == NON_CONTACT_RESIDUES:
            matched = set(binder_residues) - set(get_cached_contact_residues(input_pdb_path, distance_cutoff))
        elif action == LOW_PLDDT_RESIDUES:
            matched = {
                residue for residue, plddt in get_cached_binder_plddt(input_pdb_path).items() if plddt < plddt_threshold
            }
        else:
            matched = {residue for residue, amino_acid in zip(binder_residues, sequence) if amino_acid in amino_acids}

        matched = matched.intersection(binder_residues)
        new_selected = SELECTION_OPERATIONS[operation](selected, matched)
        new_segments_by_index[contig_index] = from_residues_to_segments(BINDER_CHAIN, sorted(new_selected))
        rows.append(
            {
                "Input": os.path.basename(input_pdb_path),
                "Length": len(binder_residues),
                "Matched": len(matched),
                "Before": len(selected),
                "After": len(new_selected),
                "Sequence": "".join(
                    amino_acid.upper() if residue in new_selected else amino_acid.lower()
                    for residue, amino_acid in zip(binder_residues, sequence)
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        height=min(250, 70 + 35 * len(rows)),
        column_config={
            "Length": st.column_config.NumberColumn(help="Number of residues in the binder chain"),
            "Matched": st.column_config.NumberColumn(help=f"Number of residues matched by: {action}"),
            "Before": st.column_config.NumberColumn(help="Number of residues redesigned before the operation"),
            "After": st.column_config.NumberColumn(help="Number of residues redesigned after the operation"),
            "Sequence": st.column_config.TextColumn(
                help="Binder sequence after the operation, with the redesigned residues in uppercase "
                "and the ones kept fixed in lowercase"
            ),
        },
    )

    empty_inputs = [row["Input"] for row, segments in zip(rows, new_segments_by_index.values()) if not segments]
    if empty_inputs:
        # Allowed, such an input is left out of the submission - see get_skipped_contig_indexes
        st.info(
            f"Nothing will be redesigned in {len(empty_inputs)} of the inputs "
            f"({', '.join(empty_inputs[:3])}{', ...' if len(empty_inputs) > 3 else ''}), "
            f"so they will be skipped when submitting."
        )

    # Equal residue counts do not mean the same residues, so the selections themselves are compared
    unchanged = all(
        new_segments == workflow.get_selected_segments(contig_index=contig_index, partial_diffusion=True)
        for contig_index, new_segments in new_segments_by_index.items()
    )
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            st.rerun()
        if st.button(operation, type="primary", disabled=unchanged):
            for contig_index, segments in new_segments_by_index.items():
                workflow.set_selected_segments(segments, contig_index=contig_index, partial_diffusion=True)
            # Re-create the molstar component, so that it shows the selection instead of the old one
            st.session_state[_SELECTION_RESET_KEY] = st.session_state.get(_SELECTION_RESET_KEY, 0) + 1
            st.rerun()


@st.fragment()
def selection_step():
    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]

    st.subheader("Select residues to be redesigned")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    if not workflow.rfdiffusion_params.contig:
        st.error("Please provide a contig in the previous step.")
        return

    st.write(
        "Select binder residues that should be redesigned. By default, we redesign the entire binder. "
        "How they are redesigned is picked in the next step."
    )

    selected_operation = None
    with st.container(horizontal=True, vertical_alignment="center", gap=5):
        st.write(":grey[Modify selection]")
        for operation in SELECTION_OPERATIONS:
            if action := st.menu_button(
                operation,
                options=SELECTION_ACTIONS,
                key=f"selection_operation_{operation}",
            ):
                selected_operation = (operation, action)

    if selected_operation:
        # Opened outside of the container above, a dialog is an overlay rather than part of the layout
        selection_action_dialog(*selected_operation)

    with st.container(horizontal=True, vertical_alignment="center", gap=5):
        if len(workflow.rfdiffusion_params.contigs) > 1:
            st.write(":grey[Input]")
            page = st.pagination(len(workflow.rfdiffusion_params.contigs), key="sel_page")
        else:
            page = 1

        input_name = workflow.get_input_pdb_path(page - 1).split("/")[-1]
        st.write(input_name)

    # Nothing selected means nothing to redesign, so that input is left out of the submission
    skipped_contig_indexes = workflow.get_skipped_contig_indexes()
    if page - 1 in skipped_contig_indexes:
        st.warning("No residues are selected, so this input will be skipped when submitting.")
    elif skipped_contig_indexes:
        st.caption(
            f":material/info: {len(skipped_contig_indexes)} of the inputs have no residues selected "
            f"and will be skipped: {', '.join(str(index + 1) for index in skipped_contig_indexes)}"
        )

    sequence_selection_fragment(
        __file__,
        input_name,
        contig_index=page - 1,
        partial_diffusion=True,
        selection_label="Residues to be redesigned",
        input_key=f"selection_{page - 1}_{st.session_state.get(_SELECTION_RESET_KEY, 0)}",
        # Undo only covers the input it is shown for, which would be misleading next to actions that
        # apply to all of them - see selection_action_dialog
        history=len(workflow.rfdiffusion_params.contigs) == 1,
    )


@st.fragment()
def sequence_design_step():
    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]

    st.subheader("Sequence design")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    with st.columns([1, 1])[0]:
        protocol = st.segmented_control(
            "Protocol",
            options=list(PROTOCOL_DESCRIPTIONS),
            default=SEQUENCE_REDESIGN_PROTOCOL
            if workflow.rfdiffusion_params.custom_backbones
            else PARTIAL_DIFFUSION_PROTOCOL,
            required=True,
            key="diversification_protocol",
        )
    # The input structures are submitted as custom backbones when they are not diffused, which skips
    # backbone design in the pipeline and redesigns their sequence as they are
    workflow.rfdiffusion_params.custom_backbones = (
        list(workflow.rfdiffusion_params.input_pdb_paths) if protocol == SEQUENCE_REDESIGN_PROTOCOL else None
    )

    st.write(PROTOCOL_DESCRIPTIONS[protocol])

    if protocol == PARTIAL_DIFFUSION_PROTOCOL:
        show_rfdiffusion_timesteps_input(workflow)

    with st.columns([1, 1])[0]:
        show_mpnn_sequence_design_inputs(workflow)


@st.fragment()
def preview_step():
    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]
    st.subheader("Preview design")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    st.write(f"Using contig: {workflow.rfdiffusion_params.contig}")

    # Generate preview
    st.write("#### Generate preview")

    submit_rfdiffusion_preview_component(workflow, timesteps=10)

    # Check if needed parameters are set
    if not workflow.preview_job_id:
        return

    # Wait until task is done
    result = wait_with_statusbar(local_scheduler, workflow.preview_job_id, label="Running RFdiffusion...")

    # Exit if job failed
    if not result:
        return

    visualize_rfdiffusion_preview(workflow, output_dir=local_scheduler.get_output_dir(workflow.preview_job_id))


@st.fragment()
def settings_step():
    st.subheader("Settings")

    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    pool_submission_inputs(__file__)

    # No backbone is designed when the input structures are submitted as custom backbones, so the
    # parameters of RFdiffusion do not apply, see selection_step
    backbone_design = not workflow.rfdiffusion_params.custom_backbones

    if backbone_design:
        show_rfdiffusion_backbone_design_inputs(workflow, suffix=" per each input structure")

    show_rfdiffusion_binder_seq_design_inputs(workflow)

    if backbone_design:
        with st.columns([1, 2])[0]:
            workflow.rfdiffusion_params.model_weights = st.radio(
                "Model weights",
                help="Use 'active site' model weights to hold better selected residues specified in the contig.",
                index=MODEL_WEIGHTS_BINDER.index(workflow.rfdiffusion_params.model_weights)
                if workflow.rfdiffusion_params.model_weights
                else 0,
                key="active_site",
                options=MODEL_WEIGHTS_BINDER,
            )

    with st.columns([1, 2])[0]:
        workflow.rfdiffusion_params.hotspots = st.text_input(
            "Hotspot residues (optional)",
            placeholder="For example B123,B124,B131",
            value=workflow.rfdiffusion_params.hotspots,
            key="hotspots",
        )
        if workflow.rfdiffusion_params.hotspots:
            if not all(
                re.fullmatch("[A-Z][0-9]+", hotspot) for hotspot in workflow.rfdiffusion_params.hotspots.split(",")
            ):
                st.error("Invalid hotspots format, expected 'B123,B124,B131'")

    # TODO carry over hotspots from original design if applicable
    if not workflow.rfdiffusion_params.hotspots:
        st.write("""
        :material/info: Note that any hotspots used in the original design were not carried over.
        Hotspots should be specified in the context of the designed structure (binder in chain A, target in chain B).
        """)

    show_rfdiffusion_advanced_settings(workflow, backbone_design=backbone_design)


@st.fragment
def review_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    st.subheader("Review settings")

    # The inputs with nothing to redesign are left out of the submission, but kept on the page, so
    # that going back to the selection step can still select residues in them
    skipped_inputs = [
        os.path.basename(workflow.get_input_pdb_path(contig_index))
        for contig_index in workflow.get_skipped_contig_indexes()
    ]
    if len(skipped_inputs) == len(workflow.get_contig_indexes()):
        st.error(
            "No residues are selected for redesign in any of the inputs. "
            "Please select the residues to redesign in the selection step."
        )
        return
    if skipped_inputs:
        st.warning(
            f"{len(skipped_inputs)} of the inputs have no residues selected for redesign and will be "
            f"skipped: {', '.join(skipped_inputs)}"
        )

    review_workflow_submission(__file__, workflow=workflow.drop_skipped_inputs())


if __name__ == "__main__":
    initialize_page(page_title="Binder diversification")

    sections = {
        "intro": intro_step,
        "input": input_step,
        "selection": selection_step,
        "sequence design": sequence_design_step,
        "preview": preview_step,
        "settings": settings_step,
        "review": review_step,
    }
    workflow = st.session_state.get("workflows", {}).get(__file__)
    if workflow and workflow.rfdiffusion_params.custom_backbones:
        # Nothing to preview when no backbone is designed, see selection_step
        del sections["preview"]

    show_prev_next_sections(
        key=__file__,
        title="♻️ Binder diversification",
        sections=sections,
    )
