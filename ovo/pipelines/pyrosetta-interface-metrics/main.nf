nextflow.enable.dsl = 2


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
    tuple val (batch_name), path (pdb_dir)
    val relax
  output:
    path "${batch_name}/pyrosetta_interface_metrics.jsonl", emit: metrics_csv
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
    ${relax ? "--relax --out-pdb ${batch_name}/relaxed_pdb" : ""}
  """
}


workflow {
  PyRosettaInterfaceMetrics(
    ['batch1', params.pdb_dir],
    params.relax
  )
}
