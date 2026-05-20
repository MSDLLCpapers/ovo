from typing import Dict, List

import pandas as pd
import streamlit as st

from ovo import db, storage
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.components.descriptor_table import residue_number_descriptor_detail_table
from ovo.app.components.descriptor_tiles import get_residue_presence_df
from ovo.app.components.download_component import download_job_designs_component
from ovo.app.components.molstar_custom_component import molstar_custom_component, StructureVisualization
from ovo.app.components.navigation import design_navigation_selector
from ovo.app.utils.cached_db import (
    get_cached_pools,
    get_cached_design,
    get_cached_design_jobs,
    get_cached_design_job,
    get_cached_available_descriptors,
    get_cached_pool,
)
from ovo.app.components.design_labeling import design_labeling_fragment
from ovo.core.database import Design, DesignWorkflow, NumericDescriptor, Descriptor
from ovo.core.database.descriptors_refolding import AF2_PRIMARY_IPAE, AF2_PRIMARY_IPTM
from ovo.core.database.descriptors_rfdiffusion import (
    INTERFACE_TARGET_RESIDUES,
    N_CONTACTS_TO_INTERFACE,
    N_CONTACTS_TO_HOTSPOTS,
    N_HOTSPOTS_ON_INTERFACE,
    PYROSETTA_DDG,
    PYROSETTA_CMS,
    PYROSETTA_SAP_SCORE,
)
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table

# Interface-related descriptors grouped by category
INTERFACE_DESCRIPTORS_BACKBONE = [
    N_CONTACTS_TO_INTERFACE,
    N_CONTACTS_TO_HOTSPOTS,
    N_HOTSPOTS_ON_INTERFACE,
    INTERFACE_TARGET_RESIDUES,
]

INTERFACE_DESCRIPTORS_PYROSETTA = [
    PYROSETTA_DDG,
    PYROSETTA_CMS,
    PYROSETTA_SAP_SCORE,
]

INTERFACE_DESCRIPTORS_AF2 = [
    AF2_PRIMARY_IPAE,
    AF2_PRIMARY_IPTM,
]

