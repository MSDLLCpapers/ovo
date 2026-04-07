import os
import re

import streamlit as st
from ovo.app.components.contigs_organizer import contigs_organizer
from ovo.app.components.molstar_custom_component import (
    molstar_custom_component,
    StructureVisualization,
    ChainVisualization,
)

from ovo import storage
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    RFdiffusionWorkflow,
    RFdiffusionBinderDesignWorkflow,
)
from ovo.app.components.trim_components import check_hotspots
from ovo.core.utils.pdb import add_glycan_to_pdb, filter_pdb_str, get_standardized_remarks_from_pdb_str
from ovo.core.utils.residue_selection import (
    from_segments_to_hotspots,
    from_hotspots_to_segments,
    from_contig_to_residues,
    from_residues_to_segments,
    parse_contig_for_input_structure,
    ContigSegment,
    parse_contig_for_output_structure,
)


def parameters_binder_preview_component(workflow: RFdiffusionBinderDesignWorkflow):
    if not workflow.target_chain:
        st.error("Please provide a target chain in the previous step.")
        return

    st.write(f"Target chain: {workflow.target_chain}")
    st.write(f"Start and end residue: {workflow.start_res_trimmed_chain} - {workflow.end_res_trimmed_chain}")

    binder_length_col, hotspots_col, _ = st.columns([1, 1, 3])

    with binder_length_col:
        binder_length = st.text_input(
            "Binder length (min-max)",
            placeholder="For example 20-40",
            value=workflow.binder_length,
            key="binder_length",
        )
        if binder_length != workflow.binder_length:
            # Reset the contig to force regeneration below
            workflow.rfdiffusion_params.contig = None
            workflow.binder_length = binder_length

    with hotspots_col:
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
                return

    # Check if the selection has changed since the last preview
    hotspots_from_first_step = from_segments_to_hotspots(workflow.selected_segments)
    if workflow.rfdiffusion_params.hotspots != hotspots_from_first_step:
        # Reset the preview_job_id to prevent the visualization of the previous preview
        workflow.preview_job_id = None
        # Update the selected segments based on the current hotspots
        workflow.selected_segments = from_hotspots_to_segments(workflow.rfdiffusion_params.hotspots)

    # Exit early if we don't have all fields required for contig
    if not workflow.target_chain or not workflow.binder_length:
        workflow.rfdiffusion_params.contig = None
        return

    # Exit early if binder length is invalid
    if not re.fullmatch(r"^\d+(-\d+)?$", binder_length):
        st.error("Binder length should be in this format: '20' or '20-40'")
        return

    # Update contig if not set yet, or if reset due to changing trim region or binder length
    if not workflow.rfdiffusion_params.contig:
        # Create contig definition for target, take trimming into account
        target_contig = from_residues_to_segments(
            workflow.target_chain,
            from_contig_to_residues(workflow.chains.get(workflow.target_chain)),
            workflow.start_res_trimmed_chain,
            workflow.end_res_trimmed_chain,
        )
        workflow.rfdiffusion_params.contig = "/".join(target_contig) + f"/0 {workflow.binder_length}"

    if workflow.rfdiffusion_params.hotspots:
        check_hotspots(workflow.rfdiffusion_params.contig, workflow.rfdiffusion_params.hotspots)


@st.fragment
def scaffold_contig_preview(pdb_input_string, parsed_contig: list[ContigSegment]):
    """Preview the fixed segments in the input structure.

    :param pdb_input_string: The input PDB string.
    :param parsed_contig: Contig segment objects, computed using parse_contig_for_input_structure()
    """

    fixed_segments = [seg for seg in parsed_contig if seg.start is not None]

    try:
        pdb_fixed_string = filter_pdb_str(
            pdb_input_string, segments=[f"{seg.chain}{seg.start}-{seg.end}" for seg in fixed_segments], add_ter=True
        )

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_fixed_string,
                    contigs=fixed_segments,
                    representation_type="cartoon+ball-and-stick",
                )
            ],
            key="fixed_segments_preview",
            height=400,
        )
    except Exception as e:
        st.error(f"Invalid contig provided: {e}")


