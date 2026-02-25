from dataclasses import dataclass
from functools import reduce

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly import express as px
from ovo.app.utils.cached_db import (
    get_cached_available_descriptors,
    get_cached_descriptor_values,
    get_cached_designs_accept_field,
)
from ovo.core.database import Threshold, NumericGlobalDescriptor, Descriptor
from ovo.core.database.descriptors import PRESETS


@dataclass
class PlotSettings:
    x: Descriptor | None = None
    y: Descriptor | None = None
    color: Descriptor | None = None
    color_type: str = "range"

    def get_x_key(self):
        return self.x.key if self.x else None

    def get_y_key(self):
        return self.y.key if self.y else None

    def get_keys(self) -> list[str]:
        keys = []
        if self.x:
            keys.append(self.x.key)
        if self.y:
            keys.append(self.y.key)
        if self.color:
            keys.append(self.color.key)
        return keys

    @classmethod
    def from_query_params(cls, descriptors_by_key: dict[str, Descriptor]):
        for field in ["x", "y", "color"]:
            # Handle case when descriptor is not available anymore - such as when switching between workflows
            if field in st.query_params and st.query_params[field] not in descriptors_by_key:
                st.warning(f"Descriptor not available: {st.query_params[field]}")
                st.query_params.pop(field)
        return cls(
            x=descriptors_by_key[st.query_params["x"]] if "x" in st.query_params else None,
            y=descriptors_by_key[st.query_params["y"]] if "y" in st.query_params else None,
            color=descriptors_by_key[st.query_params["color"]] if "color" in st.query_params else None,
            color_type=st.query_params["color_type"] if "color_type" in st.query_params else "range",
        )

    def update_query_params(self):
        st.query_params["color_type"] = self.color_type
        for field in ["x", "y", "color"]:
            if getattr(self, field):
                st.query_params[field] = getattr(self, field).key
            else:
                st.query_params.pop(field, None)


def descriptor_scatterplot_input_component(design_ids: list[str]) -> PlotSettings | None:
    descriptors_by_key = get_cached_available_descriptors(design_ids)

    # select only global numeric descriptors
    descriptors_by_key = {k: d for k, d in descriptors_by_key.items() if isinstance(d, NumericGlobalDescriptor)}

    descriptor_options = list(descriptors_by_key.keys())

    settings = PlotSettings.from_query_params(descriptors_by_key)

    available_presets = {
        key: value
        for key, value in PRESETS.items()
        if value["x"].key in descriptors_by_key and value["y"].key in descriptors_by_key
    }

    if st.session_state.get("scatterplot_update"):
        # update triggered from another component
        update, value = st.session_state["scatterplot_update"]
        if update == "x":
            st.session_state["scatterplot_x"] = value
        elif update == "y":
            st.session_state["scatterplot_y"] = value
        else:
            print("Ignoring unknown update", update, value)

    # Update settings if user just selected something in one of the dropdowns
    if st.session_state.get("scatterplot_preset") or (not settings.x and not settings.y and available_presets):
        if st.session_state.get("scatterplot_preset"):
            # user has just selected a preset
            new_preset = st.session_state.get("scatterplot_preset")
            st.session_state["flash_preset"] = new_preset
        else:
            # No x or y axis selected, choose first preset
            new_preset = list(available_presets.keys())[0]
        settings.x = available_presets[new_preset]["x"]
        settings.y = available_presets[new_preset]["y"]
        st.session_state["scatterplot_x"] = settings.x.key
        st.session_state["scatterplot_y"] = settings.y.key
        st.session_state["scatterplot_preset"] = None  # clear preset dropdown
        settings.update_query_params()
        st.rerun()
    elif st.session_state.get("scatterplot_x") and settings.get_x_key() != st.session_state.get("scatterplot_x"):
        # user has just changed the X axis
        # note that the session state is already updated here if user has just changed the value of the dropdown below
        settings.x = descriptors_by_key[st.session_state.get("scatterplot_x")]
        settings.update_query_params()
    elif st.session_state.get("scatterplot_y") and settings.get_y_key() != st.session_state.get("scatterplot_y"):
        # user has just changed the Y axis
        # note that the session state is already updated here if user has just changed the value of the dropdown below
        settings.y = descriptors_by_key[st.session_state.get("scatterplot_y")]
        settings.update_query_params()

    left, right = st.columns([1.1, 2], gap="medium", vertical_alignment="bottom")
    with left:
        st.selectbox(
            "Preset",
            placeholder="One preset available"
            if len(available_presets) == 1
            else f"{len(available_presets)} presets available",
            format_func=lambda key: PRESETS[key]["label"],
            options=list(available_presets.keys()),
            key="scatterplot_preset",
            index=None,
        )
    with right:
        if st.session_state.get("flash_preset"):
            st.success(f"Preset selected: {st.session_state['flash_preset']}")
            del st.session_state["flash_preset"]

    x_col, y_col, _ = st.columns([1, 1, 0.5], gap="medium")
    with x_col:
        st.selectbox(
            "X axis",
            format_func=lambda descriptor_key: format_descriptor_name(descriptors_by_key[descriptor_key]),
            options=descriptor_options,
            key="scatterplot_x",
            index=None,
        )
        if settings.x and settings.x.description:
            st.caption(settings.x.description)

    with y_col:
        st.selectbox(
            "Y axis",
            format_func=lambda descriptor_key: format_descriptor_name(descriptors_by_key[descriptor_key]),
            options=descriptor_options,
            key="scatterplot_y",
            index=None,
        )
        if settings.y and settings.y.description:
            st.caption(settings.y.description)

    # with color_col:
    #     key = 'scatterplot_color'
    #     color_descriptor = get_descriptor_by_key(descriptors, key) or Descriptor(name='run_id', key='run_id')
    #     color = st.selectbox(
    #         "Color",
    #         descriptors,
    #         format_func=lambda descriptor: (
    #             f"{descriptor.name} ({descriptor.tool})" if descriptor.tool else descriptor.name
    #         ),
    #         index=get_descriptor_index(descriptors, color_descriptor),
    #     )
    #     st.query_params[key] = color.key
    #
    # with color_type_col:
    #     color_type = st.selectbox(
    #         "Color type", ["range", "PDB density"], index=0, disabled=True
    #     )

    return settings


