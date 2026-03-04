import os
import re
import zipfile

import streamlit as st

from ovo import storage, get_username, config, db
from ovo.core.database.models import Pool, Design
from ovo.core.database.models_proteinqc import ProteinQCWorkflow
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow
from ovo.core.logic.round_logic import get_or_create_project_rounds
from ovo.core.utils.pdb import mmcif_to_pdb


@st.dialog("Upload new pool of designs", width="large")
def create_new_pool():
    content = st.empty()
    with content.container():
        project_id = st.session_state.project.id

        rounds_by_id = get_or_create_project_rounds(project_id=project_id)
        round_ids = list(rounds_by_id.keys())
        round_id = st.selectbox(
            "Project Round",
            options=round_ids,
            format_func=lambda i: rounds_by_id[i].name,
            key="custom_pool_round_selectbox",
            index=len(round_ids) - 1,
            width=300,
        )

        files = st.file_uploader(
            "Structure files *",
            accept_multiple_files=True,
            type=["pdb", "cif", "mmcif", "zip"],
            key="uploader",
        )

        name = st.text_input("Pool name *", placeholder="Descriptive name for this collection of designs")

        if name and db.count(Pool, round_id=round_id, name=name):
            st.error(f"A pool with this name already exists in this round. Please choose a different name.")

        description = st.text_area(
            "Pool description",
            placeholder="Optional longer description of this pool",
        )

        with st.columns(2)[0]:
            chains = st.text_input(
                "Chain(s) to analyze",
                help="Chain IDs separated by comma (A,B,C), space (A B C) or concatenated (ABC)",
                value="",
            )
            chains = chains.replace(" ", "").replace(",", "")

        if not files:
            help = "No files selected"
        elif not name:
            help = "Please enter a pool name"
        elif not chains:
            help = "Please enter chain IDs to analyze"
        else:
            help = None
        with st.columns([3, 1])[1]:
            submit = st.button(
                "Upload pool",
                disabled=not files or not name or not chains,
                help=help,
                key="submit",
                type="primary",
                width="stretch",
            )

    if submit:
        assert re.match(r"^[A-Z]+$", chains), f"Invalid chains '{chains}'"
        content.empty()

        username = get_username()

        # Create pool
        pool = Pool(id=Pool.generate_id(), author=username, round_id=round_id, name=name, description=description)

        # Save the files to storage and create designs
        st.text("Uploading designs...")
        shared_args = dict(
            storage=storage,
            chains=list(chains),
            project_id=project_id,
            pool_id=pool.id,
        )
        cif_converted = False
        conversion_warnings: list[str] = []
        designs = []
        for file in files:
            if file.name.lower().endswith(".pdb"):
                designs.append(Design.from_pdb_file(filename=file.name, pdb_str=file.read().decode(), **shared_args))
            elif file.name.lower().endswith((".cif", ".mmcif")):
                cif_converted = True
                pdb_filename = os.path.splitext(file.name)[0] + ".pdb"
                result = mmcif_to_pdb(file.read().decode())
                conversion_warnings.extend(result.warnings)
                designs.append(Design.from_pdb_file(filename=pdb_filename, pdb_str=result.pdb_string, **shared_args))
            elif file.name.lower().endswith(".zip"):
                found = False
                with zipfile.ZipFile(file) as z:
                    for zip_info in z.infolist():
                        if zip_info.filename.startswith("__MACOSX/"):
                            continue
                        filename = os.path.basename(zip_info.filename)
                        if filename.startswith("."):
                            continue
                        if filename.lower().endswith(".pdb"):
                            found = True
                            print("Reading", zip_info.filename)
                            pdb_str = z.read(zip_info.filename).decode()
                            designs.append(
                                Design.from_pdb_file(
                                    filename=filename,
                                    pdb_str=pdb_str,
                                    **shared_args,
                                )
                            )
                        elif filename.lower().endswith((".cif", ".mmcif")):
                            found = True
                            cif_converted = True
                            print("Reading and converting", zip_info.filename)
                            pdb_filename = os.path.splitext(filename)[0] + ".pdb"
                            result = mmcif_to_pdb(z.read(zip_info.filename).decode())
                            conversion_warnings.extend(result.warnings)
                            designs.append(
                                Design.from_pdb_file(
                                    filename=pdb_filename,
                                    pdb_str=result.pdb_string,
                                    **shared_args,
                                )
                            )
                if not found:
                    raise ValueError(f"No PDB or CIF files found in zip archive '{file.name}'")

        if len(designs) > 1:
            st.text(f"Saving {len(designs):,} designs to DB...")

        # Save designs to db because we load them from db when submitting the proteinqc job
        db.save_all(designs + [pool])

        # Trigger sequence composition computation with local conda scheduler
        st.text("Submitting descriptor job...")
        submit_descriptor_workflow(
            workflow=ProteinQCWorkflow(
                tools=["seq_composition"],
                chains=list(chains),
                design_ids=[design.id for design in designs],
            ),
            scheduler_key=config.local_scheduler,
            project_id=project_id,
        )

        if cif_converted:
            st.warning("Some CIF files were converted to PDB format.")
            for warning in conversion_warnings:
                st.warning(warning)

        st.session_state.files = None
        st.text("✅ Done")

        st.rerun()
