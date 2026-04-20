import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, leaves_list

from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY


@st.fragment()
def correlation_clustermap(correlation_df: pd.DataFrame, correlation_label: str):
    """
    Displays a clustermap of the correlation matrix with options to select which descriptors to include.

    Args:
        correlation_df (pd.DataFrame): A DataFrame containing the correlation matrix of descriptors. The columns should be ovo descriptor keys, index should be user uploaded endpoint columns, and the values should be correlation coefficients.
        correlation_label: The name of the correlation metric to display in the plot legend
    """

    # Drop rows and columns that are all NaN, and warn about any descriptors that are dropped
    if correlation_df.isna().any().any():
        dropped_rows = correlation_df.index[correlation_df.isna().all(axis=1)].tolist()
        if dropped_rows:
            st.warning(
                f"The correlation matrix contains only NaN values for the following endpoints, "
                f"they will be dropped from the clustermap: {', '.join(dropped_rows)}"
            )

    correlation_df = correlation_df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Initialize with only top 15 most correlated descriptors
    top_n = 15
    top_n = min(top_n, correlation_df.shape[1])  # In case there are less than top_n descriptors
    # rank all correlations with respect to each endpoint (row)
    # row in this context = correlations of all descriptors with a single endpoint
    ranks_per_endpoint = correlation_df.apply(lambda row: row.abs().rank(ascending=False), axis=1)
    # take descriptors in increasing order of their best rank across all endpoints
    top_descriptors = ranks_per_endpoint.min(axis=0).sort_values().head(top_n).index.tolist()

    # Allow user to select descriptors manually
    with st.popover("Select descriptors to include"):
        with st.container(horizontal=True):
            if st.button("Select All"):
                for descriptor_key in correlation_df.columns:
                    st.session_state[f"clustermap_{descriptor_key}"] = True
            if st.button("Deselect All"):
                for descriptor_key in correlation_df.columns:
                    st.session_state[f"clustermap_{descriptor_key}"] = False
            if st.button(f"Reset to Top {top_n}"):
                for descriptor_key in correlation_df.columns:
                    st.session_state[f"clustermap_{descriptor_key}"] = descriptor_key in top_descriptors

        columns = st.columns(3)
        descriptor_options = correlation_df.columns.tolist()
        use_cols = []
        for i, descriptor_key in enumerate(descriptor_options):
            with columns[i % 3]:
                descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key].name
                label = f"**{descriptor}**" if descriptor_key in top_descriptors else descriptor
                use = st.checkbox(label, value=descriptor_key in top_descriptors, key=f"clustermap_{descriptor_key}")
                if use:
                    use_cols.append(descriptor_key)

    if not use_cols:
        st.warning("No descriptors selected. Please select at least one descriptor.")
        return
    elif len(use_cols) == len(correlation_df.columns):
        selection_label = f"all {len(use_cols)} available descriptors"
    elif set(use_cols) == set(top_descriptors):
        selection_label = f"the top {top_n} most positively or negatively correlated descriptors"
    else:
        selection_label = f"{len(use_cols)} out of {len(correlation_df.columns)} available descriptors"

    st.write(f"Showing {correlation_label} of {selection_label} (columns) with the uploaded endpoints (rows)")

    correlation_df = correlation_df[use_cols]
    # Cluster rows and columns using hierarchical clustering
    if correlation_df.shape[0] > 1 and correlation_df.shape[1] > 1:
        correlation_df = cluster_correlation_matrix(correlation_df)
    else:
        correlation_df = correlation_df

    # Use human readable names in the clustermap
    renamed_columns = {}
    for descriptor_key in correlation_df.columns:
        nice_name = ALL_DESCRIPTORS_BY_KEY[descriptor_key].name
        renamed_columns[descriptor_key] = nice_name
    correlation_df = correlation_df.rename(columns=renamed_columns)

    fig = px.imshow(
        correlation_df,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        labels=dict(color=correlation_label, x="Descriptor", y="Uploaded endpoint"),
        height=500 + min(200, 10 * len(correlation_df)),
    )
    fig.update_layout(
        xaxis_side="top",
    )
    fig.update_xaxes(
        tickangle=45,
    )

    st.plotly_chart(fig, width="stretch")