def descriptor_scatterplot_design_explorer_component(settings: PlotSettings, design_ids: list[str]) -> list[str]:
    if not settings.x or not settings.y:
        st.caption("Please select the X and Y axes to see the scatterplot.")
        return design_ids

    x_values = get_cached_descriptor_values(settings.x.key, design_ids=design_ids)
    y_values = get_cached_descriptor_values(settings.y.key, design_ids=design_ids)
    # FIXME
    color_values = pd.Series([design_id.split("_")[1] for design_id in design_ids], index=design_ids)

    values_by_name = {
        settings.x.name: x_values,
        settings.y.name: y_values,
    }
    print_missing(values_by_name)

    st.markdown(
        """
        <style>
        /* center the plot */
        .js-plotly-plot .plotly .svg-container { margin: 0 auto; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    scatterplot_df = pd.DataFrame({"x": x_values, "y": y_values, "color": color_values, "design_id": design_ids})
    fig = px.scatter(
        scatterplot_df,
        x="x",
        y="y",
        labels={"x": settings.x.name, "y": settings.y.name},
        range_x=settings.x.get_plot_range(x_values),
        range_y=settings.y.get_plot_range(y_values),
        width=800,
        height=600,
        color="color",
        custom_data=["design_id"],
        marginal_x="histogram",
        marginal_y="histogram",
    )

    fig.update_layout(dragmode="select")
    event = st.plotly_chart(fig, on_select="rerun", width="content", key="scatterplot")

    # descriptor to create a subpool from lasso/box selected designs
    if not event["selection"]["box"] and not event["selection"]["lasso"]:
        # No selection yet
        st.info(
            "Click and drag to select a region in the plot.",
            icon=":material/info:",
        )
        return design_ids
    else:
        selected_design_ids = [point["customdata"][0] for point in event["selection"]["points"]]
        if box := event["selection"]["box"]:
            x_min, x_max = get_trimmed_min_max(box[0]["x"], settings.x)
            y_min, y_max = get_trimmed_min_max(box[0]["y"], settings.y)
            selection_label = (
                f"with **{format_range(x_min, x_max, settings.x)}** and **{format_range(y_min, y_max, settings.y)}**"
            )
        else:
            selection_label = "using lasso selection"
        st.info(
            f"Selected {len(selected_design_ids):,} designs {selection_label}. "
            f"Double-click on the plot to clear the selection.",
            icon=":material/info:",
        )
        return selected_design_ids


def descriptor_scatterplot_pool_details_component(
    settings: PlotSettings,
    design_ids: list[str],
    selected_thresholds: dict[str, Threshold] = None,
    highlight_accepted: bool = False,
) -> tuple[list[str], str | None]:
    if not settings.x or not settings.y:
        return design_ids, None

    x_values = get_cached_descriptor_values(settings.x.key, design_ids=design_ids)
    y_values = get_cached_descriptor_values(settings.y.key, design_ids=design_ids)
    # FIXME
    color_values = pd.Series([design_id.split("_")[1] for design_id in design_ids], index=design_ids)

    values_by_name = {
        settings.x.name: x_values,
        settings.y.name: y_values,
    }
    print_missing(values_by_name)

    st.markdown(
        """
        <style>
        /* center the plot */
        .js-plotly-plot .plotly .svg-container { margin: 0 auto; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    scatterplot_df = pd.DataFrame({"x": x_values, "y": y_values, "color": color_values, "design_id": design_ids})
    if highlight_accepted:
        accepted_values = get_cached_designs_accept_field(design_ids)
        scatterplot_df["accepted"] = accepted_values

        # FIXME: When we use continuous column this will need to be changed
        color_scale = px.colors.qualitative.Plotly
        unique_colors = scatterplot_df["color"].unique()
        color_map = {value: color_scale[i % len(color_scale)] for i, value in enumerate(unique_colors)}
        scatterplot_df["color_mapped"] = scatterplot_df["color"].map(color_map)

        # Hover template
        # TODO: Use X and Y names in the hover
        hovertemplate = (
            "<b>%{customdata[0]}</b><br>"
            "pool=%{customdata[1]}<br>"
            f"{settings.x.name}=%{{x}}<br>"
            f"{settings.y.name}=%{{y}}<br>"
            "<extra></extra>"  # Remove trace name from hover
        )

        # Plot seperately accepted and rejected points
        accepted_df = scatterplot_df[scatterplot_df["accepted"] == True]
        rejected_df = scatterplot_df[scatterplot_df["accepted"] == False]

        rejected_trace = go.Scatter(
            x=rejected_df["x"],
            y=rejected_df["y"],
            mode="markers",
            marker=dict(
                color=rejected_df["color_mapped"],
            ),
            customdata=rejected_df[["design_id", "color"]],
            legendgroup="rejected",
            showlegend=False,
            hovertemplate=hovertemplate,
        )
        accepted_trace = go.Scatter(
            x=accepted_df["x"],
            y=accepted_df["y"],
            mode="markers",
            marker=dict(
                color=accepted_df["color_mapped"],
                line=dict(color="lime", width=2),
            ),
            customdata=accepted_df[["design_id", "color"]],
            legendgroup="accepted",
            showlegend=False,
            hovertemplate=hovertemplate,
        )
        layout = go.Layout(
            xaxis=dict(title=settings.x.name, range=settings.x.get_plot_range(scatterplot_df["x"])),
            yaxis=dict(title=settings.y.name, range=settings.y.get_plot_range(scatterplot_df["y"])),
            width=800,
            height=600,
        )

        # FIXME: When we use continuous column this will need to be changed
        # Create individual legend traces for each color (category)
        legend_traces = []
        for category, color in color_map.items():
            legend_trace = go.Scatter(
                x=[None],
                y=[None],  # Invisible data points
                mode="markers",
                name=category,
                marker=dict(
                    color=color,
                    size=10,  # Marker size in the legend
                ),
                legendgroup=category,  # Grouping by category to ensure color consistency in the legend
                showlegend=True,  # This ensures the legend is shown
            )
            legend_traces.append(legend_trace)

        fig = go.Figure(
            data=[rejected_trace, accepted_trace] + legend_traces,
            layout=layout,
        )

    else:
        fig = px.scatter(
            scatterplot_df,
            x="x",
            y="y",
            labels={"x": settings.x.name, "y": settings.y.name},
            range_x=settings.x.get_plot_range(x_values),
            range_y=settings.y.get_plot_range(y_values),
            width=800,
            height=600,
            color="color",
            custom_data=["design_id"],
        )

    # Add a rectangle for reference based on the selected thresholds
    if selected_thresholds and (settings.x.key in selected_thresholds or settings.y.key in selected_thresholds):
        x0, x1, xref = -0.04, -0.005, "paper"  # mark a small rectangle on the left
        y0, y1, yref = -0.07, -0.01, "paper"  # mark a small rectangle on the bottom
        if settings.x.key in selected_thresholds and selected_thresholds[settings.x.key].enabled:
            t = selected_thresholds[settings.x.key]
            x0, x1 = t.min_value, t.max_value
            xref = None
            # offset range for integer values to make it clear that the range is inclusive
            is_int = all(int(v) == v for v in x_values if not pd.isna(v))
            if is_int and x0 is not None:
                x0 -= 0.5
            if is_int and x1 is not None:
                x1 += 0.5
        if settings.y.key in selected_thresholds and selected_thresholds[settings.y.key].enabled:
            t = selected_thresholds[settings.y.key]
            y0, y1 = t.min_value, t.max_value
            yref = None
            # offset range for integer values to make it clear that the range is inclusive
            is_int = all(int(v) == v for v in y_values if not pd.isna(v))
            if is_int and y0 is not None:
                y0 -= 0.5
            if is_int and y1 is not None:
                y1 += 0.5
        if xref is None or yref is None:
            # use axis limits if specified, otherwise use actual min/max values
            (xlim0, xlim1) = fig.layout.xaxis.range or (x_values.min(), x_values.max())
            (ylim0, ylim1) = fig.layout.yaxis.range or (y_values.min(), y_values.max())
            fig.add_shape(
                type="rect",
                x0=x0 if x0 is not None else xlim0,
                x1=x1 if x1 is not None else xlim1,
                xref=xref,
                y0=y0 if y0 is not None else ylim0,
                y1=y1 if y1 is not None else ylim1,
                yref=yref,
                fillcolor="#00ff00",
                opacity=0.15,
                line_width=0,
            )

    fig.update_layout(dragmode="select")
    event = st.plotly_chart(fig, on_select="rerun", width="content", key="scatterplot")

    if not event["selection"]["box"] and not event["selection"]["lasso"]:
        return design_ids, None
    else:
        selected_design_ids = [point["customdata"][0] for point in event["selection"]["points"]]
        if box := event["selection"]["box"]:
            x_min, x_max = get_trimmed_min_max(box[0]["x"], settings.x)
            y_min, y_max = get_trimmed_min_max(box[0]["y"], settings.y)
            selection_label = (
                f"**{format_range(x_min, x_max, settings.x)}** and **{format_range(y_min, y_max, settings.y)}**"
            )
        else:
            selection_label = "Using lasso selection"
        return selected_design_ids, selection_label


def format_descriptor_name(descriptor: Descriptor) -> str:
    return f"{descriptor.name} ({descriptor.tool})" if descriptor.tool else descriptor.name


def get_trimmed_min_max(box_selection, descriptor):
    """Crop selected range to actually possible descriptor range - return None if value is outside of range"""
    min_value, max_value = min(box_selection), max(box_selection)
    if descriptor.min_value is not None and min_value < descriptor.min_value:
        min_value = None
    if descriptor.max_value is not None and max_value > descriptor.max_value:
        max_value = None
    return min_value, max_value


def format_range(min_value, max_value, descriptor):
    if min_value is not None and max_value is not None:
        return f"{descriptor.name} within {min_value:.2f} — {max_value:.2f}"
    elif min_value is not None:
        return f"{descriptor.name} ≥ {min_value:.2f}"
    elif max_value is not None:
        return f"{descriptor.name} ≤ {max_value:.2f}"


def print_missing(values_by_name: dict[str, pd.Series]):
    num_missing_by_name = {}
    for name, values in values_by_name.items():
        if num_missing := values.isna().sum():
            num_missing_by_name[name] = num_missing

    if not num_missing_by_name:
        return
    num_total = len(next(iter(values_by_name.values())))
    num_missing = reduce(lambda x, y: x | y, [values.isna() for values in values_by_name.values()]).sum()
    if num_missing == num_total:
        st.warning("No designs available for selected combination of descriptors")
    elif len(set(num_missing_by_name.values())) == 1:
        # all missing counts are the same
        st.warning(
            f"Not showing {num_missing:,}/{num_total:,} designs with missing "
            + " & ".join(f"**{name}**" for name in num_missing_by_name.keys())
        )
    else:
        st.warning(
            f"Not showing {num_missing:,}/{num_total:,} designs with missing "
            + " or ".join(f"**{name}** ({count:,} missing)" for name, count in num_missing_by_name.items())
        )
