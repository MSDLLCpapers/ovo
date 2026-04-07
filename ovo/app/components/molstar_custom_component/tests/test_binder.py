import streamlit as st
import os
from ovo.app.components.molstar_custom_component import molstar_custom_component
from ovo.app.components.molstar_custom_component.dataclasses import StructureVisualization, ChainVisualization

st.set_page_config(layout="wide")

pdb_path = os.path.join(os.path.dirname(__file__), "binder.pdb")

with open(pdb_path) as f:
    pdb = f.read()

cp = molstar_custom_component(
    structures=[
        StructureVisualization(
            pdb=pdb,
            highlighted_selections=["A22-25", "A28-30"],
            representation_type="cartoon",
            color="uniform",
            color_params={"value": "0x00ff00"},
            chains=[
                ChainVisualization(
                    chain_id="B",
                    representation_type="gaussian-surface",
                    color="hydrophobicity",
                )
            ],
        ),
    ],
    selection_mode=True,
    show_controls=True,
    key="example1",
    height=700,
)

st.write(cp)
