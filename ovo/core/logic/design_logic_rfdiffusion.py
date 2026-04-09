import json
import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from typing import Callable

from ovo import (
    db,
    storage,
    config,
    get_scheduler,
    Design,
)
from ovo.core.database import descriptors_rfdiffusion
from ovo.core.database.models import Pool, Round, DesignJob, DesignSpec, DescriptorValue, Base
from ovo.core.database.models_refolding import RefoldingWorkflow
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionWorkflow,
)
from ovo.core.logic.descriptor_logic import save_descriptor_job_for_design_job, read_descriptor_file_values
from ovo.core.logic.design_logic import set_designs_accepted
from ovo.core.utils.pdb import get_standardized_remarks_from_pdb_str


def submit_rfdiffusion_preview(
    workflow: RFdiffusionWorkflow,
    timesteps: int,
    partial_diffusion: bool = False,
    pipeline_name: str = "rfdiffusion-backbone",
    scheduler_key: str = None,
    **submission_args,
) -> str | None:
    """Run the RFdiffusion workflow with reduced number of diffuser timesteps."""

    contig = workflow.get_contig()
    hotspots = workflow.get_hotspots()

    if not contig:
        raise ValueError("Contig has not been computed. Please check the workflow parameters.")

    scheduler = get_scheduler(scheduler_key or config.local_scheduler)
    input_path = storage.prepare_workflow_input(workflow.get_input_pdb_path(), workdir=scheduler.workdir)

    run_parameters = []

    if partial_diffusion:
        run_parameters.append(f"diffuser.partial_T={timesteps}")
    else:
        run_parameters.append(f"diffuser.T={timesteps}")

    params = {
        "contig": contig,
        "input_pdb": os.path.abspath(input_path),
        "num_designs": 1,
        "hotspot": hotspots,
        "run_parameters": " ".join(run_parameters),
    }

    if workflow.get_cyclic_offset():
        params["cyclic"] = True

    preview_job_id = scheduler.submit(
        pipeline_name=pipeline_name,
        params=params,
        submission_args=submission_args,
    )
    return preview_job_id