@st.fragment
def contigs_organizer_fragment(page_key: str, pdb_input_string: str):
    workflow: RFdiffusionScaffoldDesignWorkflow = st.session_state.workflows[page_key]

    contig = update_contig_based_on_selected_segments(
        old_contig=workflow.get_contig(), selected_segments=workflow.get_selected_segments()
    )

    contig_input_key = "input_contig"
    if contig_input_key not in st.session_state:
        st.session_state[contig_input_key] = contig

    if st.session_state.get("contig_updated_from_component"):
        # force update input field when contig was changed from the custom component
        # we need to use a separate session key since streamlit only allows setting the key before calling the component
        st.session_state["contig_updated_from_component"] = False
        st.session_state[contig_input_key] = contig

    new_contig = st.text_input(
        "Contig",
        placeholder="A123-456/10/A567-890/...",
        key=contig_input_key,
    ).strip()

    if new_contig != workflow.get_contig():
        workflow.set_selected_segments([s for s in new_contig.split("/") if s and s[0].isalpha()])
        workflow.set_contig(new_contig)

    # TODO
    # include_generated=True
    # We could try including generated segments to keep their color in contig organizer
    # The problem is that the color is assigned by segment value,
    # so all segments of same length will get the same color
    # Another problem is that we don't store which fixed residues are connected by each generated segment,
    # So without that information we can't visualize it as a link in the structure viewer.
    segments = parse_contig_for_input_structure(workflow.get_contig())

    left, right = st.columns([1.2, 1])

    with left:
        st.caption("Contig editor")

        if workflow.get_contig() and " " in workflow.get_contig():
            missing_chain_break = any(
                not inner_sub_contig.endswith("/0") for inner_sub_contig in workflow.get_contig().split(" ")[:-1]
            )
            if missing_chain_break:
                st.error(
                    "When contig contains multiple chains (separated by space), each chain should end with '/0' (chain break)."
                )
            # TODO elaborate on the limitations
            st.warning("Support for multi-chain contigs in scaffold design is experimental, proceed with caution.")
            return

        co = contigs_organizer(
            contigs=workflow.get_contig(),
            pdb=pdb_input_string,
            colors={f"{s.chain}{s.start}-{s.end}": s.color for s in segments},
            key="contigs_organizer",
        )

        if co:
            previous_contig = co.get("previous", {}).get("contig")
            # When passing a new contig into the component, it can still return its old state here,
            # until it gets updated to the new state (remember this happens asynchronously in the browser)
            # We only accept the change it if the "previous" state matches our current state
            if previous_contig == workflow.get_contig():
                # Update contig and selected segments based on response from component
                new_contig = co.get("current", {}).get("contig")
                if new_contig and workflow.get_contig() != new_contig:
                    workflow.set_selected_segments([s for s in new_contig.split("/") if s and s[0].isalpha()])
                    workflow.set_contig(new_contig)
                    st.session_state["contig_updated_from_component"] = True
                    st.rerun()

        if not workflow.preview_job_id and workflow.get_contig():
            try:
                all_segments = parse_contig_for_input_structure(workflow.get_contig(), include_generated=True)
                num_generated_segments = sum(s.start is None for s in all_segments)
                num_fixed_segments = sum(s.start is not None for s in all_segments)
                if num_generated_segments and num_generated_segments >= num_fixed_segments - 1:
                    st.write("Contig looks ready. Generate a preview below :material/arrow_cool_down:")
            except Exception:
                # Silently ignore parsing contig, since it might not be ready yet
                pass

    with right:
        st.caption("Fixed segments")
        scaffold_contig_preview(pdb_input_string, segments)


