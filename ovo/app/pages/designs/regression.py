import streamlit as st

import pandas as pd

from ovo import db, NumericDescriptor
from ovo.core.database.models import Design
from ovo.core.logic.descriptor_logic import get_wide_descriptor_table
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY

from ovo.app.components.descriptor_job_components import refresh_descriptors
from ovo.app.utils.cached_db import get_cached_pools
from ovo.app.components.descriptor_correlation import (
    correlation_clustermap,
    correlation_explorer,
    correlation_scatterplot_interactive,
)


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
                + ". Please mark some designs as accepted in the **Jobs** page."
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

    numeric_descriptors = [
        k for k in ALL_DESCRIPTORS_BY_KEY if isinstance(ALL_DESCRIPTORS_BY_KEY[k], NumericDescriptor)
    ]
    df = get_wide_descriptor_table(
        pool_ids=pool_ids,
        design_ids=design_ids,
        descriptor_keys=numeric_descriptors,
        human_readable=False,
        nested=False,
    )
    # Remove sequence column and any other non-numeric columns
    df = df.select_dtypes(include="number")

    file = st.file_uploader(
        "Upload custom descriptors (CSV or Excel, must include a 'design_id' column)",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
        key="custom_descriptor_upload",
        width=400,
    )
    if file:
        try:
            if file.name.endswith(".csv"):
                raw_df = pd.read_csv(file, header=0)
            elif file.name.endswith(".xlsx"):
                raw_df = pd.read_excel(file, header=0)
            if "design_id" not in raw_df.columns:
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
                    st.session_state.user_df = None
                    return
            else:
                user_df = raw_df.set_index("design_id")

            # Keep only numeric columns
            user_df = user_df.select_dtypes(include="number")

            if user_df.empty:
                st.error(
                    f"File {file.name} does not contain any numeric columns. Please check your file and try again."
                )
                st.session_state.user_df = None
                return
            st.success(
                f"Successfully uploaded {file.name} with {user_df.shape[1]} numeric descriptors for {user_df.shape[0]} designs."
            )
            st.session_state.user_df = user_df
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")
            st.session_state.user_df = None

    # Merge user_df with df if user_df exists
    if st.session_state.user_df is not None:
        user_df = st.session_state.user_df
        df_combined = pd.merge(df, user_df, left_index=True, right_index=True, how="inner", suffixes=("", "_user"))

        # Stop if no overlapping design_ids between df and user_df after merge
        if df_combined.empty:
            st.error(
                "No overlapping design IDs between selected pools and the uploaded table. Please make sure you uploaded the correct file and selected the correct project and round above."
            )
            return

        if len(df_combined) < len(user_df):
            st.warning(
                f"Only {len(df_combined)} out of {len(user_df)} designs from the uploaded file have matching design_ids with the existing descriptors. Correlation analysis will be performed on these {len(df_combined)} designs."
            )
        if len(df_combined) < len(df):
            st.warning(
                f"Only {len(df_combined)} out of {len(df)} designs from the existing descriptors have matching design_ids with the uploaded file. Correlation analysis will be performed on these {len(df_combined)} designs."
            )

        corr = get_correlation_matrix(df_combined, method="spearman")

        # Use user descriptors as rows and ovo descriptors as columns for the clustermap
        corr_for_clustermap = corr.loc[list(user_df.columns), list(df.columns)]

        clustermap_tab, explorer_tab, scatterplots_tab, modeling_tab = st.tabs(
            ["Clustermap", "Correlation Explorer", "Scatterplot", "Modeling"]
        )
        with clustermap_tab:
            correlation_clustermap(corr_for_clustermap)
        with explorer_tab:
            correlation_explorer(corr_for_clustermap, df_combined)
        with scatterplots_tab:
            correlation_scatterplot_interactive(
                df_combined, corr, x_descriptors=list(df.columns), y_descriptors=list(user_df.columns)
            )
        with modeling_tab:
            st.info("Modeling functionality coming soon!", icon=":material/info:")
    else:
        st.info("Upload custom descriptor files to see correlation analysis here.", icon=":material/info:")