@st.cache_data()
def cluster_correlation_matrix(correlation_df: pd.DataFrame) -> pd.DataFrame:
    """Clusters the correlation matrix using hierarchical clustering and returns a reordered DataFrame."""
    # Compute linkage for rows and columns
    corr_clean = correlation_df.replace([np.inf, -np.inf], np.nan).fillna(0)
    row_linkage = linkage(corr_clean.values, method="average")
    col_linkage = linkage(corr_clean.values.T, method="average")

    # Get the order of rows and columns
    row_order = leaves_list(row_linkage)
    col_order = leaves_list(col_linkage)
    correlation_df = correlation_df.iloc[row_order, col_order]
    return correlation_df


@st.fragment()
def correlation_explorer(
    correlation_df: pd.DataFrame, df_combined: pd.DataFrame, correlation_label: str, top_n: int = 10
):
    """
    Explores the correlation of a selected descriptor with other descriptors.

    Args:
        correlation_df (pd.DataFrame): A DataFrame containing the correlation matrix of descriptors. The columns should be ovo descriptor keys, index should be user uploaded descriptor keys, and the values should be correlation coefficients.
        df_combined: A DataFrame containing the combined data of uploaded and computed descriptors, indexed by design_id.
        correlation_label: The name of the correlation metric to display in the plot legend
        top_n (int): The number of top positively and negatively correlated descriptors to display.
    """

    descriptor_names = correlation_df.index.tolist()
    endpoint = st.selectbox(
        "Select uploaded endpoint",
        descriptor_names,
        bind="query-params",
        key="corr_endpoint",
    )

    st.markdown(f"### Selected endpoint: {endpoint}")

    descriptor_df = correlation_df.loc[endpoint].dropna().sort_values(ascending=False)

    descriptor_df.index.name = "descriptor_key"
    descriptor_df = descriptor_df.reset_index()

    descriptor_df[["Descriptor", "Tool"]] = descriptor_df["descriptor_key"].apply(
        lambda key: pd.Series(
            {
                "Descriptor": ALL_DESCRIPTORS_BY_KEY[key].name,
                "Tool": ALL_DESCRIPTORS_BY_KEY[key].tool,
            }
        )
    )

    descriptor_df["corr_absolute"] = descriptor_df[endpoint].abs()

    top_positive = descriptor_df.head(top_n)
    top_positive = top_positive[top_positive[endpoint] > 0].sort_values(by=endpoint, ascending=False)
    top_negative = descriptor_df.tail(top_n)
    top_negative = top_negative[top_negative[endpoint] < 0].sort_values(by=endpoint, ascending=True)
    top_combined = pd.concat([top_positive, top_negative]).sort_values(by="corr_absolute", ascending=False)
    top_combined = top_combined[["Descriptor", "Tool", endpoint, "corr_absolute"]]

    styler = top_combined.style
    styler = styler.background_gradient(
        subset=[endpoint],
        cmap="RdBu",
        vmin=-1,
        vmax=1,
    )

    left, right = st.columns(2)
    with left:
        st.markdown(
            f"##### 📈 Top {len(top_positive)} positively and {len(top_negative)} negatively correlated descriptors"
        )
        event = st.dataframe(
            styler,
            width="stretch",
            height=750,
            hide_index=True,
            selection_mode=["single-row"],
            on_select="rerun",
            column_config={
                "Descriptor": st.column_config.TextColumn("Descriptor", width="medium"),
                "Tool": st.column_config.TextColumn("Tool", width=80),
                endpoint: st.column_config.NumberColumn(
                    "Correlation",
                    help=f"{correlation_label} between the descriptor and the selected descriptor",
                    format="%0.2f",
                    width=50,
                ),
                "corr_absolute": st.column_config.ProgressColumn(
                    "Correlation Absolute Value",
                    help="The absolute value of the correlation",
                    min_value=0,
                    max_value=1,
                    color="grey",
                    format="%0.2f",
                    width=50,
                ),
            },
        )
        if len(event.selection["rows"]) > 0:
            selected_row = top_combined.iloc[event.selection["rows"][0]]
            x_descriptor_key = descriptor_df[descriptor_df["Descriptor"] == selected_row["Descriptor"]][
                "descriptor_key"
            ].values[0]
        else:
            x_descriptor_key = None

    with right:
        if x_descriptor_key is None:
            st.markdown("##### &nbsp;")
            st.info("Select a descriptor from the table on the left to see a scatter plot of its correlation")
            return
        descriptor = ALL_DESCRIPTORS_BY_KEY[x_descriptor_key]
        st.markdown(f"##### {descriptor.name} vs *{endpoint}*")
        if descriptor.description:
            st.caption(f"**{descriptor.name}:** {descriptor.description}")
        df_combined = df_combined.reset_index()

        correlation_scatterplot(
            combined_df=df_combined,
            corr_df=correlation_df,
            correlation_label=correlation_label,
            y_descriptor=endpoint,
            x_descriptor=x_descriptor_key,
            key_suffix="explorer",
        )


