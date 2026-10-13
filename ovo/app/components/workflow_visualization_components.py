import math
import os
import traceback
from dataclasses import dataclass

import pandas as pd
import streamlit as st
from cmap import Colormap
from streamlit.elements.metric import DeltaColor

from ovo import storage, Threshold, UnknownWorkflow, WorkflowTypes, DesignWorkflow
from ovo.app.components.navigation import DEFAULT_SELECTED_DESIGN_KEY, get_jobs_url, design_navigation_selector
from ovo.core.database.models import AlignmentOption
from ovo.app.components.custom_elements import simple_tabs, wrapped_columns
from ovo.app.components.design_labeling import design_labeling_fragment
from ovo.app.components.descriptor_scatterplot import format_descriptor_name
from ovo.app.components.download_component import download_job_designs_component
from ovo.core.database import (
    Design,
    descriptors,
    StructureFileDescriptor,
    descriptors_rfdiffusion,
    descriptors_refolding,
    descriptors_proteinqc,
    descriptors_disco,
)
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionWorkflow,
    RFdiffusionBinderDesignWorkflow,
    RFdiffusionScaffoldDesignWorkflow,
)
from ovo.core.database.descriptors import (
    ALL_DESCRIPTORS_BY_KEY,
    SEQUENCE_DESIGN_PATH_DESCRIPTORS,
    STRUCTURE_PATH_DESCRIPTORS,
    BACKBONE_DESIGN_PATH_DESCRIPTORS,
)

from ovo import viz
from ovo.core.plugins import load_variable, get_extension_points
from ovo.core.utils.pdb import (
    align_multiple_proteins_pdb,
    pdb_to_mmcif,
    filter_pdb_str,
    get_sequences_from_pdb_str,
    align_pdb_to_front,
)
from ovo.core.utils.colors import get_color_from_str
from ovo.app.utils.cached_db import (
    get_cached_design_descriptors,
    get_cached_design,
    get_cached_pool,
    get_cached_design_job,
    get_cached_designs,
    get_cached_available_descriptors,
    get_cached_descriptor_values,
    get_cached_workflow_types_by_design,
)
from ovo.core.utils.residue_selection import (
    from_segments_to_hotspots,
    parse_contig_for_input_structure,
    parse_contig_for_output_structure,
    MappedContigSegment,
)


def show_design_metrics(
    design_id: str,
    descriptor_keys: list[str] = None,
    thresholds: dict[str, Threshold] = None,
    allow_custom: bool = True,
) -> pd.Series:
    required_descriptor_keys = descriptor_keys or []
    all_descriptor_keys = list(required_descriptor_keys)
    thresholds = thresholds or {}
    for descriptor_key, threshold in thresholds.items():
        if threshold.enabled and descriptor_key not in required_descriptor_keys:
            all_descriptor_keys.append(descriptor_key)

    descriptor_values = get_cached_design_descriptors(design_id, descriptor_keys=all_descriptor_keys)
    columns = wrapped_columns(len(descriptor_values) + (1 if allow_custom else 0), wrap=4)
    descriptor_value_pairs = list(descriptor_values.items()) + ([(None, None)] if allow_custom else [])
    for column, (descriptor_key, value) in zip(columns, descriptor_value_pairs):
        if descriptor_key is None:
            if st.session_state.get("show_custom_metric") or column.button(
                ":material/more_horiz: Show custom metric", type="tertiary", key="add_custom"
            ):
                st.session_state["show_custom_metric"] = True
                available_descriptor_keys = get_cached_available_descriptors([design_id])
                descriptor_key = column.selectbox(
                    "Metric",
                    placeholder="Select a custom metric",
                    index=None,
                    options=available_descriptor_keys,
                    format_func=lambda key: format_descriptor_name(ALL_DESCRIPTORS_BY_KEY[key]),
                    label_visibility="collapsed",
                    key="custom_metric",
                )
                if descriptor_key:
                    value = get_cached_design_descriptors(design_id, descriptor_keys=[descriptor_key])[descriptor_key]
                    if pd.isna(value):
                        column.write("*No value available*")

        if pd.isna(value) and descriptor_key not in required_descriptor_keys:
            # do not show metric at all when value is missing and descriptor wasn't explicitly requested
            continue
        descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key]
        delta = None
        delta_description = None
        delta_color: DeltaColor = "normal"
        if descriptor_key in thresholds and thresholds[descriptor_key].enabled:
            # show threshold value in green or red
            threshold = thresholds[descriptor_key]
            if formatted_threshold := threshold.format():
                if threshold.passes(value):
                    delta = f":material/check: {formatted_threshold}"
                    delta_color = "green"
                else:
                    delta = f":material/close: {formatted_threshold}"
                    delta_color = "red"
                    delta_description = "Rejected"

        column.metric(
            label=descriptor.name,
            help=descriptor.description,
            value=descriptor.format(value),
            delta=delta,
            delta_color=delta_color,
            delta_arrow="off",
            delta_description=delta_description,
        )

    return descriptor_values


def single_design_tab(design_ids: list[str]):
    """Show design selector dropdown and visualize the design in detail

    Used as default tab at bottom of Explorer page and other pages
    """
    design_id = design_navigation_selector(design_ids)
    design_labeling_fragment(design_id, key_suffix="single_design")
    show_design(design_id)


def show_design(design_id: str):
    """Visualize a single design in detail using the workflow-specific visualization method if available

    Shows the design structure, sequence, and download button.
    """
    design = get_cached_design(design_id)
    pool = get_cached_pool(design.pool_id)

    WorkflowType = DesignWorkflow
    link = ""
    if pool.design_job_id:
        design_job = get_cached_design_job(pool.design_job_id)
        link = f'<a href="{get_jobs_url(st.session_state.project.id, pool.id)}">↑ Show job</a>'
        if design_job.workflow:
            if design_job.workflow.is_instance(UnknownWorkflow):
                st.warning(
                    f"Falling back to basic structure and sequence visualization, "
                    f"failed to load workflow information: {design_job.workflow.error}"
                )
            else:
                WorkflowType = WorkflowTypes.get(design_job.workflow.name)

    st.markdown(
        f"**Pool:** {pool.name} {link}",
        unsafe_allow_html=True,
    )
    if pool.description:
        st.write(f"**Pool description:** {pool.description}")

    try:
        WorkflowType.visualize_single_design_structures(design_id)
    except Exception as e:
        traceback.print_exc()
        st.error(f"Error visualizing structure: {e}")

    st.write("### Sequence")

    WorkflowType.visualize_single_design_sequences(design_id)

    st.write(f"### Download single design: {design_id}")

    download_job_designs_component(design_ids=[design_id], pools=[pool], key="single")


