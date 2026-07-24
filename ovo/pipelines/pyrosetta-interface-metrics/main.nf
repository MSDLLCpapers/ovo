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

process PyRosettaInterfaceMetrics {
  def containerName = "proteinmpnn-fastrelax"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label "pyrosetta_interface_metrics"
  cpus 8
  memory "32 GB"
  publishDir { params.publish_dir }
  input:
    tuple val(batch_name), path(pdb_dir)
    val relax
    val binder_chain
    val target_chain
  output:
    path "${batch_name}/pyrosetta_interface_metrics.jsonl", emit: metrics_jsonl
    path "${batch_name}/relaxed_pdb", emit: relaxed_pdb
  script:
  """
  set -euo pipefail

  mkdir -p ${batch_name}
  mkdir "${batch_name}/relaxed_pdb"

  if [[ -d /opt/ProteinMPNN ]]; then
    # Running from container
    if [[ ! -f /opt/DAlphaBall.gcc ]]; then
        echo "\n!!!\nInterface analysis now requires DAlphaBall, \nplease upgrade your OVO proteinmpnn-fastrelax container to the latest version!\n!!!\n"
        exit 2
    fi
  else
    # Running from conda, build DAlphaBall if not already present
    SITE=\$(python -c "import site; print(site.getsitepackages()[0])")
    if [[ ! -f "\$SITE/DAlphaBall/src/DAlphaBall.gcc" ]]; then
      rm -rf "\$SITE/DAlphaBall"
      git clone --depth 1 https://github.com/outpace-bio/DAlphaBall.git "\$SITE/DAlphaBall"
      cd "\$SITE/DAlphaBall/src"
      export CFLAGS="-I\$CONDA_PREFIX/include"
      export LDFLAGS="-L\$CONDA_PREFIX/lib -Wl,-rpath,\$CONDA_PREFIX/lib"
      export FC=gfortran
      export CC=gcc
      make
      chmod +x "\$SITE/DAlphaBall/src/DAlphaBall.gcc"
      cd -   # return to work directory
    fi
  fi

  set -x

  python3 ${moduleDir}/bin/pyrosetta_interface_metrics.py \
    ${pdb_dir} \
    ${batch_name}/pyrosetta_interface_metrics.jsonl \
    --binder-chain ${binder_chain} \
    --target-chain ${target_chain} \
    ${relax ? "--relax --out-pdb ${batch_name}/relaxed_pdb" : ""}
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
    def indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
    def batches = createInputFolders.out.merge(indexes, { pdb_dir, idx -> ["contig1_batch${idx}", pdb_dir] })

    PyRosettaInterfaceMetrics(batches, params.relax, params.binder_chain, params.target_chain)
}
