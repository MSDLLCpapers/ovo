nextflow.enable.dsl = 2

process RFdiffusion3 {
    def containerName = "rc-foundry"
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
        tuple val(batch_name), path(input_structure_path), val(contig), val(num_designs)
        path rfdiffusion3_models_path
        val hotspot
        val dump_trajectories
        val run_parameters
        val spec_overrides
    output:
        tuple val(batch_name), path("${batch_name}/rfdiffusion3_cif/"), emit: cif_dir
        tuple val(batch_name), path("${batch_name}/rfdiffusion3_standardized_pdb/"), emit: standardized_pdb_dir
        path "${batch_name}/rfdiffusion3_json/", emit: json_dir
        path "${batch_name}/rfdiffusion3_traj/", emit: traj_dir
    script:
    """
    set -euxo pipefail
    mkdir -p output

    # Resolve checkpoint path: if it's a directory, find the .ckpt file inside
    CKPT_PATH="${rfdiffusion3_models_path}"
    if [[ -d "\$CKPT_PATH" ]]; then
        CKPT_PATH="\$CKPT_PATH/rfd3_latest.ckpt"
    fi

    if [[ ! -e "\$CKPT_PATH" ]]; then
        echo "RFDiffusion3 model checkpoint file does not exist. Download RFD3 weights by running 'ovo init rfdiffusion'"
        exit 1
    fi

    # Write spec overrides to a file to avoid bash quoting issues with JSON strings
    SPEC_OVERRIDES_ARG=""
    if [[ -n '${spec_overrides}' ]]; then
        echo '${spec_overrides}' > spec_overrides.json
        SPEC_OVERRIDES_ARG="--spec_overrides_file spec_overrides.json"
    fi
    python3 ${moduleDir}/bin/build_input_json.py \
        --input_structure_path "${input_structure_path}" \
        --contig "${contig}" \
        --hotspot "${hotspot}" \
        --output_json input_spec.json \
        \$SPEC_OVERRIDES_ARG

    # Run RFdiffusion3 inference
    rfd3 design \
        out_dir=output \
        inputs=input_spec.json \
        ckpt_path="\$CKPT_PATH" \
        n_batches=${num_designs} \
        diffusion_batch_size=1 \
        dump_trajectories=${dump_trajectories} \
        global_prefix=${batch_name} \
        skip_existing=False \
        ${run_parameters}

    ls -al output/

    # Organize outputs
    mkdir -p ${batch_name}/rfdiffusion3_cif
    mkdir -p ${batch_name}/rfdiffusion3_json

    mv output/*.cif.gz ${batch_name}/rfdiffusion3_cif/ 2>/dev/null || true
    mv output/*.json ${batch_name}/rfdiffusion3_json/ 2>/dev/null || true

    if [[ "${dump_trajectories}" == "true" ]]; then
        mkdir -p ${batch_name}/rfdiffusion3_traj
        find output/ -name "*.traj*" -exec mv {} ${batch_name}/rfdiffusion3_traj/ \\; 2>/dev/null || true
        find output/ -name "trajectories" -type d -exec cp -r {} ${batch_name}/rfdiffusion3_traj/ \\; 2>/dev/null || true
    else
        mkdir -p ${batch_name}/rfdiffusion3_traj
    fi

    # Standardize: CIF.gz -> standardized PDB
    mkdir -p ${batch_name}/rfdiffusion3_standardized_pdb
    python3 ${moduleDir}/bin/standardize_cif.py \
        --cif_dir ${batch_name}/rfdiffusion3_cif/ \
        --json_dir ${batch_name}/rfdiffusion3_json/ \
        --output_dir ${batch_name}/rfdiffusion3_standardized_pdb/ \
        --input_contig "${contig}" \
        --hotspot "${hotspot}"
    """
}


workflow {

    ["input_structure_path", "contig"].each { param ->
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }

    RFdiffusion3(
        ["rfdiffusion3", params.input_structure_path, params.contig, params.num_designs],
        params.rfdiffusion3_models_path,
        params.hotspot,
        params.dump_trajectories,
        params.run_parameters,
        params.spec_overrides
    )
}
