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
        tuple val(batch_name), path(input_pdb), val(contig), val(num_designs)
        path rfdiffusion3_models_path
        val hotspot
        val dump_trajectories
        val run_parameters
        val spec_overrides
    output:
        tuple val(batch_name), path("${batch_name}/rfdiffusion3_pdb/"), emit: pdb_dir
        tuple val(batch_name), path("${batch_name}/rfdiffusion3_standardized_pdb/"), emit: standardized_pdb_dir
        path "${batch_name}/rfdiffusion3_json/", emit: json_dir
        path "${batch_name}/rfdiffusion3_traj/", emit: traj_dir
    script:
    """
    set -euxo pipefail
    export HYDRA_FULL_ERROR=1
    mkdir -p output

    # Resolve checkpoint path: if it's a directory, find the .ckpt file inside
    CKPT_PATH="${rfdiffusion3_models_path}"
    if [[ -d "\$CKPT_PATH" ]]; then
        CKPT_FILE=\$(find "\$CKPT_PATH/" -name "*.ckpt" | head -1)
        if [[ -z "\$CKPT_FILE" ]]; then
            echo "ERROR: No .ckpt file found in \$CKPT_PATH" >&2
            exit 1
        fi
        CKPT_PATH="\$CKPT_FILE"
    fi

    # Write spec overrides to a file to avoid bash quoting issues with JSON strings
    SPEC_OVERRIDES_ARG=""
    if [[ -n "${spec_overrides}" ]]; then
        printf '%s' "${spec_overrides}" > spec_overrides.json
        SPEC_OVERRIDES_ARG="--spec_overrides_file spec_overrides.json"
    fi
    python3 ${moduleDir}/bin/build_input_json.py \
        --input_pdb "${input_pdb}" \
        --contig "${contig}" \
        --hotspot "${hotspot}" \
        --output_json input_spec.json \
        \$SPEC_OVERRIDES_ARG

    # Run RFdiffusion3 inference
    rfd3 design \
        out_dir=output \
        inputs=input_spec.json \
        ckpt_path="\$CKPT_PATH" \
        diffusion_batch_size=${num_designs} \
        dump_trajectories=${dump_trajectories} \
        global_prefix=${batch_name} \
        skip_existing=False \
        ${run_parameters}

    ls -al output/

    # Organize outputs
    mkdir -p ${batch_name}/rfdiffusion3_pdb
    mkdir -p ${batch_name}/rfdiffusion3_json

    mv output/*.cif.gz ${batch_name}/rfdiffusion3_pdb/ 2>/dev/null || true
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
        --cif_dir ${batch_name}/rfdiffusion3_pdb/ \
        --json_dir ${batch_name}/rfdiffusion3_json/ \
        --spec_json input_spec.json \
        --output_dir ${batch_name}/rfdiffusion3_standardized_pdb/ \
        --input_contig "${contig}" \
        --hotspot "${hotspot}"
    """
}


workflow {

    if (!params.input_json) {
        ["input_pdb", "contig"].each { param ->
            params[param] = null
            if (!params[param]) {
                throw new IllegalArgumentException("Argument --${param} is required (or provide --input_json)!")
            }
        }
    }

    def input_pdb = params.input_json ? file("NO_FILE") : file(params.input_pdb)
    def contig = params.contig ?: ""

    RFdiffusion3(
        ["rfdiffusion3", input_pdb, contig, params.num_designs],
        params.rfdiffusion3_models_path,
        params.hotspot,
        params.dump_trajectories,
        params.run_parameters,
        params.spec_overrides
    )
}
