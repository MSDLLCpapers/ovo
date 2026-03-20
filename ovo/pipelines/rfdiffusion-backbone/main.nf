nextflow.enable.dsl = 2

process RFdiffusion {
    def containerName = "rfdiffusion"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"

    label 'rfdiffusion'
    cpus 4
    memory "16 GB"
    accelerator 1, type: "nvidia-tesla-t4"
    publishDir { params.publish_dir }

    input:
        tuple val (batch_name), path (input_uri), val (contig), val (num_designs)
        path rfdiffusion_models_path
        val hotspot
        val cyclic
        val save_traj
        val run_parameters
    output:
        tuple val (batch_name), path ("${batch_name}/rfdiffusion_pdb/"), emit: pdb_dir
        tuple val (batch_name), path ("${batch_name}/rfdiffusion_standardized_pdb/"), emit: standardized_pdb_dir
        path "${batch_name}/rfdiffusion_trb/", emit: trb_dir
        path "${batch_name}/rfdiffusion_traj/", emit: traj_dir
    script:
    """
    set -euxo pipefail
    mkdir -p output
    export HYDRA_FULL_ERROR=1

    echo WORKFLOW: "${workflow}"
    exit 2
    # Initialize lib directory
	if [[ ${workflow.containerEngine} == "null" ]]; then
	    SITE=\$(python -c "import site; print(site.getsitepackages()[0])")
	    if [[ ! -d "\$SITE/RFdiffusion" ]]; then
	        git clone --depth 1 https://github.com/prihoda/RFdiffusion-fork "\$SITE/RFdiffusion"
	    fi
	    ln -s "\$SITE" ./lib
	else
	    ln -s /opt/ ./lib
	fi

    # Enable importing rfdiffusion and se3_transformer modules in python
	export PYTHONPATH=./lib/RFdiffusion/:./lib/RFdiffusion/env/SE3Transformer/

    python3 ${moduleDir}/bin/validate_input.py \
        "${input_uri}" \
        "${contig}"

    python3 lib/RFdiffusion/scripts/run_inference.py \
        inference.output_prefix=output/${batch_name} \
        inference.model_directory_path=${rfdiffusion_models_path} \
        inference.schedule_directory_path=./schedules \
        inference.input_pdb="${input_uri}" \
        inference.num_designs=${num_designs} \
        'contigmap.contigs=[${contig}]' \
        ${hotspot ? "ppi.hotspot_res=[" + hotspot + "]" : ""} \
        ${cyclic ? "inference.cyclic=True" : ""} \
        inference.write_trajectory=${save_traj ? "true": "false"} \
        ${run_parameters}

    ls -al output/

    mkdir -p ${batch_name}/rfdiffusion_pdb
    mv output/*.pdb ${batch_name}/rfdiffusion_pdb/
    mkdir -p ${batch_name}/rfdiffusion_trb
    mv output/*.trb ${batch_name}/rfdiffusion_trb/
    if [[ ${save_traj} == "true" ]]; then
      mv output/traj ${batch_name}/rfdiffusion_traj
    else
      mkdir -p ${batch_name}/rfdiffusion_traj
    fi
    mkdir -p ${batch_name}/rfdiffusion_standardized_pdb/

    python3 ${moduleDir}/bin/standardize_pdb.py \
        ${batch_name}/rfdiffusion_pdb/ \
        ${batch_name}/rfdiffusion_trb/ \
        ${batch_name}/rfdiffusion_standardized_pdb/

    # remove lib link to avoid nextflow access issues when scanning output directory
    rm lib
    """
}

// static data files are in nextflow.config
workflow {

    [
        'input_pdb',
        'contig',
    ].each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }
    RFdiffusion(['rfdiffusion', params.input_pdb, params.contig, params.num_designs],
                params.rfdiffusion_models_path,
                params.hotspot,
                params.cyclic,
                params.save_traj,
                params.run_parameters
                )
}

