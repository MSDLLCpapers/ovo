nextflow.enable.dsl = 2

process BoltzRefolding {
    def containerName = "boltz"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"

    label 'boltz'
    cpus 4
    memory "16 GB"
    accelerator 1, type: "nvidia-tesla-a10g"
    publishDir { params.publish_dir }
    input:
        tuple val(meta), path(input_dir), path(native_pdb), val(design_type), val(run_parameters)
        path boltz_models_path
    output:
        tuple val(meta), path("${meta.batch_name}/${meta.test}/"), emit: pdb_dir
        path "${meta.batch_name}/${meta.test}.jsonl", emit: metrics_jsonl
    script:
    def mols_tar_file = "${boltz_models_path}/mols.tar"
    def mols_dir = "${boltz_models_path}/mols"
    def boltz_version = meta.test.contains("_") ? meta.test.tokenize("_")[0] : params.boltz_version
    """
    set -euxo pipefail

    ACCELERATOR=${workflow.profile.tokenize(",").contains("cpu_env") ? 'cpu' : 'gpu'}

    # Check that reference folder has been initialized
    if [[ ! -f "${mols_tar_file}" && ! -d "${mols_dir}" ]]; then
        echo "Boltz reference files have not been initialized in ${boltz_models_path}" >&2
        exit 2
    fi
    # Extract mols.tar if mols directory does not exist
    if [[ ! -d "${mols_dir}" ]]; then
        # Use random output path suffix to avoid conflicts in parallel processes
        TMP_DEST="${boltz_models_path}/\$RANDOM"
        mkdir "\$TMP_DEST"
        tar -xf "${mols_tar_file}" -C "\$TMP_DEST"
        if [[ ! -d "${mols_dir}" ]]; then
            # atomically rename the directory
            mv "\$TMP_DEST/mols" "${mols_dir}"
        else
            echo "Mols dir already exists, assuming it was created by another process"
        fi
    fi

    ls -lR
    export NUMBA_CACHE_DIR=/tmp

    if [[ ${design_type} == "scaffold" ]]; then
        python3 "${moduleDir}/bin/prepare_inputs.py" \
            --input_dir "${input_dir}" \
            --output_dir "${meta.batch_name}/boltz/yaml_inputs/" \
            --design_type scaffold \
            --template "${native_pdb}" \
            ${run_parameters}
    elif [[ ${design_type} == "binder" ]]; then
        python3 "${moduleDir}/bin/prepare_inputs.py" \
            --input_dir "${input_dir}" \
            --output_dir "${meta.batch_name}/boltz/yaml_inputs/" \
            --design_type binder \
            --template "${native_pdb}" \
            ${run_parameters}
    else 
        echo "Unknown design type: ${design_type}" >&2
        exit 2
    fi

    boltz predict "${meta.batch_name}/boltz/yaml_inputs/" \
        --cache "${boltz_models_path}" \
        --accelerator \$ACCELERATOR \
        --model "${boltz_version}"

    python3 "${moduleDir}/bin/compute_rmsd.py" \
        --input_dir "${input_dir}" \
        --boltz_pubdir "boltz_results_yaml_inputs/predictions/" \
        --boltz_version "${boltz_version}" \
        --design_type ${design_type} \
        --output_metrics_path "${meta.batch_name}/${meta.test}.jsonl" \
        --output_pdb_dir "${meta.batch_name}/${meta.test}/" \
        ${run_parameters}

    """
}

workflow {
    [
        'input_dir',
        'output_dir',
        'boltz_version',
        'design_type',
        'native_pdb',
    ].each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }
    BoltzRefolding(
        [
            [
                batch_name:params.output_dir, 
                test:params.boltz_version], 
            params.input_dir, 
            params.native_pdb, 
            params.design_type, 
            params.run_parameters
            ],
        params.boltz_models_path
    )
}
