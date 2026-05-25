import streamlit as st

from ovo.app.components.history_components import history_dropdown_component
from ovo.app.components.input_components import pdb_input_component, sequence_selection_fragment, initialize_workflow
from ovo import viz
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.submission_components import (
    pool_submission_inputs,
    show_bindcraft_advanced_settings,
    review_workflow_submission,
)

from ovo.app.pages import jobs_page, designs_page
from ovo.app.utils.page_init import initialize_page
from ovo import storage
from ovo.core.database.models_bindcraft import BindCraftBinderDesignWorkflow
from ovo.core.utils.formatting import get_hashed_path_for_bytes
from ovo.core.utils.residue_selection import get_chains_and_contigs


@st.fragment
def intro_step():
    # Initialize the workflow object in session state
    initialize_workflow(__file__, BindCraftBinderDesignWorkflow.name)

    with st.container(width=850):
        st.markdown(
            f"""
Miniprotein binder design using BindCraft.<sup>[1]</sup> BindCraft is a binder design pipeline using AlphaFold2<sup>[2]</sup>
backpropagation via ColabDesign<sup>[3]</sup>, followed by ProteinMPNN<sup>[4]</sup> surface sequence design, and PyRosetta<sup>[5]</sup> scoring.

Use case: Designing linear peptide or miniprotein binders to a target protein.
           
- **Input**
    - Target protein structure (PDB file or UniProt ID)
- **Main parameters**
    - Target chain
    - Binder length range (peptide to miniprotein)
    - Number of final *accepted* designs to generate, and a time limit
    - (Optional) Hotspot residues to select a preferred binding site
    - (Optional) Design protocol (Default, Beta-sheet, Peptide)
    - (Optional) Filtering settings
- **Output**
    - Designs — binder sequences and structures in complex with target protein
    - Design descriptors from BindCraft
        - Refolding metrics
        - PyRosetta descriptors
        - Secondary structure

### Features
        
After inputting your target structure, you can choose the desired binding site by selecting "hotspot" residues, 
or you can leave it blank to allow binding anywhere on the target surface. Next, you can specify optional advanced settings,
including the design protocol and filtering settings before submitting your job. 

Once the Bindcraft workflow has finished, you will see all generated designs (rejected and accepted by final filters) and their descriptors 
in {jobs_page.title} results page. 
Designs that pass BindCraft filters will be marked as *accepted designs* and shown in {designs_page.title} page, where
you can run ProteinQC, computing descriptors of predicted solubility, electrostatic and hydrophobic patch area, and more.    

The BindCraft workflow has three parts — a design phase, sequence redesign phase, and a filtering phase. 

The **design phase** iteratively refines a binder, starting from a random sequence, with AlphaFold2 (the multimer model) optimizing the
AlphaFold2 confidence metrics, binder-target contacts, and other differentiable objectives. 
By default, the 4-stage protocol is used, which has been validated by
the authors across several targets. Only if BindCraft fails to produce successful designs, the authors suggest tweaking
the design settings (see BindCraft supplement for details). With the exception of peptide binders (8–25
residues): The authors recommend the peptide-specific design (3-stage protocol) and filtering settings. 
                
The **sequence redesign phase** resamples the sequence of the non-interface residues using SolubleMPNN (by default; or
ProteinMPNN). It has been shown to improve expression and solubility compared to using the AlphaFold2-hallucinated
sequences alone.

The **filtering phase** uses the AlphaFold2 monomer model (by default), which has not seen multimer interfaces in its training
data, and checks that "the interface is sufficiently well-defined to be detected even by a model that has never been
exposed to multimeric complexes." Besides filtering for high confidence metrics, it verifies the RMSD between the
original hallucinated binder pose with AF2 multimer and the MPNN-redesigned AF2-monomer repredicted binder (AF2 Hotspot
RMSD) is sufficiently low. The default filters also filter out unstructured binders (by secondary structure), enforce
a number of interface residue contacts, etc. The designs that pass BindCraft filters are automatically marked as accepted.

BindCraft refolding metrics are similar to those in the RFdiffusion workflow, with the addition of binder metrics
computed using AF2 prediction of the binder alone — e.g. AF2 Binder pLDDT, or AF2 Binder-aligned Binder RMSD. Here the binder-only
structural model is compared to the binder in the design trajectory, the complex. (Note that this definition is different to
the metric with the same name in RFdiffusion workflow.) 
        
### Limitations

- ⚠️ **BindCraft is shown to be more compute efficient than RFdiffusion** with respect to the number of accepted designs, 
  but it is more memory intensive due to using multiple AlphaFold2 model weights concurrently. If you encounter out-of-memory errors,
  please try trimming the target chain or configuring your scheduler to use a larger GPU instance.
- ⚠️ **Discarded trajectories are not saved in OVO storage**. Please inspect the OVO workdir of your job if you need them (you will need access to the filesystem).
- ⚠️ We preserve both the rejected and accepted designs for your inspection, 
  but unlike in our RFdiffusion workflow, **BindCraft filter thresholds cannot be changed after job submission**.

### References 
1. [BindCraft](https://www.nature.com/articles/s41586-025-09429-6), [BindCraft GitHub](https://github.com/martinpacesa/BindCraft)
2. [AlphaFold2](https://www.nature.com/articles/s41586-021-03819-2)
3. [ColabDesign](https://github.com/sokrypton/ColabDesign)
4. [ProteinMPNN](https://www.science.org/doi/10.1126/science.add2187)
5. [PyRosetta](https://github.com/RosettaCommons/PyRosetta.notebooks)
""",
            unsafe_allow_html=True,
        )


