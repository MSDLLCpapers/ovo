import streamlit as st

from ovo import storage
from ovo.app.components import molstar_custom_component, StructureVisualization
from ovo.app.utils.cached_db import get_cached_design_ids, get_cached_design
from ovo.core.utils.pdb import align_multiple_proteins_pdb


@st.fragment
def __MODULE_NAME___fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = get_cached_design_ids(pool_ids=pool_ids, accepted=True)
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

    st.header(f"🔥 My Plugin | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    st.write("This is a template for a custom alignment plugin. You can modify this code to create your own view.")

    cols = st.columns([0.4, 0.1, 0.4, 0.1])

    if len(design_ids) < 2:
        st.warning("Please select at least two designs to align.")
        return

    first_design_id = cols[0].selectbox(
        "First design",
        options=design_ids,
        index=0,
        key="first_design_selectbox",
    )
    align_first_on = cols[1].text_input(
        "Align on chain",
        value="A",
        max_chars=1,
        width=100,
        key="first_align_chain_input",
    )
    second_design_id = cols[2].selectbox(
        "Second design",
        options=design_ids,
        index=1,
        key="second_design_selectbox",
    )
    align_second_on = cols[3].text_input(
        "Align on chain",
        value="A",
        max_chars=1,
        width=100,
        key="second_align_chain_input",
    )

    first_design = get_cached_design(first_design_id)
    second_design = get_cached_design(second_design_id)

    structures, rmsd = align_multiple_proteins_pdb(
        pdb_strs=[
            storage.read_file_str(first_design.structure_path),
            storage.read_file_str(second_design.structure_path),
        ],
        chain_residue_mappings=[[(align_first_on, None)], [(align_second_on, None)]],
        all_atom=False,
    )

    molstar_custom_component(
        structures=[
            StructureVisualization(pdb=structures[0], color="chain-id"),
            StructureVisualization(pdb=structures[1], color="chain-id"),
        ],
        key=f"alignment1",
        height=600,
    )

    st.write(f"Aligned on chains {align_first_on}:{align_second_on} with backbone RMSD: **{rmsd:.2f} Å**")
