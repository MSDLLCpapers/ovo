import re
import time
import traceback

import streamlit as st

from ovo import get_username, config, db
from ovo.app.components.navigation import ROUND_IDS_QUERY_PARAM
from ovo.app.components.submission_components import get_next_round_name
from ovo.core.database.models import Pool, Round
from ovo.core.database.models_proteinqc import ProteinQCWorkflow
from ovo.core.logic.descriptor_logic import submit_descriptor_workflow
from ovo.core.logic.design_logic import create_designs_from_structure_files, create_designs_from_dataframe
from ovo.core.logic.round_logic import get_or_create_project_rounds
from ovo.core.utils.export import parse_tabular_file
from ovo.core.utils.formatting import truncate_middle


@st.dialog("Upload new pool of designs", width="large")
def create_new_pool():
    content = st.empty()
    with content.container():
        project_id = st.session_state.project.id

        rounds_by_id = get_or_create_project_rounds(project_id=project_id)
        round_ids = list(rounds_by_id.keys())
        options = round_ids + ["__new__"]

        col1, col2, _ = st.columns([1, 1, 1])

        with col1:
            round_id = st.selectbox(
                "Project Round",
                options=options,
                format_func=lambda i: rounds_by_id[i].name if i != "__new__" else "+ Create new round",
                # Use len(round_ids) in key to refresh widget after creation of a new round
                key=f"custom_pool_round_selectbox_{len(round_ids)}",
                index=len(round_ids) - 1 if round_ids else 0,
            )

        new_round_name = None
        if round_id == "__new__":
            with col2:
                new_round_name = st.text_input(
                    "New round name",
                    value=get_next_round_name(rounds_by_id[round_ids[-1]].name),
                    placeholder="Enter round name",
                    key="new_round_name",
                )

        files = st.file_uploader(
            "Structures or sequences",
            accept_multiple_files=True,
            type=["pdb", "cif", "mmcif", "zip", "csv", "tsv", "xlsx", "xls"],
            key="uploader",
            help="Upload PDB/CIF/MMCIF structure files, or CSV/TSV/XLSX files with sequence data",
        )

        # Detect if any tabular files are uploaded
        tabular_files = [f for f in (files or []) if f.name.lower().endswith((".csv", ".tsv", ".xlsx", ".xls"))]
        structure_files = [f for f in (files or []) if not f.name.lower().endswith((".csv", ".tsv", ".xlsx", ".xls"))]

        if tabular_files and structure_files:
            st.error("Please upload either structure files (PDB/CIF) or tabular files (CSV/TSV/XLSX), not both.")
            return

        # Configuration for tabular files
        tabular_config = None
        if tabular_files:
            if len(tabular_files) > 1:
                # TODO should we include all in the same pool or in different pools?
                st.error("Please upload only one tabular file at a time")
                return

            # Parse the first tabular file
            with st.container(horizontal=True, horizontal_alignment="distribute"):
                header_container = st.empty()
                header = [0, 1] if st.checkbox("Two-level header", key="two_level_header") else 0
            try:
                df = parse_tabular_file(tabular_files[0], header=header)
                header_container.write(f"**Preview of {tabular_files[0].name}** ({len(df)} rows)")
                st.dataframe(df.head(5), use_container_width=True, hide_index=True)

                columns = df.columns.tolist()

                st.subheader("Column Configuration")

                # ID column selection
                id_column = st.selectbox(
                    "ID column",
                    options=columns,
                    index=0,
                    help="Select the column to use as design ID",
                    key="id_column",
                )
                id_values = df[id_column].dropna()
                if id_values.empty:
                    st.error(f"The selected ID column '{id_column}' does not contain any non-empty values.")
                    return

                st.write(
                    f"Will create design IDs from '{id_column}' column, for example: 'ovo_xyz_{id_values.iloc[0]}'"
                )

                # Sequence columns selection
                example_values = (
                    df.apply(lambda col: col.dropna().iloc[0] if not col.dropna().empty else "N/A")
                    .astype(str)
                    .to_dict()
                )
                sequence_columns = st.multiselect(
                    "Sequence column(s)",
                    placeholder="Please select at least one column containing protein sequences",
                    options=[col for col in columns if col != id_column],
                    format_func=lambda c: f"{c} | {truncate_middle(example_values[c], 30)}",
                    help="Select one or more columns containing protein sequences",
                    key="sequence_columns",
                )

                # Chain ID configuration for each sequence column
                column_chains = {}
                if sequence_columns:
                    st.write("**Chain ID assignment:**")
                    # Generate default chain IDs: A, B, C, ...
                    default_chains = [chr(65 + i) for i in range(len(sequence_columns))]

                    with st.container(horizontal=True):
                        for i, seq_col in enumerate(sequence_columns):
                            # Check if the column name is already a single capital letter
                            if len(seq_col) == 1 and seq_col.isupper():
                                default_value = seq_col
                            else:
                                default_value = default_chains[i]

                            chain_ids = st.text_input(
                                f"Chain ID(s) to be assigned to '{seq_col}'",
                                value=default_value,
                                help="Single chain ID (e.g., 'A') or multiple IDs for symmetric chains (e.g., 'A,B')",
                                key=f"chain_id_{seq_col}",
                                width=220,
                            ).strip()
                            if chain_ids:
                                if not re.match(r"^[A-Z](,[A-Z])*$", chain_ids):
                                    st.error(
                                        "Chain IDs must be single capital letters, optionally separated by commas (e.g., 'A' or 'A,B,C')"
                                    )
                                else:
                                    column_chains[seq_col] = chain_ids

                tabular_config = {
                    "df": df,
                    "id_column": id_column,
                    "column_chains": column_chains,
                }

                if column_chains:
                    st.write(f"Will create **{len(df)} designs** with the following chain assignments:")
                    for seq_col, chain_ids in column_chains.items():
                        example_seqs = df.set_index(id_column)[seq_col].dropna()
                        st.write(
                            f"- Column '{seq_col}' → Chain {chain_ids}, example: '{truncate_middle(str(example_seqs.iloc[0]), 50)}'"
                        )
                        nonstandard_mask = example_seqs.str.match(r"^[ACDEFGHIKLMNPQRSTVWY]+$")
                        if nonstandard_mask.isna().any():
                            raise ValueError(
                                f"Non-string values found in sequence column {seq_col}: "
                                f"{example_seqs[nonstandard_mask.isna()].head(3).to_dict()}"
                            )
                        nonstandard_seqs = example_seqs[~nonstandard_mask]
                        if not nonstandard_seqs.empty:
                            nonstandard_examples = [
                                f"'{i}': '{seq}'" for i, seq in nonstandard_seqs.head(3).to_dict().items()
                            ]
                            st.warning(
                                f"Column '{seq_col}' contains {len(nonstandard_seqs)} rows that don't look like protein sequences. "
                                f"Please verify or remove them to avoid downstream issues: {', '.join(nonstandard_examples)}"
                            )

            except Exception as e:
                traceback.print_exc()
                st.error(f"Error parsing table: {e}")
                return

        name = st.text_input(
            "Pool name", placeholder="Descriptive name for this collection of designs", key="pool_name"
        )

        if name and db.count(Pool, round_id=round_id, name=name):
            st.error(f"A pool with this name already exists in this round. Please choose a different name.")

        description = st.text_area(
            "Pool description (optional)",
            placeholder="Optional longer description of this pool",
        )

        # Chain input for structure files
        chains = None
        if structure_files:
            with st.columns(2)[0]:
                chains = st.text_input(
                    "Chain(s) to analyze",
                    help="Chain IDs separated by comma (A,B,C), space (A B C) or concatenated (ABC)",
                    value="",
                    key="chains_to_analyze",
                )
                chains = chains.replace(" ", "").replace(",", "")

        # Validation logic
        error = None
        if not files:
            error = "No files selected"
        elif not name:
            error = "Please enter a pool name"
        elif tabular_files:
            # For tabular files, check if configuration is complete
            if not tabular_config:
                error = "Error parsing tabular file"
            elif not tabular_config.get("column_chains"):
                error = "Please select at least one sequence column"
        elif not chains:
            error = "Please enter chain IDs to analyze"

        if round_id == "__new__":
            if not new_round_name.strip():
                error = "Please enter a name for the new round"
            else:
                if db.count(Round, project_id=project_id, name=new_round_name.strip()):
                    error = "A round with this name already exists in this project. Please choose a different name."

        with st.columns([3, 1])[1]:
            submit = st.button(
                "Upload pool",
                disabled=bool(error),
                help=error,
                key="submit",
                type="primary",
                width="stretch",
            )

    if submit:
        if structure_files and chains:
            assert re.match(r"^[A-Z]+$", chains), f"Invalid chains '{chains}'"

        content.empty()

        username = get_username()
        new_round = None

        if round_id == "__new__":
            new_round = Round(project_id=project_id, name=new_round_name.strip(), author=username)
            round_id = new_round.id

        # Create pool
        pool = Pool(id=Pool.generate_id(), author=username, round_id=round_id, name=name, description=description)

        conversion_warnings = []
        if tabular_files and tabular_config:
            # Handle tabular files
            st.text("Processing sequence data...")
            designs = create_designs_from_dataframe(
                **tabular_config,
                pool_id=pool.id,
            )

            # Get list of all unique chains from the designs for descriptor computation
            chains = sorted(
                set(chain for design in designs for chain in design.spec.chains for chain in chain.chain_ids)
            )

        # Handle structure files
        elif structure_files and chains:
            st.text("Uploading designs...")
            designs, conversion_warnings = create_designs_from_structure_files(
                structure_files=structure_files,
                chains=list(chains),
                pool=pool,
                project_id=project_id,
            )
        else:
            st.error("No valid files to process")
            return

        if conversion_warnings:
            st.warning("Some CIF files were converted to PDB format.")
            for warning in conversion_warnings:
                st.warning(warning)

        if len(designs) > 1:
            st.text(f"Saving {len(designs):,} designs to DB...")

        db.save_all(designs + ([new_round] if new_round else []) + [pool])

        # Trigger sequence composition computation with local conda scheduler
        try:
            st.text("Submitting descriptor job...")
            submit_descriptor_workflow(
                workflow=ProteinQCWorkflow(
                    tools=["seq_composition"],
                    chains=list(chains),
                    design_ids=[design.id for design in designs],
                    batch_size=100,
                ),
                scheduler_key=config.local_scheduler,
                project_id=project_id,
            )
        except Exception as e:
            traceback.print_exc()
            st.warning(f"Error submitting descriptor workflow: {e}")
            time.sleep(1)

        # Activate the selected round and pool
        st.query_params[ROUND_IDS_QUERY_PARAM] = round_id
        st.query_params["pool_ids"] = pool.id

        st.session_state.files = None
        st.text("✅ Done")

        st.rerun()
