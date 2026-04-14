import streamlit as st
from streamlit.navigation.page import StreamlitPage

from ovo import config, get_username
from ovo.core.plugins import get_extension_points, WorkflowPage
import importlib
import os

welcome_page = st.Page("app/pages/welcome.py", title="🥚 Welcome", default=True)
project_page = st.Page("app/pages/project.py", title="💼 Project")
jobs_page = st.Page("app/pages/jobs/jobs.py", title="⏳ Jobs")
designs_page = st.Page("app/pages/designs/designs.py", title="🐣 Designs")
workflows_page = st.Page("app/pages/workflows.py", title="▶️ Workflows")

import_export_page = st.Page("app/pages/import_export.py", title="📦 Import & Export")
admin_debug_page = st.Page("app/pages/debug.py", title="🖥️ Debug")


def get_pages():
    # NOTE this needs to be inside a function so that it's called for each user separately!
    # Page paths relative to entry point (run_app.py)
    main_pages = {
        "Browse": [
            welcome_page,
            project_page,
            jobs_page,
            designs_page,
        ],
        "Submit": [
            workflows_page,
        ],
    }

    if get_username() in config.auth.admin_users:
        main_pages["Admin section"] = [
            admin_debug_page,
        ]

    # These pages are not shown in the sidebar but can be accessed via switch_page or direct URL
    hidden_pages = {"Hidden": [import_export_page]}

    return main_pages, hidden_pages


builtin_workflow_pages: list[WorkflowPage] = [
    WorkflowPage(
        module_name="ovo",
        title="🏗️ RFdiffusion scaffold design",
        path="app/pages/rfdiffusion/scaffold_design.py",
        category="RFdiffusion",
        labels=["RFdiffusion", "Scaffold design"],
        thumbnail="app/assets/workflows/scaffold_design.png",
        short_description="""
        This workflow enables designing new proteins that preserve specified “motif” segments 
        from an existing structure by combining RFdiffusion for backbone generation, 
        LigandMPNN for sequence and side-chain rotamer design, 
        and AlphaFold2 or other methods of choice. 
        Such motifs may include enzyme active sites, protein-protein interaction interfaces, or any user-defined set of residues.
        Users supply a structure, mark fixed residues and define a contig describing how fixed segments 
        are connected and how many residues to generate between them.
        """,
    ),
    WorkflowPage(
        module_name="ovo",
        title="🧬 RFdiffusion binder design",
        path="app/pages/rfdiffusion/binder_design.py",
        category="RFdiffusion",
        labels=["RFdiffusion", "Binder design"],
        thumbnail="app/assets/workflows/binder_design.png",
        short_description="""
        This workflow designs new binders to a target protein by generating de novo binder backbones with RFdiffusion, 
        designing sequences and side-chain rotamers using LigandMPNN (and optionally Rosetta FastRelax), 
        and validating binder–target complexes with AlphaFold2 or other methods of choice. 
        Users provide a target structure and optional hotspot residues to define the binding site. Then they
        trim the target chain to relevant regions, set a binder length range and design/relax parameters, 
        and receive binder sequences and complex structures along with Rosetta ddG, 
        AlphaFold2 refolding metrics and other descriptors.
        """,
    ),
    WorkflowPage(
        module_name="ovo",
        title="♻️ RFdiffusion binder diversification",
        path="app/pages/rfdiffusion/binder_diversification.py",
        category="RFdiffusion",
        labels=["RFdiffusion", "Binder design", "Optimization"],
        thumbnail="app/assets/workflows/binder_diversification.png",
        short_description="""
        This workflow enables diversifying a set of protein binder designs by generating similar binder backbones 
        and additional sequence designs 
        by applying RFdiffusion partial diffusion followed by LigandMPNN sequence design and refolding with
        AlphaFold2 or other methods of choice.
        Users provide one or more structure files or OVO design IDs, may specify hotspot residues and a noising strength, 
        and receive binder sequences and complex models along with backbone, sequence, Rosetta/PyRosetta, 
        and AlphaFold2 refolding descriptors to identify promising variants.
        """,
    ),
    WorkflowPage(
        module_name="ovo",
        title="⚒️ BindCraft binder design",
        path="app/pages/bindcraft/bindcraft_binder_design.py",
        category="BindCraft",
        labels=["BindCraft", "Binder design"],
        thumbnail="app/assets/workflows/binder_design.png",
        short_description="""
        BindCraft designs linear peptide or miniprotein binders by iteratively optimizing binder sequences 
        with AlphaFold2 backpropagation (ColabDesign) in a multistage design phase, 
        redesigning non-interface residues with SolubleMPNN or ProteinMPNN for improved solubility, 
        and filtering designs using AlphaFold2 monomer reprediction plus PyRosetta scoring.
        Users input a target structure, choose hotspots and a design protocol (Default, Beta-sheet, Peptide), 
        set binder length and stopping criteria, and receive accepted binder sequences 
        and complex structures along with Rosetta ddG, 
        AlphaFold2 refolding metrics and other descriptors.
        """,
    ),
]

# Get tuple of (WorkflowPage, StreamlitPage) for all workflow pages,
# pages from plugins will be added below
workflow_page_tuples: list[tuple[WorkflowPage, StreamlitPage]] = [
    (p, st.Page(page=p.path, title=p.title)) for p in builtin_workflow_pages
]

url_paths = set(page._url_path for _, page in workflow_page_tuples)
for workflow_page in get_extension_points("ovo.workflow_page", WorkflowPage):
    assert "/" not in workflow_page.path and not workflow_page.path.endswith(".py"), (
        f"Plugin page should be defined by module path (my_tool.page_module), got {workflow_page.path}"
    )
    module_name = workflow_page.path.split(".")[0]
    module = importlib.import_module(module_name)
    url_path = workflow_page.path.split(".")[-1]
    while url_path in url_paths:
        url_path += "_copy"
    url_paths.add(url_path)
    page_file_path = workflow_page.path.removeprefix(module_name).removeprefix(".").replace(".", "/") + ".py"
    workflow_page_tuples.append(
        (
            workflow_page,
            st.Page(
                page=os.path.join(os.path.dirname(module.__file__), page_file_path),
                url_path=url_path,
                title=workflow_page.title,
            ),
        )
    )