def process_workflow_results(
    job: DesignJob,
    callback: Callable = None,
    extra_filenames: dict | None = None,
) -> list[Base]:
    extra_filenames = extra_filenames or {}
    pool = db.get(Pool, design_job_id=job.id)
    project_round = db.get(Round, id=pool.round_id)
    scheduler = get_scheduler(job.scheduler_key)
    workflow: RFdiffusionWorkflow = job.workflow
    assert workflow.is_instance(RFdiffusionWorkflow), (
        "This function expects a RFdiffusionWorkflow instance, got: {}".format(type(workflow).__name__)
    )

    # this is where result files will be stored in our storage
    destination_dir = storage.get_project_path(project_round.project_id, pool.id)

    source_dir = scheduler.get_output_dir(job.job_id)

    batch_size = int(workflow.rfdiffusion_params.batch_size)
    num_sequence_designs = workflow.protein_mpnn_params.num_sequences
    num_fastrelax_cycles = workflow.protein_mpnn_params.fastrelax_cycles

    source_backbone_paths = []
    if workflow.rfdiffusion_params.custom_backbones:
        # Find backbone paths in custom_backbones subdirectory of each batch
        num_contigs = 1
        backbone_descriptor_key = descriptors_rfdiffusion.CUSTOM_BACKBONE_STRUCTURE_PATH.key
        batch_number = 1
        backbone_number = 1
        while paths := storage.list_dir(f"{source_dir}/contig1_batch{batch_number}/custom_backbones"):
            for path in paths:
                if not path.endswith(".pdb"):
                    continue
                full_path = f"contig1_batch{batch_number}/custom_backbones/{path}"
                source_backbone_paths.append((0, f"contig1_batch{batch_number}", backbone_number, full_path))
                backbone_number += 1
            batch_number += 1
        if not source_backbone_paths:
            raise ValueError(
                f"No backbone pdb files found in custom_backbones subdirectories of scheduler output: {source_dir}"
            )
    else:
        # Get backbone pdb paths based on our RFdiffusion output structure
        num_contigs = len(workflow.rfdiffusion_params.contigs)
        backbone_descriptor_key = descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key
        for contig_idx in range(num_contigs):
            for total_idx_backbone in range(workflow.rfdiffusion_params.num_designs):
                batch_idx_backbone = total_idx_backbone % batch_size
                batch_number = (total_idx_backbone // batch_size) + 1
                backbone_number = total_idx_backbone + 1
                batch_name = f"contig{contig_idx + 1}_batch{batch_number}"
                if workflow.rfdiffusion_params.backbone_generator == "rfdiffusion":
                    source_backbone_path = (
                        f"{batch_name}/rfdiffusion_standardized_pdb/{batch_name}_{batch_idx_backbone}_standardized.pdb"
                    )
                elif workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3":
                    source_backbone_path = (
                        f"{batch_name}/rfdiffusion3_standardized_pdb/{batch_name}design_0_model_{batch_idx_backbone}_standardized.pdb"
                    )
                else:
                    raise ValueError(f"Unsupported backbone generator: {workflow.rfdiffusion_params.backbone_generator}")
                source_backbone_paths.append((contig_idx, batch_name, backbone_number, source_backbone_path))

    designs = []
    design_id_mapping = {}
    descriptor_values = []
    with (
        ThreadPoolExecutor(config.storage.num_copy_threads) as executor,
        storage.archive_context(delete_if_exists=True),
    ):
        futures = [
            executor.submit(
                process_rfdiffusion_design,
                pool_id=pool.id,
                contig_idx=contig_idx,
                num_contigs=num_contigs,
                batch_name=batch_name,
                source_backbone_path=source_backbone_path,
                backbone_descriptor_key=backbone_descriptor_key,
                backbone_number=backbone_number,
                num_backbone_designs=len(source_backbone_paths),
                num_sequence_designs=num_sequence_designs,
                num_fastrelax_cycles=num_fastrelax_cycles,
                source_dir=source_dir,
                destination_dir=destination_dir,
                refolding_primary_test=workflow.refolding_params.primary_test,
                cyclic=workflow.rfdiffusion_params.cyclic_offset,
            )
            for contig_idx, batch_name, backbone_number, source_backbone_path in source_backbone_paths
        ]

        for i, future in enumerate(futures):
            new_designs, new_mapping, new_values = future.result()
            designs.extend(new_designs)
            design_id_mapping.update(new_mapping)
            descriptor_values.extend(new_values)
            if callback and new_designs:
                callback(
                    value=(i + 1) / len(futures),
                    text=f"Downloading design {new_designs[0].id}",
                )

    # Create descriptor job on the fly
    designed_chain_ids = sorted(
        set(chain_id for design in designs for c in design.spec.chains for chain_id in c.chain_ids)
    )
    descriptor_job = save_descriptor_job_for_design_job(
        design_job=job,
        project_id=project_round.project_id,
        chains=designed_chain_ids,
        design_ids=list(design_id_mapping.keys()),
    )
    for value in descriptor_values:
        value.descriptor_job_id = descriptor_job.id

    # Generate descriptor values from the descriptor output files
    filenames = {
        "proteinqc|seq_composition": "seq_composition",
        "rfd_ee|backbone_metrics": "backbone_metrics",
        "pyrosetta_interface_metrics|pyrosetta": "pyrosetta_interface_metrics",
        **extra_filenames,
    }
    if workflow.refolding_params.primary_test:
        # Store refolding results under the same set of Descriptor objects to simplify downstream analysis
        stored_key_prefix = RefoldingWorkflow.get_descriptor_key_prefix(
            workflow.refolding_params.primary_test, primary=True
        )
        filenames[stored_key_prefix] = workflow.refolding_params.primary_test

    descriptor_values.extend(
        read_descriptor_file_values(
            descriptor_job=descriptor_job,
            design_id_mapping=design_id_mapping,
            filenames=filenames,
        )
    )

    available_descriptor_keys = set(dv.descriptor_key for dv in descriptor_values)
    missing_descriptor_keys = []
    for descriptor_key, threshold in workflow.acceptance_thresholds.items():
        if descriptor_key not in available_descriptor_keys and threshold.enabled:
            threshold.enabled = False
            missing_descriptor_keys.append(descriptor_key)

    if missing_descriptor_keys:
        job.warnings.append(
            f"Some descriptors were not computed, their acceptance threshold was not applied: {', '.join(missing_descriptor_keys)}"
        )

    # Update design.accepted fields based on descriptor values and thresholds
    set_designs_accepted(designs, descriptor_values, workflow.acceptance_thresholds)
    # Return designs and descriptors to be saved
    return designs + descriptor_values


def process_rfdiffusion_design(
    pool_id: str,
    contig_idx: int,
    num_contigs: int,
    batch_name: str,
    source_backbone_path: str,
    backbone_descriptor_key: str,
    backbone_number: int,
    num_backbone_designs: int,
    num_sequence_designs: int,
    num_fastrelax_cycles: int,
    source_dir: str,
    destination_dir: str,
    refolding_primary_test: str,
    cyclic: bool,
    backbone_generator: str = "rfdiffusion",
) -> tuple[list[Design], dict[str, tuple[str, str]]]:
    """Process a single RFdiffusion-designed backbone and its sequence designs, copying files from the scheduler output to our storage,
    and creating Design and DescriptorValue objects for the backbone and each sequence design.

    Args:
        pool_id: Pool ID
        contig_idx: Index of the contig for this backbone design, used for naming and design spec. Starting at zero.
        num_contigs: Total number of contigs in this design job, used for formatting.
        batch_name: Name of the batch folder in the scheduler output where this backbone design is located, e.g. "contig1_batch1"
        source_dir: Workflow output directory where results are located (s3://bucket/path or local path)
        source_backbone_path: Path to the backbone PDB file relative to source_dir, e.g. "rfdiffusion_standardized_pdb/contig1_batch1_0_standardized.pdb"
        backbone_descriptor_key: Descriptor key to use for the backbone structure file
        backbone_number: Number of the backbone design, used as a prefix in Design ID. Starting at one for each contig.
        num_backbone_designs: Total number of backbone designs for this contig, used for formatting the Design ID.
        num_sequence_designs: Number of sequence designs generated per backbone design, used to find output files and for formatting the Design ID.
        num_fastrelax_cycles: Number of fastrelax sequence designs generated per backbone design, used to find output files and for formatting the Design ID.
        destination_dir: Directory relative to our storage where design files should be stored, e.g. "project/proj123/round1/pools/pool123/designs"
        refolding_primary_test: Name of the primary refolding test to read results from, e.g. "af2_model_1_ptm_tt_3red
        cyclic: Whether the design is macrocyclic

    """
    # add contig suffix 01 in case of multiple contigs
    contig_suffix = "_" + str(contig_idx + 1).zfill(max(len(str(num_contigs)), 2)) if num_contigs > 1 else ""
    # backbone suffix 01, 001, 0001 based on total number of designs
    backbone_suffix = "_" + str(backbone_number).zfill(max(len(str(num_backbone_designs)), 2))
    backbone_id = f"ovo_{pool_id}{contig_suffix}{backbone_suffix}"
    backbone_filename = os.path.basename(source_backbone_path).removesuffix(".pdb")

    rfdiffusion_backbone_trb_path = None
    if backbone_descriptor_key == descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key:
        source_trb_path = source_backbone_path.removesuffix(".pdb").removesuffix("_standardized") + ".trb"
        source_trb_path = source_trb_path.replace("rfdiffusion_standardized_pdb", "rfdiffusion_trb")
        # TODO if file doesnt exist (RFD3)
        if storage.file_exists(os.path.join(source_dir, source_trb_path)):
            rfdiffusion_backbone_trb_path = storage.store_file_path(
                source_abs_path=f"{source_dir}/{source_trb_path}",
                storage_rel_path=f"{destination_dir}/rfdiffusion/{backbone_id}_backbone.trb",
                overwrite=False,
            )

    backbone_pdb_path = storage.store_file_path(
        source_abs_path=f"{source_dir}/{source_backbone_path}",
        storage_rel_path=f"{destination_dir}/rfdiffusion/{backbone_id}_backbone.pdb",
        overwrite=False,
    )
    backbone_design = Design(
        id=backbone_id,
        pool_id=pool_id,
        accepted=False,
        contig_index=contig_idx,
    )
    designs = []
    design_id_mapping = {}
    descriptor_values = []

    if num_fastrelax_cycles > 0:
        mpnn_pdb_template = "proteinmpnn_fastrelax/{backbone_filename}_dldesign_0_cycle{idx_sequence}"
        seq_id_template = "_cycle{idx_sequence}"
        sequence_design_descriptor = descriptors_rfdiffusion.FASTRELAX_STRUCTURE_PATH
        num_seqs_total = num_fastrelax_cycles
    else:
        mpnn_pdb_template = "ligandmpnn/standardized_pdb/{backbone_filename}_packed_{num_sequence}_1"
        seq_id_template = "_seq{num_sequence}"
        sequence_design_descriptor = descriptors_rfdiffusion.LIGANDMPNN_STRUCTURE_PATH
        num_seqs_total = num_sequence_designs

    for idx_sequence in range(num_seqs_total):
        mpnn_source_path = mpnn_pdb_template.format(
            backbone_filename=backbone_filename,
            idx_sequence=idx_sequence,
            num_sequence=idx_sequence + 1,
        )
        filename = os.path.basename(mpnn_source_path)
        # create Design object
        design = deepcopy(backbone_design)
        design.id = backbone_id + seq_id_template.format(
            idx_sequence=str(idx_sequence).zfill(len(str(num_seqs_total))),
            # 01, 001 based on total number of sequences
            num_sequence=str(idx_sequence + 1).zfill(len(str(num_seqs_total))),
        )

        mpnn_full_source_path = os.path.join(source_dir, batch_name, mpnn_source_path + ".pdb")
        if not storage.file_exists(mpnn_full_source_path):
            # skip designs that were filtered out before MPNN step
            # TODO read backbone_metrics.csv to know why they were filtered out,
            #  and only skip those with passed_filters=False, instead of checking file existence.
            #  The csv would need to be read from the correct batch folder, and only once per batch, not per design
            continue
        sequence_design_pdb_path = storage.store_file_path(
            source_abs_path=mpnn_full_source_path,
            storage_rel_path=f"{destination_dir}/protein_mpnn/{design.id}.pdb",
            overwrite=False,
        )
        design.structure_path = sequence_design_pdb_path
        design.structure_descriptor_key = sequence_design_descriptor.key
        design.spec = DesignSpec.from_pdb_str(
            pdb_data=storage.read_file_str(mpnn_full_source_path),
            cyclic=cyclic,
        )
        shared_args = dict(
            design_id=design.id,
            descriptor_job_id=None,
            chains=",".join(chain_id for c in design.spec.chains for chain_id in c.chain_ids),
        )
        descriptor_values.extend(
            [
                DescriptorValue(
                    descriptor_key=backbone_descriptor_key,
                    value=backbone_pdb_path,
                    **shared_args,
                ),
                DescriptorValue(
                    descriptor_key=sequence_design_descriptor.key,
                    value=sequence_design_pdb_path,
                    **shared_args,
                ),
            ]
        )
        if rfdiffusion_backbone_trb_path:
            descriptor_values.append(
                DescriptorValue(
                    descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key,
                    value=rfdiffusion_backbone_trb_path,
                    **shared_args,
                )
            )

        if rfdiffusion_backbone_trb_path:
            descriptor_values.append(
                DescriptorValue(
                    descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key,
                    value=rfdiffusion_backbone_trb_path,
                    **shared_args,
                )
            )

        descriptor_values += RefoldingWorkflow.store_output(
            test=refolding_primary_test,
            destination_dir=destination_dir,
            batch_output_path=None,
            source_structure_path=os.path.join(
                source_dir,
                batch_name,
                refolding_primary_test,
                f"{filename}_{refolding_primary_test}.pdb",
            ),
            primary=True,
            **shared_args,
        )

        designs.append(design)
        design_id_mapping[design.id] = (filename, backbone_filename)

    return designs, design_id_mapping, descriptor_values


def prepare_rfdiffusion_workflow_params(workflow: RFdiffusionWorkflow, workdir: str) -> dict:
    # prepare pdb file or txt file with multiple pdb paths
    workflow_input_path = storage.prepare_workflow_inputs(workflow.rfdiffusion_params.input_pdb_paths, workdir=workdir)
    design_type = workflow.get_refolding_design_type()
    params = {
        "batch_size": workflow.rfdiffusion_params.batch_size,
        "rfdiffusion_input_pdb": workflow_input_path,
        "rfdiffusion_num_designs": workflow.rfdiffusion_params.num_designs,
        "rfdiffusion_contig": ",".join(workflow.rfdiffusion_params.contigs),
        "rfdiffusion_run_parameters": get_rfdiffusion_run_parameters(workflow),
        "backbone_generator": workflow.rfdiffusion_params.backbone_generator,
        "refolding_tests": workflow.refolding_params.primary_test,
        "refolding_chains": ",".join(workflow.get_refolding_designed_chains()),
        "design_type": design_type,
        "mpnn_num_sequences": workflow.protein_mpnn_params.num_sequences,
    }
    if workflow.rfdiffusion_params.custom_backbones:
        params["custom_backbones"] = prepare_custom_backbones(
            custom_backbones=str(workflow.rfdiffusion_params.custom_backbones),
            workdir=workdir,
        )
    else:
        params["rfdiffusion_num_designs"] = workflow.rfdiffusion_params.num_designs
        params["rfdiffusion_contig"] = ",".join(workflow.rfdiffusion_params.contigs)
        params["rfdiffusion_run_parameters"] = get_rfdiffusion_run_parameters(workflow)

    if workflow.rfdiffusion_params.backbone_filters:
        params["backbone_filters"] = workflow.rfdiffusion_params.backbone_filters

    # Disable ddG calculations if PyRosetta license is not available
    if not config.props.pyrosetta_license:
        params["disable_pyrosetta_scoring"] = True

    if workflow.protein_mpnn_params.fastrelax_cycles:
        # Use FastRelax
        if not config.props.pyrosetta_license:
            raise ValueError("FastRelax requires a PyRosetta license which is disabled in this instance of OVO.")
        params["mpnn_fastrelax_cycles"] = workflow.protein_mpnn_params.fastrelax_cycles
        params["mpnn_run_parameters"] = (
            f'-omit_AAs "{workflow.protein_mpnn_params.omit_aa}" '
            + f"-temperature {workflow.protein_mpnn_params.sampling_temp} "
            + (f'-bias_AA "{workflow.protein_mpnn_params.bias_aa}"' if workflow.protein_mpnn_params.bias_aa else "")
            + f" {workflow.protein_mpnn_params.run_parameters}"
        ).strip()
    else:
        # Otherwise use LigandMPNN
        params["mpnn_run_parameters"] = (
            f'--omit_AA "{workflow.protein_mpnn_params.omit_aa}" '
            + f"--temperature {workflow.protein_mpnn_params.sampling_temp}"
            + (f'--bias_AA "{workflow.protein_mpnn_params.bias_aa}"' if workflow.protein_mpnn_params.bias_aa else "")
        )

    if workflow.rfdiffusion_params.cyclic_offset:
        # Note that this is not supported by the public end-to-end workflow
        params["cyclic"] = True

    if workflow.rfdiffusion_params.hotspots:
        hotspots = ",".join(workflow.rfdiffusion_params.hotspots.replace(",", " ").split())
        params["hotspot"] = hotspots

    if workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3":
        p = workflow.rfdiffusion_params
        spec_overrides = {}
        if p.rfd3_unindex:
            spec_overrides["unindex"] = p.rfd3_unindex
        if p.rfd3_select_fixed_atoms:
            spec_overrides["select_fixed_atoms"] = p.rfd3_select_fixed_atoms
        if p.rfd3_ligand:
            spec_overrides["ligand"] = p.rfd3_ligand
        if p.rfd3_length:
            spec_overrides["length"] = p.rfd3_length
        if p.rfd3_infer_ori_strategy:
            spec_overrides["infer_ori_strategy"] = p.rfd3_infer_ori_strategy
        if p.rfd3_is_non_loopy:
            spec_overrides["is_non_loopy"] = True
        if spec_overrides:
            params["rfdiffusion3_spec_overrides"] = json.dumps(spec_overrides)

    if workflow.refolding_params.esmfold_fp16:
        params["esmfold_fp16"] = True

    return params


def get_rfdiffusion_run_parameters(workflow: RFdiffusionWorkflow) -> str:
    args = ""
    if workflow.rfdiffusion_params.backbone_generator == "rfdiffusion3":
        args += f" inference_sampler.num_timesteps={workflow.rfdiffusion_params.timesteps} "
    elif workflow.rfdiffusion_params.partial_diffusion:
        args += f" diffuser.partial_T={workflow.rfdiffusion_params.timesteps} "
    else:
        args += f" diffuser.T={workflow.rfdiffusion_params.timesteps} "

    if workflow.rfdiffusion_params.backbone_generator != "rfdiffusion3":
        if workflow.rfdiffusion_params.contigmap_length:
            length_range = (
                workflow.rfdiffusion_params.contigmap_length
                if "-" in str(workflow.rfdiffusion_params.contigmap_length)
                else f"{workflow.rfdiffusion_params.contigmap_length}-{workflow.rfdiffusion_params.contigmap_length}"
            )
            args += f" contigmap.length={length_range} "

        if workflow.rfdiffusion_params.inpaint_seq:
            args += f" contigmap.inpaint_seq=[{workflow.rfdiffusion_params.inpaint_seq}] "

        if workflow.rfdiffusion_params.model_weights not in [None, "Base", "Complex_base"]:
            args += f" inference.ckpt_override_path=rfdiffusion_models/{workflow.rfdiffusion_params.model_weights}_ckpt.pt "

    args += f" {workflow.rfdiffusion_params.run_parameters} "

    return args


def prepare_custom_backbones(custom_backbones: str, workdir: str) -> str:
    """Prepare custom backbone input for RFdiffusion workflow"""
    if custom_backbones.endswith(".zip"):
        return storage.prepare_workflow_input(custom_backbones, workdir=workdir)
    else:
        custom_dir = storage.resolve_path(custom_backbones)
        custom_backbone_paths = [
            os.path.join(custom_dir, path) for path in storage.list_dir(custom_dir) if path.endswith(".pdb")
        ]
        if not custom_backbone_paths:
            raise ValueError(f"No .pdb files found in custom_backbones: {custom_backbones}")
        example_pdb_data = storage.read_file_str(custom_backbone_paths[0])
        remarks = get_standardized_remarks_from_pdb_str(example_pdb_data)
        if not remarks or not remarks.get("Standardized contig") or not remarks.get("Chains"):
            raise ValueError(
                f"Custom backbone pdb files for scaffold design must have standardized REMARK with contig and chain information, "
                f"required remarks not found in {custom_backbone_paths[0]}. Please add these to the top or bottom of your PDB file:\n"
                'REMARK   1 Standardized contig: "A123-456/10-10/A456-789"\n'
                'REMARK   1 Chains: "A"     \n'
            )
        return storage.prepare_workflow_inputs(
            storage_paths=custom_backbone_paths,
            workdir=workdir,
        )