@st.fragment
def input_step():
    workflow: BindCraftBinderDesignWorkflow = st.session_state.workflows[__file__]

    left, _, right = st.columns([4, 1, 3])
    with left:
        st.subheader("Input structure")

        if not workflow.bindcraft_params.input_pdb_path:
            if new_pdb_input := pdb_input_component(""):
                input_name, pdb_input_bytes = new_pdb_input
                workflow.selected_segments = None
                workflow.input_name = input_name
                workflow.bindcraft_params.hotspots = None
                workflow.bindcraft_params.input_pdb_path = storage.store_file_str(
                    pdb_input_bytes.decode(),
                    f"project/{st.session_state.project.id}/inputs/{get_hashed_path_for_bytes(pdb_input_bytes)}/{workflow.input_name}.pdb",
                    overwrite=False,
                )
                workflow.chains = get_chains_and_contigs(pdb_input_bytes.decode())
                st.rerun()
        elif st.button("Change input"):
            workflow.input_name = None
            workflow.set_selected_segments(None)
            workflow.bindcraft_params.input_pdb_path = None
            st.rerun()

    with right:
        history_dropdown_component(__file__, workflow_name=BindCraftBinderDesignWorkflow.name)

    if not workflow.bindcraft_params.input_pdb_path:
        # No input structure provided yet, stop here
        return

    st.subheader(workflow.input_name)

    viz.molstar(
        viz.StructureVisualization(
            data=storage.read_file_str(workflow.bindcraft_params.input_pdb_path), color="chain-id"
        ),
        key="input_structure",
    )


@st.fragment
def hotspots_step():
    workflow: BindCraftBinderDesignWorkflow = st.session_state.workflows[__file__]

    st.subheader("Select binding hotspots")

    if not workflow.bindcraft_params.input_pdb_path:
        st.error("Please provide an input structure in the input structure step.")
        return

    sequence_selection_fragment(__file__, workflow.input_name, color="hydrophobicity", write_segments=False)


