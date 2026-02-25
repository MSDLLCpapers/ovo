import pandas as pd
import streamlit as st
from sqlalchemy.orm.attributes import flag_modified

from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.utils.cached_db import get_cached_descriptor_values, Descriptor

from plotly import express as px

from ovo import db, Threshold, NumericDescriptor
from ovo.core.database import Pool, DesignJob
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.logic.design_logic import update_accepted_design_ids
from ovo.core.logic.filtering_logic import filter_designs_by_thresholds


def thresholds_and_histograms_component(
    selected_thresholds: dict[str, Threshold],
    saved_thresholds: dict[str, Threshold],
    all_design_ids: list[str],
    max_items_row=3,
) -> dict[str, Threshold]:
    """Adjust thresholds using sliders and show histograms for each descriptor, return new thresholds."""

    new_thresholds = {}
    descriptor_keys = list(selected_thresholds.keys())
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

            if saved_thresholds[descriptor.key] != new_thresholds[descriptor.key]:
                st.caption(
                    ':red[Threshold has been changed], see the new statistics above and save using the "Confirm thresholds" button.'
                )

    return new_thresholds


def thresholds_input_component(
    selected_thresholds: dict[str, Threshold],
    max_items_row: int = 3,
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

    descriptor_keys = list(selected_thresholds.keys())
    columns = wrapped_columns(len(descriptor_keys), wrap=max_items_row, divider=True, gap="large")
    for descriptor_key, column in zip(descriptor_keys, columns):
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
    with st.container(horizontal=True, vertical_alignment="bottom"):
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
    selected_thresholds: dict[str, Threshold], all_design_ids: list[str], num_accepted_by_descriptor: dict[str, int]
):
    threshold_labels = []
    for descriptor_key, threshold in selected_thresholds.items():
        descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key]
        if not threshold.enabled:
            continue
        num_accepted = num_accepted_by_descriptor[descriptor_key]
        fraction_accepted = num_accepted / len(all_design_ids)
        num_accepted_str = (
            f"{num_accepted:,} design{'s' if num_accepted > 1 else ''} passing threshold ({fraction_accepted:.2%})"
            if num_accepted > 0
            else ":red[No designs passing threshold]"
        )
        threshold_str = threshold.format(descriptor.name)
        if threshold_str:
            threshold_labels.append(f"- **{threshold_str}**: {num_accepted_str}")
    st.markdown("\n".join(threshold_labels) or "No customizable thresholds available")