def select_structure_prediction_descriptor(paths: dict[str, str]) -> StructureFileDescriptor | None:
    prediction_descriptors = [
        d for d in STRUCTURE_PATH_DESCRIPTORS if d.structure_type == "prediction" and d.key in paths
    ]

    if not prediction_descriptors:
        st.info("No structure prediction was run for this design.")
        return None
    elif len(prediction_descriptors) == 1:
        prediction_descriptor = prediction_descriptors[0]
    else:
        prediction_descriptor = st.segmented_control(
            "Structure prediction method",
            options=prediction_descriptors,
            key="structure_prediction_method",
            format_func=lambda d: d.name,
        )
        if not prediction_descriptor:
            st.write(":material/arrow_upward: *Please select a structure prediction method above*")
    return prediction_descriptor


def rfdiffusion_scaffold_design_visualization(design_id: str | None):
    design: Design = get_cached_design(design_id)

    chain_contigs = [c.contig for c in design.spec.chains]
    st.write(f"**Contig:** {' '.join(chain_contigs)}")

    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id)
    workflow: RFdiffusionScaffoldDesignWorkflow = design_job.workflow

    show_design_metrics(
        design_id,
        descriptor_keys=[
            descriptors_proteinqc.LENGTH.key,
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key,
            descriptors_rfdiffusion.PYDSSP_HELIX_PERCENT.key,
            descriptors_rfdiffusion.PYDSSP_SHEET_PERCENT.key,
        ],
        thresholds=workflow.acceptance_thresholds,
    )

    paths = (
        get_cached_design_descriptors(
            design_id,
            [
                *[d.key for d in descriptors.STRUCTURE_PATH_DESCRIPTORS],
            ],
        )
        .dropna()
        .to_dict()
    )
    input_pdb_str = storage.read_file_str(workflow.get_input_pdb_path(design.contig_index))
    if not all(c.contig for c in design.spec.chains):
        st.error("Contig not found in design spec")
        return
    contig = " ".join(c.contig for c in design.spec.chains if c.contig)
    input_segments = parse_contig_for_input_structure(contig)
    output_segments = parse_contig_for_output_structure(contig)

    input_mapping = [
        (segment.input_chain, list(range(segment.input_start, segment.input_end + 1)))
        for segment in output_segments
        if segment.input_chain
    ]
    output_mapping = [
        (segment.chain, list(range(segment.start, segment.end + 1)))
        for segment in output_segments
        if segment.input_chain
    ]

    left, middle, right = st.columns(3, gap="medium")

    with left:
        st.write("##### Full input structure")

        viz.molstar(
            viz.StructureVisualization(
                data=input_pdb_str, contigs=input_segments, representation="cartoon+ball-and-stick"
            ),
            key="full_input",
            height=350,
        )

    backbone_design_descriptor = None
    for d in BACKBONE_DESIGN_PATH_DESCRIPTORS:
        if paths.get(d.key):
            backbone_design_descriptor = d

    with middle:
        st.write(f"##### {backbone_design_descriptor.name}")

        representation = "cartoon"
        if "RFdiffusion3" in backbone_design_descriptor.tool:
            representation = "cartoon+ball-and-stick"

        viz.molstar(
            viz.StructureVisualization(
                data=storage.read_file_str(paths[backbone_design_descriptor.key]),
                contigs=output_segments,
                representation=representation,
            ),
            key="rfdiff_contig_segments",
            height=350,
        )

        st.write(backbone_design_descriptor.description)

    sequence_design_descriptor = None
    for d in SEQUENCE_DESIGN_PATH_DESCRIPTORS:
        if paths.get(d.key):
            sequence_design_descriptor = d

    with right:
        st.write(f"##### {sequence_design_descriptor.name}")

        viz.molstar(
            viz.StructureVisualization(
                data=storage.read_file_str(paths[sequence_design_descriptor.key]),
                contigs=output_segments,
                representation="cartoon+ball-and-stick",
            ),
            key="mpnn_contig_segments",
            height=350,
        )

        st.write(sequence_design_descriptor.description)

    st.write("### Refolding tests")

    prediction_descriptor = select_structure_prediction_descriptor(paths)

    if not prediction_descriptor:
        return

    left, middle, right = st.columns(3, gap="medium")

    prediction_storage_path = paths[prediction_descriptor.key]
    prediction_pdb = storage.read_file_str(prediction_storage_path)

    with left:
        st.write(f"##### {prediction_descriptor.name}")
        description = prediction_descriptor.description

        if prediction_descriptor.b_factor_value == "plddt":
            pdb_str = pdb_to_mmcif(prediction_pdb, "-", True)
            description += " (colored by pLDDT confidence)"
        elif prediction_descriptor.b_factor_value == "fractional_plddt":
            pdb_str = pdb_to_mmcif(prediction_pdb, "-", True, fractional_plddt=True)
            description += " (colored by pLDDT confidence)"
        else:
            pdb_str = prediction_pdb

        viz.molstar(
            viz.StructureVisualization(
                data=pdb_str,
                representation="cartoon",
                color="plddt",
            ),
            key=f"pred_{prediction_descriptor.key}",
            height=350,
        )
        st.write(description)

    with middle:
        st.write("##### Input motif aligned to prediction")

        input_motif_pdb = filter_pdb_str(input_pdb_str, [f"{s.chain}{s.start}-{s.end}" for s in input_segments])
        structures = [
            viz.StructureVisualization(
                data=input_motif_pdb, contigs=input_segments, representation="cartoon+ball-and-stick"
            )
        ]

        (_, aligned_prediction_pdb), rmsd = align_multiple_proteins_pdb(
            pdb_strs=[input_motif_pdb, prediction_pdb],
            chain_residue_mappings=[
                input_mapping,
                output_mapping,
            ],
            all_atom=True,
        )
        num_fixed = sum(segment.end - segment.start + 1 for segment in input_segments)

        structures.append(
            viz.StructureVisualization(
                data=aligned_prediction_pdb,
                representation="cartoon+ball-and-stick",
            )
        )

        viz.molstar(
            *structures,
            key=f"input_motif_aligned_to_{prediction_descriptor.name}",
            height=350,
            html_filename=os.path.basename(prediction_storage_path).replace(".pdb", "_aligned_motif"),
        )

        st.write(
            f"""
            {prediction_descriptor.name} vs native motif all atom RMSD: **{rmsd:.2f} Å**

            {prediction_descriptor.name} prediction (white) aligned to original input structure (colored segments) 
            of the {num_fixed} fixed input motif residues.
            """
        )

    with right:
        st.write("##### Design aligned to prediction")

        structures, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[
                storage.read_file_str(paths[sequence_design_descriptor.key]),
                prediction_pdb,
            ],
            chain_residue_mappings=[
                # align on all chains (sequences of design and prediction are identical)
                [(chain_id, None) for c in design.spec.chains for chain_id in c.chain_ids],
                [(chain_id, None) for c in design.spec.chains for chain_id in c.chain_ids],
            ],
            all_atom=False,
        )
        aligned_str = structures[1]

        if prediction_descriptor.b_factor_value == "plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True)
        elif prediction_descriptor.b_factor_value == "fractional_plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True, fractional_plddt=True)

        viz.molstar(
            viz.StructureVisualization(data=structures[0], contigs=output_segments),
            viz.StructureVisualization(
                data=aligned_str,
                representation="cartoon",
                color="plddt",
            ),
            key=f"design_aligned_to_{prediction_descriptor.key}",
            height=350,
        )

        st.write(
            f"""
            {prediction_descriptor.name} vs design backbone RMSD: **{rmsd:.2f} Å**
            
            Agreement between {sequence_design_descriptor.name} and {prediction_descriptor.name}
            """
        )


