nextflow.enable.dsl = 2


process ProteinMPNN_Fast_Relax {
    def containerName = "proteinmpnn-fastrelax"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName }"
    label "fastrelax"
    cpus { 2 }
    memory "16 GB"
    publishDir { params.publish_dir }
    input:
        tuple val (batch_name), path (pdb_dir)
        val relax_cycles
        val run_parameters
    output:
        tuple val(batch_name), path ("${batch_name}/proteinmpnn_fastrelax"), emit: pdb_dir
    script:
    """
    set -euxo pipefail

    # Initialize lib directory
    if [[ ! -d /opt/ProteinMPNN ]]; then
        SITE=\$(python -c "import site; print(site.getsitepackages()[0])")
        if [[ ! -d "\$SITE/dl_binder_design" ]]; then
            git clone --depth 1 https://github.com/nrbennet/dl_binder_design.git "\$SITE/dl_binder_design"
        fi
        if [[ ! -d "\$SITE/ProteinMPNN" ]]; then
            git clone --depth 1 https://github.com/dauparas/ProteinMPNN.git "\$SITE/ProteinMPNN"
        fi
        ln -s "\$SITE" ./lib
	else
	    ln -s /opt/ ./lib
	fi

    export PYTHONPATH=lib/dl_binder_design/include/:lib/dl_binder_design/mpnn_fr/:lib/

    mkdir ${batch_name}

    python ${moduleDir}/bin/dl_interface_design_extended.py \
        -debug \
        -pdbdir ${pdb_dir} \
        -outpdbdir ${batch_name}/proteinmpnn_fastrelax \
        -checkpoint_path lib/ProteinMPNN/vanilla_model_weights/v_48_020.pt \
        -relax_cycles ${relax_cycles} \
        -output_intermediates \
        ${run_parameters}

    python ${moduleDir}/bin/copy_remarks.py \
      ${pdb_dir} \
      ${batch_name}/proteinmpnn_fastrelax

    # remove lib link to avoid nextflow access issues when scanning output directory
    rm lib
    """
}

workflow {

    ProteinMPNN_Fast_Relax(
        ['batch1', params.pdb_dir],
        params.relax_cycles,
        params.run_parameters
    )

}