@st.fragment()
def settings_step():
    st.subheader("Settings")

    workflow: BindCraftBinderDesignWorkflow = st.session_state.workflows[__file__]

    if not workflow.bindcraft_params.input_pdb_path:
        st.error("Please provide an input structure in the input structure step.")
        return

    pool_submission_inputs(__file__)

    with st.columns([1, 2])[0]:
        if workflow.bindcraft_params.target_chains is None and len(workflow.chains) == 1:
            # If there is only one chain, set it as the default target chain
            workflow.bindcraft_params.target_chains = list(workflow.chains.keys())[0]

        workflow.bindcraft_params.target_chains = st.text_input(
            "Target chain(s)",
            value=workflow.bindcraft_params.target_chains,
            key="target_chains",
            help="Which chains of your PDB to target? Can be one or multiple, in a comma-separated format. Other chains will be ignored during design.",
        )
        if len(workflow.chains) > 1:
            st.write(f"*Available chains: {','.join(workflow.chains.keys())}*")

        workflow.bindcraft_params.binder_length = st.text_input(
            "Binder length",
            value=workflow.bindcraft_params.binder_length,
            key="binder_length",
            help="Comma-separated range of minimum and maximum number of residues in designed binder. Length of each design will be uniformly sampled from this range.",
        )

        workflow.bindcraft_params.hotspots = st.text_input(
            "Hotspot residues (optional)", value=workflow.bindcraft_params.hotspots, key="hotspots"
        )

        workflow.bindcraft_params.num_replicas = st.number_input(
            "Number of parallel replicas (GPU jobs)",
            value=workflow.bindcraft_params.num_replicas,
            key="num_replicas",
            min_value=1,
            max_value=20,
        )

        workflow.bindcraft_params.number_of_final_designs = st.number_input(
            "Desired number of final designs passing all filters (per replica)",
            value=workflow.bindcraft_params.number_of_final_designs,
            key="number_of_final_designs",
            min_value=0,
        )

        workflow.bindcraft_params.time_limit_hours = st.number_input(
            "Time limit (hours)",
            value=workflow.bindcraft_params.time_limit_hours,
            key="time_limit_hours",
            max_value=24 * 14,
        )
        summary = (
            f"**Summary:** Will run {workflow.bindcraft_params.num_replicas} parallel replicas, each stopping when it reaches "
            f"the time limit of {workflow.bindcraft_params.time_limit_hours} hours or when it generates "
            f"{workflow.bindcraft_params.number_of_final_designs} accepted designs. "
        )
        if workflow.bindcraft_params.num_replicas > 1:
            summary += f"Total number of accepted designs can be up to {workflow.bindcraft_params.num_replicas * workflow.bindcraft_params.number_of_final_designs}."
        st.write(summary)

        if workflow.bindcraft_params.num_replicas > 1 and workflow.bindcraft_params.time_limit_hours:
            st.caption(
                f"Each replica will run up to {workflow.bindcraft_params.time_limit_hours} hours. Total runtime may be longer in case when all replicas cannot run in parallel."
            )

        # Dropdowns for user selections
        workflow.bindcraft_params.design_protocol = st.selectbox(
            "Which binder design protocol to run?",
            options=["Default", "Beta-sheet", "Peptide"],
            help=(
                '"Default" is recommended. '
                '"Beta-sheet" promotes the design of more beta-sheeted proteins, but requires more sampling. '
                '"Peptide" is optimized for helical peptide binders.'
            ),
        )

        workflow.bindcraft_params.prediction_protocol = st.selectbox(
            "What prediction protocol to use?",
            options=["Default", "HardTarget"],
            help=(
                '"Default" performs single-sequence prediction of the binder. '
                '"HardTarget" uses an initial guess to improve complex prediction for difficult targets, but may introduce bias.'
            ),
        )

        workflow.bindcraft_params.interface_protocol = st.selectbox(
            "What interface design method to use?",
            options=["AlphaFold2", "MPNN"],
            help=(
                '"AlphaFold2" is the default; the interface is generated by AlphaFold2. '
                '"MPNN" uses soluble MPNN to optimize the interface.'
            ),
        )

        workflow.bindcraft_params.template_protocol = st.selectbox(
            "What target template protocol to use?",
            options=["Default", "Masked"],
            help=(
                '"Default" allows for limited flexibility. '
                '"Masked" allows for greater target flexibility on both sidechain and backbone levels.'
            ),
        )

        types = ["Default", "Peptide", "Relaxed", "Peptide_Relaxed", "None"]

        workflow.bindcraft_params.filter_type = st.selectbox(
            "Filtering",
            key="filtering",
            options=types,
            index=(
                types.index(workflow.bindcraft_params.filter_type)
                if workflow.bindcraft_params.filter_type in types
                else 0
            ),
        )

    show_bindcraft_advanced_settings(workflow)


@st.fragment
def review_step():
    st.subheader("Review settings")

    review_workflow_submission(__file__)


if __name__ == "__main__":
    initialize_page(page_title="BindCraft binder design")

    show_prev_next_sections(
        key=__file__,
        title="️⚒️ BindCraft binder design",
        sections={
            "intro": intro_step,
            "input": input_step,
            "hotspots": hotspots_step,
            "settings": settings_step,
            "review": review_step,
        },
    )
