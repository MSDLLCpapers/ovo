from collections import defaultdict
from typing import Collection

import pandas as pd
import streamlit as st
from sqlalchemy.orm.attributes import flag_modified

from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.utils.cached_db import get_cached_descriptor_values, Descriptor

from plotly import express as px

from ovo import db, Threshold, NumericDescriptor
from ovo.core.database import Pool, DesignJob, Design
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.logic.design_logic import update_accepted_design_ids
from ovo.core.logic.filtering_logic import filter_designs_by_thresholds

# Pool ID of the extra acceptance DataFrame row that combines all pools
TOTAL_POOL_ID = "Total"

# Shown as the threshold of the combined row when pools use different thresholds
MIXED_THRESHOLD = "Various"

# Options of the workflow parameter segmented control
NO_PARAMS = "Thresholds only"
ALL_PARAMS = "All parameters"
DISTINCT_PARAMS = "Distinct parameters"

# Column groups of the design jobs table that are already shown in the acceptance table
DUPLICATE_PARAM_GROUPS = ["Pool", "Job", "Designs", "Thresholds"]


def thresholds_and_histograms_component(
    selected_thresholds: dict[str, Threshold],
    saved_thresholds: dict[str, Threshold],
    all_design_ids: list[str],
    acceptance_df: pd.DataFrame,
    inconsistent_keys: set[str],
    max_items_row=3,
) -> dict[str, Threshold]:
    """Adjust thresholds using sliders and show histograms for each descriptor, return new thresholds."""
    new_thresholds = {}
    descriptor_keys = list(selected_thresholds.keys())

    st.subheader("Acceptance thresholds")

    if not descriptor_keys:
        st.write("No dynamic acceptance thresholds are configured for this workflow.")

    columns = wrapped_columns(len(descriptor_keys), wrap=max_items_row, divider=True, gap="large")
    for descriptor_key, column in zip(descriptor_keys, columns):
        with column:
            descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key]

            plot_container = st.container()

            descriptor_values = get_cached_descriptor_values(descriptor.key, design_ids=all_design_ids)

            new_thresholds[descriptor.key] = single_threshold_input_component(
                threshold=selected_thresholds[descriptor.key],
                descriptor=descriptor,
                descriptor_values=descriptor_values,
            )

            with plot_container:
                descriptor_histogram_component(
                    descriptor_values=descriptor_values,
                    descriptor=descriptor,
                    threshold=new_thresholds[descriptor.key],
                )

            if descriptor.description:
                st.caption(descriptor.description)

            if new_thresholds[descriptor.key].enabled and (num_missing := descriptor_values.isna().sum()):
                st.warning(
                    f"{num_missing}/{len(all_design_ids)} designs are missing values for this descriptor. "
                    f"These designs will be marked as NOT accepted."
                )
            if descriptor_key in inconsistent_keys:
                # Group pools by their threshold values (excluding the combined row)
                threshold_col = f"threshold_{descriptor_key}"
                pool_rows = acceptance_df[acceptance_df["pool_id"] != TOTAL_POOL_ID]
                pools_by_threshold = pool_rows.groupby(threshold_col, dropna=False)["pool_id"].apply(list).to_dict()
                threshold_list = []
                for threshold_val, pool_ids in pools_by_threshold.items():
                    pool_str = ", ".join(pool_ids) if len(pool_ids) <= 2 else f"{pool_ids[0]} +{len(pool_ids) - 1} more"
                    threshold_list.append(f"**{threshold_val}** ({pool_str})")

                st.warning(f"⚠️ Inconsistent thresholds: {', '.join(threshold_list)}")

            if saved_thresholds[descriptor.key] != new_thresholds[descriptor.key]:
                st.caption(
                    ':red[Threshold has been changed], see the new statistics above and save using the "Confirm thresholds" button.'
                )

    return new_thresholds


