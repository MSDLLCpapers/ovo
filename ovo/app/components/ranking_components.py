import streamlit as st

from ovo.core.database.models import NumericGlobalDescriptor
from ovo.app.components.descriptor_scatterplot import format_descriptor_name


def configure_rank_aggregation_descriptors(
    descriptors_by_key: dict[str, NumericGlobalDescriptor],
    design_ids: list[str],
    selection_limit: int = 100,
) -> tuple[list[str], dict[str, str], dict[str, float]]:
    """Select descriptors to rank by and specify if higher or lower values are better for each descriptor and their weights."""
    from ovo.app.utils.cached_db import get_cached_wide_descriptor_table

    # Multi-select descriptors
    selected_keys = st.multiselect(
        "Select descriptors to rank by",
        options=list(descriptors_by_key.keys()),
        format_func=lambda key: format_descriptor_name(descriptors_by_key[key], with_description=True),
        default=None,
        key=f"ranking_descriptors_{len(descriptors_by_key)}_options",
    )
    if len(selected_keys) > selection_limit:
        # Avoid exploding the UI when user clicks "Select all" for a large number of descriptors
        raise ValueError(f"Please select at most {selection_limit} descriptors.")

    # For each selected descriptor, ask user to specify if higher or lower values are better
    descriptor_comparisons = {}

    # For each selected descriptor, ask user to specify a weight for that descriptor
    descriptor_weights = {}

    # Query missing values for selected descriptors
    missing_counts = {}
    total_designs = len(design_ids)

    if selected_keys:
        # Get descriptor values for all selected descriptors
        df = get_cached_wide_descriptor_table(
            design_ids=design_ids,
            descriptor_keys=selected_keys,
            human_readable=False,
        )

        # Count missing values per descriptor
        for key in selected_keys:
            missing_count = df[key].isna().sum()
            if missing_count > 0:
                missing_counts[key] = missing_count

    if not selected_keys:
        return selected_keys, descriptor_comparisons, descriptor_weights

    with st.container(border=True):
        comparison_options = ["higher_is_better", "lower_is_better"]
        weight_options_map = {"Default weight": 1, "Low weight": 0.5, "High weight": 2}
        for key in selected_keys:
            descriptor = descriptors_by_key[key]
            st.write(f"**{format_descriptor_name(descriptor)}**")
            st.write(descriptor.description)
            with st.container(horizontal=True):
                descriptor_comparisons[key] = st.selectbox(
                    "Comparison",
                    options=comparison_options,
                    format_func=lambda x: "Higher is better" if x == "higher_is_better" else "Lower is better",
                    index=comparison_options.index(descriptor.comparison)
                    if descriptor.comparison in comparison_options
                    else None,
                    width=250,
                    key=f"comparison_{key}",
                    label_visibility="collapsed",
                )

                weight = st.selectbox(
                    "Weight",
                    options=weight_options_map.items(),
                    format_func=lambda x: f"{x[0]} ({x[1]})",
                    index=0,
                    width=250,
                    key=f"weight_{key}",
                    accept_new_options=True,
                    label_visibility="collapsed",
                )
            # Display missing value info if applicable
            if key in missing_counts:
                missing_count = missing_counts[key]
                pct = (missing_count / total_designs) * 100
                st.caption(
                    f"⚠️ {missing_count:,} of {total_designs:,} designs ({pct:.1f}%) missing value for **{descriptor.name}**, will be ranked last"
                )
            if isinstance(weight, tuple):
                weight_value = weight[1]
                try:
                    weight_value = float(weight_value)
                except ValueError:
                    st.error(
                        f"Invalid weight value: {weight_value}. Please enter a number or select a predefined option."
                    )
            elif isinstance(weight, str) and weight in weight_options_map:
                weight_value = weight_options_map[weight]
            else:
                try:
                    weight_value = float(weight)
                except ValueError:
                    st.error(f"Invalid weight value: {weight}. Please enter a number or select a predefined option.")
            descriptor_weights[key] = weight_value

    return selected_keys, descriptor_comparisons, descriptor_weights
