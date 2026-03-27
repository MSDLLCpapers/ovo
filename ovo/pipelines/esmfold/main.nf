nextflow.enable.dsl = 2

process ESMFold {
  def containerName = "huggingface-transformers"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label "esmfold"
  cpus 4
  memory "16 GB"
  accelerator 1, type: "nvidia-tesla-t4"
  publishDir { params.publish_dir }
  input:
    tuple val(meta), path (input_path), val (run_parameters)
    path esmfold_model_path
  output:
    tuple val (meta), path ("${meta.batch_name}/${meta.test}"), emit: pdb_dir
    path "${meta.batch_name}/${meta.test}.jsonl", emit: metrics_jsonl
  script:
  """
  set -euxo pipefail

  mkdir ${meta.batch_name}

  python3 ${moduleDir}/bin/esm_fold.py \
    --input_path=${input_path} \
    --output_dir=${meta.batch_name} \
    --name="${meta.test}" \
    --esmfold_model_path=${esmfold_model_path} \
    ${run_parameters}
  """
}

workflow {
  ESMFold(
    [
      [
        batch_name: params.output_dir, 
        test: "esmfold"], 
    params.input_path, params.run_parameters],
    params.esmfold_model_path
  )
}
