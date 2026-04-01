import re

from ovo import config, local_scheduler, storage
from ovo.app.components.history_components import history_dropdown_component
from ovo.app.components.input_components import pdb_input_component, sequence_selection_fragment, initialize_workflow
from ovo.app.components.molstar_custom_component import ContigsParser, molstar_custom_component, StructureVisualization
from ovo.app.components.navigation import show_prev_next_sections
from ovo.app.components.preview_components import parameters_binder_preview_component, visualize_rfdiffusion_preview
from ovo.app.components.scheduler_components import wait_with_statusbar
from ovo.app.components.submission_components import (
    pool_submission_inputs,
    show_rfdiffusion_advanced_settings,
    review_workflow_submission,
    show_rfdiffusion_binder_seq_design_inputs,
)
from ovo.app.components.trim_components import parameters_trim_structure_component, trimmed_structure_visualizer

from ovo.app.pages import jobs_page, designs_page
from ovo.app.utils.page_init import initialize_page
from ovo.core.auth import get_username
from ovo.core.database import descriptors_rfdiffusion, descriptors_refolding
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionBinderDesignWorkflow,
    RFdiffusionWorkflow,
    MODEL_WEIGHTS_BINDER,
)
from ovo.core.logic.design_logic_rfdiffusion import submit_rfdiffusion_preview
from ovo.core.utils.formatting import get_hashed_path_for_bytes
from ovo.core.utils.pdb import check_rfdiffusion_input
from ovo.core.utils.residue_selection import from_contig_to_residues
from ovo.core.utils.residue_selection import get_chains_and_contigs
import streamlit as st


