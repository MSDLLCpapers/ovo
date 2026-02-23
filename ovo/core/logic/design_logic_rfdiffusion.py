import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from typing import Callable

from ovo import (
    db,
    storage,
    config,
    local_scheduler,
    get_scheduler,
    Design,
)
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionWorkflow,
    RFdiffusionBinderDesignWorkflow,
    RFdiffusionScaffoldDesignWorkflow,
)
from ovo.core.database import descriptors_rfdiffusion, descriptors_refolding

from ovo.core.database.models import Pool, Round, DesignJob, DesignSpec, DescriptorValue, StructureFileDescriptor, Base
from ovo.core.logic.descriptor_logic import save_descriptor_job_for_design_job, read_descriptor_file_values
from ovo.core.logic.design_logic import set_designs_accepted


def submit_rfdiffusion_preview(
    workflow: RFdiffusionWorkflow,
    timesteps: int,
    partial_diffusion: bool = False,
    pipeline_name="rfdiffusion-backbone",
    **submission_args,
) -> str | None:
    """Run the RFdiffusion workflow with reduced number of diffuser timesteps."""

    contig = workflow.get_contig()
    hotspots = workflow.get_hotspots()

    if not contig:
        raise ValueError("Contig has not been computed. Please check the workflow parameters.")

    input_path = storage.prepare_workflow_input(workflow.get_input_pdb_path(), workdir=local_scheduler.workdir)

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

    preview_job_id = local_scheduler.submit(
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
    # make sure to remove trailing slash otherwise S3 will keep two slashes in the path
    destination_dir = os.path.join("project", project_round.project_id, "pools", pool.id, "designs").rstrip("/")

    source_output_path = scheduler.get_output_dir(job.job_id)

    batch_size = int(workflow.rfdiffusion_params.batch_size)

    alphafold_file_suffix = None
    if workflow.refolding_params.primary_test and workflow.refolding_params.primary_test.startswith("af2_"):
        alphafold_file_suffix = workflow.refolding_params.primary_test

    esmfold_file_suffix = None
    if workflow.refolding_params.primary_test == "esmfold":
        esmfold_file_suffix = workflow.refolding_params.primary_test

    num_contigs = len(workflow.rfdiffusion_params.contigs)
    num_backbone_designs = workflow.rfdiffusion_params.num_designs
    num_sequence_designs = workflow.protein_mpnn_params.num_sequences
    num_fastrelax_cycles = workflow.protein_mpnn_params.fastrelax_cycles

    designs = []
    design_id_mapping = {}
    descriptor_values = []
    with ThreadPoolExecutor(config.storage.num_copy_threads) as executor:
        futures = [
            executor.submit(
                process_rfdiffusion_design,
                pool_id=pool.id,
                batch_size=batch_size,
                contig_idx=contig_idx,
                num_contigs=num_contigs,
                total_idx_backbone=total_idx_backbone,
                num_backbone_designs=num_backbone_designs,
                num_sequence_designs=num_sequence_designs,
                num_fastrelax_cycles=num_fastrelax_cycles,
                source_output_path=source_output_path,
                destination_dir=destination_dir,
                alphafold_file_suffix=alphafold_file_suffix,
                esmfold_file_suffix=esmfold_file_suffix,
                cyclic=workflow.rfdiffusion_params.cyclic_offset,
            )
            for contig_idx in range(num_contigs)
            for total_idx_backbone in range(num_backbone_designs)
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
    descriptor_job = save_descriptor_job_for_design_job(
        design_job=job, project_id=project_round.project_id, chains=["A"], design_ids=list(design_id_mapping.keys())
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
        if workflow.refolding_params.primary_test.startswith("af2_"):
            descriptor_key_prefix = "refolding|af2_primary"
        else:
            descriptor_key_prefix = f"refolding|{workflow.refolding_params.primary_test}"
        # tool_key -> filename
        filenames[descriptor_key_prefix] = workflow.refolding_params.primary_test

    descriptor_values.extend(
        read_descriptor_file_values(
            descriptor_job=descriptor_job, design_id_mapping=design_id_mapping, filenames=filenames
        )
    )

    # Update design.accepted fields based on descriptor values and thresholds
    set_designs_accepted(designs, descriptor_values, workflow.acceptance_thresholds)
    # Return designs and descriptors to be saved
    return designs + descriptor_values


def process_rfdiffusion_design(
    pool_id: str,
    batch_size: int,
    contig_idx: int,
    num_contigs: int,
    total_idx_backbone: int,
    num_backbone_designs: int,
    num_sequence_designs: int,
    num_fastrelax_cycles: int,
    source_output_path: str,
    destination_dir: str,
    alphafold_file_suffix: str | None,
    esmfold_file_suffix: str | None,
    cyclic: bool,
) -> tuple[list[Design], dict[str, tuple[str, str]]]:
    batch_number = (total_idx_backbone // batch_size) + 1
    batch_name = f"contig{contig_idx + 1}_batch{batch_number}"
    batch_idx_backbone = total_idx_backbone % batch_size
    backbone_filename = f"{batch_name}_{batch_idx_backbone}"

    # add contig suffix 01 in case of multiple contigs
    contig_suffix = "_" + str(contig_idx + 1).zfill(max(len(str(num_contigs)), 2)) if num_contigs > 1 else ""
    # backbone suffix 01, 001, 0001 based on total number of designs
    backbone_suffix = "_" + str(total_idx_backbone + 1).zfill(max(len(str(num_backbone_designs)), 2))
    backbone_id = f"ovo_{pool_id}{contig_suffix}{backbone_suffix}"
    rfdiffusion_backbone_pdb_path = storage.store_file_path(
        source_abs_path=f"{source_output_path}/{batch_name}/rfdiffusion_standardized_pdb/{backbone_filename}_standardized.pdb",
        storage_rel_path=f"{destination_dir}/rfdiffusion/{backbone_id}_backbone.pdb",
        overwrite=False,
    )
    rfdiffusion_backbone_trb_path = storage.store_file_path(
        source_abs_path=f"{source_output_path}/{batch_name}/rfdiffusion_trb/{backbone_filename}.trb",
        storage_rel_path=f"{destination_dir}/rfdiffusion/{backbone_id}_backbone.trb",
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
        mpnn_pdb_template = "proteinmpnn_fastrelax/{backbone_filename}_standardized_dldesign_0_cycle{idx_sequence}"
        seq_id_template = "_cycle{idx_sequence}"
        sequence_design_descriptor = descriptors_rfdiffusion.FASTRELAX_STRUCTURE_PATH
        num_seqs_total = num_fastrelax_cycles
    else:
        mpnn_pdb_template = "ligandmpnn/standardized_pdb/{backbone_filename}_standardized_packed_{num_sequence}_1"
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

        mpnn_full_source_path = os.path.join(source_output_path, batch_name, mpnn_source_path + ".pdb")
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
            pdb_data=storage.read_file_str(design.structure_path), chains=["A"], cyclic=cyclic
        )
        shared_args = dict(
            design_id=design.id,
            descriptor_job_id=None,
            chains="A",
        )
        descriptor_values.extend(
            [
                DescriptorValue(
                    descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_STRUCTURE_PATH.key,
                    value=rfdiffusion_backbone_pdb_path,
                    **shared_args,
                ),
                DescriptorValue(
                    descriptor_key=descriptors_rfdiffusion.RFDIFFUSION_TRB_PATH.key,
                    value=rfdiffusion_backbone_trb_path,
                    **shared_args,
                ),
                DescriptorValue(
                    descriptor_key=sequence_design_descriptor.key,
                    value=sequence_design_pdb_path,
                    **shared_args,
                ),
            ]
        )

        if alphafold_file_suffix:
            descriptor_values.append(
                DescriptorValue(
                    descriptor_key=descriptors_refolding.AF2_PRIMARY_STRUCTURE_PATH.key,
                    value=storage.store_file_path(
                        source_abs_path=os.path.join(
                            source_output_path,
                            batch_name,
                            alphafold_file_suffix,
                            f"{filename}_{alphafold_file_suffix}.pdb",
                        ),
                        storage_rel_path=f"{destination_dir}/alphafold_initial_guess/{design.id}_{alphafold_file_suffix}.pdb",
                        overwrite=False,
                    ),
                    **shared_args,
                )
            )

        if esmfold_file_suffix:
            descriptor_values.append(
                DescriptorValue(
                    descriptor_key=descriptors_refolding.ESMFOLD_STRUCTURE_PATH.key,
                    value=storage.store_file_path(
                        source_abs_path=os.path.join(
                            source_output_path, batch_name, esmfold_file_suffix, f"{filename}_{esmfold_file_suffix}.pdb"
                        ),
                        storage_rel_path=f"{destination_dir}/esmfold/{design.id}_{esmfold_file_suffix}.pdb",
                        overwrite=False,
                    ),
                    **shared_args,
                )
            )

        designs.append(design)
        design_id_mapping[design.id] = (filename, backbone_filename + "_standardized")

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
        "refolding_tests": workflow.refolding_params.primary_test,
        "design_type": design_type,
        "mpnn_num_sequences": workflow.protein_mpnn_params.num_sequences,
    }

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

    if workflow.refolding_params.esmfold_fp16:
        params["esmfold_fp16"] = True

    return params


def get_rfdiffusion_run_parameters(workflow: RFdiffusionWorkflow) -> str:
    args = ""
    if workflow.rfdiffusion_params.partial_diffusion:
        args += f" diffuser.partial_T={workflow.rfdiffusion_params.timesteps} "
    else:
        args += f" diffuser.T={workflow.rfdiffusion_params.timesteps} "

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
