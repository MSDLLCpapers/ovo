from __future__ import annotations

from typing import Any

from ovo.app.components.molstar_custom_component.dataclasses import (
    ColorScheme as ColorScheme,
    Representation as Representation,
    RepresentationType as RepresentationType,
    StructureFormat as StructureFormat,
    StructureVisualization as StructureVisualization,
    TrajectoryFormat as TrajectoryFormat,
    BondVisualization as BondVisualization,
)
from ovo.core.auth import is_running_in_streamlit


def is_running_in_jupyter() -> bool:
    try:
        ip = get_ipython()  # type: ignore[name-defined]  # noqa: F821
        return ip is not None and "IPKernelApp" in ip.config
    except NameError:
        return False


def molstar(
    *structures: StructureVisualization,
    height: str | int = "500px",
    width: str | int = "auto",
    key: str | None = None,
    show_controls: bool = False,
    selection_mode: bool = False,
    download_filename: str | None = None,
    html_filename: str | None = None,
    force_reload: bool = False,
) -> Any:
    """Render structures in a Mol* viewer with automatic environment detection (Streamlit/Jupyter/HTML).

    In Streamlit, renders an interactive component. In Jupyter, renders an iframe.
    Otherwise, returns an HTML string.
    """
    struct_list = list(structures)

    if is_running_in_streamlit():
        from ovo.app.components.molstar_custom_component import molstar_custom_component

        return molstar_custom_component(
            structures=struct_list,
            key=key,
            height=height,
            width="100%" if width == "auto" else width,
            show_controls=show_controls,
            selection_mode=selection_mode,
            download_filename=download_filename,
            html_filename=html_filename,
            force_reload=force_reload,
        )

    if is_running_in_jupyter():
        from ovo.app.components.molstar_custom_component import molstar_notebook

        if width == "auto":
            width = 800
        h = f"{height}px" if isinstance(height, int) else height
        w = f"{width}px" if isinstance(width, int) else width
        return molstar_notebook(struct_list, height=h, width=w)

    from ovo.app.components.molstar_custom_component import molstar_html

    return molstar_html(struct_list)
