from typing import Dict, List

import pandas as pd
import json
import streamlit as st

from ovo import db, storage, schedulers, ResidueNumberDescriptor
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import residue_number_descriptor_detail_table
from ovo.app.components.descriptor_tiles import get_residue_presence_df
from ovo.app.components.download_component import download_job_designs_component
from ovo import viz
from ovo.app.components.navigation import design_navigation_selector
from ovo.app.components.submission_components import scheduler_selectbox
from ovo.app.components.workflow_visualization_components import show_design_metrics
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design,
    get_cached_design_job,
    get_cached_available_descriptors,
    get_cached_pool,
)
from ovo.app.components.design_labeling import design_labeling_fragment
from ovo.core.database import (
    Design,
    DesignWorkflow,
    NumericDescriptor,
    Descriptor,
    descriptors_rfdiffusion,
    descriptors_refolding,
    descriptors_bindcraft,
)
from ovo.core.database.descriptors import ALL_DESCRIPTORS
from ovo.core.database.models_interface_analysis import InterfaceAnalysisWorkflow
from ovo.core.database.models import WorkflowTypes, InteractionDescriptor
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table, submit_descriptor_workflow


@st.fragment
def interface_fragment(pool_ids: List[str], design_ids: List[str] | None = None):
    """Main interface analysis view."""
    pools = get_cached_pools(pool_ids)

    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = sorted(db.select_values(Design, "id", pool_id__in=pool_ids, accepted=True))

        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". All generated designs can be explored in the **Jobs** page."
            )
            return

    elif not design_ids:
        # Empty list explicitly passed to design_ids
        st.write("No designs selected")
        return

    st.header(f"Interface analyzer | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    if st.button("Submit interface analysis", type="primary", key="submit_interface_analysis_btn"):
        submit_interface_analysis_dialog(design_ids)

    badges = [f":grey-badge[{pool.name}]" for pool in pools]
    st.write("Selected pools: " + " ".join(badges))

    subclass_names = WorkflowTypes.get_subclass_names(InterfaceAnalysisWorkflow)

    # Refresh descriptors
    refresh_descriptors(design_ids=design_ids, workflow_names=subclass_names)

    interaction_descriptors = [d for d in ALL_DESCRIPTORS if isinstance(d, InteractionDescriptor)]

    # Collect all descriptors from all subclasses of InterfaceAnalysisWorkflow
    residue_number_descriptors = {}
    subclass_descriptors = []
    for subclass_name in subclass_names:
        WorkflowSubclass = WorkflowTypes.get(subclass_name)
        residue_number_descriptors.update(WorkflowSubclass.residue_number_descriptors)
        subclass_descriptors += WorkflowSubclass.interface_descriptors
    for pair in residue_number_descriptors.values():
        subclass_descriptors += pair

    all_interface_descriptors = (
        [
            # Backbone metrics
            descriptors_rfdiffusion.N_CONTACTS_TO_INTERFACE,
            descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS,
            descriptors_rfdiffusion.N_HOTSPOTS_ON_INTERFACE,
            # Refolding metrics
            descriptors_refolding.AF2_PRIMARY_IPAE,
            descriptors_refolding.AF2_PRIMARY_IPTM,
            descriptors_refolding.BOLTZ_PRIMARY_IPDE,
            # Bindcraft metrics
            descriptors_bindcraft.AF2_IPAE,
            descriptors_bindcraft.AF2_IPTM_SCORE,
        ]
        + interaction_descriptors
        + subclass_descriptors
    )

    available_descriptors_by_key = get_cached_available_descriptors(design_ids)
    interface_descriptors_by_key = {
        desc.key: desc for desc in all_interface_descriptors if desc.key in available_descriptors_by_key
    }

    if not interface_descriptors_by_key:
        st.write("No results yet.")
        return

    # Get table of all relevant descriptor values
    descriptors_df = get_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=interface_descriptors_by_key.keys(), nested=False, human_readable=False
    )
    # NOTE: We parse interaction descriptors from JSON string to list of dictionaries here
    for d in interaction_descriptors:
        if d.key in descriptors_df.columns:
            descriptors_df[d.key] = descriptors_df[d.key].apply(lambda x: parse_interaction(x))

    # show dropdown
    residue_number_counts = {
        k: (~descriptors_df[t.key].isna()).sum()
        for k, (t, b) in residue_number_descriptors.items()
        if t.key in descriptors_df.columns and b.key in descriptors_df.columns
    }
    available_residue_number_descriptors = {
        k: residue_number_descriptors[k]
        for k in sorted(residue_number_counts.keys(), key=lambda k: residue_number_counts[k], reverse=True)
    }
    if not available_residue_number_descriptors:
        target_irn_descriptor, binder_irn_descriptor = None, None
    elif len(available_residue_number_descriptors) == 1:
        target_irn_descriptor, binder_irn_descriptor = list(available_residue_number_descriptors.values())[0]
    else:
        residue_number_key = st.segmented_control(
            "Interface residue annotation method",
            options=list(available_residue_number_descriptors.keys()),
            default=list(available_residue_number_descriptors.keys())[0],
            key="residue_number_key",
            bind="query-params",
        )
        if not residue_number_key:
            st.warning("Please select an interface residue annotation method")
            return
        target_irn_descriptor, binder_irn_descriptor = available_residue_number_descriptors[residue_number_key]

    # TODO show histograms or some other stats summary for all selected designs

    # Summary table per target interface residue
    st.write("#### Target interface residue statistics")
    st.text(
        "Shows which target residues are in contact with the binder",
        help="Note that pools may have different target structures and residue numberings.",
    )
    # NOTE: different pools may have different target structures and thus different interface residues and residue numberings
    interface_residues_table(descriptors_df, target_irn_descriptor=target_irn_descriptor)

    # Summary table per design and per target interface residue
    st.write("#### Target interface residues by design")
    st.text(
        "Matrix showing which target residues are in contact with the binder in each design",
        help="Note that pools may have different target structures and residue numberings.",
    )
    # NOTE: different pools may have different target structures and thus different interface residues and residue numberings
    interface_residues_table_by_design(descriptors_df, target_irn_descriptor=target_irn_descriptor)

    # TODO: Target structure view
    # We could visualize the target and color all interface residues on it (darker residues = more designs with that contact)
    # Issue: In the pools, we can have different target structures, so we would need to group by target structure first...

    # Individual design exploration
    st.write("#### Design details")

    interface_design_visualization_fragment(
        design_ids,
        descriptors_df,
        interface_descriptors_by_key,
        target_irn_descriptor=target_irn_descriptor,
        binder_irn_descriptor=binder_irn_descriptor,
    )


