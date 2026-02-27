import os
import json
from ovo.app.components.molstar_custom_component.dataclasses import StructureVisualization, ChainVisualization
import uuid
import glob

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "frontend/build")

_component_func = None


def molstar_custom_component(
    structures: list[StructureVisualization],
    key: str | None,
    height: str | int = "500px",
    width: str | int = "100%",
    show_controls=False,
    selection_mode=False,
    download_filename=None,
    html_filename=None,
    force_reload=False,
):
    """Create a new instance of "molstar_custom_component".

    Parameters
    ----------
    structures: list[StructureVisualization]
        A list containing definitions for the structure visualizations.
    height: str
        Height of the component
    width: str
        Width of the component
    show_controls: bool
        Show panels with tools and sequence
    selection_mode: bool
        Turn on selection mode
    download_filename : str or None, optional
        If provided, enables a download button for the structure's PDB files with this filename.
    html_filename : str or None, optional
        If provided, enables a button to download the current visualization as an HTML file with this filename.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    force_reload: bool, default False
        although component should reload all settings automatically, sometimes it's useful to force reload of the component,
        should be turned on only when something has just changed (such as highlighted selections)

    Returns
    -------
    Data from Mol* in JSON format.

    """
    global _component_func
    if _component_func is None:
        import streamlit.components.v1 as components

        _component_func = components.declare_component("molstar_custom_component", path=build_dir)

    serializedStructures = json.dumps([struct.to_dict() for struct in structures])

    component_value = _component_func(
        structures=serializedStructures,
        height=f"{height}px" if isinstance(height, int) else height,
        width=f"{width}px" if isinstance(width, int) else width,
        showControls=show_controls,
        selectionMode=selection_mode,
        forceReload=force_reload,
        key=key,
    )

    if download_filename:
        import streamlit as st

        for structure in structures:
            st.download_button(
                label="Download PDB",
                data=structure.pdb,
                file_name=f"{download_filename}.pdb",
            )
            break

    if html_filename:
        import streamlit as st

        st.download_button(
            "Download HTML",
            data=molstar_html(structures),
            file_name=f"{html_filename}.html",
            mime="text/html",
        )

    return component_value


_static_files = None


def read_static_files():
    global _static_files
    if _static_files is None:
        css_files = sorted(glob.glob(os.path.join(build_dir, "chunk-*.css")))
        if not css_files:
            raise FileNotFoundError("No CSS file found in the build directory.")
        with open(css_files[0]) as f:
            css_content = f.read()
        js_files = sorted(glob.glob(os.path.join(build_dir, "chunk-*.js")))
        if not js_files:
            raise FileNotFoundError("No JS file found in the build directory.")
        with open(js_files[0]) as f:
            js_content = f.read()
        _static_files = css_content, js_content
    return _static_files


def molstar_html(structures: list[StructureVisualization]):
    css_content, js_content = read_static_files()

    return f"""
            <div id="root" class="molstar_notebook"></div>
            <style type="text/css">
            {css_content}
            </style>
            <script>
            window.STRUCTURES = {json.dumps([s.to_dict() for s in structures])};
            
            // JS bundle
            {js_content.replace('</script>"', '</" + "script>"')}
            // watch out that here the original js_content might also include closing script tags NOT in quotes!
            // the problem is that doing things like replacing with </ script> will break the code functionality anyway...
            </script>
            """


def molstar_notebook(
    structures: list[StructureVisualization],
    height="500px",
    width="800px",
):
    from IPython.display import display, HTML, Javascript

    html_data = molstar_html(structures).strip()
    assert html_data.endswith("</script>"), "Molstar HTML should end with </script>"

    wrapper_id = f"molstar_{uuid.uuid4()}"

    # JavaScript code to create a Blob URL and a download link
    # We turn "...</script>" into "...</script" + ">" to avoid closing script tag in VScode
    js_code = f"""
    setTimeout(function(){{
        var wrapper = document.getElementById("{wrapper_id}")
        if (wrapper === null) {{
            throw new Error("Wrapper element #{wrapper_id} not found anymore")      
        }}
        var blob = new Blob([{json.dumps(html_data[:-1])} + ">"], {{ type: 'text/html' }});
        var url = URL.createObjectURL(blob);
    
        // Create the iframe
        var iframe = document.createElement('iframe');
        iframe.src = url;
        iframe.style = "border: 0; width: {width}; height: {height}"
        iframe.allowFullscreen = true;
        wrapper.appendChild(iframe);
    
        // Create the download link
        var link = document.createElement('a');
        link.href = url;
        link.download = "molstar_my_filename.html";
        link.innerText = "Download HTML";
        link.style.display = "block";
        link.style.marginTop = "10px";
        wrapper.appendChild(link);
    }}, 100);
    """

    # Display the iframe
    display(HTML(f'<div id="{wrapper_id}"></div>'))
    display(Javascript(js_code))
