nextflow.enable.dsl = 2


process LigandMpnn {
    def containerName = "ligandmpnn-v2"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"
    label 'ligandmpnn'
    cpus { 4 }
    memory "8 GB"
    accelerator 1, type: "nvidia-tesla-t4"
    publishDir { params.publish_dir }
    input:
        path (pdb_path)
        val number_of_batches
        val run_parameters
    output:
        path "ligandmpnn", emit: pdb_dir
    script:
    """
    set -euxo pipefail

    if [[ ! -f "${pdb_path}" ]]; then
        echo "PDB file does not exist: ${pdb_path}"
        exit 1
    fi

    ligandmpnn \
        --out_folder "ligandmpnn" \
        --number_of_batches ${number_of_batches} \
        --pdb_path "${pdb_path}" \
        ${run_parameters}

    """
}

workflow {
    LigandMpnn(
        params.pdb_path,
        params.number_of_batches,
        params.run_parameters + (params.helpfull ? " --help" : "")
    )
}
