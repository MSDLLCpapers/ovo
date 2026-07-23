import json
import os
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")
_component_func = components.declare_component("contigs_organizer", path=build_dir)


# Create a wrapper function for the component. This is an optional
# best practice to validate input and add documentation comments.
def contigs_organizer(
    contigs: str,
    pdb: str,
    colors: dict[str, str],
    key: str,
    unindexed_segments: list[str] | None = None,
):
    """Create a new instance of "contigs_organizer".

    Parameters
    ----------
    contigs: str
        Original contigs definition
    pdb: str
        PDB of the relevant structure
    key: str
        A key that uniquely identifies this component to avoid re-mounting on changed parameters.
    colors: dict[str, str]
        Dictionary mapping segment strings (A123-456) to colors (#00ff00)
    unindexed_segments: list[str] | None
        Fixed segments (e.g. "A244-246") that should be initially marked as unindexed.

    Returns
    -------
    A JSON information about the organized contigs.

    """
    component_value = _component_func(
        contigs=contigs,
        pdb=pdb,
        colors=json.dumps(colors),
        unindexed_segments=json.dumps(unindexed_segments or []),
        key=key,
    )

    return component_value
