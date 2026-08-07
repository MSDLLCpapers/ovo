import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px

from ovo.app.components.acceptance_thresholds_components import TOTAL_POOL_ID
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY

# Scale options of the acceptance rate axis
SCALE_LOG = "Log 0-100%"
SCALE_LINEAR = "Linear 0-100%"
SCALE_NORMALIZED = "Normalized 0-1"
SCALE_OPTIONS = [SCALE_LOG, SCALE_LINEAR, SCALE_NORMALIZED]

# Ticks of the logarithmic acceptance rate axis (in %)
LOG_AXIS_TICK_RATES = [0.001, 0.01, 0.1, 1, 10, 100]

# A log axis cannot show 0%, so rates of 0 are clamped to this value and plotted
# on an extra leftmost tick labelled "0%", one decade below the lowest real tick.
LOG_AXIS_ZERO_RATE = LOG_AXIS_TICK_RATES[0] / 10

# Label the clamped position as "0%", the real ticks with their value
LOG_AXIS_LABEL_EXPR = f"datum.value <= {LOG_AXIS_ZERO_RATE} ? '0%' : datum.value + '%'"


def _create_pool_acceptance_bar_chart(df: pd.DataFrame):
    """Create bar chart showing total acceptance rate per pool.

    Used when only overall acceptance rate is available (no individual criteria).

    Args:
        df: DataFrame with pool_id, pool_name, and percent_accepted columns

    Returns:
        Plotly figure
    """
    # Rename for display
    df = df.rename(columns={"percent_accepted": "% Accepted"})
    df["pool_label"] = df["pool_id"] + " (" + df["pool_name"] + ")"

    fig = px.bar(
        df,
        x="pool_label",
        y="% Accepted",
        color="pool_label",
        labels={"pool_label": "Pool"},
        hover_data={
            "pool_label": False,
            "pool_id": True,
            "pool_name": True,
            "% Accepted": ":.1f",
        },
        height=400,
    )

    fig.update_yaxes(range=[0, 100])
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)

    return fig


def _add_plotted_rate(chart: alt.Chart, scale: str) -> alt.Chart:
    """Add the "plotted_rate" field that is shown on the acceptance rate axis.

    Args:
        chart: Chart with an "acceptance_rate" and a "criterion" field
        scale: Scale of the acceptance rate axis, one of SCALE_OPTIONS

    Returns:
        Chart with the added transform
    """
    if scale == SCALE_NORMALIZED:
        # Scale each criterion independently based on its min and max value
        return chart.transform_joinaggregate(
            rate_min="min(acceptance_rate)", rate_max="max(acceptance_rate)", groupby=["criterion"]
        ).transform_calculate(
            plotted_rate="isValid(datum.acceptance_rate) ? (datum.rate_max === datum.rate_min ? 0.5 : "
            "(datum.acceptance_rate - datum.rate_min) / (datum.rate_max - datum.rate_min)) : null"
        )
    if scale == SCALE_LOG:
        # A log axis cannot show 0%, clamp it to the axis minimum so that it is still plotted
        return chart.transform_calculate(
            plotted_rate=f"isValid(datum.acceptance_rate) ? max(datum.acceptance_rate, {LOG_AXIS_ZERO_RATE}) : null"
        )
    return chart.transform_calculate(plotted_rate="datum.acceptance_rate")


def _get_rate_axis(scale: str) -> alt.X:
    """Get the acceptance rate axis encoding for the given scale option.

    Args:
        scale: One of SCALE_OPTIONS

    Returns:
        Altair X encoding of the "plotted_rate" field
    """
    if scale == SCALE_LOG:
        return alt.X(
            "plotted_rate:Q",
            title="Acceptance Rate (%)",
            scale=alt.Scale(type="log", domain=[LOG_AXIS_ZERO_RATE, 100], nice=False, clamp=True),
            axis=alt.Axis(values=[LOG_AXIS_ZERO_RATE] + LOG_AXIS_TICK_RATES, labelExpr=LOG_AXIS_LABEL_EXPR),
        )
    if scale == SCALE_LINEAR:
        return alt.X(
            "plotted_rate:Q",
            title="Acceptance Rate (%)",
            scale=alt.Scale(domain=[0, 100.05]),
        )
    return alt.X(
        "plotted_rate:Q",
        title="Normalized Scale (0-1)",
        scale=alt.Scale(domain=[-0.05, 1.05]),
    )


