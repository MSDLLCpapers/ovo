import re
import time
import traceback

import pandas as pd
import streamlit as st

from ovo import get_username, config, db
from ovo.app.components.download_component import download_bulk_config_button
from ovo.app.components.custom_elements import simple_tabs
from ovo.app.components.navigation import ROUND_IDS_QUERY_PARAM
from ovo.app.components.submission_components import get_next_round_name
from ovo.core.database.models import Design, Pool, Round
from ovo.core.logic.pool_logic import PoolUpload, create_pool_from_uploads
from ovo.core.plugins import DesignUploadOption, get_extension_points, load_variable
from ovo.app.utils.cached_db import get_cached_round, get_cached_pool_count
from ovo.core.logic.round_logic import get_or_create_project_rounds, get_or_create_archived_round, ARCHIVED_ROUND_NAME
from ovo.core.utils.export import parse_tabular_file
from ovo.core.utils.formatting import truncate_middle


# the built-in upload source, shown first and selected by default
FILE_UPLOAD_TAB = "File upload"


@st.dialog("Upload new pool of designs", width="large")
def create_new_pool():
    """Create a pool from uploaded files, or from any source a plugin contributes.

    A plugin adds a source by declaring an ``ovo.design_upload`` extension point, see
    :class:`~ovo.core.plugins.DesignUploadOption`. The sources are shown as tabs after the built-in
    "File upload" one, and no tabs are shown when no plugin contributes any.
    """
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

    # A plugin adds a source by declaring this extension point in its plugin dict:
    #
    #     plugin = dict(
    #         extension_points={
    #             "ovo.design_upload": [
    #                 dict(title="Chaperone run", path="my_plugin.app.my_upload:show_my_upload"),
    #             ],
    #         },
    #     )
    options = get_extension_points("ovo.design_upload", DesignUploadOption)
    if not options:
        show_file_upload(project_id, round_id, new_round_name)
        return

    options_by_title = {option.title: option for option in options}
    tab_name = simple_tabs([FILE_UPLOAD_TAB] + list(options_by_title), key="design_upload_tab")
    if tab_name == FILE_UPLOAD_TAB:
        show_file_upload(project_id, round_id, new_round_name)
        return

    option = options_by_title[tab_name]
    show_func = load_variable(option.path)
    assert callable(show_func), f"Design upload '{option.title}' should be a function: {option.path}"
    show_func(project_id=project_id, round_id=round_id, new_round_name=new_round_name)


def show_file_upload(project_id: str, round_id: str, new_round_name: str | None):
    """Show the built-in source: structure files, or a table of sequences."""
    content = st.empty()
    with content.container():
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
                st.dataframe(df.head(5), hide_index=True)

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
            st.error("A pool with this name already exists in this round. Please choose a different name.")

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
        if not (tabular_files and tabular_config) and not (structure_files and chains):
            st.error("No valid files to process")
            return

        content.empty()

        result = create_pool_from_uploads(
            PoolUpload(
                project_id=project_id,
                pool_name=name,
                round_id=None if round_id == "__new__" else round_id,
                new_round_name=new_round_name,
                description=description,
                structure_files=structure_files if not tabular_config else None,
                chains=chains if not tabular_config else None,
                dataframe=tabular_config["df"] if tabular_config else None,
                id_column=tabular_config["id_column"] if tabular_config else None,
                column_chains=tabular_config["column_chains"] if tabular_config else None,
            ),
            callback=st.text,
        )

        if result.conversion_warnings:
            st.warning("Some CIF files were converted to PDB format.")
            for warning in result.conversion_warnings:
                st.warning(warning)

        if result.descriptor_job_error:
            st.warning(f"Error submitting descriptor workflow: {result.descriptor_job_error}")
            time.sleep(1)

        # Activate the selected round and pool
        st.query_params[ROUND_IDS_QUERY_PARAM] = result.pool.round_id
        st.query_params["pool_ids"] = result.pool.id

        st.session_state.files = None
        st.text("✅ Done")

        st.rerun()


