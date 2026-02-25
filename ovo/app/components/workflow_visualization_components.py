import os

import pandas as pd
import streamlit as st

from ovo import db, storage
from ovo.app.components.custom_elements import wrapped_columns
from ovo.app.components.molstar_custom_component.dataclasses import ContigSegment
from ovo.core.database import (
    Design,
    descriptors,
    StructureFileDescriptor,
    descriptors_rfdiffusion,
    descriptors_refolding,
    descriptors_proteinqc,
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
)

from ovo.app.components.molstar_custom_component import (
    molstar_custom_component,
    StructureVisualization,
    ChainVisualization,
    ContigsParser,
)
from ovo.core.utils.pdb import align_multiple_proteins_pdb, pdb_to_mmcif, filter_pdb_str, get_sequences_from_pdb_str
from ovo.core.utils.colors import get_color_from_str
from ovo.app.utils.cached_db import (
    get_cached_design_descriptors,
    get_cached_design,
    get_cached_pool,
    get_cached_design_job,
    get_cached_designs,
)
from ovo.core.utils.residue_selection import from_segments_to_hotspots


def show_design_metrics(design_id: str, descriptor_keys: list[str]) -> pd.Series:
    descriptor_values = get_cached_design_descriptors(design_id, descriptor_keys=descriptor_keys)
    columns = wrapped_columns(len(descriptor_values), wrap=4)
    for column, (descriptor_key, value) in zip(columns, descriptor_values.items()):
        descriptor = ALL_DESCRIPTORS_BY_KEY[descriptor_key]
        column.metric(
            label=descriptor.name,
            help=descriptor.description,
            value=descriptor.format(value),
        )
    return descriptor_values


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
    return prediction_descriptor