@st.fragment
def intro_step():
    # Initialize the workflow object in session state
    initialize_workflow(__file__, RFdiffusionBinderDesignWorkflow.name)

    with st.container(width=850):
        st.markdown(
            f"""
This workflow enables designing new binders to your input structure. It implements and extends the end-to-end workflow 
for binder design from RFdiffusion<sup>[1]</sup>.
            
Use case: designing linear peptide or miniprotein binders to a desired site on a target protein.
            
This workflow combines RFdiffusion<sup>[1]</sup> for de novo backbone design, ProteinMPNN PyRosetta FastRelax
protocol<sup>[2]</sup> for sequence design and side-chain rotamer prediction, and AlphaFold2<sup>[3]</sup> for independent
validation.
        
- **Input**
    - Target protein structure (PDB file or UniProt ID)
- **Main parameters**
    - Target chain ID and trimming boundary
    - Binder length range (peptide to miniprotein)
    - Number of backbone designs and relax steps
    - (Optional) Hotspot residues to select preferred binding site
    - (Optional) ProteinMPNN amino acid bias to enrich or deplete specific amino acids in the binder
- **Output**
    - Designs — binder sequences and structures in complex with target protein
    - Design descriptors
        - Refolding metrics
        - Rosetta descriptors
        - Backbone metrics
        - Sequence composition
            

### Features

After inputting your target structure, you can choose the desired binding site by selecting "hotspot" residues, 
or you can leave it blank to allow binding anywhere on the target surface.
Next, you'll be asked to trim the protein chain. Runtime scales quadratically with the
number of residues in the input structure, so trimming the protein to relevant regions (e.g. around a hotspot, if specified) 
will speed up the design process. After specifying the desired binder length range, you can optionally generate 
a quick RFdiffusion preview of the design with reduced number of timesteps to verify your inputs.
Finally, you will set the number of designs to generate and optional advanced settings and submit the workflow.

Once the workflow has finished, all designs are saved to the OVO *storage* and registered in the OVO *database*.
You will be able to view all designs and their descriptors in the {jobs_page.title} results page and adjust thresholds to select *accepted designs*.
The accepted designs (usually only around 0.1% to 1% of all generated designs in typical RFdiffusion workflows) can be further 
analyzed in the {designs_page.title} page. For example, you can run ProteinQC to compute descriptors of predicted solubility, electrostatic and hydrophobic patch area, and more.
    
#### Backbone metrics
- Computed for the RFdiffusion backbone design (before sequence design)
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
- Sequence entropy, highlighting sequences with compositionally biased regions
- And more; computed using BioPython ProteinAnalysis<sup>[4]</sup>

#### Rosetta descriptors<sup>[2]</sup>
- **{descriptors_rfdiffusion.PYROSETTA_DDG.name}** — Rosetta binding energy of the complex (in Rosetta energy units). Lower (negative) values indicate better binding affinity.
- **{descriptors_rfdiffusion.PYROSETTA_CMS.name}** — Rosetta molecular surface area (in square angstroms).
- **{descriptors_rfdiffusion.PYROSETTA_SAP_SCORE.name}** — Evaluates hydrophobicity of surface exposed regions. Positive values indicate hydrophobic molecules.

#### AlphaFold2 initial guess refolding metrics<sup>[2][3][5]</sup>
- **{descriptors_refolding.AF2_PRIMARY_IPAE.name}** — Binder–target pose error (predicted) in angstroms. Predicted Aligned Error (residue–residue 
    matrix) averaged over binder→target residue values.
- **{descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.name}** — Cα RMSD of the binder between RFdiffusion output and AF2 prediction (aligned on target).
  This measures how much the designed binder structure agrees with its AF2 prediction.
- **{descriptors_refolding.AF2_PRIMARY_BINDER_PAE.name}** — Binder error (predicted) including the binder–target pose, in angstroms. Predicted Aligned Error 
    <sup>[5]]</sup> (residue–residue matrix) averaged over binder→binder and binder→target residue values.

We also include AF2 binder pLDDT and pTM scores. In RFdiffusion<sup>[1]</sup> in silico success for binder design was
defined as AF2&nbsp;Binder&nbsp;pLDDT >&nbsp;80, AF2&nbsp;Interface&nbsp;PAE <&nbsp;10 and AF2&nbsp;monomer&nbsp;RMSD
<&nbsp;1.0 (we do not include this metric with the binder predicted in isolation, you could use
AF2&nbsp;Binder&nbsp;RMSD which includes the pose RMSD in the complex).
                
### Limitations

- ⚠️ **RFdiffusion workflows are computationally intensive** and typically require many designs (10,000 backbones or more) to obtain a few high-quality designs. 
     Such a workflow can take weeks of GPU time (finishing under a day thanks to parallelization). Please consider starting with a small number of designs (100-200 backbones) to verify your inputs and settings before scaling up.
- ⚠️ **Only one target chain is supported.** You may circumvent this by merging multiple chains into a single chain in your 
    input PDB file, adding residue index jumps (gap of at least 50 residues between the original chains), this influences both RFdiffusion 
    and AlphaFold2. <!--clipped to -32, 32 in alphafold2, colabdesign adds 50 between binder and target --->
- ⚠️ **High AF2 Target-aligned Binder RMSD for good designs in symmetric targets.** In case the binding site occurs multiple times in the 
    target by symmetry (e.g. a homo-n-mer)
    AF2 may predict the binder to the other occurrence of the binding site. This will cause the RMSD to be high, even
    though the design can indeed bind the correct epitope. The designs' RMSD can adopt a multimodal distribution as a
    result, where the peaks correspond to the binding site-to-binding site distances. Currently, we do not correct for
    this symmetry and when filtering designs based on AF2 Target-aligned Binder RMSD in such cases, some good designs may be discarded.
- ⚠️ **This page enables running the end-to-end workflow**. Individual steps like ProteinMPNN redesign or AlphaFold2 scoring 
    alone cannot currently be executed through the user interface.

### Methods
                    
RFdiffusion generates a backbone → PyRosetta FastRelax–ProteinMPNN protocol generates sequences and side-chain
rotamers → AlphaFold2 evaluates design by repredicting the complex, computing the confidence of the prediction, 
and by comparing the binder pose from RFdiffusion backbone to the AlphaFold2 prediction.

|             | Purpose     |  Input | Output |
|-------------|-------------|-------------|-------------|
| RFdiffusion | Backbone generation       | Trimmed target protein, hotspots (optional), binder length | Complex backbone structure |
| FastRelax–ProteinMPNN  | Sequence generation and side-chain rotamer prediction | Complex backbone structure with target sequence | Binder sequence and complex structure with side-chains |
| LigandMPNN  | Sequence generation and side-chain rotamer prediction | Backbone structure | Binder sequence and complex structure with side-chains |
| AlphaFold2  | Refolding evaluation (via structure prediction)      | Designed sequence & structure | Predicted structure |
| PyRosetta   | Additional descriptors used for filtering  |  Designed sequence & structure  | Complex binding energy, Contact molecular surface, and other descriptors  |

**Details** 
               
RFdiffusion generation
- RFdiffusion does not explicitly predict sequences for the binder; however it uses an implicit notion of sequence 
  while generating backbones. The authors note it could have been trained to co-design sequence and backbone, but they 
  found the RFdiffusion + ProteinMPNN workflow works well. Using ProteinMPNN also enables generating multiple sequences
  for the same backbone.
- Note that RFdiffusion discards all side-chain atoms of the target in the output PDB. These are reconstructed by LigandMPNN and by the AlphaFold2 prediction.

ProteinMPNN FastRelax protocol
- Successive rounds of ProteinMPNN sequence design and PyRosetta FastRelax aims to converge to a low-energy sequence–structure pair.
- Designs from each round are retained, each producing one (usually similar) sequence and structure.
- Note that we modified the protocol to perform relaxation of the final design so that all designs are relaxed and ready for downstream analysis.

AlphaFold2 protocol
- Initial guess: the complex structure (from FastRelax) is supplied to the structure module before the first recycle, 
    influencing the starting conformation. Target chain structure is always provided as template input.
- Runs in single-sequence mode (no MSA), achieving speeds of around 20 seconds for a 100aa binder and 100aa target on a low-end T4 GPU. 
  However, scales quadratically with sequence length (same as regular AlphaFold2).

### References
1. [RFdiffusion](https://www.nature.com/articles/s41586-023-06415-8), (and [Binder Design GitHub guide](https://github.com/RosettaCommons/RFdiffusion?tab=readme-ov-file#binder-design))
2. [PyRosetta FastRelax–ProteinMPNN protocol](https://www.nature.com/articles/s41467-023-38328-5)
3. [AlphaFold2](https://www.nature.com/articles/s41586-021-03819-2)
4. [BioPython ProteinAnalysis](https://biopython.org/docs/latest/api/Bio.SeqUtils.ProtParam.html#Bio.SeqUtils.ProtParam.ProteinAnalysis)
5. [ColabDesign](https://github.com/sokrypton/ColabDesign)
6. [Predicted Aligned Error (PAE)](https://www.ebi.ac.uk/training/online/courses/alphafold/inputs-and-outputs/evaluating-alphafolds-predicted-structures-using-confidence-scores/pae-a-measure-of-global-confidence-in-alphafold-predictions/)
""",
            unsafe_allow_html=True,
        )