def pool_actions_menu(pool_ids: list[str], project_id: str, round_id: str | None = None, **button_kwargs):
    """Render an "Actions" menu with pool management actions.

    `pool_ids` is a list of selected pool IDs to operate on. If not selected, only actions related to the round are shown.
    Downloading the bulk submission config is the only action available on a read-only server.

    If ``round_id`` is provided (i.e. a single round is active), a "Rename round" action is included.
    Extra keyword arguments are forwarded to the ``st.menu_button``.
    """
    # Don't offer archiving when the active round is already the Archived round
    is_archived_round = round_id is not None and get_cached_round(round_id).name == ARCHIVED_ROUND_NAME
    # A round can only be deleted when it is empty (has no pools)
    round_is_empty = round_id is not None and get_cached_pool_count(round_id=round_id) == 0

    noun = "pool" if len(pool_ids) == 1 else "pools"
    bulk_config_action = ":material/download: Download bulk submission config"
    edit_action = f":material/edit: Edit {noun}"
    archive_action = f":material/drive_file_move: Archive {noun}"
    rename_round_action = ":material/edit_note: Rename round"
    delete_round_action = ":material/delete: Delete round"

    options = []
    # These actions modify the project, so they are left out on a read-only server
    if not config.props.read_only:
        if pool_ids:
            options.append(edit_action)
            if not is_archived_round:
                options.append(archive_action)
        if round_id is not None:
            options.append(rename_round_action)
            if round_is_empty:
                options.append(delete_round_action)
    if pool_ids:
        options.append(bulk_config_action)

    action = st.menu_button(
        "Actions",
        options=options or [None],
        disabled=not options,
        key=f"pool_actions_{'_'.join(pool_ids)}_{round_id}",
        **button_kwargs,
    )

    if action == edit_action:
        edit_pools_dialog(pool_ids, project_id)
    elif action == archive_action:
        archive_pools_dialog(pool_ids, project_id)
    elif action == rename_round_action:
        rename_round_dialog(round_id)
    elif action == delete_round_action:
        delete_round_dialog(round_id)
    elif action == bulk_config_action:
        download_bulk_config_dialog(pool_ids)


@st.dialog("Download bulk submission config")
def download_bulk_config_dialog(pool_ids: list[str]):
    noun = "pool" if len(pool_ids) == 1 else "pools"
    st.write(
        f"Download the workflows of the selected {noun} as a bulk submission config, "
        "including their input files. Upload it on the Bulk submission page to resubmit them, "
        "optionally after editing the parameters or adding a grid of values."
    )
    download_bulk_config_button(pool_ids, key=f"download_bulk_config_dialog_{'_'.join(pool_ids)}")


@st.dialog("Edit pools", width="large")
def edit_pools_dialog(pool_ids: list[str], project_id: str):
    pools = db.select(Pool, id__in=pool_ids, order_by="-created_date_utc")
    if not pools:
        st.error("No pools selected.")
        return

    rounds_by_id = get_or_create_project_rounds(project_id=project_id)
    round_name_by_id = {round_id: r.name for round_id, r in rounds_by_id.items()}
    round_id_by_name = {name: round_id for round_id, name in round_name_by_id.items()}

    st.caption("Double-click the table cell to start editing.")

    pools_df = pd.DataFrame(
        [
            {
                "ID": pool.id,
                "Name": pool.name,
                "Description": pool.description or "",
                "Round": round_name_by_id.get(pool.round_id),
            }
            for pool in pools
        ]
    )

    edited = st.data_editor(
        pools_df,
        key=f"edit_pools_{'_'.join(pool_ids)}",
        hide_index=True,
        width="stretch",
        column_config={
            "ID": st.column_config.TextColumn("ID", disabled=True),
            "Name": st.column_config.TextColumn("Name", required=True),
            "Description": st.column_config.TextColumn("Description"),
            "Round": st.column_config.SelectboxColumn("Round", options=list(round_id_by_name.keys()), required=True),
        },
    )

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            # Close the dialog without saving
            st.rerun(scope="app")
        save = st.button("Save changes", type="primary")

    if save:
        pools_by_id = {pool.id: pool for pool in pools}
        edited_ids = set(pools_by_id)
        updated_pools = []
        seen_name_round = set()
        for _, row in edited.iterrows():
            pool = pools_by_id[row["ID"]]
            new_round_id = round_id_by_name.get(row["Round"])

            name = (row["Name"] or "").strip()
            if not name:
                st.error("Pool name cannot be empty.")
                return

            # Guard against two edited pools ending up with the same name in the same round
            if (name, new_round_id) in seen_name_round:
                st.error(f"Multiple pools named '{name}' in round '{row['Round']}'. Names must be unique.")
                return
            seen_name_round.add((name, new_round_id))

            # Check name uniqueness against other pools in the target round (excluding those being edited)
            other_conflicts = [p for p in db.select(Pool, round_id=new_round_id, name=name) if p.id not in edited_ids]
            if other_conflicts:
                st.error(f"A pool named '{name}' already exists in round '{row['Round']}'.")
                return

            pool.name = name
            pool.description = (row["Description"] or "").strip()
            pool.round_id = new_round_id
            updated_pools.append(pool)

        db.save_all(updated_pools)
        st.rerun()


