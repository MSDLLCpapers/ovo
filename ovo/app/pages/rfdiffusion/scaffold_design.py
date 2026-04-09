import streamlit as st

from ovo import (
    local_scheduler,
    storage,
    config,
)
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    MODEL_WEIGHTS_SCAFFOLD,
)
from ovo.app.components import molstar_custom_component, StructureVisualization
from ovo.app.components.history_components import history_dropdown_component
from ovo.app.components.input_components import pdb_input_component, sequence_selection_fragment, initialize_workflow
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.preview_components import visualize_rfdiffusion_preview, contigs_organizer_fragment
from ovo.app.components.scheduler_components import wait_with_statusbar
from ovo.app.components.submission_components import (
    pool_submission_inputs,
    show_rfdiffusion_advanced_settings,
    review_workflow_submission,
)
from ovo.app.pages import jobs_page, designs_page
from ovo.app.utils.page_init import initialize_page
from ovo.core.auth import get_username
from ovo.core.database import descriptors_refolding
from ovo.core.logic.design_logic_rfdiffusion import submit_rfdiffusion_preview
from ovo.core.utils.formatting import get_hashed_path_for_bytes
from ovo.core.utils.residue_selection import parse_contig_for_input_structure


@st.fragment
def intro_step():
    # Initialize the workflow object in session state
    initialize_workflow(__file__, RFdiffusionScaffoldDesignWorkflow.name)

    with st.container(width=850):
        st.markdown(
            f"""
This workflow enables designing a new protein structure that supports fixed segments (*motifs*) from an existing structure. 
It implements and extends the end-to-end workflow for motif scaffolding from RFdiffusion<sup>[1]</sup>.

Possible use cases include:

- Scaffolding a new enzyme around a defined active-site geometry
- Truncating a region of a protein formed from multiple discontinuous regions of the sequence
- Designing a new scaffold that stabilizes that fixed region and enhances solubility (e.g. by removing an unwanted hydrophobic interface)
            
This workflow combines RFdiffusion<sup>[1]</sup> for de novo backbone design, LigandMPNN<sup>[2]</sup> for sequence design 
and side-chain rotamer prediction and AlphaFold2<sup>[3]</sup> or ESMFold<sup>[4]</sup> for independent validation.

- **Input**
    - Protein structure (PDB file or UniProt ID)
- **Main parameters**
    - "Contig" string describing stretches of residues to keep and stretches of residues to generate
    - (Optional) Stretches of residues to keep in the structure but redesign in sequence (inpainting)
- **Output**
    - Designs — protein sequences and structures
    - Design descriptors
        - Refolding metrics
        - Backbone metrics
        - Sequence composition

### Features

After inputting your structure, you'll first select segments of "fixed" residues to keep in the design.
Next, you will defined *contig* that specifies how the fixed segments are connected and how many residues are designed in between 
(and in C-/N-termini). You can generate a quick RFdiffusion preview to verify your contig.
You can choose to redesign some of the fixed residues in sequence while keeping their backbone coordinates fixed (inpainting).
Finally, you will set the number of designs to generate and optional advanced settings and submit the workflow.

Once the workflow has finished, all designs are copied from the workflow working directory to the OVO *storage* and registered in the OVO *database*.
You will be able to view all designs and their descriptors in the {jobs_page.title} results page and adjust thresholds to select *accepted designs*.
The accepted designs (usually only around 0.1% to 1% of all generated designs in typical RFdiffusion workflows) can be further 
analyzed in the {designs_page.title} page.

##### Backbone metrics

- Computed for the RFdiffusion backbone design
- Secondary structure composition
    - Percentages of helix, sheet, loop (the remaining residues); computed using PyDSSP<sup>[5]</sup>
- Radius of gyration
    - A measure of compactness of the protein structure, defined as the root mean square distance of the atoms from the center of mass (using Cα atoms only).

##### Sequence composition

- Percentage of individual amino acids
- Charge at pH 7.4 and 5.5, isoelectric point
- Sequence entropy, highlighting sequences with compositionally biased regions
- Aromaticity
- And more; computed using BioPython ProteinAnalysis<sup>[6]</sup>

##### Refolding metrics

- **AlphaFold2 initial guess<sup>[3][7][8]</sup>**
    - **{descriptors_refolding.AF2_PRIMARY_PAE.name}** — Predicted Aligned Error <sup>[9]</sup> averaged over the residue–residue matrix, the lower the more confident the model is about overall design. <sup>*</sup>
    - **{descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.name}** — Cα RMSD between RFdiffusion output and AF2 prediction, measuring the agreement between the design method and the structure prediction method.
    - **{descriptors_refolding.AF2_PRIMARY_NATIVE_MOTIF_RMSD.name}** — All-atom RMSD between motif in your input structure and the motif as predicted by AF2, ensuring the original motif was neither disrupted by RFdiffusion or by the AlphaFold2 prediction.
- **ESMFold (if enabled)**
    - **{descriptors_refolding.ESMFOLD_PAE.name}** — as in AF2 PAE
    - **{descriptors_refolding.ESMFOLD_DESIGN_BACKBONE_RMSD.name}** - Cα RMSD between whole RFdiffusion output and ESMFold prediction
    - **{descriptors_refolding.ESMFOLD_DESIGN_ALL_ATOM_RMSD.name}** - All-atom RMSD between whole RFdiffusion output and ESMFold prediction
    - Note that "Native Motif RMSD" is not computed for ESMFold yet

<sup>*</sup> Note that should your design not have a static structure (e.g. domains whose relative positions can change), PAE will be higher.

In RFdiffusion<sup>[1]</sup> in silico success for scaffold design was defined as 
AF2&nbsp;PAE&nbsp; <&nbsp;5.0, 
AF2&nbsp;Design&nbsp;RMSD <&nbsp;2.0, 
and AF2&nbsp;Native&nbsp;Motif RMSD <&nbsp;1.0.
         
For both AlphaFold2 and ESMFold we also include pLDDT and pTM scores.

### Limitations

- ⚠️ **RFdiffusion workflows are computationally intensive** and typically require many designs (10,000 backbones or more) to obtain a few high-quality designs. 
     Such a workflow can take weeks of GPU time (finishing under a day thanks to parallelization). 
     Please consider starting with a small number of designs (100-200 backbones) to verify your inputs and settings before scaling up.
- ❌ **Cofactors are not supported**; only protein entities
- ❌ **SolubleMPNN weights are currently not supported**
- ⚠️ **Design of multi-chain complexes is supported but experimental**, some UI components may not behave as expected
- ⚠️ **This page enables running the end-to-end workflow**. Individual steps like ProteinMPNN redesign or AlphaFold2 scoring 
    alone cannot currently be executed through the user interface.

### Methods
                    
RFdiffusion generates a backbone → LigandMPNN generates sequences and side-chain rotamers → AlphaFold2 and/or ESMFold evaluates the design by predicting structures 
from the designed sequence comparing them to the RFdiffusion backbone (refolding, sometimes called self-consistency or designability test).

|             | Purpose     |  Input | Output |
|-------------|-------------|-------------|-------------|
| RFdiffusion | Backbone generation       | Residue stretches to fix (structure and, by default, sequence) and stretches to design | Backbone structure |
| LigandMPNN  | Sequence generation and side-chain rotamer prediction | Backbone structure | Sequence and structure with side-chains |
| AlphaFold2  | Refolding evaluation (via structure prediction)      | Designed sequence, structure (from LigandMPNN, see below) | Structure |
| ESMFold     | Refolding evaluation (via structure prediction)      | Designed sequence only | Structure |

**Details**
                
RFdiffusion generation
- RFdiffusion does not explicitly predict sequences for designed regions; however it uses an implicit notion of sequence while generating backbones. The authors note it could have been trained to co-design sequence and backbone, but they found the RFdiffusion + ProteinMPNN workflow works well. Using ProteinMPNN also enables generating multiple sequences for the same backbone.
- With `inpaint_seq` parameter, RFdiffusion holds only the backbone coordinates fixed while allowing the sequence to change by masking it out for the specified stretches (e.g. you can keep the backbone of a whole beta sheet and redesign the residues on one side).
- Note that RFdiffusion discards all side-chain atoms in the output PDB - including regions of fixed segments and chains. These are reconstructed by LigandMPNN and by the AlphaFold2 prediction.

LigandMPNN (vs. ProteinMPNN<sup>[10]</sup>)
- Incorporates explicit atomic context for small molecules and metal ions, improving sequence prediction when ligands are present. (However ligands are not currently supported.)
- Predicts side-chain rotamers and can fix side-chain conformations for selected residues; ProteinMPNN returns sequence only.
- Similar training set

AlphaFold2 protocol
- Initial guess: the design structure (from LigandMPNN) is supplied to the structure module before the first recycle, influencing the starting conformation. This is always enabled.
- Template input: the design structure is provided to every recycle, giving a stronger persistent structural context.
- Runs in single-sequence mode (no MSA), achieving speeds of around 10 seconds for a 100aa design on a low-end T4 GPU. 
  However, scales quadratically with sequence length (same as regular AlphaFold2).

### References
1. [RFdiffusion](https://www.nature.com/articles/s41586-023-06415-8), (and [Motif Scaffolding GitHub guide](https://github.com/RosettaCommons/RFdiffusion?tab=readme-ov-file#motif-scaffolding))
2. [LigandMPNN](https://www.nature.com/articles/s41592-025-02626-1)
3. [AlphaFold2](https://www.nature.com/articles/s41586-021-03819-2)
4. [ESMFold](https://www.science.org/doi/10.1126/science.ade2574)
5. [PyDSSP](https://github.com/ShintaroMinami/PyDSSP)
6. [BioPython ProteinAnalysis](https://biopython.org/docs/latest/api/Bio.SeqUtils.ProtParam.html#Bio.SeqUtils.ProtParam.ProteinAnalysis)
7. [AlphaFold2 initial guess](https://www.nature.com/articles/s41467-023-38328-5)
8. [ColabDesign](https://github.com/sokrypton/ColabDesign)
9. [Predicted Aligned Error (PAE)](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/pae-a-measure-of-global-confidence-in-alphafold-predictions/)
10. [ProteinMPNN](https://www.science.org/doi/10.1126/science.add2187)
""",
            unsafe_allow_html=True,
        )