def thresholds_input_component(
    selected_thresholds: dict[str, Threshold],
    max_items_row: int = 3,
    skipped_threshold_keys: Collection[str] | None = None,
) -> dict[str, Threshold]:
    """Adjust thresholds using sliders, return new thresholds."""
    if not selected_thresholds:
        # TODO when we enable adding custom thresholds, don't forget to change this part
        return {}

    new_thresholds = {}

    st.markdown("#### Acceptance thresholds")
    st.markdown(
        'Designs passing *all* the thresholds will be marked as "Accepted" '
        "and become available in the Design explorer. "
        "You can change these thresholds later."
    )

    active_descriptor_keys = []
    for descriptor_key, threshold in selected_thresholds.items():
        if skipped_threshold_keys and descriptor_key in skipped_threshold_keys:
            # For skipped descriptors, keep original threshold but don't show the input component in the UI
            new_thresholds[descriptor_key] = threshold
            continue
        active_descriptor_keys.append(descriptor_key)
    columns = wrapped_columns(len(active_descriptor_keys), wrap=max_items_row, divider=True, gap="large")
    for descriptor_key, column in zip(active_descriptor_keys, columns):
        with column:
            descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key]
            new_thresholds[descriptor.key] = single_threshold_input_component(
                threshold=selected_thresholds[descriptor_key], descriptor=descriptor, descriptor_values=None
            )
            if descriptor.description:
                st.caption(descriptor.description)

    return new_thresholds


def single_threshold_input_component(
    threshold: Threshold, descriptor: NumericDescriptor, descriptor_values: pd.Series | None = None
) -> Threshold:
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
        st.markdown(f"##### " + (descriptor.name if threshold.enabled else f":grey[{descriptor.name}]"))
        if not threshold.enabled:
            if st.toggle("Disabled", key=f"{descriptor.key}_toggle"):
                st.session_state.thresholds_expanded = True
                st.success("Enabling threshold...")
                min_value = descriptor.min_value  # value or None
                max_value = descriptor.max_value  # value or None
                if descriptor_values is not None and len(descriptor_values):
                    min_value, max_value = descriptor_values.min(), descriptor_values.max()
                # if threshold already set, use the existing values, otherwise use the descriptor min/max
                if descriptor.min_value is not None or descriptor.max_value is not None:
                    return threshold.copy(enabled=True)
                elif descriptor.comparison == "higher_is_better":
                    return Threshold(min_value=min_value)
                elif descriptor.comparison == "lower_is_better":
                    return Threshold(max_value=max_value)
                else:
                    return Threshold(min_value=min_value, max_value=max_value)
        else:
            if not st.toggle("Enabled", value=True, key=f"{descriptor.key}_toggle"):
                st.session_state.thresholds_expanded = True
                return threshold.copy(enabled=False)

    kwargs = dict(
        min_value=float(descriptor.min_value) if descriptor.min_value is not None else None,
        max_value=float(descriptor.max_value) if descriptor.max_value is not None else None,
        disabled=not threshold.enabled,
        step=0.1,
    )
    min_value, max_value = threshold.min_value, threshold.max_value
    if descriptor.comparison == "higher_is_better":
        min_value = st.number_input(
            "Min value",
            value=float(min_value) if min_value is not None else None,
            key=f"{descriptor.key}_min",
            **kwargs,
        )
    elif descriptor.comparison == "lower_is_better":
        max_value = st.number_input(
            "Max value",
            value=float(max_value) if max_value is not None else None,
            key=f"{descriptor.key}_max",
            **kwargs,
        )
    else:
        left, right = st.columns(2)
        min_value = left.number_input(
            "Min value",
            value=float(min_value) if min_value is not None else None,
            key=f"{descriptor.key}_min",
            **kwargs,
        )
        max_value = right.number_input(
            "Max value",
            value=float(max_value) if max_value is not None else None,
            key=f"{descriptor.key}_max",
            **kwargs,
        )

    return threshold.copy(min_value=min_value, max_value=max_value)


def descriptor_histogram_component(descriptor_values: pd.Series, descriptor: Descriptor, threshold: Threshold):
    fig = px.histogram(
        x=descriptor_values,
        labels={"x": descriptor.name},
        nbins=50,
        height=250,
        width=500,
        color_discrete_sequence=["#1f77b4"] if threshold.enabled else ["#888888"],
    )
    fig.update_layout(
        yaxis_title_text="Number of designs",
    )

    if bounds := threshold.get_bounds(descriptor, descriptor_values):
        # plot accepted range in green
        fig.add_shape(
            type="rect",
            x0=bounds[0],
            x1=bounds[1],
            y0=0,
            y1=1,
            yref="paper",  # treat y0 and y1 as a fraction of the y-axis
            fillcolor="#00ff00" if threshold.enabled else "#aaaaaa",
            opacity=0.15,
            line_width=0,
        )

    # Disable zoom controls
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    fig.layout.margin["b"] = 0
    fig.layout.margin["t"] = 0

    st.plotly_chart(fig, width="content", key=f"{descriptor.key}_histogram")