DESIGN_STRUCTURE_OPTION = "Design structure"
# target chains are shared by all designs, showing them in one neutral color keeps the designed chains apart
TARGET_CHAIN_COLOR = "#eeeeee"
GRID_COLUMNS = 3
GRID_ROWS = 2


@dataclass
class DesignTab:
    title: str
    path: str


@st.fragment
def show_designs_fragment(design_ids: list[str]):
    if not design_ids:
        st.warning("No designs to show")
        return

    workflow_types = set(get_cached_workflow_types_by_design(design_ids).values())
    tabs = {}
    for WorkflowType in workflow_types:
        tabs.update(WorkflowType.get_design_tabs())

    # enable plugins to implement additional tabs by declaring an extension point
    for design_tab in get_extension_points("ovo.design_tab", DesignTab):
        title = design_tab.title
        n = 1
        while title in tabs:
            title = f"{design_tab.title} ({n})"
            n += 1
        tabs[title] = load_variable(design_tab.path)

    tab_name = simple_tabs(list(tabs), key="design_tab")
    tabs[tab_name](design_ids)


def get_structure_options(design_ids: list[str]) -> dict[str, dict[str, str]]:
    """Get the structures available for the given designs

    Options are the main design structure plus all structure descriptors available for the given designs.

    :return: mapping of structure label to a mapping of design ID to storage path
    """
    structure_descriptors = [
        d for d in get_cached_available_descriptors(design_ids).values() if isinstance(d, StructureFileDescriptor)
    ]
    options = {DESIGN_STRUCTURE_OPTION: {design.id: design.structure_path for design in get_cached_designs(design_ids)}}
    for descriptor in structure_descriptors:
        options[descriptor.name] = get_cached_descriptor_values(descriptor.key, design_ids).dropna().to_dict()

    available = {label: {i: path for i, path in paths.items() if path} for label, paths in options.items()}
    return {label: paths for label, paths in available.items() if paths}


def multiple_designs_grid_tab(design_ids: list[str], key: str = "multi_design_grid"):
    """Paginated grid of individual structure viewers, one per design"""
    options = get_structure_options(design_ids)
    if not options:
        st.info("No structure types available for the selected designs.")
        return

    columns = st.columns(4, vertical_alignment="center")

    with columns[1]:
        label = st.selectbox(
            "Structure type",
            options=list(options),
            key=f"{key}_structure",
            label_visibility="collapsed",
        )

    paths = options[label]

    shown_design_ids = [design_id for design_id in design_ids if design_id in paths]
    if not shown_design_ids:
        st.info(f"No {label} available for the selected designs.")
        return
    if skipped := len(design_ids) - len(shown_design_ids):
        st.warning(f"Skipping {skipped:,} designs without a {label}.")

    per_page = GRID_COLUMNS * GRID_ROWS
    num_pages = math.ceil(len(shown_design_ids) / per_page)

    with columns[0]:
        page = st.pagination(num_pages, key=f"{key}_page", width="stretch") if num_pages > 1 else 1
        page_design_ids = shown_design_ids[(page - 1) * per_page : page * per_page]

    with columns[2]:
        representation_type = representation_type_selectbox(key=f"{key}_representation")

    with columns[3]:
        color = representation_color_selectbox(key=f"{key}_color")

    with storage.bulk_read_context():
        pdb_strs = {design_id: storage.read_file_str(paths[design_id]) for design_id in page_design_ids}

    columns = wrapped_columns(len(page_design_ids), wrap=GRID_COLUMNS, gap="medium")
    for i, (design_id, column) in enumerate(zip(page_design_ids, columns)):
        with column:
            # the fragment header is a subheader that wraps to its own row in a narrow grid column,
            # so we show the design ID as a caption next to the labels instead
            with st.container(horizontal=True, vertical_alignment="center", gap="small"):
                st.caption(design_id, width="content")
                design_labeling_fragment(
                    design_id, key_suffix="grid", allow_edit=False, show_header=False, compact=True
                )
            viz.molstar(
                viz.StructureVisualization(
                    data=pdb_strs[design_id],
                    color=color,
                    representation=representation_type,
                ),
                # the key is the grid position, so switching pages reloads the data of the same viewers
                key=f"{key}_{i}",
                height="300px",
            )


def multiple_designs_alignment_tab(
    design_ids: list[str],
    max_examples: int = 15,
    key: str = "multi_design_alignment",
):
    """Superposition of any combination of designs and their structures

    Every selected structure of every selected design is superposed in one viewer, so a single design can be
    compared across all of its structures (design, prediction, backbone, ...) and multiple designs can be
    compared on one structure - or any mix of both.
    """
    options = get_structure_options(design_ids)
    if not options:
        st.info("No structure types available for the selected designs.")
        return

    selected_design_ids = st.multiselect(
        "Designs to align",
        options=design_ids,
        key=f"{key}_designs",
        default=st.query_params[DEFAULT_SELECTED_DESIGN_KEY]
        if st.query_params.get(DEFAULT_SELECTED_DESIGN_KEY) in design_ids
        else None,
    )
    if not selected_design_ids:
        st.info("Select the designs you want to align.")
        return

    selected_labels = st.multiselect(
        "Structure types",
        options=list(options),
        # default to the design structure only, to keep the viewer readable
        default=list(options)[:1],
        key=f"{key}_structures",
    )
    if not selected_labels:
        st.info("Select at least one structure type to align.")
        return

    structures = [
        (design_id, label, options[label][design_id])
        for design_id in selected_design_ids
        for label in selected_labels
        if design_id in options[label]
    ]
    if not structures:
        st.info("None of the selected designs have any of the selected structure types.")
        return
    if len(structures) > max_examples:
        st.warning(
            f"Showing only first {max_examples} out of {len(structures):,} selected structures for performance reasons."
        )
        structures = structures[:max_examples]

    align_structures_component(structures, key=key)

    sequences = pd.DataFrame(
        [
            {"Design": design.id, "Chains": ", ".join(chain.chain_ids), "Sequence": chain.sequence}
            for design in get_cached_designs(selected_design_ids)
            for chain in design.spec.chains
        ]
    )
    if not sequences.empty:
        st.dataframe(sequences, hide_index=True, width="stretch")


