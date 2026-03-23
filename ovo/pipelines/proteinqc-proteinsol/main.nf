nextflow.enable.dsl = 2

process proteinQCProteinSol {
  def containerName = "proteinsol"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label 'proteinsol'
  cpus 1
  memory "1 GB"
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

  # Initialize lib directory
  if [[ ! -d /opt/protein-sol-sequence-prediction-software ]]; then
      SITE=\$(python -c "import site; print(site.getsitepackages()[0])")
      if [[ ! -d "\$SITE/protein-sol-sequence-prediction-software" ]]; then
          wget -O "\$SITE/proteinsol.zip" https://protein-sol.manchester.ac.uk/cgi-bin/utilities/download_sequence_code.php
          unzip "\$SITE/proteinsol.zip" -d "\$SITE/"
      fi
      ln -s "\$SITE" ./lib
  else
      ln -s /opt/ ./lib
  fi

  python3 ${moduleDir}/bin/proteinsol.py \
    ${pdb_dir} \
    "${batch_dir}/proteinsol.csv" \
    --chains "${chains}"

  # remove lib link to avoid nextflow access issues when scanning output directory
  rm lib
  """
}

workflow {
  proteinQCProteinSol([params.output_dir, params.pdb_dir], params.chains)
}