@st.fragment
@st.dialog("Interface analysis submission", width="medium")
def submit_interface_analysis_dialog(all_design_ids: list[str]):
    content = st.empty()
    with content.container():
        subclass_names = WorkflowTypes.get_subclass_names(InterfaceAnalysisWorkflow)

        selected_design_option = st.selectbox(
            "Select designs",
            options=[f"All {len(all_design_ids)} designs"] + all_design_ids
            if len(all_design_ids) > 1
            else all_design_ids,
            index=0,
            key="interface_design_selection_option",
        )
        selected_design_ids = all_design_ids if selected_design_option.startswith("All ") else [selected_design_option]

        selected_method = st.selectbox(
            "Analysis method",
            placeholder="Select a method",
            options=subclass_names,
            index=None,
            key="interface_method_selectbox",
        )

        if not selected_method:
            st.write("Please select an analysis method")
            return

        WorkflowType = WorkflowTypes.get(selected_method)
        workflows = WorkflowType.from_ui(design_ids=selected_design_ids)
        if not workflows:
            return

        scheduler_key = scheduler_selectbox(workflows)

        error = None
        try:
            for workflow in workflows:
                workflow.validate()
        except Exception as e:
            error = str(e)

        if error:
            st.error(error)
            return

        if st.button("Submit", key="submit_interface_analysis_confirm_btn", type="primary"):
            with st.spinner("Submitting..."):
                for workflow in workflows:
                    submit_descriptor_workflow(workflow, scheduler_key, st.session_state.project.id)
            content.empty()
            st.success("Interface analysis submitted!")
            st.rerun()