def get_shared_alignment_options(options_by_design: dict[str, dict[str, AlignmentOption]]) -> list[str]:
    """Get the alignment options offered by every one of the given designs

    Designs of different workflows use different chains for the same option ("On target" is chain B for an
    RFdiffusion binder and chain A for a BindCraft one), so only the option labels are shared, not the chains.

    :param options_by_design: mapping of design ID to its alignment options
    :return: option labels available for all designs, in the order of the first design
    """
    if not options_by_design:
        return []
    first_options, *other_options = options_by_design.values()
    return [label for label in first_options if all(label in options for options in other_options)]


def get_selected_alignments(
    structure_design_ids: list[str], options_by_design: dict[str, dict[str, AlignmentOption]], alignment: str
) -> list[AlignmentOption]:
    """Get the alignment to use for each structure, based on the design the structure belongs to

    The same option label uses different chains for each design, so every structure is aligned using the
    option of its own design.

    :param structure_design_ids: design ID of each structure to align, in the order of the structures
    :param options_by_design: mapping of design ID to its alignment options
    :param alignment: label of the selected option
    """
    return [options_by_design[design_id][alignment] for design_id in structure_design_ids]


def create_color_legend(structures, designs_by_id):
    unique_design_ids = list(designs_by_id)
    cmap = Colormap("seaborn:tab10_light")
    color_index = 0

    with st.container(key="structure_legend"):
        legend_columns = wrapped_columns(len(unique_design_ids), wrap=2)
        legend_containers = [col.container(gap=3) for col in legend_columns]
        st.html(
            """
            <style>
            .st-key-structure_legend .stColorPicker,
            .st-key-structure_legend .stColorPicker button,
            .st-key-structure_legend .stColorPicker div[data-testid="stColorPickerBlock"] {
              min-width: 1rem;
              width: 1rem;
              height: 1rem;
            }
            .st-key-structure_legend .stColorPicker div[data-testid="stColorPickerBlock"] {
              border-radius: 3px;
            }
            </style>
            """
        )

    default_structures = [structure for structure in structures if structure[1] == DESIGN_STRUCTURE_OPTION]
    default_structures_by_design = {design_id: path for design_id, label, path in default_structures}

    def get_chain_color(design_id, label, path, chain):
        nonlocal color_index, legend_containers, default_structures_by_design
        designed_chain_ids = designs_by_id[design_id].get_designed_chain_ids()
        if chain in designed_chain_ids:
            caption = f"{design_id} | {label}"
            if len(designed_chain_ids) > 1:
                caption += f" | chain {chain}"
            if label != DESIGN_STRUCTURE_OPTION and path == default_structures_by_design.get(design_id):
                caption += f" (same as {DESIGN_STRUCTURE_OPTION})"
            # the colormap clamps above its last color, so we cycle through it instead
            color = cmap(color_index % cmap.num_colors).hex.lower()
            color_index += 1
            with legend_containers[unique_design_ids.index(design_id)]:
                with st.container(horizontal=True, horizontal_alignment="left", vertical_alignment="center", gap=10):
                    color = st.color_picker(
                        label=f"color{color_index}",
                        key=f"color_{color_index}",
                        value=color,
                        label_visibility="collapsed",
                    )
                    st.caption(caption, width="content")

            return color
        else:
            return TARGET_CHAIN_COLOR

    return get_chain_color


def align_structures_component(structures: list[tuple[str, str, str]], key: str, height="500px"):
    """Superpose the given structures in a single viewer, colored by design

    :param structures: list of (design ID, structure label, storage path) to superpose
    """
    with storage.bulk_read_context():
        pdb_strs = [storage.read_file_str(path) for _, _, path in structures]

    chains_per_structure = [sorted(get_sequences_from_pdb_str(pdb_str)) for pdb_str in pdb_strs]
    structure_design_ids = [design_id for design_id, _, _ in structures]
    designs_by_id = {design.id: design for design in get_cached_designs(sorted(set(structure_design_ids)))}
    workflow_types = get_cached_workflow_types_by_design(list(designs_by_id))
    # a design is aligned on its own chains, they can differ between workflows (RFdiffusion A, BindCraft B),
    # and only chains present in all of its selected structures can be used, a prediction may omit the target
    options_by_design = {
        design_id: workflow_types[design_id].get_alignment_options(
            design,
            sorted(
                set.intersection(
                    *[set(chains) for chains, i in zip(chains_per_structure, structure_design_ids) if i == design_id]
                )
            ),
        )
        for design_id, design in designs_by_id.items()
    }

    shared_options = get_shared_alignment_options(options_by_design)
    if not shared_options:
        st.warning(
            "The selected structures have no alignment option in common, they cannot be aligned. "
            "Select fewer structure types or designs with the same chains."
        )
        return

    left, middle, right = st.columns([3, 3, 4], vertical_alignment="bottom")

    with left:
        alignment = st.segmented_control(
            "Align",
            options=shared_options,
            default=shared_options[0],
            key=f"{key}_alignment",
        )
        if not alignment:
            st.info("Select how the structures should be aligned.")
            return
        selected_alignments = get_selected_alignments(structure_design_ids, options_by_design, alignment)

    with middle:
        # every option comes with the representation that shows what it aligns on ("On motif" shows side
        # chains), and a widget only honors index= when it is first created, so the default is part of the
        # key - switching the alignment then creates a new selectbox that starts at its representation
        default_representation = selected_alignments[0].representation if selected_alignments else None
        representation_type = representation_type_selectbox(
            representation_type=default_representation,
            key=f"{key}_representation_{default_representation}",
        )

    with right:
        color = representation_color_selectbox(key=f"{key}_color")

    # TODO when we have the Structure object, we could use it for alignment here.
    # It could return multiple RMSD values - target RMSD, target-aligned binder RMSD, ...
    aligned_pdb_strs, rmsd = align_multiple_proteins_pdb(
        pdb_strs=pdb_strs,
        chain_residue_mappings=[option.chain_residue_mapping for option in selected_alignments],
        all_atom=any(option.all_atom for option in selected_alignments),
    )

    get_chain_color = create_color_legend(structures, designs_by_id)

    viz.molstar(
        *[
            viz.StructureVisualization(
                data=aligned_pdb_str,
                representations=[
                    viz.Representation(
                        chain,
                        representation_type=representation_type,
                        color=get_chain_color(design_id, label, path, chain) if color == "chain-id" else color,
                        label=f"{design_id} | {label} | chain {chain}",
                    )
                    for chain in chains
                ],
            )
            for (design_id, label, path), aligned_pdb_str, chains, option in zip(
                structures, aligned_pdb_strs, chains_per_structure, selected_alignments
            )
        ],
        key=key,
        height=height,
    )

    if len(structures) > 1:
        metric = "average RMSD" if len(structures) > 2 else "RMSD"
        atom_description = (
            "all shared atom positions"
            if any(option.all_atom for option in selected_alignments)
            else "Cα atom positions"
        )
        st.text(
            f"The {metric} for the aligned structure complexes is {round(rmsd, 3)}",
            help=f"The root mean square deviation (RMSD) of {atom_description} after optimal rotational and "
            "translational superposition relative to the first structure shown.",
        )


