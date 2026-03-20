nextflow.enable.dsl = 2


process LigandMpnn {
    def containerName = "ligandmpnn"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"
    label "ligandmpnn"
    cpus { 4 }
    memory "8 GB"
    accelerator 1, type: "nvidia-tesla-t4"
    publishDir { params.publish_dir }
    input:
        tuple val (batch_name), path (pdb_dir)
        val num_seq_per_target
        val run_parameters
    output:
        tuple val (batch_name), path ("${batch_name}/ligandmpnn/packed/"), emit: pdb_dir
        tuple val (batch_name), path ("${batch_name}/ligandmpnn/standardized_pdb/"), emit: standardized_pdb_dir
    script:
    """
    set -euxo pipefail

    if [[ ! -d /opt/LigandMPNN ]]; then
        ligandmpnn=ligandmpnn # assume available on PATH (conda version)
    else
        ln -s /opt/LigandMPNN/model_params ./model_params; ligandmpnn='python /opt/LigandMPNN/run.py'
    fi

    mkdir ${batch_name}

    pdb_json_file="./pdb_ids.json"
    redesigned_json_file="./redesigned_residues_multi.json"
    remark_json_file="./remark_multi.json"

    # Check if the input PDB directory exists
    # Generate a JSON file with the PDB IDs and designed_chains and segments
    # based on the standardized PDB header produced by RFdiffusion or other workflow
    python "${moduleDir}/bin/prepare_json.py" \
        --pdb_dir "${pdb_dir}" \
        --pdb_ids_json "\$pdb_json_file" \
        --redesigned_residues_json "\$redesigned_json_file" \
        --remark_json "\$remark_json_file"

    # Number of designs per target (default is 4)
    \$ligandmpnn \
        --model_type "ligand_mpnn" \
        --pdb_path_multi "\$pdb_json_file" \
        --redesigned_residues_multi "\$redesigned_json_file" \
        --out_folder "${batch_name}/ligandmpnn" \
        --number_of_batches ${num_seq_per_target} \
        --pack_side_chains 1 \
        --number_of_packs_per_design 1 \
        --repack_everything 1 \
        ${run_parameters}

    bash "${moduleDir}/bin/copy_remarks.sh" \
        "\$remark_json_file" \
        "${batch_name}/ligandmpnn/packed/" \
        "${batch_name}/ligandmpnn/standardized_pdb/"
    """
}

workflow {
    LigandMpnn(
        ['batch1', params.pdb_path],
        params.num_seq_per_target,
        params.run_parameters
    )
}