def parse_interaction(interaction_str: str):
    """Parse an interaction string into its components."""
    if pd.isna(interaction_str) or interaction_str == "[]" or interaction_str == "":
        return []
    return json.loads(interaction_str)


@st.fragment()
def interface_residues_table(descriptors_df: pd.DataFrame, target_irn_descriptor: ResidueNumberDescriptor):
    """Display table of interface residues and their presence across designs."""

    if not target_irn_descriptor:
        st.write("No interface residue data available.")
        return

    # Check if interface residues column exists
    if target_irn_descriptor.key not in descriptors_df.columns:
        st.warning("No interface residue data available.")
        return

    # Get residue values from DataFrame
    residue_values = descriptors_df[target_irn_descriptor.key].dropna().tolist()

    if not residue_values:
        st.warning("No interface residue data available.")
        return

    residue_df = get_residue_presence_df(target_irn_descriptor, residue_values, len(descriptors_df))

    if residue_df is None or residue_df.empty:
        st.warning("No interface residue data available.")
    else:
        st.dataframe(
            residue_df,
            column_config={
                target_irn_descriptor.name: st.column_config.Column(target_irn_descriptor.name),
                "% of designs": st.column_config.ProgressColumn(
                    "% of designs",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                    help="Percentage of designs with contact to this residue",
                ),
            },
            hide_index=True,
            width="content",
            height="auto",
        )


@st.fragment()
def interface_residues_table_by_design(descriptors_df: pd.DataFrame, target_irn_descriptor: ResidueNumberDescriptor):
    """Display table showing which interface residues are present in each design."""

    if not target_irn_descriptor:
        st.write("No interface residue data available.")
        return

    # Check if interface residues column exists
    if target_irn_descriptor.key not in descriptors_df.columns:
        st.warning("No interface residue data available.")
        return

    # Get residue values as a Series with design IDs as index
    descriptor_values = descriptors_df[target_irn_descriptor.key]

    if not any(v is not None and pd.notna(v) for v in descriptor_values):
        st.warning("No interface residue data available.")
        return

    table_data, column_config, caption, format_func = residue_number_descriptor_detail_table(
        target_irn_descriptor, descriptor_values
    )
    # st.caption(caption)
    st.dataframe(
        table_data,
        column_config=column_config,
        width="stretch",
        height="auto",
    )