def rfdiffusion_binder_design_visualization(design_id: str):
    design: Design = get_cached_design(design_id)
    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id)
    workflow: RFdiffusionBinderDesignWorkflow = design_job.workflow
    paths = (
        get_cached_design_descriptors(
            design_id,
            [
                *[d.key for d in descriptors.STRUCTURE_PATH_DESCRIPTORS],
            ],
        )
        .dropna()
        .to_dict()
    )
    input_pdb_path = workflow.get_input_pdb_path(design.contig_index)

    st.write(f"**Input structure:** {os.path.basename(input_pdb_path)}")

    show_design_metrics(
        design_id,
        descriptor_keys=[
            descriptors_proteinqc.LENGTH.key,
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key,
            descriptors_rfdiffusion.PYDSSP_HELIX_PERCENT.key,
            descriptors_rfdiffusion.PYDSSP_SHEET_PERCENT.key,
            descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS.key,
            descriptors_rfdiffusion.PYROSETTA_DDG.key,
            descriptors_rfdiffusion.PYROSETTA_CMS.key,
            descriptors_rfdiffusion.PYROSETTA_SAP_SCORE.key,
        ],
        thresholds=workflow.acceptance_thresholds,
    )

    # TODO use target spec for this
    # Note this assumes that the target chain is B in the RFdiffusion output PDB,
    # and that the residue numbers are same as in the input PDB
    hotspot_selections = (
        [h.replace(workflow.target_chain, "B") for h in workflow.rfdiffusion_params.hotspots.split(",")]
        if workflow.rfdiffusion_params.hotspots and workflow.target_chain
        else None
    )

    left, middle, right = st.columns(3, gap="medium")

    backbone_design_descriptor = None
    for d in BACKBONE_DESIGN_PATH_DESCRIPTORS:
        if paths.get(d.key):
            backbone_design_descriptor = d

    with left:
        st.write(f"##### {backbone_design_descriptor.name}")

        binder_representation = "cartoon"
        if "RFdiffusion3" in backbone_design_descriptor.tool:
            binder_representation = "cartoon+ball-and-stick"

        viz.molstar(
            viz.StructureVisualization(
                data=storage.read_file_str(paths[backbone_design_descriptor.key]),
                selection=hotspot_selections,
                representations=[
                    viz.Representation(
                        "A",
                        binder_representation,
                        color=get_color_from_str(design.id, "seaborn:tab10_light"),
                        label=f"{backbone_design_descriptor.name} {design.id}",
                    ),
                    viz.Representation("B", "cartoon", label=f"{design.id} target"),
                ],
            ),
            key="backbone_design",
            height=350,
        )

        st.write(backbone_design_descriptor.description)

    if design.structure_descriptor_key in paths:
        sequence_design_descriptor = ALL_DESCRIPTORS_BY_KEY.get(design.structure_descriptor_key)
    else:
        # use first available sequence design descriptor (if any) if not specified in the design
        sequence_design_descriptor = None
        for d in SEQUENCE_DESIGN_PATH_DESCRIPTORS:
            if paths.get(d.key):
                sequence_design_descriptor = d
                break

    sequence_design_pdb_data = align_pdb_to_front(storage.read_file_str(paths[sequence_design_descriptor.key]), "A")

    with middle:
        st.write(f"##### {sequence_design_descriptor.name}")

        viz.molstar(
            viz.StructureVisualization(
                data=sequence_design_pdb_data,
                selection=hotspot_selections,
                representations=[
                    viz.Representation(
                        "A",
                        "cartoon+ball-and-stick",
                        color=get_color_from_str(design.id, "seaborn:tab10_light"),
                        label=f"{sequence_design_descriptor.name} {design.id}",
                    ),
                    viz.Representation("B", "cartoon+ball-and-stick", label=f"{design.id} target"),
                ],
                auto_zoom_chains=["A"],
            ),
            key="sequence_design_1",
            height=350,
        )

        st.write(sequence_design_descriptor.description)

    with right:
        st.write("##### Designed binding pose")

        viz.molstar(
            viz.StructureVisualization(
                data=sequence_design_pdb_data,
                selection=hotspot_selections,
                representations=[
                    viz.Representation(
                        "A",
                        "cartoon+ball-and-stick",
                        color=get_color_from_str(design.id, "seaborn:tab10_light"),
                        label=f"{sequence_design_descriptor.name} {design.id}",
                    ),
                    viz.Representation("B", "molecular-surface", color="hydrophobicity", label=f"{design.id} target"),
                ],
                auto_zoom_chains=["A"],
            ),
            key="sequence_design_2",
            height=350,
        )

        st.write(
            f"{sequence_design_descriptor.name} against target surface colored by hydrophobicity scale :green-badge[**green** = hydroPHOBIC] :red-badge[**red** = hydroPHILIC]"
        )

    st.write("### Refolding tests")

    prediction_descriptor = select_structure_prediction_descriptor(paths)

    if not prediction_descriptor:
        return

    is_binder_alone = (
        "binderalone" in prediction_descriptor.key.lower() or "binder_alone" in prediction_descriptor.key.lower()
    )

    left, middle, right = st.columns(3, gap="medium")

    if is_binder_alone:
        middle, right = left, middle

    with left:
        if not is_binder_alone:
            st.write("##### Input structure aligned to prediction")

            input_pdb_str = storage.read_file_str(input_pdb_path)
            prediction_str = storage.read_file_str(paths[prediction_descriptor.key])

            # here, manual alignment is needed
            structures, rmsd = align_multiple_proteins_pdb(
                pdb_strs=[input_pdb_str, prediction_str], chain_residue_mappings=[None, [("B", None)]]
            )
            aligned_str = structures[1]
            if prediction_descriptor.b_factor_value == "plddt":
                aligned_str = pdb_to_mmcif(aligned_str, "-", True)
            elif prediction_descriptor.b_factor_value == "fractional_plddt":
                aligned_str = pdb_to_mmcif(aligned_str, "-", True, fractional_plddt=True)

            viz.molstar(
                viz.StructureVisualization(
                    data=structures[0],
                    representation="cartoon",
                    color="chain-id",
                    selection=workflow.selected_segments,
                ),
                viz.StructureVisualization(
                    data=aligned_str,
                    representation=None,
                    representations=[
                        viz.Representation(
                            "A",
                            "cartoon+ball-and-stick",
                            color="plddt",
                            label=prediction_descriptor.name,
                        ),
                        viz.Representation(
                            "B",
                            "cartoon",
                            label="Prediction of target chain aligned to input target chain",
                        ),
                    ],
                ),
                key="full_input_aligned_to_prediction",
                height=350,
            )

            st.write(
                f"All chains from input structure aligned to {prediction_descriptor.name} of binder chain (ball and stick colored by pLDDT confidence) and target chain (white)."
            )

    with middle:
        st.write("##### Design aligned to prediction")

        if is_binder_alone:
            structures, _ = align_multiple_proteins_pdb(
                pdb_strs=[
                    filter_pdb_str(storage.read_file_str(paths[sequence_design_descriptor.key]), "A"),
                    filter_pdb_str(storage.read_file_str(paths[prediction_descriptor.key]), "A"),
                ],
                chain_residue_mappings=[[("A", None)] for _ in range(2)],
                all_atom=True,
            )
        else:
            structures, _ = align_multiple_proteins_pdb(
                pdb_strs=[
                    storage.read_file_str(paths[sequence_design_descriptor.key]),
                    storage.read_file_str(paths[prediction_descriptor.key]),
                ],
                chain_residue_mappings=[[("B", None)] for _ in range(2)],
            )

        aligned_str = structures[1]
        if prediction_descriptor.b_factor_value == "plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True)

        viz.molstar(
            viz.StructureVisualization(
                data=structures[0],
                representation=None,
                representations=[
                    viz.Representation(
                        "A",
                        "cartoon+ball-and-stick",
                        color=get_color_from_str(design.id, "seaborn:tab10_light"),
                        label=sequence_design_descriptor.name,
                    ),
                    viz.Representation("B", "cartoon", label="MPNN target"),
                ],
            ),
            viz.StructureVisualization(
                data=aligned_str,
                representation=None,
                representations=[
                    viz.Representation(
                        "A",
                        "cartoon+ball-and-stick",
                        color="plddt",
                        label=prediction_descriptor.name,
                    ),
                    viz.Representation("B", "cartoon", label="Target chain"),
                ],
            ),
            key="design_aligned_to_af2_2",
            height=350,
        )

        st.write(
            f"""
            Agreement between {sequence_design_descriptor.name} and {prediction_descriptor.name}
            """
        )
        if prediction_descriptor == descriptors_refolding.BOLTZ_PRIMARY_STRUCTURE_PATH:
            rmsd_descriptor = descriptors_refolding.BOLTZ_PRIMARY_TARGET_ALIGNED_BINDER_RMSD
        elif prediction_descriptor == descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH:
            rmsd_descriptor = descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD
        else:
            rmsd_descriptor = None
            rmsd_suffix = "binder_alone_aa_rmsd" if is_binder_alone else "target_aligned_binder_rmsd"
            key = f"{prediction_descriptor.key.rsplit('|', 1)[0]}|{rmsd_suffix}"
            rmsd_descriptor = ALL_DESCRIPTORS_BY_KEY.get(key)

        if rmsd_descriptor:
            rmsd_value = get_cached_design_descriptors(design_id, [rmsd_descriptor.key])[rmsd_descriptor.key]
            if not pd.isna(rmsd_value):
                st.write(f"{rmsd_descriptor.name}: **{rmsd_value:.2f} Å**")

    with right:
        st.write("##### Predicted binding pose")

        pdb_str = storage.read_file_str(paths[prediction_descriptor.key])
        if prediction_descriptor.b_factor_value == "plddt":
            pdb_str = pdb_to_mmcif(pdb_str, "-", True)

        viz.molstar(
            viz.StructureVisualization(
                data=pdb_str,
                representation=None,
                representations=[
                    viz.Representation(
                        "A", "cartoon+ball-and-stick", color="plddt", label="Prediction of binder chain"
                    ),
                    viz.Representation(
                        "B", "molecular-surface", color="hydrophobicity", label="Prediction of target chain"
                    ),
                ],
            ),
            key="binding_pose_predicted",
            height=350,
        )

        st.write(
            "Prediction of binder (ball and stick colored by pLDDT confidence) "
            + (
                "and target (surface colored by hydrophobicity scale) :green-badge[**green** = hydroPHOBIC] :red-badge[**red** = hydroPHILIC]"
                if not is_binder_alone
                else ""
            )
        )


