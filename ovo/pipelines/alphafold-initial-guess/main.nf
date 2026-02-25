nextflow.enable.dsl = 2

process AlphaFoldInitialGuess {
  def containerName = "colabdesign"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName + (workflow.profile.tokenize(",").contains("cpu_env") ? "-cpu" : "")
    : params.docker_repository + 'ovo-' + containerName + (workflow.profile.tokenize(",").contains("cpu_env") ? "-cpu" : "") }"

  label 'colabdesign'
  cpus 8
  memory "16 GB"
  accelerator 1, type: "nvidia-tesla-t4"
  publishDir { params.publish_dir }
  input:
    tuple val (meta), path (native_pdb), path (pdb_dir), val(design_type), val(run_parameters)
    path model_weights
  output:
    tuple val (meta), path ("${meta.batch_name}/${meta.test}"), emit: pdb_dir
    path "${meta.batch_name}/${meta.test}.jsonl", emit: losses_jsonl
  script:
  """
  set -euxo pipefail

  # unpack if tar file
  UNPACKED_DEST="${model_weights}.unpacked"
  if [[ "${model_weights}" =~ .*\\.tar\$ ]]; then
    if [[ ! -d "\$UNPACKED_DEST" ]]; then
      # Unpack model weights next to the .tar file (so that they can be shared between processes on the same node)
      # Use random output path suffix to avoid conflicts in parallel processes
      # Then move it to the final destination with an atomic rename
      echo "Unpacking model weights from ${model_weights}"
      TMP_DEST="${model_weights}.unpacked.\$RANDOM.\$RANDOM"
      mkdir "\$TMP_DEST"
      tar -xf "${model_weights}" -C "\$TMP_DEST"
      if [[ ! -d "\$UNPACKED_DEST" ]]; then
          # atomically rename the directory
          mv "\$TMP_DEST" "\$UNPACKED_DEST"
      else
          echo "Unpacked model dir already exists, assuming it was created by another process"
          # Clean up temporary directory created by this process to avoid leaking disk space
          rm -rf "\$TMP_DEST"
      fi
    fi
    ln -s "\$UNPACKED_DEST" ./alphafold_params
  else
    ln -s "${model_weights}" ./alphafold_params
  fi

  rm -f check.point 2>/dev/null

  mkdir -p ${meta.batch_name}

  unset MPLBACKEND
  python3 ${moduleDir}/bin/af2_initial_guess_${design_type}_eval.py \
    ${pdb_dir} \
	${meta.batch_name}/${meta.test} \
	--params ./alphafold_params \
	${design_type == "scaffold" && "${native_pdb}" != "NO_FILE" ? "--native-pdb ${native_pdb}" : ""} \
	${run_parameters}
  """

  // Dry run
  stub:
  """
  set -euxo pipefail

  mkdir -p ${meta.batch_name}/af2_initial_guess

  for file in ${pdb_dir}/*.pdb; do
    base=\$(basename \$file)
    outpath=${meta.batch_name}/af2_initial_guess/\${base}
    cp \$file \$outpath
    echo "{\"id\": "\$base", \"dry_run\": true}" >> ${meta.batch_name}/${meta.test}.jsonl
  done
  """
}


workflow {
  AlphaFoldInitialGuess(
    [
      [batch_name: 'batch1', test: 'initial_guess'],
      params.native_pdb,
      params.pdb_dir,
      params.design_type,
      params.run_parameters,
    ],
    params.alphafold_models_path,
  )
}