ALL_INTERFACE_DESCRIPTORS = INTERFACE_DESCRIPTORS_BACKBONE + INTERFACE_DESCRIPTORS_PYROSETTA + INTERFACE_DESCRIPTORS_AF2


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
                + ". Please mark some designs as accepted in the **Jobs** page."
            )
            return

    elif not design_ids:
        # Empty list explicitly passed to design_ids
        st.write("No designs selected")
        return

    st.header(f"Interface analyzer | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    design_jobs = get_cached_design_jobs([pool.design_job_id for pool in pools if pool.design_job_id])
    if not design_jobs:
        st.warning("Selected pools have no design jobs. Please select pools with completed design jobs.")
        return

    badges = [f":grey-badge[{pool.name}]" for pool in pools]
    st.write("Selected pools: " + " ".join(badges))

    # Refresh descriptors
    refresh_descriptors(
        design_ids=design_ids,
    )

    descriptors_by_key = get_cached_available_descriptors(design_ids)
    interface_descriptors_by_key = {
        desc.key: desc for desc in ALL_INTERFACE_DESCRIPTORS if desc.key in descriptors_by_key
    }

    if INTERFACE_TARGET_RESIDUES.key not in interface_descriptors_by_key:
        st.warning("Interface analysis metrics are not provided by this design workflow.")
        return

    descriptors_df = get_wide_descriptor_table(
        design_ids=design_ids, descriptor_keys=interface_descriptors_by_key.keys(), nested=False, human_readable=False
    )

    # Average interface metrics
    st.write("#### Interface metrics summary")
    interface_metrics_summary(descriptors_df, interface_descriptors_by_key)

    # Summary table per target interface residue
    st.write("#### Target interface residue statistics")
    st.text(
        "Shows which target residues are in contact with the binder backbone (CA within 8Å)",
        help="Note that pools may have different target structures and residue numberings.",
    )
    # NOTE: different pools may have different target structures and thus different interface residues and residue numberings
    interface_residues_table(descriptors_df)

    # Summary table per design and per target interface residue
    st.write("#### Target interface residues by design")
    st.text(
        "Matrix showing which target residues are in contact with the binder backbone (CA within 8Å) in each design",
        help="Note that pools may have different target structures and residue numberings.",
    )
    # NOTE: different pools may have different target structures and thus different interface residues and residue numberings
    interface_residues_table_by_design(descriptors_df)

    # TODO: Target structure view
    # We could visualize the target and color all interface residues on it (darker residues = more designs with that contact)
    # Issue: In the pools, we can have different target structures, so we would need to group by target structure first...

    # Individual design exploration
    st.write("#### Design details")

    interface_design_visualization_fragment(design_ids, descriptors_df, interface_descriptors_by_key)


@st.fragment()
def interface_metrics_summary(descriptors_df: pd.DataFrame, descriptors_by_key: Dict[str, Descriptor]):
    """Display summary statistics for interface metrics.

    Args:
        descriptors_df: DataFrame with descriptor values (can be multiple designs or single design)
        descriptors_by_key: Dictionary mapping descriptor keys to descriptor objects
    """
    if descriptors_df.empty:
        st.info("No interface metrics available for the selected designs.")
        return

    # Determine if we should show averages or individual values
    is_single_design = len(descriptors_df) == 1

    # Display metrics in columns
    n_cols = 3
    cols = st.columns(n_cols)

    col_idx = 0
    for col_key in descriptors_df.columns:
        descriptor = descriptors_by_key.get(col_key)
        values = descriptors_df[col_key].dropna()

        if descriptor is None or not isinstance(descriptor, NumericDescriptor):
            continue

        if len(values) == 0:
            continue

        # Compute value: mean for multiple designs, single value otherwise
        value = values.mean() if not is_single_design else values.iloc[0]

        # Format values based on column name
        if "pTM" in col_key or "pLDDT" in col_key:
            formatted_value = f"{value:.3f}"
        elif "RMSD" in col_key or "PAE" in col_key or "ddG" in col_key:
            formatted_value = f"{value:.2f}"
        else:
            formatted_value = f"{value:.1f}"

        # Add "Average " prefix for multiple designs
        label = f"Average {descriptor.name}" if not is_single_design else descriptor.name

        with cols[col_idx % n_cols]:
            st.metric(
                label=label,
                value=formatted_value,
                delta=None,
                help=descriptor.description,
            )

        col_idx += 1

    if col_idx == 0:
        st.info("No interface metrics available.")


@st.fragment()
def interface_residues_table(descriptors_df: pd.DataFrame):
    """Display table of interface residues and their presence across designs."""
    descriptor = INTERFACE_TARGET_RESIDUES

    # Check if interface residues column exists
    if descriptor.key not in descriptors_df.columns:
        st.warning("No interface residue data available.")
        return

    # Get residue values from DataFrame
    residue_values = descriptors_df[descriptor.key].dropna().tolist()

    if not residue_values:
        st.warning("No interface residue data available.")
        return

    residue_df = get_residue_presence_df(descriptor, residue_values, len(descriptors_df))

    if residue_df is None or residue_df.empty:
        st.warning("No interface residue data available.")
    else:
        st.dataframe(
            residue_df,
            column_config={
                descriptor.name: st.column_config.Column(descriptor.name),
                "% of designs": st.column_config.ProgressColumn(
                    "% of designs",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                    help="Percentage of designs with contact to this residue",
                ),
            },
            hide_index=True,
            width="stretch",
            height="auto",
        )


@st.fragment()
def interface_residues_table_by_design(descriptors_df: pd.DataFrame):
    """Display table showing which interface residues are present in each design."""
    descriptor = INTERFACE_TARGET_RESIDUES

    # Check if interface residues column exists
    if descriptor.key not in descriptors_df.columns:
        st.warning("No interface residue data available.")
        return

    # Get residue values as a Series with design IDs as index
    descriptor_values = descriptors_df[descriptor.key]

    if not any(v is not None and pd.notna(v) for v in descriptor_values):
        st.warning("No interface residue data available.")
        return

    table_data, column_config, caption, format_func = residue_number_descriptor_detail_table(
        descriptor, descriptor_values
    )
    # st.caption(caption)
    st.dataframe(
        table_data,
        column_config=column_config,
        width="stretch",
        height="auto",
    )


def get_molstar_residue_selections(interface_residues: List[str]) -> List[str]:
    """Convert interface residue strings to molstar selection format."""
    selections = []
    for res in interface_residues:
        res_number = int(res[1:])
        selections.append(f"{res}-{res_number}")
    return selections


@st.fragment()
def design_interface_detail(
    design_id: str, descriptors_df: pd.DataFrame, interface_descriptors_by_key: Dict[str, Descriptor]
):
    """Display detailed interface information for a single design."""
    design = get_cached_design(design_id)

    # Get interface residues for this design from descriptors_df
    interface_residues_str = (
        descriptors_df.loc[design_id, INTERFACE_TARGET_RESIDUES.key]
        if design_id in descriptors_df.index and INTERFACE_TARGET_RESIDUES.key in descriptors_df.columns
        else None
    )

    # Parse residues list once
    interface_residues = []
    if interface_residues_str and pd.notna(interface_residues_str):
        interface_residues = [r.strip() for r in str(interface_residues_str).split(",") if r.strip()]

    # TODO: Improve visualization of the interface - Maybe it is possible to display contacts?
    colors = {
        "chain-id": "Color by chain",
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
    molstar_custom_component(
        structures=[
            StructureVisualization(
                pdb=storage.read_file_str(design.structure_path),
                color=color,
                representation_type="cartoon+ball-and-stick",
                highlighted_selections=get_molstar_residue_selections(interface_residues),
            )
        ],
        key="interface_highlighted_structure",
    )

    # Display interface residues
    st.write("**Interface Residues**")
    if interface_residues:
        badges = " ".join([f":gray-badge[{res}]" for res in interface_residues])
        st.write(badges)
    else:
        st.info("No interface residues found.")

    # Display interface metrics
    if design_id in descriptors_df.index:
        interface_metrics_summary(
            descriptors_df.loc[[design_id]],
            interface_descriptors_by_key,
        )
    else:
        st.info("No interface metrics available for this design.")

    st.markdown("#### Sequence")

    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id) if pool.design_job_id else None
    WorkflowType = type(design_job.workflow) if design_job and design_job.workflow else DesignWorkflow
    WorkflowType.visualize_single_design_sequences(design_id)

    st.markdown(f"#### Download {design_id}")

    download_job_designs_component(design_ids=[design_id], pools=[pool], key="single")


@st.fragment
def interface_design_visualization_fragment(
    design_ids: List[str], descriptors_df: pd.DataFrame, interface_descriptors_by_key: dict
):
    """Fragment for browsing individual designs."""
    # Optional filter for designs with contact to specific target residue
    if INTERFACE_TARGET_RESIDUES.key not in descriptors_df.columns:
        st.warning("No interface residue data available")
        return

    interface_residues = set(
        x.strip() for row in descriptors_df[INTERFACE_TARGET_RESIDUES.key].dropna() for x in row.split(",")
    )
    target_residue = st.selectbox(
        "Filter designs by target interface residue",
        options=interface_residues,
        index=None,
        placeholder="Show all designs (no residue filter)",
        help=(
            "Select a target interface residue to only show designs where the binder contacts this residue. "
            "Residue contacts are determined by backbone CA atoms within 8Å of the target. "
        ),
    )
    if target_residue:
        selected_design_ids = descriptors_df[
            descriptors_df[INTERFACE_TARGET_RESIDUES.key].apply(
                lambda x: target_residue in str(x).split(",") if pd.notna(x) else False
            )
        ].index.tolist()
        st.write(f"Showing {len(selected_design_ids):,} designs that interact with target residue {target_residue}")
    else:
        st.write("Showing all designs. Use the dropdown above to select designs that bind a specific target residue.")
        selected_design_ids = design_ids

    # Use the navigation selector component
    labels_by_design_id = descriptors_df.loc[selected_design_ids, INTERFACE_TARGET_RESIDUES.key].to_dict()
    design_id = design_navigation_selector(
        selected_design_ids, key="interface_selected_design", fmt=labels_by_design_id
    )

    design_labeling_fragment(design_id=design_id, key_suffix=f"interface_{design_id}")

    design_interface_detail(design_id, descriptors_df, interface_descriptors_by_key)