def bindcraft_binder_design_visualization(design_id: str):
    design = get_cached_design(design_id)

    show_design_metrics(
        design_id,
        descriptor_keys=[
            "bindcraft|sequence|Length",
            "bindcraft|dssp|Average_Binder_Helix%",
            "bindcraft|dssp|Average_Binder_BetaSheet%",
            "bindcraft|dssp|Average_Binder_Loop%",
            "bindcraft|af2|Average_pLDDT",
            "bindcraft|af2|Average_i_pAE",
            "bindcraft|af2|Average_Hotspot_RMSD",
            "bindcraft|interface|Average_InterfaceUnsatHbondsPercentage",
            "bindcraft|interface|Average_dG",
            "bindcraft|interface|Average_Relaxed_Clashes",
            "bindcraft|interface|Average_n_InterfaceResidues",
            "bindcraft|interface|Average_n_InterfaceHbonds",
        ],
    )

    viz.molstar(
        viz.StructureVisualization(
            data=storage.read_file_str(design.structure_path),
            color="plddt",
        ),
        key="bindcraft_1",
    )


def disco_design_visualization(design_id: str):
    design: Design = get_cached_design(design_id)
    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id)
    workflow = design_job.workflow

    show_design_metrics(
        design_id,
        descriptor_keys=[
            descriptors_disco.SEQUENCE_LENGTH.key,
            descriptors_disco.LIGANDMPNN_OVERALL_CONFIDENCE.key,
            descriptors_disco.LIGANDMPNN_LIGAND_CONFIDENCE.key,
        ],
        thresholds=workflow.acceptance_thresholds,
    )

    paths: dict = (
        get_cached_design_descriptors(
            design_id,
            [d.key for d in descriptors.STRUCTURE_PATH_DESCRIPTORS],
        )
        .dropna()
        .to_dict()
    )

    # DISCO packed design (side chains packed by LigandMPNN, includes the ligand)
    packed_descriptor = descriptors_disco.DISCO_PACKED_STRUCTURE_PATH
    packed_path = paths.get(packed_descriptor.key) or design.structure_path

    left, right = st.columns(2, gap="medium")

    with left:
        st.write(f"##### {packed_descriptor.name}")
        viz.molstar(
            viz.StructureVisualization(
                data=storage.read_file_str(packed_path),
                color="chain-id",
                representation="cartoon+ball-and-stick",
            ),
            key="disco_packed",
            height=350,
        )
        st.write(packed_descriptor.description)

    backbone_descriptor = descriptors_disco.DISCO_BACKBONE_STRUCTURE_PATH
    backbone_path = paths.get(backbone_descriptor.key)
    with right:
        if backbone_path:
            st.write(f"##### {backbone_descriptor.name}")
            viz.molstar(
                viz.StructureVisualization(
                    data=storage.read_file_str(backbone_path),
                    color="chain-id",
                ),
                key="disco_backbone",
                height=350,
            )
            st.write(backbone_descriptor.description)

    st.write("### Refolding tests")

    prediction_descriptor = select_structure_prediction_descriptor(paths)
    if not prediction_descriptor:
        return

    # Only Boltz performs ligand-aware refolding; warn when a ligand-conditioned design was refolded
    # with a test that ignores the ligand (e.g. AlphaFold2 or ESMFold).
    is_ligand_aware = prediction_descriptor.key.split("|")[1].startswith("boltz")
    if workflow.disco_params.ligand and not is_ligand_aware:
        st.warning(
            f"{prediction_descriptor.name} does not support ligand-aware refolding — this prediction was "
            f"performed **without the ligand molecule** (protein only). Use a Boltz refolding test for "
            f"ligand-aware structure prediction."
        )

    prediction_storage_path = paths[prediction_descriptor.key]
    prediction_pdb = storage.read_file_str(prediction_storage_path)

    left, right = st.columns(2, gap="medium")

    with left:
        st.write(f"##### {prediction_descriptor.name}")
        description = prediction_descriptor.description
        if prediction_descriptor.b_factor_value == "plddt":
            pred_str = pdb_to_mmcif(prediction_pdb, "-", True)
            description += " (colored by pLDDT confidence)"
        elif prediction_descriptor.b_factor_value == "fractional_plddt":
            pred_str = pdb_to_mmcif(prediction_pdb, "-", True, fractional_plddt=True)
            description += " (colored by pLDDT confidence)"
        else:
            pred_str = prediction_pdb

        viz.molstar(
            viz.StructureVisualization(
                data=pred_str,
                representation="cartoon",
                color="plddt",
            ),
            key=f"disco_pred_{prediction_descriptor.key}",
            height=350,
        )
        st.write(description)

    with right:
        st.write("##### Design aligned to prediction")

        # Align on all chains (the design and its prediction share the same sequence)
        chain_mapping = [(chain_id, None) for c in design.spec.chains for chain_id in c.chain_ids]
        aligned_pdb_strs, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[storage.read_file_str(packed_path), prediction_pdb],
            chain_residue_mappings=[chain_mapping, chain_mapping],
            all_atom=False,
        )
        aligned_prediction = aligned_pdb_strs[1]
        if prediction_descriptor.b_factor_value == "plddt":
            aligned_prediction = pdb_to_mmcif(aligned_prediction, "-", True)
        elif prediction_descriptor.b_factor_value == "fractional_plddt":
            aligned_prediction = pdb_to_mmcif(aligned_prediction, "-", True, fractional_plddt=True)

        viz.molstar(
            viz.StructureVisualization(data=aligned_pdb_strs[0], representation="cartoon+ball-and-stick"),
            viz.StructureVisualization(data=aligned_prediction, representation="cartoon", color="plddt"),
            key=f"disco_design_aligned_to_{prediction_descriptor.key}",
            height=350,
            html_filename=os.path.basename(prediction_storage_path).replace(".pdb", "_aligned_design"),
        )
        st.write(
            f"""
            {prediction_descriptor.name} vs design backbone RMSD: **{rmsd:.2f} Å**

            DISCO packed design (ball and stick) aligned to the {prediction_descriptor.name} prediction
            (cartoon colored by pLDDT confidence).
            """
        )