@st.fragment
def input_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    # Something is wrong - this object should not be None
    if not workflow.rfdiffusion_params:
        return

    left, _, right = st.columns([4, 1, 3])
    with left:
        st.subheader("Input structure")
        if new_pdb_input := pdb_input_component(workflow.input_name):
            input_name, pdb_input_bytes = new_pdb_input

            workflow.rfdiffusion_params.input_pdb = storage.store_file_str(
                pdb_input_bytes.decode(),
                f"project/{st.session_state.project.id}/inputs/{get_hashed_path_for_bytes(pdb_input_bytes)}/{input_name}.pdb",
                overwrite=False,
            )
            workflow.input_name = input_name
            workflow.selected_segments = []
            workflow.rfdiffusion_params.hotspots = None
            workflow.target_chain = None
            # TODO use presets to initialize this instead
            workflow.refolding_params.primary_test = "af2_model_1_multimer_tt_3rec"
    with right:
        history_dropdown_component(
            page_key=__file__,
            workflow_name=RFdiffusionBinderDesignWorkflow.name,
            filter_func=lambda w: not w.rfdiffusion_params.partial_diffusion,
        )

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


@st.fragment
def hotspots_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]

    st.subheader("Select binding hotspots")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    sequence_selection_fragment(__file__, workflow.input_name, color="hydrophobicity", write_segments=False)


