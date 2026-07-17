import json
import os
from io import StringIO
from typing import Callable

import pandas as pd

from ovo import storage, Pool, Round, db, get_scheduler
from ovo.core.database import DesignJob, DesignSpec, Design, Base
from ovo.core.database.models_bindcraft import BindCraftBinderDesignWorkflow
from ovo.core.utils.advanced_parameters import load_json_from_file, merge_dictionaries
from ovo.core.logic.descriptor_logic import read_descriptor_file_values, save_descriptor_job_for_design_job

from ovo.core.database.descriptors_bindcraft import DESCRIPTORS


def prepare_bindcraft_params(workflow: BindCraftBinderDesignWorkflow, workdir: str) -> dict:
    input_dict = {
        "design_path": "output",
        "starting_pdb": "target.pdb",
        "binder_name": "design",
        "chains": workflow.bindcraft_params.target_chains,
        "target_hotspot_residues": workflow.bindcraft_params.hotspots,
        "lengths": [int(v) for v in workflow.bindcraft_params.binder_length.split(",")],
        "number_of_final_designs": workflow.bindcraft_params.number_of_final_designs,
    }

    settings_advanced, settings_filters = workflow.get_settings_paths()

    merged_advanced_dict = merge_dictionaries(
        load_json_from_file(settings_advanced),
        workflow.bindcraft_params.custom_advanced_settings,
    )
    merged_filter_dict = merge_dictionaries(
        load_json_from_file(settings_filters),
        workflow.bindcraft_params.custom_filter_settings,
    )

    return {
        "time_limit_seconds": workflow.bindcraft_params.time_limit_hours * 3600,
        "input_pdb": storage.prepare_workflow_input(workflow.bindcraft_params.input_pdb_path, workdir=workdir),
        "input_json_path": storage.prepare_workflow_input(
            "input.json",
            workdir=workdir,
            input_bytes=json.dumps(input_dict).encode("utf-8"),
        ),
        "settings_advanced": storage.prepare_workflow_input(
            "settings_advanced.json",
            workdir=workdir,
            input_bytes=json.dumps(merged_advanced_dict, indent=2).encode("utf-8"),
        ),
        "settings_filters": storage.prepare_workflow_input(
            "settings_filters.json",
            workdir=workdir,
            input_bytes=json.dumps(merged_filter_dict, indent=2).encode("utf-8"),
        ),
        "num_replicas": workflow.bindcraft_params.num_replicas,
    }


def _include_trajectory_designs(
    source_dir: str,
    batch_dir: str,
    pool_id: str,
    num_replicas: int,
    replica: int,
    destination_dir: str,
    callback: Callable = None,
    extra_spec_args=None,
):
    extra_spec_args = extra_spec_args or {}

    # Empty descriptor values to avoid raising error when parsing descriptors from dataframe
    empty_values = {
        desc.key.split("|")[-1]: None for desc in DESCRIPTORS if desc.key.split("|")[-1] not in {"DesignVariant"}
    }

    trajectory_dir_names = [
        "LowConfidence",
        "Clashing",
        # "Relaxed",
        # NOTE: We do not include "Relaxed" trajectories because these are the trajectories that proceed
        # to MPNN redesign and other stages, so they will be present in the regular Accepted/Rejected folders.
    ]
    # All trajectory variants and paths to their directories.
    trajectory_dir_paths = {
        trajectory_dir_name: os.path.join(
            source_dir,
            f"{batch_dir}/bindcraft/Trajectory/{trajectory_dir_name}",
        )
        for trajectory_dir_name in trajectory_dir_names
    }
    # All files in each trajectory directory. We compute this beforehand to be
    # able to show accurate progress in the callback.
    all_trajectory_filenames = {
        trajectory_dir_name: [filename for filename in storage.list_dir(trajectory_dir) if filename.endswith(".pdb")]
        for trajectory_dir_name, trajectory_dir in trajectory_dir_paths.items()
    }

    total_trajectory_files = sum(len(filenames) for filenames in all_trajectory_filenames.values())
    trajectory_count = 1
    designs = []
    rows = []
    design_id_mapping = {}
    for trajectory_dir_name, trajectory_dir in trajectory_dir_paths.items():
        # Iterate through all Trajectory variants.
        for filename in all_trajectory_filenames[trajectory_dir_name]:
            # Iterate through
            design_name = filename.removesuffix(".pdb")

            if callback:
                callback(
                    value=(trajectory_count) / total_trajectory_files,
                    text=f"Downloading design {design_name}",
                )

            id_prefix = f"ovo_{pool_id}"
            if num_replicas > 1:
                replica_str = str(replica).zfill(len(str(num_replicas)))
                id_prefix += f"_batch{replica_str}"

            structure_path = os.path.join(trajectory_dir, filename)
            id_suffix = filename.replace("design_", "traj_").removesuffix(".pdb")
            design_id = f"{id_prefix}_{trajectory_dir_name}_{id_suffix}"
            design_id_mapping[design_id] = (
                design_id,
                filename.removesuffix(".pdb"),
            )

            design = Design(
                id=design_id,
                pool_id=pool_id,
                accepted=False,
                structure_path=storage.store_file_path(
                    structure_path,
                    os.path.join(destination_dir, f"{design_id}.pdb"),
                ),
            )
            design.spec = DesignSpec.from_pdb_str(
                pdb_data=storage.read_file_str(design.structure_path),
                chains=["B"],
                **extra_spec_args,
            )
            designs.append(design)
            rows.append(
                {
                    "ID": design_id,
                    "Rank": None,
                    "Model": "rejected trajectory (no model)",  # model
                    "DesignVariant": f"Trajectory-{trajectory_dir_name}",
                    **empty_values,
                    "Length": len(design.spec.chains[0].sequence),
                }
            )
            trajectory_count += 1
    return designs, rows, design_id_mapping


