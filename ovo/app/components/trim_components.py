import streamlit as st

from ovo.core.database.models_rfdiffusion import RFdiffusionBinderDesignWorkflow

from ovo.core.utils.pdb import trim_pdb_str
from ovo.core.utils.residue_selection import (
    from_contig_to_residues,
    from_residues_to_chain_breaks,
    parse_contig_for_input_structure,
)
from ovo.app.components.molstar_custom_component import molstar_custom_component, StructureVisualization


def parameters_trim_structure_component(workflow: RFdiffusionBinderDesignWorkflow):
    st.write("Trim the target chain to save computation time, and to avoid running out of GPU memory")

    if workflow.rfdiffusion_params.hotspots:
        st.write(f"Binding hotspots: {workflow.rfdiffusion_params.hotspots}")
        chains_in_hotspot = set([hotspot[0] for hotspot in workflow.rfdiffusion_params.hotspots.split(",")])
        if len(chains_in_hotspot) == 1 and workflow.target_chain is None:
            # pre-fill target chain if determined by selected hotspot
            workflow.target_chain = list(chains_in_hotspot)[0]

    if workflow.target_chain is None and len(workflow.chains) == 1:
        workflow.target_chain = list(workflow.chains)[0]

    target_chain_col, start_trimmed_col, end_trimmed_col, _ = st.columns([0.15, 0.15, 0.15, 0.45])
    with target_chain_col:
        try:
            selected_idx = list(workflow.chains.keys()).index(workflow.target_chain) if workflow.target_chain else None
        except ValueError:
            # chain ID not present in our list
            selected_idx = None

        target_chain = st.selectbox(
            label="Target chain",
            placeholder=f"{len(workflow.chains)} available chains",
            index=selected_idx,
            key="target_chain",
            options=workflow.chains,
            help="Preview supports only one chain at the moment.",
        )

    if not target_chain:
        workflow.target_chain = None
        workflow.start_res_trimmed_chain = None
        workflow.start_end_trimmed_chain = None
        return

    # List residues from the selected chain
    residues = list(map(int, from_contig_to_residues(workflow.chains.get(target_chain))))
    # Check if selected chain has changed
    target_chain_is_unchanged: bool = workflow.target_chain == target_chain

    # Set the start and end residues based on the selected chain if they are not set or the selected chain has changed
    if not workflow.start_res_trimmed_chain or not target_chain_is_unchanged:
        workflow.start_res_trimmed_chain = residues[0]
    if not workflow.end_res_trimmed_chain or not target_chain_is_unchanged:
        workflow.end_res_trimmed_chain = residues[-1]

    with start_trimmed_col:
        start_res = st.number_input(
            "Start residue",
            min_value=residues[0],
            max_value=residues[-1],
            value=workflow.start_res_trimmed_chain,
            key=f"start_trim_residue_{target_chain}",
            args=(
                target_chain,
                residues,
            ),
        )

        if start_res not in residues:
            start_res = min([res for res in residues if res > start_res], key=lambda res: abs(res - start_res))
            st.warning(
                "Start residue is not in the list of residues (between chain breaks). "
                f"Choosing {target_chain}{start_res} as start residue."
            )

    with end_trimmed_col:
        end_res = st.number_input(
            "End residue",
            min_value=residues[0],
            max_value=residues[-1],
            value=workflow.end_res_trimmed_chain,
            key=f"end_trim_residue_{target_chain}",
            args=(
                target_chain,
                residues,
            ),
        )

        if end_res not in residues:
            end_res = min([res for res in residues if res < end_res], key=lambda res: abs(res - end_res))
            st.warning(
                "End residue is not in the list of residues (between chain breaks). "
                f"Choosing {target_chain}{end_res} as end residue."
            )

    trimmed_residues = [res for res in residues if (res <= end_res) and (res >= start_res)]
    chain_break_segments = from_residues_to_chain_breaks(trimmed_residues)
    if chain_break_segments:
        st.info(
            f"Trimmed region {target_chain}{start_res}-{end_res} contains chain breaks: "
            f"{', '.join(chain_break_segments)}. "
            f"AlphaFold2 should detect these and insert a chain break in the prediction, "
            f"but please verify this in the predicted structure."
        )

    if not end_res > start_res:
        workflow.start_res_trimmed_chain = None
        workflow.end_res_trimmed_chain = None
        st.error("End residue must be greater than start residue.")
        return

    # Check if the hotspots are included in the selected range / chain
    if workflow.rfdiffusion_params.hotspots:
        mock_contig = f"{target_chain}{start_res}-{end_res}"
        check_hotspots(mock_contig, workflow.rfdiffusion_params.hotspots)

    # Check if the start and end residues selection has changed since the last preview
    selection_is_unchanged: bool = (
        (workflow.start_res_trimmed_chain == start_res)
        and (workflow.end_res_trimmed_chain == end_res)
        and target_chain_is_unchanged
    )

    # Update the trimmed chain based on the current selection
    workflow.start_res_trimmed_chain = start_res
    workflow.end_res_trimmed_chain = end_res

    # Update the target_chain based on the current selection
    workflow.target_chain = target_chain

    if not selection_is_unchanged:
        # Reset contig to be recomputed in the preview step
        workflow.rfdiffusion_params.contig = None
        return


