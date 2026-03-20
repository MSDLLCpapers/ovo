nextflow.enable.dsl = 2

process proteinQCPepPatch {
  def containerName = "pep-patch"
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label "peppatch"
  cpus 4
  // 8 GB, 16 GB, 32 GB
  memory { Math.pow(8, task.attempt) * 1.GB }
  errorStrategy { task.exitStatus in 137..140 ? "retry" : "terminate" }
  maxRetries 2
  publishDir { params.publish_dir }
  input:
    tuple val (batch_dir), path (pdb_dir)
    val chains
    val peppatch_config_path
    val hydrophobicity_scale_path
  output:
    path "${batch_dir}/*", emit: output_csv
  script:
  """
  set -euxo pipefail

  if [[ ! -d /opt/resources ]]; then
      echo "PepPatch is only supported with containers (Docker/Singularity/Apptainer/...)";
      exit 1;
  fi

  # Calculate memory limit = requested memory - 100MB
  mem_limit_kb=\$(( (${task.memory.toMega()} - 100) * 1024 ))
  echo "Setting ulimit -v to \$mem_limit_kb KB"
  ulimit -v \$mem_limit_kb
  ulimit -d \$mem_limit_kb
  ulimit -m \$mem_limit_kb

  mkdir -p ${batch_dir}

  # Hydrophobicity scale file is expected in the current working directory
  cp ${hydrophobicity_scale_path} .

  python3 ${moduleDir}/bin/peppatch.py \
    ${pdb_dir} \
	"${batch_dir}"/peppatch.csv \
	--chains "${chains}" \
    --peppatch_config_path "${peppatch_config_path}"
  """
}


workflow {
    proteinQCPepPatch([params.output_dir, params.pdb_dir], params.chains, params.peppatch_config_path, params.hydrophobicity_scale_path)
}
