nextflow.enable.dsl = 2

process RFdiffusion3 {
    def containerName = "rfdiffusion3"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"

    label 'rfdiffusion3'
    cpus 4
    memory "16 GB"
    accelerator 1, type: "nvidia-tesla-t4"
    publishDir { params.publish_dir }

    input:
        tuple val (batch_name), path (input_pdb), val (contig), val (num_designs)
        path rfdiffusion3_models_path
        val hotspot
        val run_parameters
    output:
        tuple val (batch_name), path ("${batch_name}/rfdiffusion3_pdb/"), emit: pdb_dir
        tuple val (batch_name), path ("${batch_name}/rfdiffusion3_standardized_pdb/"), emit: standardized_pdb_dir
    script:
    """
    set -euxo pipefail
    mkdir -p output
    export HYDRA_FULL_ERROR=1

    # TODO: Add RFdiffusion3 inference command
    echo "RFdiffusion3 inference placeholder"
    echo "Input PDB: ${input_pdb}"
    echo "Contig: ${contig}"
    echo "Num designs: ${num_designs}"
    echo "Models path: ${rfdiffusion3_models_path}"

    mkdir -p ${batch_name}/rfdiffusion3_pdb
    mkdir -p ${batch_name}/rfdiffusion3_standardized_pdb
    """
}

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
    RFdiffusion3(['rfdiffusion3', params.input_pdb, params.contig, params.num_designs],
                params.rfdiffusion3_models_path,
                params.hotspot,
                params.run_parameters
                )
}