def rfdiffusion_scaffold_design_visualization(design_id: str | None):
    design: Design = get_cached_design(design_id)

    chain_contigs = [c.contig + "/0" for c in design.spec.chains]
    st.write(f"Contig: **{' '.join(chain_contigs)}**")

    show_design_metrics(
        design_id,
        descriptor_keys=[
            descriptors_proteinqc.LENGTH.key,
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key,
            descriptors_rfdiffusion.PYDSSP_HELIX_PERCENT.key,
            descriptors_rfdiffusion.PYDSSP_SHEET_PERCENT.key,
            descriptors_refolding.AF2_PRIMARY_PAE.key,
            descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key,
            descriptors_refolding.AF2_PRIMARY_NATIVE_MOTIF_RMSD.key,
            descriptors_refolding.AF2_PRIMARY_PLDDT.key,
        ],
    )

    pool = get_cached_pool(design.pool_id)
    design_job = get_cached_design_job(pool.design_job_id)
    workflow: RFdiffusionScaffoldDesignWorkflow = design_job.workflow

    parser = ContigsParser()
    paths = (
        get_cached_design_descriptors(
            design_id,
            [
                descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key,
                *[d.key for d in descriptors.STRUCTURE_PATH_DESCRIPTORS],
            ],
        )
        .dropna()
        .to_dict()
    )
    trb_dict = storage.read_file_pickle(paths[descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key])
    input_pdb_str = storage.read_file_str(workflow.get_input_pdb_path(design.contig_index))
    input_segments = [segment for contig in trb_dict["sampled_mask"] for segment in parser.parse_contigs_str(contig)]
    output_segments = parser.parse_contigs_trb(trb_dict)

    input_mapping = [
        (segment.input_res_chain, list(range(segment.input_res_start, segment.input_res_end + 1)))
        for segment in input_segments
        if segment.type == "fixed"
    ]
    output_mapping = [
        (segment.out_res_chain, list(range(segment.out_res_start, segment.out_res_end + 1)))
        for segment in output_segments
        if segment.type == "fixed"
    ]

    left, middle, right = st.columns(3, gap="medium")

    with left:
        st.write("##### Full input structure")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=input_pdb_str, contigs=input_segments, representation_type="cartoon+ball-and-stick"
                ),
            ],
            key="full_input",
            height=350,
        )

    backbone_design_descriptor = descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH

    with middle:
        st.write(f"##### {backbone_design_descriptor.name}")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=storage.read_file_str(paths[backbone_design_descriptor.key]),
                    contigs=output_segments,
                )
            ],
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

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=storage.read_file_str(paths[sequence_design_descriptor.key]),
                    contigs=output_segments,
                    representation_type="cartoon+ball-and-stick",
                )
            ],
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

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_str,
                    representation_type="cartoon",
                    color="plddt",
                ),
            ],
            key=f"pred_{prediction_descriptor.key}",
            height=350,
        )
        st.write(description)

    with middle:
        st.write(f"##### Input motif aligned to prediction")

        input_motif_pdb = filter_pdb_str(input_pdb_str, [s.value for s in input_segments if s.type == "fixed"])
        structures = [
            StructureVisualization(
                pdb=input_motif_pdb, contigs=input_segments, representation_type="cartoon+ball-and-stick"
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
        num_fixed = sum(
            segment.out_res_end - segment.out_res_start + 1 for segment in output_segments if segment.type == "fixed"
        )

        structures.append(
            StructureVisualization(
                pdb=aligned_prediction_pdb,
                representation_type="cartoon+ball-and-stick",
            )
        )

        molstar_custom_component(
            structures=structures,
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
        st.write(f"##### Design aligned to prediction")

        structures, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[
                storage.read_file_str(paths[sequence_design_descriptor.key]),
                prediction_pdb,
            ],
            chain_residue_mappings=[[("A", None)], [("A", None)]],
            all_atom=False,
        )
        aligned_str = structures[1]

        if prediction_descriptor.b_factor_value == "plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True)
        elif prediction_descriptor.b_factor_value == "fractional_plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True, fractional_plddt=True)

        molstar_custom_component(
            structures=[
                StructureVisualization(pdb=structures[0], contigs=output_segments),
                StructureVisualization(
                    pdb=aligned_str,
                    representation_type="cartoon",
                    color="plddt",
                ),
            ],
            key=f"design_aligned_to_{prediction_descriptor.key}",
            height=350,
        )

        st.write(
            f"""
            {prediction_descriptor.name} vs design backbone RMSD: **{rmsd:.2f} Å**
            
            Agreement between {sequence_design_descriptor.name} and {prediction_descriptor.name}
            """
        )


def rfdiffusion_multiple_binder_designs_visualization(all_design_ids: list[str], max_examples: int = 20):
    if len(all_design_ids) > max_examples:
        st.warning(
            f"Showing only first {max_examples} out of {len(all_design_ids):,} selected designs for performance reasons."
        )

    example_design_ids = all_design_ids[:max_examples]
    example_designs: list[Design] = get_cached_designs(example_design_ids)
    # TODO add caching
    backbone_paths = (
        db.select_descriptor_values(descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key, example_design_ids)
        .dropna()
        .to_dict()
    )
    left, right = st.columns(2, gap="medium")

    with left:
        st.write("##### RFdiffusion backbone designs")
        aligned_pdb_strs, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[storage.read_file_str(backbone_paths[design.id]) for design in example_designs],
            chain_residue_mappings=[[("B", None)] for _ in example_designs],
        )

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=aligned_pdb_str,
                    representation_type=None,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": get_color_from_str(design.id, "seaborn:tab10_light")},
                            representation_type="cartoon",
                            label=f"RFdiffusion {design.id} binder backbone",
                        ),
                        ChainVisualization(
                            chain_id="B", representation_type="cartoon", label=f"RFdiffusion {design.id} target"
                        ),
                    ],
                )
                for design, aligned_pdb_str in zip(example_designs, aligned_pdb_strs)
            ],
            key="rfdiff_backbone",
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
                descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key,
                *[d.key for d in descriptors.STRUCTURE_PATH_DESCRIPTORS],
            ],
        )
        .dropna()
        .to_dict()
    )
    input_pdb_path = workflow.get_input_pdb_path(design.contig_index)

    st.write(f"Input structure: **{os.path.basename(input_pdb_path)}**")

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
            descriptors_refolding.AF2_PRIMARY_IPAE.key,
            descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.key,
            descriptors_refolding.AF2_PRIMARY_PLDDT.key,
        ],
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

    backbone_design_descriptor = descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH
    with left:
        st.write(f"##### {backbone_design_descriptor.name}")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=storage.read_file_str(paths[backbone_design_descriptor.key]),
                    highlighted_selections=hotspot_selections,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": get_color_from_str(design.id, "seaborn:tab10_light")},
                            representation_type="cartoon",
                            label=f"{backbone_design_descriptor.name} {design.id}",
                        ),
                        ChainVisualization(chain_id="B", representation_type="cartoon", label=f"{design.id} target"),
                    ],
                )
            ],
            key="backbone_design",
            height=350,
        )

        st.write(backbone_design_descriptor.description)

    sequence_design_descriptor = None
    for d in SEQUENCE_DESIGN_PATH_DESCRIPTORS:
        if paths.get(d.key):
            sequence_design_descriptor = d

    with middle:
        st.write(f"##### {sequence_design_descriptor.name}")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=storage.read_file_str(paths[sequence_design_descriptor.key]),
                    highlighted_selections=hotspot_selections,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": get_color_from_str(design.id, "seaborn:tab10_light")},
                            representation_type="cartoon+ball-and-stick",
                            label=f"{sequence_design_descriptor.name} {design.id}",
                        ),
                        ChainVisualization(
                            chain_id="B", representation_type="cartoon+ball-and-stick", label=f"{design.id} target"
                        ),
                    ],
                )
            ],
            key="sequence_design_1",
            height=350,
        )

        st.write(sequence_design_descriptor.description)

    with right:
        st.write("##### Designed binding pose")

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=storage.read_file_str(paths[sequence_design_descriptor.key]),
                    highlighted_selections=hotspot_selections,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": get_color_from_str(design.id, "seaborn:tab10_light")},
                            representation_type="cartoon+ball-and-stick",
                            label=f"{sequence_design_descriptor.name} {design.id}",
                        ),
                        ChainVisualization(
                            chain_id="B",
                            representation_type="molecular-surface",
                            color="hydrophobicity",
                            label=f"{design.id} target",
                        ),
                    ],
                )
            ],
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

    left, middle, right = st.columns(3, gap="medium")
    with left:
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

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=structures[0],
                    representation_type="cartoon",
                    color="chain-id",
                    highlighted_selections=workflow.selected_segments,
                ),
                StructureVisualization(
                    pdb=aligned_str,
                    representation_type=None,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            representation_type="cartoon+ball-and-stick",
                            color="plddt",
                            label=prediction_descriptor.name,
                        ),
                        ChainVisualization(
                            chain_id="B",
                            representation_type="cartoon",
                            label="Prediction of target chain aligned to input target chain",
                        ),
                    ],
                ),
            ],
            key="full_input_aligned_to_prediction",
            height=350,
        )

        st.write(
            f"All chains from input structure aligned to {prediction_descriptor.name} of binder chain (ball and stick colored by pLDDT confidence) and target chain (white)."
        )

    with middle:
        st.write("##### Design aligned to prediction")

        # here, we do not need manual alignment, but we still do it
        structures, rmsd = align_multiple_proteins_pdb(
            pdb_strs=[
                storage.read_file_str(paths[sequence_design_descriptor.key]),
                storage.read_file_str(paths[prediction_descriptor.key]),
            ],
            chain_residue_mappings=[[("B", None)] for _ in range(2)],
        )

        aligned_str = structures[1]
        if prediction_descriptor.b_factor_value == "plddt":
            aligned_str = pdb_to_mmcif(aligned_str, "-", True)

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=structures[0],
                    representation_type=None,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            color_params={"value": get_color_from_str(design.id, "seaborn:tab10_light")},
                            representation_type="cartoon+ball-and-stick",
                            label=sequence_design_descriptor.name,
                        ),
                        ChainVisualization(chain_id="B", representation_type="cartoon", label="MPNN target"),
                    ],
                ),
                StructureVisualization(
                    pdb=aligned_str,
                    representation_type=None,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            representation_type="cartoon+ball-and-stick",
                            color="plddt",
                            label=prediction_descriptor.name,
                        ),
                        ChainVisualization(chain_id="B", representation_type="cartoon", label="Target chain"),
                    ],
                ),
            ],
            key="design_aligned_to_af2_2",
            height=350,
        )

        st.write(
            f"""
            {prediction_descriptor.name} vs design backbone RMSD: **{rmsd:.2f} Å**
            
            Agreement between {sequence_design_descriptor.name} and {prediction_descriptor.name}
            """
        )

    with right:
        st.write("##### Predicted binding pose")

        pdb_str = storage.read_file_str(paths[prediction_descriptor.key])
        if prediction_descriptor.b_factor_value == "plddt":
            pdb_str = pdb_to_mmcif(pdb_str, "-", True)

        molstar_custom_component(
            structures=[
                StructureVisualization(
                    pdb=pdb_str,
                    representation_type=None,
                    chains=[
                        ChainVisualization(
                            chain_id="A",
                            representation_type="ball-and-stick",
                            color="plddt",
                            label="Prediction of binder chain",
                        ),
                        ChainVisualization(
                            chain_id="B",
                            color="hydrophobicity",
                            representation_type="molecular-surface",
                            label="Prediction of target chain",
                        ),
                    ],
                ),
            ],
            key="binding_pose_predicted",
            height=350,
        )

        st.write(
            "Prediction of binder (ball and stick colored by pLDDT confidence) and target (surface colored by hydrophobicity scale) :green-badge[**green** = hydroPHOBIC] :red-badge[**red** = hydroPHILIC]"
        )