def trimmed_structure_visualizer(workflow: RFdiffusionBinderDesignWorkflow, pdb_input_string: str):
    target_chain = workflow.get_target_chain()
    trim_start, trim_end = workflow.get_target_trim_boundary()
    pdb_input_string_trimmed = trim_pdb_str(pdb_input_string, target_chain, trim_start, trim_end)

    left, right = st.columns([2, 1])

    with right:
        colors_and_types = {
            ("uniform", "cartoon"): "Cartoon",
            ("hydrophobicity", "molecular-surface"): "Surface hydrophobicity",
        }
        color, representation_type = st.selectbox(
            "Representation",
            options=list(colors_and_types.keys()),
            format_func=lambda x: colors_and_types[x],
            key="colors_and_types_input",
            label_visibility="collapsed",
        )

    left, right = st.columns([1, 1])

    with left:
        st.write("Input structure")
        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_input_string,
                    contigs=parse_contig_for_input_structure(f"{target_chain}{trim_start}-{trim_end}"),
                    highlighted_selections=workflow.get_selected_segments(),
                    color="uniform",
                    representation_type="cartoon",
                )
            ]
            + (
                [
                    StructureVisualization(
                        pdb=pdb_input_string_trimmed,
                        highlighted_selections=workflow.get_selected_segments(),
                        color=color,
                        representation_type=representation_type,
                    )  # include surface of the trimmed structure when displaying surface
                ]
                if "molecular-surface"
                else []
            ),
            key="inp_trim_structure",
        )

    with right:
        st.write("Trimmed structure")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_input_string_trimmed,
                    highlighted_selections=workflow.get_selected_segments(),
                    color=color,
                    representation_type=representation_type,
                )
            ],
            height="524px",  # to level with other visualization
            key="trimmed_structure",
        )


def check_hotspots(contig: str, hotspots: str):
    if hotspots is None or hotspots == "":
        return

    target_chain = contig[0]
    contig_res = contig[1:].split(" ")[0].removesuffix("/0").split("-")
    start_resnum = int(contig_res[0])
    end_resnum = int(contig_res[-1])

    hotspots_list = hotspots.split(",")
    not_included = []
    for hotspot in hotspots_list:
        hotspot_chain, hotspot_resnum = hotspot[0], int(hotspot[1:])

        if hotspot[0] != target_chain:
            not_included.append(hotspot)
            st.error(f"Hotspot {hotspot} is not in the target chain {target_chain}. ")
            continue

        if hotspot_resnum < start_resnum or hotspot_resnum > end_resnum:
            not_included.append(hotspot)

    if not_included:
        st.error(
            f"Trimmed region {start_resnum}-{end_resnum} does not contain "
            f"some of selected hotspots: {', '.join(not_included)}"
        )
