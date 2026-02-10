nextflow.enable.dsl = 2

workflow {
    // Check required arguments
    [
        'input_pdb',
        'chains',
    ].each { param ->
        params[param] = null // this only sets the default as null to avoid missing param warning
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }

    // Reusable logic to create PDB folder batches
    def fileList = getFileList()
    createInputFolders(fileList)
    indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
    batches = createInputFolders.out.pdb_dir.merge(indexes, { pdb_dir, idx -> ["contig1_batch${idx}", pdb_dir] })

    // Run process with provided params
    __MODULE_SUFFIX__(
        batches,
        chains=params.chains,
    )
}

process __MODULE_SUFFIX__ {
  // docker container name
  def containerName = "__MODULE_SUFFIX__"
  conda { params.getSharedEnv("__MODULE_NAME__.${containerName}", workflow.profile) }
  container "${ (workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container)
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  // label enables customizing configuration for specific jobs using nextflow config files
  label "__MODULE_SUFFIX__"
  // default compute resources
  cpus 1
  memory "4 GB"
  // GPU
  // accelerator 1, type: "nvidia-tesla-t4"

  publishDir { params.publish_dir }
  input:
    tuple val(batch_dir), path(pdb_dir)
    val chains
  output:
    path "${batch_dir}/*", emit: output_csv
  script:
  """
  set -euxo pipefail

  mkdir "${batch_dir}"

  python3 ${moduleDir}/bin/example.py \
    ${pdb_dir} \
    "${batch_dir}"/__MODULE_SUFFIX__.csv \
    --chain "${chains}"

  """
}

def getFileList() {
    def pdbPaths
    if (params.input_pdb.endsWith('.txt')) {
        pdbPaths = Channel.fromList(file(params.input_pdb).readLines())
    } else if (params.input_pdb.endsWith('.pdb')) {
        pdbPaths = Channel.fromPath(params.input_pdb)
    } else if (params.input_pdb.endsWith('/')) {
        pdbPaths = Channel.fromPath(params.input_pdb + '*.pdb')
    } else {
        throw new IllegalArgumentException("Input file must be a .pdb file, a .txt file with a list of .pdb files, or a directory ending with /, got: ${params.input_pdb}")
    }
    return pdbPaths.collate(params.batch_size)
}

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