def _create_standard_pool_criteria_parallel_coords(
    df: pd.DataFrame, descriptor_columns: list[str], threshold_cols: list[str], scale: str = SCALE_LOG
) -> alt.Chart:
    """Create parallel coordinates plot comparing pools across acceptance criteria.

    With SCALE_LOG or SCALE_LINEAR, all criteria share the same 0-100% scale, useful for
    directly comparing absolute acceptance rates across different criteria. With
    SCALE_NORMALIZED, each criterion is independently scaled (0=min, 1=max), useful for
    comparing relative performance across criteria with different value ranges.

    Args:
        df: DataFrame with pool data and descriptor columns
        descriptor_columns: List of descriptor column names to plot
        threshold_cols: List of threshold column names for tooltips
        scale: Scale of the acceptance rate axis, one of SCALE_OPTIONS

    Returns:
        Altair chart
    """
    # Create rename mappings for readable names
    df = df.copy()
    descriptor_rename_map = {}
    threshold_rename_map = {}

    for col in descriptor_columns:
        if col == "percent_accepted":
            descriptor_rename_map[col] = "% Accepted"
        elif col in ALL_DESCRIPTORS_BY_KEY:
            descriptor_rename_map[col] = ALL_DESCRIPTORS_BY_KEY[col].name

    for col in threshold_cols:
        descriptor_key = col.replace("threshold_", "")
        if descriptor_key in ALL_DESCRIPTORS_BY_KEY:
            threshold_rename_map[col] = f"{ALL_DESCRIPTORS_BY_KEY[descriptor_key].name} Threshold"

    # Rename columns in dataframe
    df = df.rename(columns={**descriptor_rename_map, **threshold_rename_map})

    # Update column lists with new names
    descriptor_columns = [descriptor_rename_map.get(col, col) for col in descriptor_columns]
    threshold_cols = [threshold_rename_map.get(col, col) for col in threshold_cols]

    # Create legend selection
    legend_selection = alt.selection_point(fields=["pool_label"], bind="legend")

    # Create pan selection (scroll to zoom disabled so that page scrolling is not captured by the chart)
    pan = alt.selection_interval(bind="scales", encodings=["x"], zoom=False)

    altair_long_df = df.melt(
        id_vars=["pool_name", "pool_id", "pool_label", "pool_index_str"] + threshold_cols,
        value_vars=descriptor_columns,
        var_name="criterion",
        value_name="acceptance_rate",
    )

    # Base line chart with legend interaction
    lines = (
        _add_plotted_rate(alt.Chart(altair_long_df), scale)
        .mark_line()
        .encode(
            x=_get_rate_axis(scale),
            y=alt.Y("criterion:N", title="Acceptance Criterion", axis=alt.Axis(labelLimit=300)),
            color=alt.Color("pool_label:N", title="Pool"),
            detail="pool_index_str:N",
            # Connect the points in axis order, they would be sorted by acceptance rate otherwise
            order=alt.Order("criterion:N"),
            opacity=alt.when(legend_selection).then(alt.value(1)).otherwise(alt.value(0.2)),
            strokeWidth=alt.when(legend_selection).then(alt.value(2)).otherwise(alt.value(1)),
        )
        .add_params(legend_selection, pan)
    )

    # Points with tooltips (also affected by legend selection)
    points = (
        _add_plotted_rate(
            alt.Chart(altair_long_df)
            .transform_pivot(
                "criterion",
                value="acceptance_rate",
                groupby=["pool_name", "pool_id", "pool_label", "pool_index_str"] + threshold_cols,
            )
            .transform_fold(descriptor_columns, as_=["criterion", "acceptance_rate"]),
            scale,
        )
        .mark_point(size=150, filled=True)
        .encode(
            x=_get_rate_axis(scale),
            y=alt.Y("criterion:N"),
            color=alt.Color("pool_label:N"),
            opacity=alt.when(legend_selection).then(alt.value(1)).otherwise(alt.value(0.2)),
            tooltip=[
                alt.Tooltip("pool_id:N", title="Pool ID"),
                alt.Tooltip("pool_name:N", title="Pool Name"),
            ]
            + [
                # Significant digits instead of ".1f" so that rates below 0.1% are not shown as "0.0"
                alt.Tooltip(f"{col}:Q", title=col if col == "% Accepted" else f"{col} (%)", format=".3~g")
                for col in descriptor_columns
            ]
            + [alt.Tooltip(f"{col}:N", title=col) for col in threshold_cols],
        )
    )

    # Horizontal rules for each axis
    rules = (
        alt.Chart(altair_long_df)
        .mark_rule(color="#ccc", tooltip=None)
        .encode(
            y="criterion:N",
            detail="count():Q",
        )
    )

    # Combine layers
    chart = alt.layer(lines, points, rules).properties(width="container", height=400)

    return chart