def visualize_design_structure(design_id: str, height="500px"):
    design = get_cached_design(design_id)
    if not design.structure_path:
        st.write("No structure available for this design.")
        return

    viz.molstar(
        viz.StructureVisualization(
            data=storage.read_file_str(design.structure_path),
            color="chain-id",
            representation="cartoon+ball-and-stick",
        ),
        key="default_structure",
        height=height,
    )


def visualize_design_sequence(design_id: str):
    design = get_cached_design(design_id)

    sequence_fasta = "\n".join(
        f">{design_id} {chain.type}|{','.join(chain.chain_ids)}\n{chain.sequence}" for chain in design.spec.chains
    )
    st.code(sequence_fasta, wrap_lines=True)


def visualize_rfdiffusion_design_sequence(design_id: str):
    # visualize regular sequence
    visualize_design_sequence(design_id)

    # visualize alignment
    st.write("##### Alignment of input sequence to designed sequence")

    design: Design = get_cached_design(design_id)
    pool = get_cached_pool(design.pool_id)
    workflow: RFdiffusionWorkflow = get_cached_design_job(pool.design_job_id).workflow

    input_pdb_path = workflow.get_input_pdb_path(design.contig_index)
    input_seq_by_resno: dict[str, dict[str, str]] = get_sequences_from_pdb_str(
        storage.read_file_str(input_pdb_path), by_residue_number=True
    )
    designed_sequences: dict[str, str] = {
        chain_id: chain.sequence for chain in design.spec.chains for chain_id in chain.chain_ids
    }

    if not all(c.contig for c in design.spec.chains):
        st.warning("Contig not found in design spec")
        return
    contig = " ".join(c.contig for c in design.spec.chains if c.contig)

    # individual positions in this format ['A1', 'A2', ...]
    inpainted_positions = (
        from_segments_to_hotspots(workflow.rfdiffusion_params.inpaint_seq.split("/"))
        if workflow.rfdiffusion_params.inpaint_seq
        else []
    )
    visualize_scaffold_alignment(
        input_seq_by_resno=input_seq_by_resno,
        designed_sequences=designed_sequences,
        parsed_segments=parse_contig_for_output_structure(contig),
        inpainted_positions=inpainted_positions,
    )


