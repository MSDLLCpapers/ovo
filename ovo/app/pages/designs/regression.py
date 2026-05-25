import io
from typing import Sequence

import pandas as pd
import streamlit as st

from ovo import db, NumericDescriptor, storage
from ovo.app.components.attachment_components import select_project_attachments
from ovo.app.components.custom_elements import simple_tabs
from ovo.app.components.descriptor_correlation import (
    correlation_clustermap,
    correlation_explorer,
    correlation_scatterplot_interactive,
)
from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.utils.cached_db import get_cached_pools
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.database.models import Design, Pool
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table


@st.cache_data(show_spinner="Calculating correlation matrix...")
def get_correlation_matrix(df: pd.DataFrame, method: str = "spearman", **kwargs) -> pd.DataFrame:
    return df.corr(numeric_only=True, method=method, **kwargs)


@st.fragment()
def regression_fragment(pool_ids: list[str], design_ids: list[str] | None = None):
    pools = get_cached_pools(pool_ids)

    if design_ids is None:
        # design_ids not explicitly passed, use all accepted designs in the selected pools
        design_ids = sorted(db.select_values(Design, "id", pool_id__in=pool_ids, accepted=True))

        if not design_ids:
            st.write(
                "No accepted designs in the selected "
                + ("pools" if len(pool_ids) > 1 else "pool")
                + ". All generated designs can be explored in the **Jobs** page."
            )
            return

    elif not design_ids:
        # Empty list explicitly passed to design_ids
        st.write("No designs selected")
        return

    st.header(f"Regression | {len(design_ids):,} {'design' if len(design_ids) == 1 else 'designs'}")

    badges = [f":grey-badge[{pool.name}]" for pool in pools]
    st.write("Selected pools: " + " ".join(badges))

    refresh_descriptors(
        design_ids=design_ids,
    )

    files = st.file_uploader(
        "Upload numeric results (CSV or Excel, must include a 'design_id' column)",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="custom_descriptor_upload",
        width=500,
    )

    # Handle saved attachments
    attachments = select_project_attachments(st.session_state.project, extensions=(".csv", ".xlsx"))
    for attachment in attachments:
        try:
            file_bytes = storage.read_file_bytes(attachment.file_path)
            # Create a file-like object for processing
            attachment_file = io.BytesIO(file_bytes)
            attachment_file.name = attachment.original_filename
            files = files + [attachment_file]
        except Exception as e:
            st.error(f"Error loading attachment: {e}")

    if not files:
        return

    st.session_state.user_df = None
    for file in files:
        try:
            if file.name.endswith(".csv"):
                raw_df = pd.read_csv(file, header=0)
            elif file.name.endswith(".xlsx"):
                raw_df = pd.read_excel(file, header=0)
            if "design_id" not in raw_df.columns:
                # Try reading with multi-index header
                if file.name.endswith(".csv"):
                    raw_df = pd.read_csv(file, header=[0, 1])
                elif file.name.endswith(".xlsx"):
                    raw_df = pd.read_excel(file, header=[0, 1])
                id_columns = [c for c in raw_df.columns if c[1] == "design_id"]
                if id_columns:
                    user_df = raw_df.set_index(id_columns[0])
                    # Reset to one header level
                    columns = [f"{level2} ({level1})" for (level1, level2) in user_df.columns]
                    user_df.columns = columns
                    user_df.index.name = "design_id"
                else:
                    st.error(
                        f"File {file.name} does not contain a 'design_id' column. Please check your file and try again."
                    )
                    continue
            else:
                user_df = raw_df.set_index("design_id")

            # Keep only numeric columns
            user_df = user_df.select_dtypes(include="number")

            if user_df.empty:
                st.error(
                    f"File {file.name} does not contain any numeric columns. Please check your file and try again."
                )
                continue
            st.success(
                f"Selected {file.name} with {user_df.shape[1]} numeric endpoints for {user_df.shape[0]} designs."
            )
            if st.session_state.user_df is None:
                st.session_state.user_df = user_df
            else:
                # Outer join to keep all designs and all descriptors from each file
                st.session_state.user_df = pd.merge(
                    st.session_state.user_df, user_df, left_index=True, right_index=True, how="outer"
                )
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")

    if st.session_state.user_df is None:
        return

    with st.spinner("Loading descriptor data..."):
        numeric_descriptors = [
            k for k in ALL_DESCRIPTORS_BY_KEY if isinstance(ALL_DESCRIPTORS_BY_KEY[k], NumericDescriptor)
        ]
        descriptor_df = get_wide_descriptor_table(
            pool_ids=pool_ids,
            design_ids=design_ids,
            descriptor_keys=numeric_descriptors,
            human_readable=False,
            nested=False,
        )
        # Remove sequence column and any other non-numeric columns
        descriptor_df = descriptor_df.select_dtypes(include="number")

    # Merge user_df with df if user_df exists
    user_df = st.session_state.user_df
    df_combined = pd.merge(
        user_df, descriptor_df, left_index=True, right_index=True, how="inner", suffixes=("user_", "")
    )

    # Stop if no overlapping design_ids between df and user_df after merge
    if df_combined.empty:
        st.error(
            "No overlapping design IDs between selected pools and the uploaded table. Please make sure you uploaded the correct file and selected the correct project and round above."
        )
        return

    if len(df_combined) < len(user_df):
        st.warning(
            f"Only {len(df_combined)} out of {len(user_df)} designs from the uploaded file have matching design_ids with the selected pools. Correlation analysis will be performed on these {len(df_combined)} designs."
        )
    if len(df_combined) < len(descriptor_df):
        st.warning(
            f"Only {len(df_combined)} out of {len(descriptor_df)} designs in the selected pools have matching design_ids with the uploaded file. Correlation analysis will be performed on these {len(df_combined)} designs."
        )

    correlation_methods = {
        "Spearman rank correlation ρ": "spearman",
        "Pearson correlation R": "pearson",
    }
    with st.container(horizontal=True, vertical_alignment="center"):
        st.write("Correlation method:")
        correlation_label = st.segmented_control(
            "Correlation method",
            options=list(correlation_methods.keys()),
            key="corr_method",
            label_visibility="collapsed",
            default="Spearman rank correlation ρ",
        )
        if not correlation_label:
            st.write("Please select a correlation method to view the correlation analysis.")
            st.stop()

    corr = get_correlation_matrix(df_combined, method=correlation_methods[correlation_label])
    # Index = user endpoints, Columns = descriptors
    corr = corr.loc[user_df.columns, descriptor_df.columns]

    regression_analysis_fragment(pools, df_combined, corr, correlation_label)