def process_workflow_results(
    job: DesignJob, callback: Callable = None, extra_filenames: dict | None = None, extra_spec_args: dict | None = None
) -> list[Base]:
    """Process the results of a BindCraft design workflow, return Design and DescriptorValue entries to be saved in the database."""
    pool = db.get(Pool, design_job_id=job.id)
    project_round = db.get(Round, id=pool.round_id)
    scheduler = get_scheduler(job.scheduler_key)
    source_dir = scheduler.get_output_dir(job.job_id)

    designs, design_id_mapping, final_df = process_bindcraft_output_folder(
        source_dir=source_dir,
        destination_dir=storage.get_project_path(project_round.project_id, pool.id),
        num_replicas=job.workflow.bindcraft_params.num_replicas,
        pool_id=pool.id,
        callback=callback,
        extra_spec_args=extra_spec_args,
    )

    if final_df.empty:
        # Case when no trajectories proceeded to filtering stage nor any trajectories were generated.
        job.job_result = False
        job.warnings.append(
            f"No designs nor rejected trajectories found! Please use a higher time limit. You can inspect the current results in the output path: {source_dir}"
        )
        # Job will be saved by caller
        return []

    descriptor_job = save_descriptor_job_for_design_job(
        design_job=job,
        project_id=project_round.project_id,
        chains=["B"],
        design_ids=list(design_id_mapping.keys()),
    )
    descriptor_values = read_descriptor_file_values(
        descriptor_job=descriptor_job,
        design_id_mapping=design_id_mapping,
        descriptor_tables={
            "bindcraft|sequence": final_df,
            "bindcraft|af2": final_df,
            "bindcraft|mpnn": final_df,
            "bindcraft|interface": final_df,
            "bindcraft|dssp": final_df,
            "bindcraft|designs": final_df,
        },
        filenames=extra_filenames or {},
    )

    return designs + descriptor_values