@st.cache_data(ttl="1h")
def filter_designs_by_thresholds_cached(
    all_design_ids: list[str], thresholds: dict[str, Threshold]
) -> tuple[list[str], dict[str, int]]:
    return filter_designs_by_thresholds(
        all_design_ids=all_design_ids,
        thresholds=thresholds,
        values={
            descriptor_key: get_cached_descriptor_values(descriptor_key, design_ids=all_design_ids).to_dict()
            for descriptor_key, threshold in thresholds.items()
            if threshold.enabled
        },
    )


@st.dialog("Accept designs")
def accept_designs_dialog(
    pools: list[Pool],
    jobs: list[DesignJob],
    all_design_ids: list[str],
    new_accepted_design_ids: list[str],
    num_accepted_by_descriptor: dict[str, int],
    selected_thresholds: dict[str, Threshold],
):
    st.write(
        f"Accept **{len(new_accepted_design_ids):,} / {len(all_design_ids):,}** ({len(new_accepted_design_ids) / len(all_design_ids):.0%}) designs based on new thresholds:"
    )

    if len(pools) > 1:
        st.write(f"This will update {len(pools):,} pools: **{', '.join(p.id for p in pools)}**")

    display_current_thresholds(
        selected_thresholds=selected_thresholds,
        all_design_ids=all_design_ids,
        num_accepted_by_descriptor=num_accepted_by_descriptor,
    )

    jobs_by_id = {j.id: j for j in jobs}

    with st.columns(2)[1]:
        if st.button("Save", type="primary", width="stretch"):
            updated_pool_ids = []
            for pool in pools:
                if not pool.design_job_id:
                    continue
                job = jobs_by_id[pool.design_job_id]
                job.workflow.acceptance_thresholds = selected_thresholds
                # tell sqlalchemy that we modified the workflow object - with dataclasses this is not auto-detected
                flag_modified(job, "workflow")
                updated_pool_ids.append(pool.id)
            db.save_all(pools)
            db.save_all(jobs_by_id.values())
            update_accepted_design_ids(pool_ids=updated_pool_ids, accepted_design_ids=new_accepted_design_ids)
            st.session_state.flash_success = "Accepted designs saved successfully"
            st.rerun()


def display_current_thresholds(
    selected_thresholds: dict[str, Threshold],
    all_design_ids: list[str],
    num_accepted_by_descriptor: dict[str, int],
):
    threshold_labels: list[str] = []
    total = len(all_design_ids)

    for descriptor_key, threshold in selected_thresholds.items():
        descriptor = ALL_DESCRIPTORS_BY_KEY.get(descriptor_key)
        if descriptor is None:
            continue

        if not threshold.enabled:
            threshold_labels.append(f"- **{descriptor.name}**: :grey[disabled]")
            continue

        num_passing = num_accepted_by_descriptor.get(descriptor_key, 0)
        fraction_passing = (num_passing / total) if total else 0
        num_passing_str = (
            f"{num_passing:,} design{'s' if num_passing != 1 else ''} passing threshold ({fraction_passing:.2%})"
            if num_passing > 0
            else ":red[No designs passing threshold]"
        )
        threshold_str = threshold.format(descriptor.name)
        if threshold_str:
            threshold_labels.append(f"- **{threshold_str}**: {num_passing_str}")

    st.markdown("\n".join(threshold_labels) or "No customizable thresholds available")


