nextflow.enable.dsl = 2

process BindCraft {
    def containerName = "bindcraft"
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"

    label 'bindcraft'
    cpus 4
    memory "16 GB"
    accelerator 1, type: "nvidia-tesla-a10g"
    publishDir { params.publish_dir }

    input:
        tuple val (batch_name), path (input_pdb), path (input_json_path), path (settings_advanced), path (settings_filters)
        path alphafold_models_path
        val time_limit_seconds
        val alphafold_single_model
    output:
        tuple val(batch_name), path ("${batch_name}/bindcraft"), emit: pdb_dir
    script:
    """
    set -euxo pipefail

    if [[ ! -d /content/bindcraft ]]; then
        echo "BindCraft is only supported with containers (Docker/Singularity/Apptainer/...)";
        exit 1;
    fi

    # unpack if tar file
    if [[ "${alphafold_models_path}" =~ .*\\.tar\$ ]]; then
        mkdir -p ./alphafold_models_path/
        tar -xvf ${alphafold_models_path} -C ./alphafold_models_path/
    else
        ln -s "${alphafold_models_path}" alphafold_models_path
    fi

    ln -s "${input_pdb}" target.pdb
    # validate that input JSON refers to target.pdb
    grep '"target.pdb"' "${input_json_path}"

    if [[ "${alphafold_single_model}" == "true" ]]; then
        sed -i 's/design_models = \\[0,1,2,3,4\\]/design_models = [0]/' /content/bindcraft/functions/generic_utils.py
        sed -i 's/prediction_models = \\[0,1\\]/prediction_models = [0]/' /content/bindcraft/functions/generic_utils.py
    fi

    # Add AF2 path to advanced settings JSON
    cp "${settings_advanced}" advanced.json
    sed -i 's/"af_params_dir": .*/"af_params_dir": "alphafold_models_path",/' advanced.json

    bash "${moduleDir}/bin/timeout.sh" "${time_limit_seconds}" \
        python /content/bindcraft/bindcraft.py \
          --settings "${input_json_path}" \
          --advanced advanced.json \
          --filters "${settings_filters}"

    ls -lR ./output/

    mkdir -p ${batch_name}
    mv ./output/ ${batch_name}/bindcraft/
    """

    stub:
    """
    unzip "${moduleDir}/local/mock-output.zip"
    """
}

// static data files are in nextflow.config
workflow {
    [
        'input_pdb',
        'input_json_path',
        'settings_advanced',
        'settings_filters',
        'alphafold_models_path',
        'time_limit_seconds',
    ].each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }

    def inputs = (1..params.num_replicas).collect { i ->
        ["contig1_batch${i}", params.input_pdb, params.input_json_path, params.settings_advanced, params.settings_filters]
    }

    BindCraft(
        Channel.fromList(inputs),
        params.alphafold_models_path,
        params.time_limit_seconds,
        params.alphafold_single_model,
    )
}