def update_contig_based_on_selected_segments(old_contig: str, selected_segments: list[str]):
    contig = old_contig
    if old_contig is None:
        if selected_segments is None:
            # Generate new empty contig
            st.warning("No segments selected, please select them in the previous step or fill in the contig manually")
            contig = ""
        else:
            # Generate first contig template
            contig = "/".join(selected_segments or [])
    else:
        if " " in old_contig.strip():
            # do not try updating the contig if it contains a space (might be a mistake from the user, let them fix it below)
            # do not exit here - more errors will be shown below
            pass
        else:
            # Get all contig segments (including generated: A10-20/10/A30-40 -> ['A10-20', '10', 'A30-40'])
            contig_segments = [s for s in old_contig.strip().split("/") if s]
            # Get fixed selected segments from contig, for example [(0, 'A10-20'), (2, 'A30-40')]
            fixed_contig_segments_with_index = [(i, s) for i, s in enumerate(contig_segments) if s[0].isalpha()]
            fixed_contig_segments = [s for i, s in fixed_contig_segments_with_index]
            if fixed_contig_segments != selected_segments:
                # Regenerate contig if user changed the selection in previous step
                if len(fixed_contig_segments) == len(selected_segments) and any(
                    a == b for a, b in zip(fixed_contig_segments, selected_segments)
                ):
                    # Same number of fixed segments, and some segments are unchanged
                    # (that check is done to give up when segments are reordered,
                    #  since molstar discards user's ordering and returns selection in PDB order,
                    #  so it's better to just regenerate the contig in that case)
                    # -> Preserve contig, keep lengths of all generated segments in between
                    changed_segments = []
                    for (i, old_segment), new_segment in zip(fixed_contig_segments_with_index, selected_segments):
                        if old_segment != new_segment:
                            changed_segments.append(f"{old_segment} -> {new_segment}")
                            # replace contig_segment to selected_segment
                            assert old_segment == contig_segments[i], (
                                f"Expected segment {old_segment} at index {i} in {contig_segments}"
                            )
                            contig_segments[i] = new_segment
                    contig = "/".join(contig_segments)
                    st.success(f"""
                    Contig was updated based on changed segments: {", ".join(changed_segments)}
                    
                    Previous contig: {old_contig}
                    
                    New contig: {contig}
                    """)
                else:
                    # TODO we could preserve at least the generated segment lengths in between segments that haven't changed
                    contig = "/".join(selected_segments or [])
                    if fixed_contig_segments:
                        st.warning(f"""
                        Number of selected segments changed, generating new contig template.
                        
                        Previous contig: {old_contig}
                        
                        New contig: {contig}
                        """)
    return contig


def visualize_rfdiffusion_preview(workflow: RFdiffusionWorkflow, output_dir: str):
    pdb_preview_path = os.path.join(
        output_dir, "rfdiffusion", "rfdiffusion_standardized_pdb", "rfdiffusion_0_standardized.pdb"
    )

    pdb_preview_string = storage.read_file_str(pdb_preview_path)

    remarks = get_standardized_remarks_from_pdb_str(pdb_preview_string)
    standardized_contig = remarks.get("Standardized contig")
    if not standardized_contig:
        st.error("Standardized contig not found in PDB remarks, cannot visualize structure.")
        return

    input_segments = parse_contig_for_input_structure(workflow.get_contig())
    output_segments = parse_contig_for_output_structure(standardized_contig)

    pdb_input_string = storage.read_file_str(workflow.get_input_pdb_path())

    if st.toggle(
        "Show glycosylation sites",
        key="show_glycosylation_sites_input",
        help="Glycans are grafted to all NXS and NXT motifs (except NGS and NGT) "
        "based on a glycan template from PDB 5ELI. Nonexistent bonds might be displayed.",
    ):
        pdb_input_string, _ = add_glycan_to_pdb(pdb_input_string)
        pdb_preview_string, glycosylated_residues = add_glycan_to_pdb(pdb_preview_string)

        if glycosylated_residues:
            st.warning(f"Glycosylated motif found at {','.join(glycosylated_residues)}")
        else:
            st.info("No glycosylation motif found.")

    hotspot_segments = from_hotspots_to_segments(workflow.get_hotspots()) or []

    # visualize preview
    visual_col1, visual_col2 = st.columns(2)
    with visual_col1:
        st.write("Input structure")
        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_input_string,
                    contigs=input_segments,
                    highlighted_selections=hotspot_segments,
                    representation_type="cartoon+ball-and-stick",
                )
            ],
            key="inp_structure",
        )
    with visual_col2:
        st.write("RFdiffusion design preview")

        # Note: this is a heuristic to identify binder design workflows,
        #  we use the same function in the binder input components
        is_binder = hasattr(workflow, "get_target_chain")

        # TODO
        # Note this assumes that the target chain is B in the RFdiffusion output PDB,
        # and that the residue numbers are same as in the input PDB
        output_hotspot_segments = [s.replace(workflow.get_target_chain(), "B") for s in hotspot_segments or []]

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_preview_string,
                    contigs=None if is_binder else output_segments,
                    highlighted_selections=output_hotspot_segments,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": "0xde853c"},
                        )
                    ]
                    if is_binder
                    else None,
                )
            ],
            key="preview_structure",
            download_filename="rfdiffusion_preview",
        )