def visualize_scaffold_alignment(
    input_seq_by_resno: dict[str, dict[str, str]],
    designed_sequences: dict[str, str],
    parsed_segments: list[MappedContigSegment],
    inpainted_positions: list[str],
):
    """Visualize alignment between input and designed sequences based on contig segments.

    :param input_seq_by_resno: Mapping from chain ID -> residue number (as string) -> amino acid.
    :param designed_sequences: Mapping from chain ID -> designed sequence.
    :param parsed_segments: List of MappedContigSegment objects representing the contig segments.
    :param inpainted_positions: List of positions (e.g., 'A12') that were inpainted.
    """
    html = [
        '<div style="font-family: monospace; font-size: 14px; margin: 10px 2px; display: inline-block;">'
        "&nbsp;&nbsp;&nbsp;&nbsp;Region<br />"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Input<br />"
        "&nbsp;&nbsp;&nbsp;&nbsp;Design<br />"
        "</div>"
    ]
    aligned_input = []
    aligned_design = []
    for s in parsed_segments:
        segment_length = s.end - s.start + 1
        for chunk_offset in range(0, segment_length, 10):
            chunk_length = min(segment_length - chunk_offset, 10)
            output_start = chunk_offset + s.start
            # TODO s.out_res_chain might not be correct when multiple chains are designed
            generated_seq = designed_sequences[s.chain][output_start - 1 : output_start + chunk_length - 1]
            if s.input_chain is None:
                label = s.middle_label if chunk_offset == 0 else " "
                input_seq = " " * chunk_length
                input_seq_formatted = "Generated&nbsp;" if chunk_offset == 0 else "&nbsp;" * 10
                generated_seq_formatted = generated_seq
                fmt = f"background-color: {s.color}"
            else:
                input_start = chunk_offset + s.input_start
                label = f"{s.input_chain}{input_start}-{input_start + chunk_length - 1}"
                input_positions = list(range(input_start, input_start + chunk_length))
                input_seq = "".join([input_seq_by_resno[s.input_chain].get(str(pos), "?") for pos in input_positions])
                input_seq_formatted = "".join(
                    [
                        f"<b>{aa}</b>" if f"{s.input_chain}{pos}" in inpainted_positions else aa
                        for pos, aa in zip(input_positions, input_seq)
                    ]
                )
                fmt = f"color: {s.color}"
                generated_seq_formatted = "".join(
                    [f"<b>{aa}</b>" if aa != bb else aa for aa, bb in zip(generated_seq, input_seq)]
                )
            aligned_input.extend(list(input_seq))
            aligned_design.extend(list(generated_seq))
            html.append(
                f'<div style="font-family: monospace; font-size: 14px; margin: 10px 2px; display: inline-block;">'
                f'<span style="display: inline-block; border-radius: 2px; padding: 1px 2px; {fmt}">{label.ljust(10).replace(" ", "&nbsp;")}</span><br />'
                f'<span style="color: #bbbbbb;">{input_seq_formatted}</span><br />'
                f"{generated_seq_formatted}<br />"
                f"</div>"
            )

    st.html("\n".join(html))

    if inpainted_positions:
        st.write("Sequence-inpainted positions shown in **bold**.")

    contig_identity = (
        sum(aa == bb for aa, bb in zip(aligned_input, aligned_design)) / len(aligned_design) if aligned_design else None
    )
    st.write(
        "Identity: **{:.2%}** :grey[:material/info: Not considering potential matches within generated structure regions]".format(
            contig_identity
        )
    )


def visualize_align_structure_selection(
    design_ids: list[str],
    align_chains: list[str],
    visualize_chains: list[str],
    max_examples: int = 15,
    default_representation_type=None,
    color="secondary-structure",
    auto_zoom_chains=None,
    key="struct_visualization",
    chains_by_design_id: dict[str, list[str]] = None,
):
    """Align and visualize the structures of the given designs.

    :param chains_by_design_id: optional - use different chains for each design, overriding align_chains,
        visualize_chains and auto_zoom_chains. Needed when designs have differently labelled designed chains.
    """
    # If list of designs too large, align only subset (max_examples) of designs
    max_examples = min(max_examples, len(design_ids))
    example_designs: list[Design] = get_cached_designs(design_ids[:max_examples])

    if chains_by_design_id is not None:
        design_align_chains = [chains_by_design_id[design.id] for design in example_designs]
        design_visualize_chains = design_align_chains
        design_auto_zoom_chains = design_align_chains
    else:
        design_align_chains = [align_chains] * len(example_designs)
        design_visualize_chains = [visualize_chains] * len(example_designs)
        design_auto_zoom_chains = [auto_zoom_chains] * len(example_designs)

    with storage.bulk_read_context():
        aligned_subset_pdb_strs, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[storage.read_file_str(design.structure_path) for design in example_designs],
            # Align atoms of provided chains
            chain_residue_mappings=[[(chain, None) for chain in chains] for chains in design_align_chains],
        )

    viz.molstar(
        *[
            viz.StructureVisualization(
                data=aligned_pdb_str,
                representation_type=default_representation_type,
                representations=[viz.Representation(design_chains, "cartoon", color=color)],
                auto_zoom_chains=zoom_chains,
            )
            for aligned_pdb_str, design_chains, zoom_chains in zip(
                aligned_subset_pdb_strs, design_visualize_chains, design_auto_zoom_chains
            )
        ],
        key=key,
        height="400px",
    )

    if len(design_ids) > max_examples:
        st.warning(
            f"Showing only first {max_examples} out of {len(design_ids):,} selected designs for performance reasons."
        )
    if rmsd is not None:
        st.text(
            f"The RMSD for the aligned structures is {round(rmsd, 3)}",
            help="The root mean square deviation (RMSD) of Cα atom positions after optimal rotational and translational superposition relative to a reference structure for all members of the cluster.",
        )


def representation_type_selectbox(representation_type: str = None, key: str = "representation_type_input") -> str:
    representation_types = {
        "cartoon": "Cartoon",
        "cartoon+ball-and-stick": "Cartoon + Side chains",
        "cartoon+ball-and-stick+label": "Cartoon + Side chains + Label",
        "molecular-surface": "Molecular Surface",
    }
    return st.selectbox(
        "Representation type",
        options=list(representation_types.keys()),
        index=list(representation_types.keys()).index(representation_type)
        if representation_type in representation_types
        else 0,
        format_func=lambda x: representation_types[x],
        key=key,
        label_visibility="collapsed",
    )


def representation_color_selectbox(color: str = None, key: str = "color_scheme_input") -> str:
    colors = {
        "chain-id": "Color by chain",
        "hydrophobicity": "Color by hydrophobicity (green = hydrophobic, red = hydrophilic)",
        "residue-charge": "Color by residue charge (blue = positive, red = negative)",
        "plddt": "Color by pLDDT confidence",
    }
    return st.selectbox(
        "Color scheme",
        options=list(colors.keys()),
        index=list(colors.keys()).index(color) if color in colors else 0,
        format_func=lambda x: colors[x],
        key=key,
        label_visibility="collapsed",
    )