@st.fragment
def input_step():
    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[__file__]

    left, _, right = st.columns([4, 1, 3])
    with left:
        st.subheader("Input structure")
        if new_pdb_input := pdb_input_component(workflow.input_name):
            input_name, pdb_input_bytes = new_pdb_input
            file_hash = get_hashed_path_for_bytes(pdb_input_bytes)

            workflow.rfdiffusion_params.input_pdb = storage.store_file_str(
                pdb_input_bytes.decode(),
                f"project/{st.session_state.project.id}/inputs/{file_hash}/{input_name}.pdb",
                overwrite=False,
            )
            workflow.input_name = input_name
            workflow.selected_segments = []
            # TODO use presets to initialize this instead
            workflow.refolding_params.primary_test = "af2_model_1_ptm_ft_3rec"
    with right:
        history_dropdown_component(__file__, workflow_name=RFdiffusionScaffoldDesignWorkflow.name)

    if not workflow.rfdiffusion_params.input_pdb:
        # No input structure provided yet, stop here
        return

    st.subheader(workflow.input_name)

    molstar_custom_component(
        structures=[
            StructureVisualization(pdb=storage.read_file_str(workflow.rfdiffusion_params.input_pdb), color="chain-id")
        ],
        key="input_structure",
        width=700,
        height=400,
    )


