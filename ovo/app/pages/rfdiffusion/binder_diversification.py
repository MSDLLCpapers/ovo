import os
import re
from copy import deepcopy

import streamlit as st

from ovo.app.components.history_components import history_dropdown_component
from ovo.app.components.input_components import sequence_selection_fragment, initialize_workflow
from ovo.app.components.molstar_custom_component import molstar_custom_component, StructureVisualization
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.preview_components import visualize_rfdiffusion_preview
from ovo.app.components.scheduler_components import wait_with_statusbar
from ovo.app.components.submission_components import (
    pool_submission_inputs,
    review_workflow_submission,
    show_rfdiffusion_binder_seq_design_inputs,
)

from ovo.app.pages import jobs_page, designs_page, rf_binder_design_page
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
)
from ovo.app.components.submission_components import show_rfdiffusion_advanced_settings
from ovo.core.database import descriptors_rfdiffusion, descriptors_refolding
from ovo.core.database.models import WorkflowTypes, Pool, DesignJob
from ovo.core.logic.design_logic_rfdiffusion import submit_rfdiffusion_preview
from ovo.core.utils.formatting import get_hashed_path_for_bytes, safe_filename
from ovo.core.utils.residue_selection import get_chains_and_contigs


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

You can run this workflow as a next step after {rf_binder_design_page.title} — besides partial diffusion, the methods and computed 
metrics are the same.

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

            if initialize_workflow_input():
                # Input structure was just provided, generate contigs and rerun
                # workflow instance was updated in initialize_workflow(), read it again
                workflow = st.session_state.workflows[__file__]
                workflow.preview_job_id = None
                workflow.rfdiffusion_params.partial_diffusion = True
                workflow.rfdiffusion_params.timesteps = 20
                workflow.rfdiffusion_params.num_designs = 10
                # TODO use presets to initialize this instead
                workflow.refolding_params.primary_test = "af2_model_1_multimer_tt_3rec"

                # Generate a contig for each input file
                workflow.rfdiffusion_params.contigs = []
                for pdb_path in workflow.rfdiffusion_params.input_pdb_paths:
                    chain_contigs = get_chains_and_contigs(storage.read_file_str(pdb_path))
                    # read target length 100 from A1-100/0
                    chain_ids = sorted(chain_contigs.keys())
                    try:
                        assert chain_ids == ["A", "B"], (
                            f"This pipeline expects two chains - binder (A) and target (B), got: {chain_ids}"
                        )
                        assert chain_contigs["A"].removeprefix("A").startswith("1-"), (
                            f"Expected binder chain to start with residue 1, got: {chain_contigs['A']}"
                        )
                        binder_len = int(chain_contigs["A"].removeprefix("A").removeprefix("1-").removesuffix("/0"))
                        # 100-100/0 B20-130
                        workflow.rfdiffusion_params.contigs.append(f"{binder_len}-{binder_len}/0 {chain_contigs['B']}")
                    except Exception as e:
                        st.error(e)
                        workflow.rfdiffusion_params.input_name = None
                        workflow.rfdiffusion_params.input_pdb_paths = []
                        st.stop()
                        return

                st.rerun()

        elif st.button("Change input"):
            workflow.input_name = None
            workflow.rfdiffusion_params.input_pdb_paths = []
            st.rerun()

    with right:
        history_dropdown_component(
            page_key=__file__,
            workflow_name=RFdiffusionBinderDesignWorkflow.name,
            filter_func=lambda w: w.rfdiffusion_params.partial_diffusion,
        )

    if not workflow.rfdiffusion_params.input_pdb:
        # No input structure provided yet, stop here
        return

    st.subheader(workflow.input_name)

    if len(workflow.rfdiffusion_params.input_pdb_paths) > 1:
        indexes = {v: i for i, v in enumerate(workflow.rfdiffusion_params.input_pdb_paths, start=1)}
        input_pdb_path = st.selectbox(
            "Visualize input",
            options=workflow.rfdiffusion_params.input_pdb_paths,
            format_func=lambda x: f"{indexes[x]} | {x.split('/')[-1].removesuffix('.pdb')}",
        )
    else:
        input_pdb_path = workflow.rfdiffusion_params.input_pdb

    molstar_custom_component(
        structures=[StructureVisualization(pdb=storage.read_file_str(input_pdb_path))],
        height=500,
        key="diversification",
    )