@st.fragment()
def design_interface_detail(
    design_id: str,
    descriptor_values: pd.Series,
    interface_descriptors_by_key: Dict[str, Descriptor],
    target_irn_descriptor: ResidueNumberDescriptor,
    binder_irn_descriptor: ResidueNumberDescriptor,
):
    """Display detailed interface information for a single design."""
    design = get_cached_design(design_id)

    if target_irn_descriptor is None or binder_irn_descriptor is None:
        st.warning(f"No interface residue data available.")
        binder_interface_residues = []
        target_interface_residues = []
    else:
        if target_irn_descriptor.key not in descriptor_values or binder_irn_descriptor.key not in descriptor_values:
            st.warning(f"{target_irn_descriptor.tool} interface residue annotations not available for this design.")
            binder_interface_residues = []
            target_interface_residues = []
        else:
            binder_interface_residues_str = descriptor_values[binder_irn_descriptor.key]
            target_interface_residues_str = descriptor_values[target_irn_descriptor.key]

            binder_interface_residues = [r.strip() for r in str(binder_interface_residues_str).split(",") if r.strip()]
            target_interface_residues = [r.strip() for r in str(target_interface_residues_str).split(",") if r.strip()]

    if binder_interface_residues:
        binder_chain = binder_interface_residues[0][0]  # Assuming format like "A123"
    else:
        # Fallback to design spec if no interface residues found
        binder_chain = (
            design.spec.chains[0].chain_ids[0] if design.spec.chains and design.spec.chains[0].chain_ids else "A"
        )

    if target_interface_residues:
        target_chain = target_interface_residues[0][0]
    else:
        # Fallback to the other chain in the design if no interface residues found, assuming a two-chain design
        # FIXME we should fallback to the descriptor job target_chain instead
        target_chain = "B" if binder_chain == "A" else "A"
        st.warning("No target interface residues found. Assuming target chain is " + target_chain)

    # Get all interactions at the interface
    interaction_descriptors: list[InteractionDescriptor] = [
        d for d in ALL_DESCRIPTORS if d.key in descriptor_values and isinstance(d, InteractionDescriptor)
    ]
    if interaction_descriptors:
        selected_interactions: list[InteractionDescriptor] = st.pills(
            label="Select interactions to show on structure",
            options=interaction_descriptors,
            key="interaction_selection",
            selection_mode="multi",
            format_func=lambda x: x.name,
            default=interaction_descriptors,
        )
        show_interaction_labels = st.checkbox("Show interaction labels", value=True, key="show_interaction_labels")

        bonds = []
        for interaction_descriptor in selected_interactions:
            bond_label = interaction_descriptor.short_name
            bond_color = interaction_descriptor.color or "#CCCCCC"
            if not show_interaction_labels:
                bond_label = None
            for interaction in descriptor_values[interaction_descriptor.key]:
                bonds.append(
                    viz.BondVisualization(
                        binder_atoms=interaction["binder"],
                        target_atoms=interaction["target"],
                        label=bond_label,
                        color=bond_color,
                    )
                )
    else:
        st.write(
            "No interaction annotations available. "
            "Please submit the Biotite Interface Analysis workflow to show residue-residue interactions in the structure viewer."
        )
        bonds = []

    if target_irn_descriptor and binder_irn_descriptor:
        show_residue_labels = st.checkbox("Show residue labels", value=True, key="show_residue_labels")
    else:
        show_residue_labels = False

    with st.container(horizontal=True):
        colors = {
            "uniform": "Uniform color",
            "hydrophobicity": "Color by hydrophobicity (green = hydrophobic, red = hydrophilic)",
            "residue-charge": "Color by residue charge (blue = positive, red = negative)",
        }
        color = st.selectbox(
            "Color scheme",
            options=list(colors.keys()),
            format_func=lambda x: colors[x],
            key="color_scheme_input",
            label_visibility="collapsed",
            width=500,
        )
        binder_color = "#ddddff" if color == "uniform" else color
        binder_interface_color = "#bbbbff" if color == "uniform" else color
        target_color = "#ffeeee" if color == "uniform" else color
        target_interface_color = "#ffcccc" if color == "uniform" else color

        representations = {
            "interface_sidechains": "Show interface side chains",
            "all_sidechains": "Show all side chains",
        }
        representation_type = st.selectbox(
            "Representation",
            options=list(representations.keys()),
            format_func=lambda x: representations[x],
            key="representation_type_input",
            label_visibility="collapsed",
            width=250,
            index=0 if target_interface_residues else 1,
        )
        binder_sidechain_selection = (
            binder_chain if representation_type == "all_sidechains" else binder_interface_residues
        )
        target_sidechain_selection = (
            target_chain if representation_type == "all_sidechains" else target_interface_residues
        )

    viz.molstar(
        viz.StructureVisualization(
            # TODO allow user to select which structure should be used here, perhaps through some reusable component.
            #  Also implement processing of the pyrosetta relaxed structure, so it can be picked here
            #  (in cases when not already generated as part of the end-to-end workflow)
            data=storage.read_file_str(design.structure_path),
            representation_type=None,
            bonds=bonds,
            representations=[
                viz.Representation(binder_chain, "cartoon", color=binder_color),
                viz.Representation(target_chain, "cartoon", color=target_color),
                viz.Representation(binder_sidechain_selection, "ball-and-stick", color=binder_interface_color),
                viz.Representation(target_sidechain_selection, "ball-and-stick", color=target_interface_color),
            ]
            + (
                [
                    viz.Representation(binder_sidechain_selection, "label"),
                    viz.Representation(target_sidechain_selection, "label"),
                ]
                if show_residue_labels
                else []
            ),
            auto_zoom_chains=[binder_chain, target_chain],
            auto_zoom_extra_radius=-10,
        ),
        key="interface_highlighted_structure",
        height=600,
    )
    st.caption(
        ":green-badge[Tip: Click on a residue to focus the view around it. Use ctrl+scroll to zoom and ctrl+drag to pan.]"
    )

    # Display interface residues
    st.write(f"#### Interface metrics for {design_id}")
    st.write("**Target Interface Residues**")
    if target_interface_residues:
        #
        # TODO show residue names here instead of chain ids - this would require storing target chain in the spec,
        #  so we don't have to parse it out from the structure
        #
        badges = " ".join([f":gray-badge[{res}]" for res in target_interface_residues])
        st.write(badges)
    else:
        st.info("No target interface residues found.")

    # Display interface metrics
    if interface_descriptors_by_key:
        show_design_metrics(
            design_id,
            [k for k, d in interface_descriptors_by_key.items() if isinstance(d, NumericDescriptor)],
        )
    else:
        st.info("No interface metrics available for this design.")

    # Display interface interactions
    interface_badges = {}
    for descriptor in interaction_descriptors:
        if descriptor.key in descriptor_values:
            value = descriptor_values[descriptor.key]
            if value and len(value) > 0:
                badges = []
                for interaction in value:
                    binder_pos = interaction.get("binder")[0].split(":")[0]
                    target_pos = interaction.get("target")[0].split(":")[0]
                    target_aa = interaction.get("target_aa", "UNK")
                    binder_aa = interaction.get("binder_aa", "UNK")
                    badges.append(f":gray-badge[{target_pos} ({target_aa}) - {binder_pos} ({binder_aa})]")
                interface_badges[descriptor.name] = " ".join(badges)
    if interface_badges:
        st.write("**Interface Interactions**: Target residue - Binder residue")
        for interaction_name, badges in interface_badges.items():
            st.write(f"{interaction_name}: {badges}")

    st.markdown("#### Sequence")

    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id) if pool.design_job_id else None
    WorkflowType = type(design_job.workflow) if design_job and design_job.workflow else DesignWorkflow
    WorkflowType.visualize_single_design_sequences(design_id)

    st.markdown(f"#### Download {design_id}")

    download_job_designs_component(design_ids=[design_id], pools=[pool], key="single")


