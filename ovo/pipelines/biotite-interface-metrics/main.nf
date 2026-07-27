nextflow.enable.dsl = 2

process createInputFolders {
  executor 'local'
  input:
    path inputs
  output:
    path pdb_dir, emit: pdb_dir
  script:
  """
    mkdir pdb_dir
    cp ${inputs} pdb_dir
  """
}

process BiotiteInterfaceMetrics {
  def containerName = "python-structure"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label "interface_metrics"
  publishDir { params.publish_dir }
  input:
    tuple val(batch_dir), path(pdb_dir)
    val binder_chain_id
    val target_chain_id
  output:
    path "${batch_dir}/biotite_interface_metrics.csv", emit: output_csv
  script:
  """
  set -euxo pipefail

  mkdir -p "${batch_dir}"

  python3 ${moduleDir}/bin/interface_metrics.py \
    ${pdb_dir} \
    "${batch_dir}/biotite_interface_metrics.csv" \
    --binder_chain ${binder_chain_id} \
    --target_chain ${target_chain_id}
  """
}

workflow {
    if (!params.pdb_dir) {
        throw new IllegalArgumentException("Argument --pdb_dir is required!")
    }

    def pdbPaths
    if (params.pdb_dir.endsWith('.txt')) {
        pdbPaths = Channel.fromList(file(params.pdb_dir).readLines())
    } else if (params.pdb_dir.endsWith('.pdb')) {
        pdbPaths = Channel.fromPath(params.pdb_dir)
    } else if (params.pdb_dir.endsWith('/')) {
        pdbPaths = Channel.fromPath(params.pdb_dir + '*.pdb')
    } else {
        throw new IllegalArgumentException("--pdb_dir must be a .pdb file, a .txt file with a list of .pdb paths, or a directory ending with /, got: ${params.pdb_dir}")
    }

    createInputFolders(pdbPaths.collate(params.batch_size))
    indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
    batches = createInputFolders.out.merge(indexes, { pdb_dir, idx -> ["contig1_batch${idx}", pdb_dir] })

    BiotiteInterfaceMetrics(batches, params.binder_chain_id, params.target_chain_id)
}
