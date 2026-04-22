import traceback
from pathlib import Path
import streamlit as st

from ovo import config, __version__
from ovo.app.utils.page_init import initialize_page

initialize_page("OVO, where new proteins hatch!")

st.title("Welcome to OVO" + (f", {st.user.given_name}!" if st.user.get("given_name") else "!"))

with st.container(width=800):
    if config.templates.welcome:
        st.markdown(Path(config.templates.welcome).read_text(), unsafe_allow_html=True)

    st.markdown(f"""
    
### Getting started

Please select a *design* workflow in the left panel.
Each step-by-step submission form is customized to help you select all workflow parameters for a specific design use case. 
Submitting the workflow will create a *job*. 
Each job produces a *pool* of designs. You can also use OVO to upload a custom pool structures or sequences for analysis.
        
The project dropdown in the left sidebar allows you to organize your jobs and designs into *projects*.
Jobs in each project can be organized into *rounds*.

The ⏳ *Jobs* page shows all running and finished jobs neatly together with their workflow parameters. 
In each *job result* page, you can explore all generated designs and their descriptors such as AlphaFold2 RMSD and Rosetta ddG. 
You will be able to adjust *acceptance thresholds* to find the most promising designs we call *accepted designs*.

The 🐣 *Designs* page focuses further on the *accepted designs*. The 🔵 *Explorer* view enables plotting
design descriptors and visualizing their structures. The 🔎 *ProteinQC* view provides additional computational evaluation
informing you about the quality of the designs using additional descriptors focused on 
physicochemical properties, sequence composition, and fitness from protein language models.
""")


@st.cache_data(show_spinner=False)
def get_latest_ovo_version():
    try:
        # use pip api to check latest version of ovo
        import requests

        response = requests.get("https://pypi.org/pypi/ovo/json", timeout=5)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        latest_version_tuple = tuple(int("".join(v for v in x if v.isnumeric())) for x in latest_version.split("."))
        current_version_tuple = tuple(
            int("".join([v for v in x if v.isnumeric()] or "0")) for x in __version__.split(".")
        )
        if latest_version_tuple > current_version_tuple:
            return latest_version
        else:
            return None
    except:
        # Silently ignore any errors
        traceback.print_exc()
        return False


if config.props.check_new_version:
    if new_version := get_latest_ovo_version():
        st.write(f"""
✨ A new version is available: **OVO {new_version}**! You are currently using version **OVO {__version__}**.
See [release notes](https://ovo.dichlab.org/docs/user_guide/release_notes.html) for more information.
""")

st.write(
    """
### Learning resources

- [User Guide](https://ovo.dichlab.org/docs/user_guide/)
- [Ovo 2-Minute Overview Video](https://github.com/user-attachments/assets/7b339fa6-c6de-467d-90d0-5cd15f83c498)
- [Ovo Protein Design Workflows Webinar](https://www.youtube.com/watch?v=qzACZcLWnTs)
- [Release Notes](https://ovo.dichlab.org/docs/user_guide/release_notes.html)
"""
)
if config.templates.welcome_appendix:
    st.markdown(Path(config.templates.welcome_appendix).read_text(), unsafe_allow_html=True)
else:
    st.markdown("""
    ---
    Report bugs and feature requests at [github.com/MSDLLCpapers/ovo/issues](https://github.com/MSDLLCpapers/ovo/issues)            
    """)
