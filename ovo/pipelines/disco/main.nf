nextflow.enable.dsl = 2
include { Refolding } from params.getSharedPipelinePath("ovo.refolding")

process Disco {
    def containerName = "disco"
    container "${workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + containerName
        : params.docker_repository + 'ovo-' + containerName}"

    label 'disco'
    cpus 4
    memory "16 GB"
    accelerator 1, type: "nvidia-tesla-a10g"
    publishDir { params.publish_dir }

    input:
        tuple val(batch_name), path(input_json)
        path hf_cache_path
        path ligand_file
        val experiment
        val effort
        val num_designs

    output:
        tuple val(batch_name), path("${batch_name}/disco_packed"), emit: output_dir
        path("${batch_name}/disco_raw"), emit: output_dir_raw
        path("${batch_name}/ligandmpnn_out/seqs"), emit: ligandmpnn_seqs

    script:
    """
    set -euxo pipefail

    export HF_HOME=\$(realpath ${hf_cache_path})
    # If the cache is already populated, skip network lookups entirely (e.g. HealthOmics has no internet egress).
    # Otherwise stay online so the first run populates the cache (only persists when the cache dir is shared, e.g. HPC/local).
    if [ -f "\$HF_HOME/hub/models--DISCO-Design--DISCO/refs/main" ] && [ -f "\$HF_HOME/hub/models--airkingbd--dplm_650m/refs/main" ]; then
        export HF_HUB_OFFLINE=1
        export TRANSFORMERS_OFFLINE=1
    fi

    # When a ligand is supplied as a file, the input JSON references it as "FILE_<basename>" and the file
    # is symlinked into the task working directory by the ligand_file input, so DISCO can resolve it.

    # we need to update the json to use the absolute path to the ligand file
    sed -i "s|FILE_\$(basename "${ligand_file}")|FILE_\$(realpath "${ligand_file}")|" "${input_json}"

    # DISCO writes designs to batch_name/disco/pdbs/*.pdb and the matching
    # sequences to batch_name/disco/sequences/*.txt.
    python3 /opt/DISCO/runner/inference.py \
        experiment=${experiment} \
        effort=${effort} \
        input_json_path=${input_json} \
        num_inference_seeds=${num_designs} \
        hydra.run.dir=${batch_name}/hydra_outputs \
        dump_dir=${batch_name}/disco_raw

    pdbs_dir=${batch_name}/disco_raw/pdbs
    python3 "${moduleDir}/bin/prepare_ligandmpnn_params.py" \
        --pdb-dir "\$pdbs_dir" \
        --pdb-path-multi-json ./pdb_path_multi.json \
        --fixed-residues-json ./fixed_residues_multi.json

    ln -s /opt/LigandMPNN/model_params ./model_params

    python /opt/LigandMPNN/run.py \
        --model_type ligand_mpnn \
        --pdb_path_multi ./pdb_path_multi.json \
        --fixed_residues_multi ./fixed_residues_multi.json \
        --out_folder "${batch_name}/ligandmpnn_out" \
        --pack_side_chains 1 \
        --number_of_packs_per_design 1 \
        --repack_everything 1

    # LigandMPNN names packed files <input>_packed_<seq_idx>_<pack_idx>.pdb;
    # with one sequence and one pack that is _packed_1_1.pdb.
    mkdir -p "${batch_name}/disco_packed"
    for packed in ${batch_name}/ligandmpnn_out/packed/*_packed_1_1.pdb; do
        # get basename and trim the suffix
        name=\$(basename "\$packed" _packed_1_1.pdb)
        cp "\$packed" "${batch_name}/disco_packed/\${name}_packed.pdb"
        # Carry the ground-truth ligand SMILES to refolding in a REMARK header: the packed PDB has no
        # bond orders, so prepare_inputs.py reads the remark instead of perceiving them from coordinates.
        ligands="${batch_name}/disco_raw/pdbs/\${name}_ligands.txt"
        if [ -f "\$ligands" ]; then
            python3 "${moduleDir}/bin/add_ligand_remarks.py" \
                --pdb "${batch_name}/disco_packed/\${name}_packed.pdb" \
                --ligands-txt "\$ligands"
        fi
    done
    """

    stub:
    """
    tar -xzf "${moduleDir}/local/mock-output.tar.gz"
    """
}



workflow {
    ['input_json', 'hf_cache_path'].each { param ->
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }
    // Optional ligand file (when ligand is provided as an uploaded structure file); falls back to NO_FILE sentinel
    def ligandFile = params.ligand_file ? params.ligand_file : "${projectDir}/lib/NO_FILE"
    Disco(
        ['batch1', file(params.input_json)],
        params.hf_cache_path,
        file(ligandFile),
        params.experiment,
        params.effort,
        params.num_designs
    )

    disco_out = Disco.out.output_dir

    Refolding(
        disco_out.map({
            batch_name, output_dir ->
            [
                batch_name: batch_name,
                batch_design_dir: output_dir,
                native_pdb: "${projectDir}/lib/NO_FILE",
                designed_chains: "A",   // DISCO only supports single-chain designs, designed chain is always "A"
            ]
        }),
        "boltz2_scaffold_nt",   // hardcoded test name
        "scaffold",
    )
}