def initialize_workflow_input() -> RFdiffusionBinderDesignWorkflow | None:
    workflow = st.session_state.workflows[__file__]

    design_ids_raw = st.text_area(
        "Design IDs to be diversified",
        placeholder="Enter design IDs separated by spaces, commas, or lines",
        value="\n".join(workflow.design_ids),
    )
    design_ids = [design_id.strip() for design_id in design_ids_raw.replace(",", " ").split()]

    if st.button("Confirm"):
        designs: list[Design] = db.select(Design, id__in=design_ids)
        if not designs:
            st.error("No designs found for the provided IDs.")
            return False
        if missing_ids := (set(design_ids).difference([d.id for d in designs])):
            st.error(f"Designs not found for IDs: {', '.join(missing_ids)}")
            return False
        pool_ids = sorted(set(design.pool_id for design in designs))

        # Get rfdiffusion params (use arbitrary pool in case of multiple pools)
        rfdiffusion_params = None
        source_workflow_names = set()
        for pool_id in pool_ids:
            pool = db.get(Pool, pool_id)
            if not pool.design_job_id:
                continue
            design_job = db.get(DesignJob, id=pool.design_job_id)
            if not design_job.workflow or not design_job.workflow.is_instance(RFdiffusionBinderDesignWorkflow):
                continue
            source_workflow_names.add(design_job.workflow.name)
            if rfdiffusion_params is None:
                rfdiffusion_params = deepcopy(design_job.workflow.rfdiffusion_params)

        assert source_workflow_names, "Designs do not come from RFdiffusion binder design workflow"
        assert len(source_workflow_names) == 1, (
            f"Expected all designs to come from the same workflow, got: {', '.join(source_workflow_names)}"
        )
        source_workflow_name = source_workflow_names.pop()
        if source_workflow_name != workflow.name:
            # Designs can come from a subclass of the current workflow, create appropriate workflow instance
            workflow = WorkflowTypes.get(source_workflow_name)()
            st.session_state.workflows[__file__] = workflow
        workflow.input_name = design_ids[0] if len(design_ids) == 1 else f"{len(design_ids)} designs"
        workflow.design_ids = design_ids
        workflow.rfdiffusion_params = rfdiffusion_params
        # Use ProteinMPNN path, the RFdiffusion PDB does not have any sidechain coords (even on the target chain)
        workflow.rfdiffusion_params.input_pdb_paths = [design.structure_path for design in designs]
        # Do not preserve the original hotspots - they are not correct anymore.
        # We could parse them from the standardized PDB but from which design? The first one?
        # We should just expose it to the user in the UI so they get visibility on it.
        workflow.rfdiffusion_params.hotspots = None

    st.markdown("##### Or upload a custom structure")

    uploaded_file = st.file_uploader(
        "Upload a PDB file with binder chain (A) and target chain (B)",
        type=["pdb", "pdb1"],
        key="input_pdb_file",
    )

    # Check if a file has just been uploaded
    if uploaded_file is not None:
        pdb_input_bytes = uploaded_file.getvalue()
        filename, _ = os.path.splitext(safe_filename(uploaded_file.name))
        workflow.input_name = filename
        workflow.rfdiffusion_params.input_pdb = storage.store_file_str(
            pdb_input_bytes.decode("utf-8"),
            f"project/{st.session_state.project.id}/inputs/{get_hashed_path_for_bytes(pdb_input_bytes)}/{workflow.input_name}.pdb",
            overwrite=False,
        )

    if workflow.rfdiffusion_params.input_pdb_paths:
        return workflow
    else:
        return None


@st.fragment()
def selection_step():
    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]

    st.subheader("Select residues for partial diffusion")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    if not workflow.rfdiffusion_params.contig:
        st.error("Please provide a contig in the previous step.")
        return

    if len(workflow.rfdiffusion_params.contigs) > 1:
        #
        # TODO support residue selection for multiple inputs
        #
        st.warning(
            "Selection of residues is not yet supported when multiple input structures are provided. "
            "Whole binder will be redesigned."
        )
        return

    sequence_selection_fragment(
        __file__,
        workflow.input_name,
        contig_index=0,
        partial_diffusion=True,
        selection_help=(
            "Select binder residues that should be redesigned by applying RFdiffusion partial diffusion "
            "followed by ProteinMPNN sequence design. By default, we redesign the entire binder."
        ),
        selection_label="Residues to be redesigned",
    )


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
    num_timesteps = 10
    with st.columns([2, 1])[0]:
        st.write(f"""
        Generate a quick RFdiffusion preview of the design with {num_timesteps} partial diffusion timesteps to verify your inputs.

        This should take 2-10 minutes depending on the length of the target and binder.
        """)

    if st.button(":material/wand_stars: Generate preview"):
        with st.spinner("Submitting RFdiffusion job..."):
            workflow.preview_job_id = submit_rfdiffusion_preview(
                workflow, partial_diffusion=True, timesteps=num_timesteps
            )

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

    with st.columns([1, 2])[0]:
        is_admin = get_username() in config.auth.admin_users
        workflow.rfdiffusion_params.num_designs = st.number_input(
            "Number of structure designs (RFdiffusion backbones) per each input structure",
            min_value=1,
            max_value=config.props.rfdiffusion_backbones_limit_admin
            if is_admin
            else config.props.rfdiffusion_backbones_limit,
            value=workflow.rfdiffusion_params.num_designs,
            key="num_designs",
        )

    show_rfdiffusion_binder_seq_design_inputs(workflow)

    with st.columns([1, 2])[0]:
        workflow.rfdiffusion_params.model_weights = st.selectbox(
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

    show_rfdiffusion_advanced_settings(workflow)


@st.fragment
def review_step():
    st.subheader("Review settings")

    review_workflow_submission(__file__)


if __name__ == "__main__":
    initialize_page(page_title="Binder diversification")

    show_prev_next_sections(
        key=__file__,
        title="♻️ Binder diversification",
        sections={
            "intro": intro_step,
            "input": input_step,
            "selection": selection_step,
            "preview": preview_step,
            "settings": settings_step,
            "review": review_step,
        },
    )