@st.fragment()
def correlation_scatterplot_interactive(combined_df: pd.DataFrame, corr_df: pd.DataFrame, correlation_label: str):
    with st.container(horizontal=True):
        x_descriptor = st.selectbox(
            "Select X (descriptor)",
            corr_df.columns,
            index=0,
            key="x_descriptor",
            format_func=lambda key: ALL_DESCRIPTORS_BY_KEY[key].name,
        )
        y_descriptor = st.selectbox(
            "Select Y (uploaded endpoint)",
            corr_df.index,
            index=0,
            key="y_descriptor",
        )
    correlation_scatterplot(
        combined_df=combined_df,
        corr_df=corr_df,
        correlation_label=correlation_label,
        x_descriptor=x_descriptor,
        y_descriptor=y_descriptor,
        key_suffix="custom",
    )


@st.fragment()
def correlation_scatterplot(
    combined_df: pd.DataFrame,
    corr_df: pd.DataFrame,
    correlation_label: str,
    x_descriptor: str,
    y_descriptor: str,
    key_suffix: str = "",
):
    """
    Displays scatterplots for the correlation between selected descriptors.

    Args:
        combined_df (pd.DataFrame): A DataFrame containing the combined data of uploaded and computed descriptors.
        corr_df (pd.DataFrame): A DataFrame containing the correlation matrix of descriptors.
        correlation_label: The name of the correlation metric to display in the plot legend
        x_descriptor (str): The ovo descriptor key to use for the X axis.
        y_descriptor (str): The user descriptor key to use for the Y axis.
    """

    metrics_container = st.container(horizontal=True, horizontal_alignment="left", gap="medium")
    corr = corr_df.loc[y_descriptor, x_descriptor]
    with metrics_container:
        st.metric(
            correlation_label,
            f"{corr:.2f}",
            help=f"{correlation_label} between the two columns",
            width="content",
        )
    combined_df = combined_df.reset_index()

    fig = px.scatter(
        combined_df,
        x=x_descriptor,
        y=y_descriptor,
        custom_data=["design_id"],
        labels={
            x_descriptor: f"{ALL_DESCRIPTORS_BY_KEY[x_descriptor].name}",
            y_descriptor: f"{y_descriptor}",
        },
        hover_data=["design_id"],
    )

    # Overlay a regression line using least-squares fit on non-NaN data
    x = combined_df[x_descriptor]
    y = combined_df[y_descriptor]

    # Drop rows with NaNs in either x or y
    mask = x.notna() & y.notna()
    x_valid = x[mask]
    y_valid = y[mask]

    if len(x_valid) < 2:
        st.info("Not enough data points to compute a regression line.")
    elif x_valid.nunique() <= 1:
        # Constant X: cannot fit a meaningful regression line
        st.info("X values are constant; skipping regression line.")
    else:
        # Least-squares linear fit: y = slope * x + intercept
        slope, intercept = np.polyfit(x_valid, y_valid, 1)

        y_pred = slope * x_valid + intercept
        r2 = r2_score_pandas(y_valid, y_pred)
        with metrics_container:
            st.metric(
                "Regression R² score",
                f"{r2:.2f}",
                help="How much variance in Y is explained by the linear relationship with X",
                width="content",
            )

        # Generate line points across the observed X range
        x_line = np.array([x_valid.min(), x_valid.max()])
        y_line = slope * x_line + intercept

        fig.add_traces(
            px.line(x=x_line, y=y_line).data,
        )
    st.plotly_chart(fig, key=f"correlation_explorer_scatter_{key_suffix}", height=520, width=520)


@st.cache_data()
def r2_score_pandas(y_true: pd.Series, y_pred: pd.Series) -> float:
    y_true = y_true.astype(float)
    y_pred = y_pred.astype(float)
    ss_res = ((y_true - y_pred) ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    return 1 - ss_res / ss_tot