@st.dialog("Archive pools", width="medium")
def archive_pools_dialog(pool_ids: list[str], project_id: str):
    pools = db.select(Pool, id__in=pool_ids, order_by="-created_date_utc")
    if not pools:
        st.error("No pools selected.")
        return

    accepted_by_pool = db.count_distinct(Design, group_by="pool_id", pool_id__in=pool_ids, accepted=True)
    total_by_pool = db.count_distinct(Design, group_by="pool_id", pool_id__in=pool_ids)

    noun = "pool" if len(pools) == 1 else "pools"
    st.write(f"Move the following {len(pools)} {noun} to the **Archived** round?")
    bullets = []
    for pool in pools:
        accepted = accepted_by_pool.get(pool.id, 0)
        total = total_by_pool.get(pool.id, 0)
        bullets.append(f"- **{pool.name.strip()}**: {accepted:,} accepted and {total:,} total designs")
    st.write("\n".join(bullets))

    st.caption(
        """
        :material/info: No data will be deleted. This action can be reverted by moving the pool to another round using Actions → Edit pools.

        :material/info: Designs from archived pools will remain in any Rankings or Clustering results created earlier.
        """
    )
    message = st.text_area(
        "Message to add to description (Optional)",
        placeholder="Explain why the pool is being archived",
    )

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            # Close the dialog without archiving
            st.rerun(scope="app")
        archive = st.button("Archive", type="primary")

    if archive:
        archived_round = get_or_create_archived_round(project_id)

        # Check for pools already having the same name in the archived round
        existing_names = set(db.select_values(Pool, "name", round_id=archived_round.id))
        conflicts = [pool.name for pool in pools if pool.round_id != archived_round.id and pool.name in existing_names]
        if conflicts:
            st.error(
                f"Cannot archive, a pool with the same name already exists in the Archived round: "
                f"{', '.join(conflicts)}"
            )
            return

        username = get_username()
        message = f"Archived by {username}. " + (message or "").strip()
        for pool in pools:
            pool.round_id = archived_round.id
            pool.description = f"{pool.description}\n\n{message}" if pool.description else message
        db.save_all(pools)
        st.rerun()


@st.dialog("Rename round")
def rename_round_dialog(round_id: str):
    round = db.get(Round, id=round_id)
    if not round:
        st.error("Round not found.")
        return

    st.write(f"Rename round **{round.name}**")

    name = st.text_input("Rename to", value=round.name, placeholder="Enter new round name")

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            # Close the dialog without renaming
            st.rerun(scope="app")
        save = st.button("Save", type="primary")

    if save:
        name = (name or "").strip()
        if not name:
            st.error("Round name cannot be empty.")
            return
        if name != round.name and db.count(Round, project_id=round.project_id, name=name):
            st.error(f"A round named '{name}' already exists in this project. Please choose a different name.")
            st.error(
                "If you are trying to move the pools to an existing round, please use the 'Edit pools' action instead."
            )
            return

        round.name = name
        db.save(round)
        st.rerun()


@st.dialog("Delete round")
def delete_round_dialog(round_id: str):
    rounds = db.select(Round, id=round_id, limit=1)
    if not rounds:
        st.error("Round not found.")
        return
    round = rounds[0]

    st.write(f"Delete round **{round.name}**?")

    with st.container(horizontal=True, horizontal_alignment="distribute"):
        if st.button("Cancel"):
            # Close the dialog without deleting
            st.rerun(scope="app")
        delete = st.button("Delete", type="primary")

    if delete:
        # Re-verify the round is empty right before removing it, to avoid deleting pools
        num_pools = db.count(Pool, round_id=round_id)
        if num_pools:
            st.error(f"Cannot delete round '{round.name}', it contains {num_pools} pool(s).")
            return

        db.remove(Round, id=round_id)

        # Clear the deleted round from the active selection so we don't land on a missing round
        if ROUND_IDS_QUERY_PARAM in st.query_params:
            remaining = [r for r in st.query_params[ROUND_IDS_QUERY_PARAM].split(",") if r != round_id]
            if remaining:
                st.query_params[ROUND_IDS_QUERY_PARAM] = ",".join(remaining)
            else:
                del st.query_params[ROUND_IDS_QUERY_PARAM]

        st.rerun()