@st.fragment
def interface_design_visualization_fragment(
    design_ids: List[str],
    descriptors_df: pd.DataFrame,
    interface_descriptors_by_key: dict,
    target_irn_descriptor: ResidueNumberDescriptor,
    binder_irn_descriptor: ResidueNumberDescriptor,
):
    """Fragment for browsing individual designs."""
    # Optional filter for designs with contact to specific target residue
    selected_design_ids = design_ids

    labels_by_design_id = {}
    if target_irn_descriptor:
        interface_residues = set(
            x.strip() for row in descriptors_df[target_irn_descriptor.key].dropna() for x in row.split(",")
        )
        labels_by_design_id = descriptors_df.loc[selected_design_ids, target_irn_descriptor.key].to_dict()
        target_residue = st.selectbox(
            "Filter designs by target interface residue",
            options=interface_residues,
            index=None,
            placeholder="Show all designs (no residue filter)",
            help=(
                "Select a target interface residue to only show designs where the binder contacts this residue. "
                f"Residue contacts are determined by {target_irn_descriptor.tool}: {target_irn_descriptor.description}"
            ),
        )
        if target_residue:
            selected_design_ids = descriptors_df[
                descriptors_df[target_irn_descriptor.key].apply(
                    lambda x: target_residue in str(x).split(",") if pd.notna(x) else False
                )
            ].index.tolist()
            st.write(f"Showing {len(selected_design_ids):,} designs that interact with target residue {target_residue}")
        else:
            st.write(
                "Showing all designs. Use the dropdown above to select designs that bind a specific target residue."
            )

    # Use the navigation selector component
    design_id = design_navigation_selector(
        selected_design_ids, key="interface_selected_design", fmt=labels_by_design_id
    )

    design_labeling_fragment(design_id, key_suffix=f"interface_{design_id}")

    design_interface_detail(
        design_id,
        descriptors_df.loc[design_id].dropna(),
        interface_descriptors_by_key,
        binder_irn_descriptor=binder_irn_descriptor,
        target_irn_descriptor=target_irn_descriptor,
    )