@st.fragment
def parallel_coordinates_plot_component(
    acceptance_df: pd.DataFrame,
    threshold_descriptor_keys: list[str],
):
    """Display a parallel coordinates plot comparing success rates across jobs.

    Each line represents a pool/job, and each axis represents the success rate
    (% of designs passing) for a specific acceptance criterion.

    Args:
        acceptance_df: DataFrame containing acceptance data for pools
        threshold_descriptor_keys: List of descriptor keys used for thresholds
    """
    if acceptance_df.empty:
        st.warning("No pools with designs found.")
        return

    # Compare the individual pools, the combined row would just be another line
    df = acceptance_df[acceptance_df["pool_id"] != TOTAL_POOL_ID].copy()

    # Get descriptor columns (all except pool info, design counts and threshold columns)
    threshold_cols = [f"threshold_{key}" for key in threshold_descriptor_keys]
    excluded_cols = ["pool_name", "pool_id", "pool_description", "num_designs", "num_accepted"] + threshold_cols
    descriptor_columns = [col for col in df.columns if col not in excluded_cols]

    if not descriptor_columns:
        st.warning("No descriptor data available for the parallel coordinates plot.")
        return

    # Reorder to put % Accepted first
    if "percent_accepted" in descriptor_columns:
        descriptor_columns.remove("percent_accepted")
        descriptor_columns = ["percent_accepted"] + descriptor_columns

    # If only percent_accepted exists (no other criteria), show a simple bar chart
    if descriptor_columns == ["percent_accepted"]:
        if len(df) > 1:
            st.info("No individual acceptance criteria enabled. Showing overall acceptance rate only.")

            fig = _create_pool_acceptance_bar_chart(df.copy())
            st.plotly_chart(fig, width="content")

    else:
        # Scale of the acceptance rate axis (only shown for parallel coordinates plot)
        with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
            st.markdown(
                "Scale:",
                help="Log and linear scales share the same 0-100% axis for all criteria. "
                "Normalized scales each criterion independently (0=min, 1=max for that criterion).",
            )
            scale = st.radio(
                "Scale",
                options=SCALE_OPTIONS,
                horizontal=True,
                key="scale_parallel_coords",
                label_visibility="collapsed",
            )

        # Create pool label with format {ID}:{name}
        df["pool_label"] = df["pool_id"] + " (" + df["pool_name"] + ")"
        df["pool_index_str"] = df.index.astype(str)  # For detail encoding

        chart = _create_standard_pool_criteria_parallel_coords(df, descriptor_columns, threshold_cols, scale=scale)
        caption_text = (
            "Click on legend items to highlight/filter pools. Shift+Click multiple items to compare specific pools. "
            "Hover over points to see all criteria values. Drag to pan the X-axis, double-click to reset."
        )
        if scale == SCALE_NORMALIZED:
            caption_text += " Each criterion is independently scaled (0=min, 1=max)."

        st.altair_chart(chart, width="stretch")
        st.caption(caption_text)
