import streamlit as st
import os

from ovo.app.components.molstar_custom_component import molstar_custom_component
from ovo.app.components.molstar_custom_component.dataclasses import StructureVisualization
from ovo.core.utils.pdb import get_standardized_remarks_from_pdb_str
from ovo.core.utils.residue_selection import parse_contig_for_input_structure, parse_contig_for_output_structure

st.set_page_config(layout="wide")


@st.cache_data
def read_pdbs():
    with open(os.path.join(os.path.dirname(__file__), "scaffold_input.pdb")) as f:
        input_pdb = f.read()

    with open(os.path.join(os.path.dirname(__file__), "scaffold_output.pdb")) as f:
        output_pdb = f.read()

    return input_pdb, output_pdb


input_pdb, output_pdb = read_pdbs()

remarks = get_standardized_remarks_from_pdb_str(output_pdb)

contig = remarks["Standardized contig"]
st.write(contig)


input_segments = parse_contig_for_input_structure(contig)
output_segments = parse_contig_for_output_structure(contig)

left, right = st.columns(2)

with left:
    molstar_custom_component(
        structures=[
            StructureVisualization(pdb=input_pdb, contigs=input_segments),
        ],
        selection_mode=True,
        show_controls=True,
        key="example1",
        height=500,
    )
    st.write(input_segments)

with right:
    molstar_custom_component(
        structures=[
            StructureVisualization(pdb=output_pdb, contigs=output_segments),
        ],
        selection_mode=True,
        show_controls=True,
        key="example2",
        height=500,
    )
    st.write(output_segments)