@st.fragment()
def regression_analysis_fragment(
    pools: list[Pool], df_combined: pd.DataFrame, corr: pd.DataFrame, correlation_label: str
):
    """Fragment with tabs and results.

    :param pools: list of Pool objects corresponding to the selected pools for this regression analysis
    :param df_combined: DataFrame with user-uploaded numeric endpoints joined to descriptor values.
    :param corr: Correlation matrix DataFrame with user endpoints as rows and descriptors as columns.
    :param correlation_label: Label for the correlation method used, e.g. "Spearman rank correlation ρ"
    """

    tab_name = simple_tabs(
        ["Clustermap", "Correlation Explorer", "Scatterplot", "Modeling", "Data"],
        "regression_tab",
    )

    if tab_name == "Clustermap":
        correlation_clustermap(corr, correlation_label=correlation_label)
    elif tab_name == "Correlation Explorer":
        correlation_explorer(corr, df_combined, correlation_label=correlation_label)
    elif tab_name == "Scatterplot":
        correlation_scatterplot_interactive(
            df_combined,
            corr,
            correlation_label=correlation_label,
        )
    elif tab_name == "Modeling":
        st.info("Modeling functionality coming soon!", icon=":material/info:")
    elif tab_name == "Data":
        if len(pools) < 10:
            filename_prefix = "ovo_" + "_".join(p.id for p in pools)
        else:
            filename_prefix = f"ovo_{len(pools)}_pools"
        with st.container(horizontal=True):
            st.download_button(
                "Download combined data as CSV",
                data=lambda: df_combined.to_csv(),
                file_name=f"{filename_prefix}_combined_data.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download correlation matrix as CSV",
                data=lambda: corr.to_csv(),
                file_name=f"{filename_prefix}_correlation_matrix.csv",
                mime="text/csv",
            )

        st.dataframe(df_combined)