def get_acceptance_df(
    pools: list[Pool], thresholds_by_pool_id: dict[str, dict[str, Threshold]]
) -> tuple[pd.DataFrame, list[str]]:
    """Build DataFrame comparing acceptance rates and thresholds across pools.

    Returns:
        (DataFrame with pool info, acceptance rates (%), and threshold strings, list of descriptor keys)
    """

    # Collect all enabled threshold keys across all pools
    all_threshold_keys = set()
    for pool_thresholds in thresholds_by_pool_id.values():
        enabled_keys = {k for k, v in pool_thresholds.items() if v.enabled}
        all_threshold_keys.update(enabled_keys)

    # Sort for deterministic column ordering
    all_threshold_keys = sorted(all_threshold_keys)

    data = []

    # Design and accepted design counts summed over all pools, used for the combined "Total" row.
    # Each descriptor is counted only over the pools where it is enabled, so its own
    # number of designs has to be tracked separately from the overall one.
    total_num_designs = 0
    total_num_accepted = 0
    total_num_designs_by_key = defaultdict(int)
    total_num_accepted_by_key = defaultdict(int)
    thresholds_by_key = defaultdict(set)

    for pool in pools:
        pool_thresholds = thresholds_by_pool_id.get(pool.id, {})
        pool_design_ids = db.select_values(Design, "id", pool_id__in=[pool.id])
        num_designs = len(pool_design_ids)
        if not pool_design_ids:
            continue  # Skip pools with no designs
        if not pool_thresholds:
            num_accepted = len(db.select_values(Design, "id", pool_id=pool.id, accepted=True))
            # Use number of accepted designs from the database
            filtering_result = {}
        else:
            # Filter designs by thresholds
            filtered_design_ids, filtering_result = filter_designs_by_thresholds_cached(
                all_design_ids=pool_design_ids, thresholds=pool_thresholds
            )
            num_accepted = len(filtered_design_ids)

        total_num_designs += num_designs
        total_num_accepted += num_accepted

        row = {
            "pool_id": pool.id,
            "pool_name": pool.name,
            "pool_description": pool.description,
            "num_designs": num_designs,
            "num_accepted": num_accepted,
            "percent_accepted": num_accepted / num_designs * 100 if num_designs > 0 else 0,
        }
        for descriptor_key in all_threshold_keys:
            if descriptor_key in pool_thresholds and pool_thresholds[descriptor_key].enabled:
                row[f"threshold_{descriptor_key}"] = pool_thresholds[descriptor_key].format()
                thresholds_by_key[descriptor_key].add(row[f"threshold_{descriptor_key}"])
            else:
                row[f"threshold_{descriptor_key}"] = "N/A"
            if descriptor_key in filtering_result:
                row[descriptor_key] = filtering_result[descriptor_key] / num_designs * 100 if num_designs > 0 else 0
                total_num_designs_by_key[descriptor_key] += num_designs
                total_num_accepted_by_key[descriptor_key] += filtering_result[descriptor_key]
            else:
                row[descriptor_key] = None

        data.append(row)

    if len(data) > 1:
        # Add a combined row summing the design counts over all pools
        total_row = {
            "pool_id": TOTAL_POOL_ID,
            "pool_name": "Total",
            "pool_description": "All pools combined",
            "num_designs": total_num_designs,
            "num_accepted": total_num_accepted,
            "percent_accepted": total_num_accepted / total_num_designs * 100 if total_num_designs > 0 else 0,
        }
        for descriptor_key in all_threshold_keys:
            descriptor_thresholds = thresholds_by_key[descriptor_key]
            if not descriptor_thresholds:
                total_row[f"threshold_{descriptor_key}"] = "N/A"
            elif len(descriptor_thresholds) == 1:
                total_row[f"threshold_{descriptor_key}"] = next(iter(descriptor_thresholds))
            else:
                # Pools use different thresholds for this descriptor, there is no single value to show
                total_row[f"threshold_{descriptor_key}"] = MIXED_THRESHOLD
            num_designs = total_num_designs_by_key[descriptor_key]
            if num_designs > 0:
                total_row[descriptor_key] = total_num_accepted_by_key[descriptor_key] / num_designs * 100
            else:
                total_row[descriptor_key] = None

        data.append(total_row)

    return pd.DataFrame(data), all_threshold_keys