@st.fragment()
def selection_step():
    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[__file__]

    st.subheader("Select residues to keep")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    sequence_selection_fragment(__file__, workflow.input_name)


@st.fragment()
def contig_preview_step():
    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[__file__]
    st.subheader("Enter contig and generate preview")

    st.write(
        """
        The contig defines which parts of the structure will be preserved,
        in which order they will be connected, and how many residues will be designed in between.
        """
    )

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    # Input parameters for the preview
    contigs_organizer_fragment(__file__, pdb_input_string=storage.read_file_str(workflow.rfdiffusion_params.input_pdb))

    # Generate preview
    st.write("#### Generate preview")

    help_column = st.columns([2, 1])[0]

    with st.columns(3)[0]:
        if "preview_timesteps" not in st.session_state:
            st.session_state.preview_timesteps = 5
        new_timesteps = st.slider(
            "Num RFdiffusion timesteps (T)",
            min_value=1,
            max_value=20,
            value=st.session_state.preview_timesteps,
            key="timesteps_input",
        )
        if new_timesteps and new_timesteps != st.session_state.preview_timesteps:
            st.session_state.preview_timesteps = new_timesteps
            # Clear previous preview if settings changed
            workflow.preview_job_id = None

    with help_column:
        st.write(f"""
        Generate a quick RFdiffusion preview of the design with reduced number of timesteps
        ({st.session_state.preview_timesteps}/50) to verify your inputs. This step is optional.

        This should take from 30 seconds to a few minutes depending on the length of the protein.
        """)

    if st.button(":material/wand_stars: Generate preview"):
        with st.spinner("Submitting RFdiffusion job..."):
            workflow.preview_job_id = submit_rfdiffusion_preview(workflow, timesteps=st.session_state.preview_timesteps)

    # Check if needed parameters are set
    if not workflow.preview_job_id:
        return

    if workflow.rfdiffusion_params.contig is None:
        return

    # Wait until task is done
    result = wait_with_statusbar(local_scheduler, workflow.preview_job_id, label="Running RFdiffusion...")

    # Exit if job failed
    if not result:
        return

    visualize_rfdiffusion_preview(workflow, output_dir=local_scheduler.get_output_dir(workflow.preview_job_id))


