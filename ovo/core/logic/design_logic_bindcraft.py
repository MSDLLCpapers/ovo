import json
import os
from io import StringIO
from typing import Callable

import pandas as pd

from ovo import storage, Pool, Round, db, get_scheduler
from ovo.core.database import DesignJob, DesignSpec, Design, Base
from ovo.core.database.models_bindcraft import BindCraftBinderDesignWorkflow
from ovo.app.utils.bindcraft_utils import load_json_from_file, merge_dictionaries
from ovo.core.logic.descriptor_logic import read_descriptor_file_values, save_descriptor_job_for_design_job


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
        load_json_from_file(settings_advanced), workflow.bindcraft_params.custom_advanced_settings
    )
    merged_filter_dict = merge_dictionaries(
        load_json_from_file(settings_filters), workflow.bindcraft_params.custom_filter_settings
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


def process_workflow_results(
    job: DesignJob, callback: Callable = None, extra_filenames: dict | None = None
) -> list[Base]:
    pool = db.get(Pool, design_job_id=job.id)
    project_round = db.get(Round, id=pool.round_id)
    scheduler = get_scheduler(job.scheduler_key)
    extra_filenames = extra_filenames or {}

    # this is where result files will be stored in our storage
    # make sure to remove trailing slash otherwise S3 will keep two slashes in the path
    destination_dir = os.path.join("project", project_round.project_id, "pools", pool.id, "designs").rstrip("/")

    source_output_path = scheduler.get_output_dir(job.job_id)

    num_replicas = job.workflow.bindcraft_params.num_replicas

    designs = []
    final_rows = []
    design_id_mapping = {}
    for replica in range(1, num_replicas + 1):
        batch_dir = f"batch{replica}"
        accepted_dir = os.path.join(source_output_path, f"{batch_dir}/bindcraft/Accepted")
        accepted_filenames = [filename for filename in storage.list_dir(accepted_dir) if filename.endswith(".pdb")]
        accepted_designs = [filename.split("_model")[0] for filename in accepted_filenames]

        final_designs = pd.read_csv(
            StringIO(
                storage.read_file_str(os.path.join(source_output_path, f"{batch_dir}/bindcraft/final_design_stats.csv"))
            ),
        ).drop(columns=["Rank"])
        if missing_designs := set(final_designs["Design"]).difference(accepted_designs):
            raise FileNotFoundError(
                f"Unexpected error: Missing files for accepted designs: {missing_designs}, "
                f"found only {accepted_designs} in {accepted_dir}"
            )

        rejected_dir = os.path.join(source_output_path, f"{batch_dir}/bindcraft/Rejected")
        rejected_filenames = [filename for filename in storage.list_dir(rejected_dir) if filename.endswith(".pdb")]

        design_df = pd.read_csv(
            StringIO(
                storage.read_file_str(os.path.join(source_output_path, f"{batch_dir}/bindcraft/mpnn_design_stats.csv"))
            ),
        )
        design_df = design_df.sort_values("Average_i_pTM", ascending=False)

        # check the ranking of the designs and copy them with new ranked IDs to the folder
        rank = 1
        rejected = 1
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
                id_prefix = f"ovo_{pool.id}"
                if num_replicas > 1:
                    replica_str = str(replica).zfill(len(str(num_replicas)))
                    id_prefix += f"_batch{replica_str}"

                if accepted:
                    structure_path = os.path.join(accepted_dir, filename)
                    rank_str = str(rank).zfill(max(2, len(str(rank))))
                    design_id = f"{id_prefix}_rank{rank_str}_bindcraft"
                    rank += 1
                else:
                    structure_path = os.path.join(rejected_dir, filename)
                    rejected_str = str(rejected).zfill(max(2, len(str(rejected))))
                    design_id = f"{id_prefix}_rejected{rejected_str}_bindcraft"
                    rejected += 1
                design_id_mapping[design_id] = design_id
                final_rows.append(
                    {
                        "ID": design_id,
                        "Rank": rank if accepted else None,
                        "Model": model,
                        **row[final_designs.columns].to_dict(),
                    }
                )
                design = Design(
                    id=design_id,
                    pool_id=pool.id,
                    accepted=accepted,
                    structure_path=storage.store_file_path(
                        structure_path,
                        os.path.join(destination_dir, f"{design_id}.pdb"),
                    ),
                )
                design.spec = DesignSpec.from_pdb_str(
                    pdb_data=storage.read_file_str(design.structure_path), chains=["B"]
                )
                designs.append(design)

    if not final_rows:
        # Case when no trajectories proceeded to filtering stage
        job.job_result = False
        job.warnings.append(
            f"No designs found! Please use a higher time limit. You can inspect discarded trajectories in the output path: {source_output_path}"
        )
        # Job will be saved by caller
        return

    # ID, Rank, Model, Average_i_pTM, ...
    final_df = pd.DataFrame(final_rows).set_index("ID")

    # IMPORTANT
    # We convert pLDDT to 0-100 scale and PAE to 0-31 scale to be consistent with ColabDesign
    for column in final_df.columns:
        if "_plddt" in column.lower():
            final_df[column] *= 100
        if "_pae" in column.lower():
            final_df[column] *= 31

    descriptor_job = save_descriptor_job_for_design_job(
        design_job=job,
        project_id=project_round.project_id,
        # TODO currently binder chain is B, this might be changed later to chain A
        chains=["B"],
        design_ids=list(design_id_mapping.keys()),
    )
    descriptor_values = read_descriptor_file_values(
        descriptor_job=descriptor_job,
        design_id_mapping=design_id_mapping,
        descriptor_tables={
            "bindcraft|af2": final_df,
            "bindcraft|mpnn": final_df,
            "bindcraft|interface": final_df,
            "bindcraft|dssp": final_df,
        },
        filenames=extra_filenames,
    )

    return designs + descriptor_values