def bindcraft_binder_design_visualization(design_id: str):
    design = get_cached_design(design_id)

    show_design_metrics(
        design_id,
        descriptor_keys=[
            "bindcraft|af2|Average_pLDDT",
            "bindcraft|af2|Average_i_pAE",
            "bindcraft|af2|Average_Hotspot_RMSD",
            "bindcraft|interface|Average_dG",
            "bindcraft|interface|Average_Relaxed_Clashes",
            "bindcraft|interface|Average_n_InterfaceResidues",
            "bindcraft|dssp|Average_Binder_Helix%",
            "bindcraft|dssp|Average_Binder_BetaSheet%",
        ],
    )

    molstar_custom_component(
        structures=[StructureVisualization(pdb=storage.read_file_str(design.structure_path))], key="bindcraft_1"
    )


def visualize_design_structure(design_id: str, height="500px"):
    design = get_cached_design(design_id)

    molstar_custom_component(
        structures=[
            StructureVisualization(
                pdb=storage.read_file_str(design.structure_path),
                color="chain-id",
                representation_type="cartoon+ball-and-stick",
            )
        ],
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
    paths = (
        get_cached_design_descriptors(design_id, [descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key]).dropna().to_dict()
    )

    parser = ContigsParser()
    # TODO this could be parsed from spec contig instead
    parsed_segments = parser.parse_contigs_trb(
        storage.read_file_pickle(paths[descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key])
    )
    # individual positions in this format ['A1', 'A2', ...]
    inpainted_positions = (
        from_segments_to_hotspots(workflow.rfdiffusion_params.inpaint_seq.split("/"))
        if workflow.rfdiffusion_params.inpaint_seq
        else []
    )
    visualize_scaffold_alignment(
        input_seq_by_resno=input_seq_by_resno,
        designed_sequences=designed_sequences,
        parsed_segments=parsed_segments,
        inpainted_positions=inpainted_positions,
    )


def visualize_scaffold_alignment(
    input_seq_by_resno: dict[str, dict[str, str]],
    designed_sequences: dict[str, str],
    parsed_segments: list[ContigSegment],
    inpainted_positions: list[str],
):
    """Visualize alignment between input and designed sequences based on contig segments.

    :param input_seq_by_resno: Mapping from chain ID -> residue number (as string) -> amino acid.
    :param designed_sequences: Mapping from chain ID -> designed sequence.
    :param parsed_segments: List of ContigSegment objects representing the contig segments.
    :param inpainted_positions: List of positions (e.g., 'A12') that were inpainted.
    """
    html = [
        f'<div style="font-family: monospace; font-size: 14px; margin: 10px 2px; display: inline-block;">'
        f"&nbsp;&nbsp;&nbsp;&nbsp;Region<br />"
        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Input<br />"
        f"&nbsp;&nbsp;&nbsp;&nbsp;Design<br />"
        f"</div>"
    ]
    aligned_input = []
    aligned_design = []
    for s in parsed_segments:
        segment_length = s.out_res_end - s.out_res_start + 1
        for chunk_offset in range(0, segment_length, 10):
            chunk_length = min(segment_length - chunk_offset, 10)
            output_start = chunk_offset + s.out_res_start
            # TODO s.out_res_chain might not be correct when multiple chains are designed
            generated_seq = designed_sequences[s.out_res_chain][output_start - 1 : output_start + chunk_length - 1]
            if s.type == "generated":
                label = s.value if chunk_offset == 0 else "&nbsp;"
                input_seq = " " * chunk_length
                input_seq_formatted = "Generated&nbsp;" if chunk_offset == 0 else "&nbsp;" * 10
                generated_seq_formatted = generated_seq
                fmt = f"background-color: {s.color}" if chunk_offset == 0 else ""
            else:
                input_start = chunk_offset + s.input_res_start
                label = f"{s.input_res_chain}{input_start}-{input_start + chunk_length - 1}"
                input_positions = list(range(input_start, input_start + chunk_length))
                input_seq = "".join(
                    [input_seq_by_resno[s.input_res_chain].get(str(pos), "?") for pos in input_positions]
                )
                input_seq_formatted = "".join(
                    [
                        f"<b>{aa}</b>" if f"{s.input_res_chain}{pos}" in inpainted_positions else aa
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