@st.fragment()
def trim_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]
    st.subheader("Target chain trimming")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    pdb_input_string = storage.read_file_str(workflow.rfdiffusion_params.input_pdb)
    workflow.chains = get_chains_and_contigs(pdb_input_string)

    # Input parameters for the preview
    parameters_trim_structure_component(workflow)

    # Check if inputs are set
    if workflow.start_res_trimmed_chain is None or workflow.end_res_trimmed_chain is None:
        return

    # Make sure that structure does not contain chain breaks without a gap in residue
    # numbering (required in refolding step)
    try:
        check_rfdiffusion_input(
            pdb_input_string, workflow.target_chain, workflow.start_res_trimmed_chain, workflow.end_res_trimmed_chain
        )
    except ValueError as e:
        st.error(str(e))
        return

    # Visualize trimmed structure
    with st.container(height=630, border=False):
        trimmed_structure_visualizer(workflow, pdb_input_string)


@st.fragment()
def preview_step():
    workflow: RFdiffusionBinderDesignWorkflow = st.session_state.workflows[__file__]
    st.subheader("Enter binder settings and preview design")

    if not workflow.rfdiffusion_params.input_pdb:
        st.error("Please provide an input structure in the input structure step.")
        return

    # Input parameters for the preview
    parameters_binder_preview_component(workflow)

    # Generate preview
    st.write("#### Generate preview")
    num_timesteps = 15
    with st.columns([2, 1])[0]:
        st.write(f"""
        Generate a quick RFdiffusion preview of the design with reduced number of timesteps 
        ({num_timesteps}/50) to verify your inputs. This step is optional.
        
        This should take 2-10 minutes depending on the length of the target and binder.
        """)

    if st.button(":material/wand_stars: Generate preview"):
        with st.spinner("Submitting RFdiffusion job..."):
            workflow.preview_job_id = submit_rfdiffusion_preview(workflow, timesteps=num_timesteps)

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
def settings_step():
    st.subheader("Settings")

    workflow: RFdiffusionWorkflow = st.session_state.workflows[__file__]

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

    with st.columns([1, 2])[0]:
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

    show_rfdiffusion_binder_seq_design_inputs(workflow)

    if not is_rfd3:
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

    contig = st.text_input(
        "Contig",
        placeholder="A123-456/0 20-40",
        value=workflow.rfdiffusion_params.contig,
        key="input_contig",
    )

    # Step needed to update contig and (if binder design) target_chain and binder length
    if contig != workflow.rfdiffusion_params.contig and check_contig_parsed(contig, True):
        workflow.rfdiffusion_params.contig = contig

        chain_segment, workflow.binder_length = workflow.rfdiffusion_params.contig.split("/0 ")

        workflow.target_chain = chain_segment[0]

        residues = from_contig_to_residues(workflow.rfdiffusion_params.contig)
        workflow.start_res_trimmed_chain = residues[0]
        workflow.end_res_trimmed_chain = residues[-1]

    with st.columns([1, 2])[0]:
        workflow.rfdiffusion_params.hotspots = st.text_input(
            "Hotspot residues (optional)",
            placeholder="For example A123,A124,A131",
            value=workflow.rfdiffusion_params.hotspots,
            key="hotspots",
        )
        if workflow.rfdiffusion_params.hotspots:
            if not all(
                re.fullmatch("[A-Z][0-9]+", hotspot) for hotspot in workflow.rfdiffusion_params.hotspots.split(",")
            ):
                st.error("Invalid hotspots format, expected 'A123,A124,A131'")

    show_rfdiffusion_advanced_settings(workflow)


@st.fragment
def review_step():
    st.subheader("Review settings")

    review_workflow_submission(__file__)


def check_contig_parsed(contig: str | None, verbose: bool = False) -> bool:
    parser = ContigsParser()
    if not len(contig.split("/0 ")) == 2:
        if verbose:
            st.error("Contig must be in the format 'A123-456/0 20-40'")
        return False

    if contig.islower():
        st.warning("Input contigs are lowercase. Workflow can behave unexpectedly.")
    try:
        _ = parser.parse_contigs_str(contig) if contig else None
        return True
    except Exception as e:
        if verbose:
            st.error(
                f"There is an error in the contig specification. Please make sure you provide valid contigs. Error: {e}"
            )
        return False


if __name__ == "__main__":
    initialize_page(page_title="RFdiffusion Binder design")

    show_prev_next_sections(
        key=__file__,
        title="🧬 Binder design",
        sections={
            "intro": intro_step,
            "input": input_step,
            "hotspots": hotspots_step,
            "trim": trim_step,
            "preview": preview_step,
            "settings": settings_step,
            "review": review_step,
        },
    )