def _format_acceptance_rate(row: pd.Series, descriptor_key: str, threshold_col: str) -> str | None:
    """Format the acceptance rate of a single descriptor, along with a badge showing its threshold.

    Args:
        row: Row of the acceptance DataFrame
        descriptor_key: Column with the acceptance rate in % (or None if not evaluated)
        threshold_col: Column with the formatted threshold (or "N/A" if not enabled)

    Returns:
        Markdown string, None if the threshold was not evaluated for the given pool
    """
    rate = row[descriptor_key]
    threshold = row[threshold_col]
    if pd.isna(rate) or threshold == "N/A":
        return None
    if rate == 0:
        # Highlight pools where no design passed the threshold
        return f":red-badge[No passing designs] :grey-badge[{threshold}]"
    return f"{rate:.1f}% :grey-badge[{threshold}]"


@st.fragment()
def display_acceptance_df(df: pd.DataFrame, threshold_descriptor_keys: list[str], params_table: pd.DataFrame = None):
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="bottom"):
        st.subheader("Acceptance rates", width="content")
        if params_table is not None and not params_table.empty:
            show_params = st.segmented_control(
                "Workflow parameters",
                options=[NO_PARAMS, ALL_PARAMS, DISTINCT_PARAMS],
                default=NO_PARAMS,
                key="show_params_acceptance",
                label_visibility="collapsed",
                help="Show the workflow parameters of each pool along with its acceptance rates.",
            )
        else:
            show_params = NO_PARAMS

    if df.empty:
        st.info("No pool data to display")
        return

    df = df.copy()

    # Set pool_id as index
    df = df.set_index("pool_id")

    # Format design counts and the percentage of accepted designs
    for count_col in ["num_designs", "num_accepted"]:
        if count_col in df.columns:
            df[count_col] = df[count_col].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")
    if "percent_accepted" in df.columns:
        df["percent_accepted"] = df["percent_accepted"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")

    # Create column multi-index: Pool (name, description), Designs (counts) and for each descriptor (threshold, rate)
    new_columns = []

    # Pool columns
    if "pool_name" in df.columns:
        new_columns.append((("Pool", "Name"), df["pool_name"]))
    if "pool_description" in df.columns:
        new_columns.append((("Pool", "Description"), df["pool_description"]))

    # Design count columns
    if "num_designs" in df.columns:
        new_columns.append((("Designs", "Num Total"), df["num_designs"]))
    if "num_accepted" in df.columns:
        new_columns.append((("Designs", "Num Accepted"), df["num_accepted"]))
    if "percent_accepted" in df.columns:
        new_columns.append((("Designs", "% Accepted"), df["percent_accepted"]))

    # Descriptor columns - group threshold and rate together
    for descriptor_key in threshold_descriptor_keys:
        descriptor = ALL_DESCRIPTORS_BY_KEY.get(descriptor_key)
        if not descriptor:
            continue

        descriptor_name = descriptor.name
        threshold_col = f"threshold_{descriptor_key}"

        if threshold_col in df.columns and descriptor_key in df.columns:
            new_columns.append(
                (
                    ("Threshold", descriptor_name),
                    df.apply(_format_acceptance_rate, axis=1, args=(descriptor_key, threshold_col)),
                )
            )

    # Build new dataframe with multi-index columns
    if not new_columns:
        st.info("No data to display")
        return

    multi_index_df = pd.DataFrame({col_name: col_data for col_name, col_data in new_columns}, index=df.index)

    if show_params in (ALL_PARAMS, DISTINCT_PARAMS):
        # Join the workflow parameters of each pool, skipping the groups already shown above.
        # Format as strings before reindexing, so that the missing values of the combined row
        # (which has no parameters of its own) are left empty instead of turning the column into floats.
        params_table = params_table.drop(columns=DUPLICATE_PARAM_GROUPS, level=0, errors="ignore")
        params_table = params_table.astype(str).reindex(multi_index_df.index, fill_value="")
        if show_params == DISTINCT_PARAMS:
            # Only keep parameters that differ between pools (ignoring the combined row)
            pool_params = params_table.drop(index=TOTAL_POOL_ID, errors="ignore")
            params_table = params_table[params_table.columns[pool_params.nunique() > 1]]
        multi_index_df = pd.concat([multi_index_df, params_table], axis=1)

    st.table(multi_index_df.T)