def process_bindcraft_output_folder(
    source_dir: str,
    destination_dir: str,
    num_replicas: int,
    pool_id: str,
    callback: Callable = None,
    extra_spec_args: dict | None = None,
) -> tuple[list[Design], dict[str, tuple[str, str]], pd.DataFrame]:
    """Process the output folder of a BindCraft workflow and return

    Args:
        source_dir: Source directory containing contig1_batch1 folders
        destination_dir: Destination pool directory to store processed PDB files
        num_replicas: Number of batch replicas to process (e.g. 5 if contig1_batch1 to contig1_batch5)
        pool_id: ID of the pool to associate with the Designs
        callback: Optional callback function to report progress, takes arguments (value: float, text: str)
        extra_spec_args: Optional extra arguments to pass to DesignSpec.from_pdb_str for each design

    Returns:
    - the list of Designs
    - a mapping from design IDs to their original design names,
    - and a dataframe with design statistics.
    """
    extra_spec_args = extra_spec_args or {}

    designs = []
    final_rows = []
    design_id_mapping = {}
    for replica in range(1, num_replicas + 1):
        batch_dir = f"contig1_batch{replica}"
        accepted_dir = os.path.join(source_dir, f"{batch_dir}/bindcraft/Accepted")
        accepted_filenames = [filename for filename in storage.list_dir(accepted_dir) if filename.endswith(".pdb")]
        accepted_designs = [filename.split("_model")[0] for filename in accepted_filenames]

        final_designs = pd.read_csv(
            StringIO(storage.read_file_str(os.path.join(source_dir, f"{batch_dir}/bindcraft/final_design_stats.csv"))),
        ).drop(columns=["Rank"])
        if missing_designs := set(final_designs["Design"]).difference(accepted_designs):
            raise FileNotFoundError(
                f"Unexpected error: Missing files for accepted designs: {missing_designs}, "
                f"found only {accepted_designs} in {accepted_dir}"
            )

        rejected_dir = os.path.join(source_dir, f"{batch_dir}/bindcraft/Rejected")
        rejected_filenames = [filename for filename in storage.list_dir(rejected_dir) if filename.endswith(".pdb")]

        design_df = pd.read_csv(
            StringIO(storage.read_file_str(os.path.join(source_dir, f"{batch_dir}/bindcraft/mpnn_design_stats.csv"))),
        )
        design_df = design_df.sort_values("Average_i_pTM", ascending=False)

        # check the ranking of the designs and copy them with new ranked IDs to the folder
        rank = 0
        rejected = 0
        for i, (_, row) in enumerate(design_df.iterrows()):
            model_filenames = [
                filename
                for filename in accepted_filenames + rejected_filenames
                if filename.startswith(row["Design"] + "_model")
            ]
            if not model_filenames:
                raise ValueError(
                    f"Unexpected error: Missing accepted or rejected PDB model files for design {row['Design']}"
                )

            for filename in model_filenames:
                design, model = filename.removesuffix(".pdb").split("_model")

                if callback:
                    callback(
                        value=(i + 1) / len(design_df),
                        text=f"Downloading design {design}",
                    )

                accepted = filename in accepted_filenames
                id_prefix = f"ovo_{pool_id}"
                if num_replicas > 1:
                    replica_str = str(replica).zfill(len(str(num_replicas)))
                    id_prefix += f"_batch{replica_str}"

                if accepted:
                    rank += 1
                    structure_path = os.path.join(accepted_dir, filename)
                    rank_str = str(rank).zfill(max(2, len(str(rank))))
                    design_id = f"{id_prefix}_rank{rank_str}_bindcraft"
                else:
                    rejected += 1
                    structure_path = os.path.join(rejected_dir, filename)
                    rejected_str = str(rejected).zfill(max(2, len(str(rejected))))
                    design_id = f"{id_prefix}_rejected{rejected_str}_bindcraft"
                design_id_mapping[design_id] = (
                    design_id,
                    filename.removesuffix(".pdb"),
                )
                final_rows.append(
                    {
                        "ID": design_id,
                        "Rank": rank if accepted else None,
                        "Model": model,
                        "DesignVariant": "Accepted" if accepted else "Rejected",
                        **row[final_designs.columns].to_dict(),
                    }
                )
                design = Design(
                    id=design_id,
                    pool_id=pool_id,
                    accepted=accepted,
                    structure_path=storage.store_file_path(
                        structure_path,
                        os.path.join(destination_dir, f"{design_id}.pdb"),
                    ),
                )
                design.spec = DesignSpec.from_pdb_str(
                    pdb_data=storage.read_file_str(design.structure_path),
                    chains=["B"],
                    **extra_spec_args,
                )
                designs.append(design)

    # Process all rejected trajectory PDBs:
    for replica in range(1, num_replicas + 1):
        batch_dir = f"contig1_batch{replica}"
        trajectory_designs, trajectory_rows, trajectory_mapping = _include_trajectory_designs(
            source_dir=source_dir,
            batch_dir=batch_dir,
            pool_id=pool_id,
            num_replicas=num_replicas,
            replica=replica,
            destination_dir=destination_dir,
            extra_spec_args=extra_spec_args,
        )
        designs.extend(trajectory_designs)
        final_rows.extend(trajectory_rows)
        design_id_mapping.update(trajectory_mapping)

    # ID, Rank, Model, Average_i_pTM, ...
    final_df = pd.DataFrame(final_rows)
    if final_rows:
        final_df = final_df.set_index("ID")

    # IMPORTANT
    # We convert pLDDT to 0-100 scale and PAE to 0-31 scale to be consistent with ColabDesign
    for column in final_df.columns:
        if "_plddt" in column.lower():
            final_df[column] *= 100
        if "_pae" in column.lower():
            final_df[column] *= 31

    return designs, design_id_mapping, final_df