@st.fragment()
def inpainting_step():
    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[__file__]

    st.subheader("Sequence inpainting")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    if not workflow.rfdiffusion_params.contig:
        st.error("Please provide a contig in the previous step.")
        return

    fixed_segments = parse_contig_for_input_structure(workflow.rfdiffusion_params.contig)

    sequence_selection_fragment(
        __file__,
        workflow.input_name,
        fixed_segments=fixed_segments,
        selection_help="Select input structure residues that will be kept in the structure but redesigned with ProteinMPNN. This step is optional.",
        selection_label="Residues to be inpainted (redesigned)",
        inpainting=True,
    )


@st.fragment()
def settings_step():
    st.subheader("Settings")

    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[__file__]

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    if not workflow.rfdiffusion_params.contig:
        st.error("Contig has not been computed. Please fill in all inputs in previous step.")
        return

    pool_submission_inputs(__file__)

    with st.columns([1, 2])[0]:
        generator_options = ["rfdiffusion", "rfdiffusion3"]
        workflow.rfdiffusion_params.backbone_generator = st.selectbox(
            "Backbone generator",
            options=generator_options,
            format_func=lambda x: "RFdiffusion v1" if x == "rfdiffusion" else "RFdiffusion3 (beta)",
            index=generator_options.index(workflow.rfdiffusion_params.backbone_generator),
            key="backbone_generator",
        )
    is_rfd3 = workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3"

    contig = st.text_input(
        "Contig",
        placeholder="A123-456/10/A567-890/...",
        value=workflow.rfdiffusion_params.contig,
        key="input_contig",
    )

    if check_contig_parsed(contig):
        workflow.rfdiffusion_params.contig = contig

    with st.columns([1, 2])[0]:
        if not is_rfd3:
            workflow.rfdiffusion_params.model_weights = st.selectbox(
                "Model weights",
                help="Use 'active site' model weights to hold better selected residues specified in the contig.",
                index=MODEL_WEIGHTS_SCAFFOLD.index(workflow.rfdiffusion_params.model_weights)
                if workflow.rfdiffusion_params.model_weights
                else 0,
                key="active_site",
                options=MODEL_WEIGHTS_SCAFFOLD,
            )

        is_admin = get_username() in config.auth.admin_users
        workflow.rfdiffusion_params.num_designs = st.number_input(
            "Number of structure designs (RFdiffusion backbones)",
            min_value=1,
            max_value=config.props.rfdiffusion_backbones_limit_admin
            if is_admin
            else config.props.rfdiffusion_backbones_limit,
            value=workflow.rfdiffusion_params.num_designs,
            key="num_designs",
        )

        workflow.protein_mpnn_params.num_sequences = st.number_input(
            "Number of sequence designs per backbone (ProteinMPNN)",
            min_value=1,
            max_value=config.props.mpnn_sequences_limit,
            value=workflow.protein_mpnn_params.num_sequences,
            key="num_sequences",
        )

    show_rfdiffusion_advanced_settings(workflow)


@st.fragment
def review_step():
    st.subheader("Review settings")

    review_workflow_submission(__file__)


def check_contig_parsed(contig: str | None, verbose: bool = False) -> bool:
    if not len(contig.split(" ")) == 1:
        if verbose:
            st.warning("Support of multi-chain scaffold design is experimental, proceed with caution")

    if contig.islower():
        st.warning("Input contigs are lowercase. Workflow can behave unexpectedly.")

    try:
        parse_contig_for_input_structure(contig) if contig else None
        return True
    except Exception as e:
        if verbose:
            st.error(
                f"There is an error in the contig specification. Please make sure you provide valid contigs. Error: {e}"
            )
        return False


if __name__ == "__main__":
    initialize_page(page_title="Scaffold design")

    show_prev_next_sections(
        key=__file__,
        title="🏗️ Scaffold design",
        sections={
            "intro": intro_step,
            "input": input_step,
            "selection": selection_step,
            "contig": contig_preview_step,
            "sequence inpainting": inpainting_step,
            "settings": settings_step,
            "review": review_step,
        },
    )
