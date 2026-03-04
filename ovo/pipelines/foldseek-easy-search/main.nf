nextflow.enable.dsl = 2

process FoldseekEasySearch {
  def containerName = "foldseek"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label = 'foldseek'

  publishDir { params.publish_dir }
  input:
    val chains
    tuple \
      val(output_dir),
      path(query_pdb_dir, stageAs: 'query_dir'),
      path(target_pdb_dir, stageAs: 'target_dir')
    val exhaustive_search
    val e
    val alignment_type
    val format_output
    val c
    val s
  output:
    path "${output_dir}/foldseek_similarity.tsv"  , emit: similarity_tsv
  script:
  """
  set -euxo pipefail

  # Create output directory
  mkdir "${output_dir}"

  # Create a temporary directory for filtered PDBs
  mkdir -p filtered_query_pdbs
  mkdir -p filtered_target_pdbs

  # Copy PDB files to temporary directories
  cp ${query_pdb_dir}/*.pdb filtered_query_pdbs/
  cp ${target_pdb_dir}/*.pdb filtered_target_pdbs/

  # Filter the copied PDB files (not the originals)
  python3 ${moduleDir}/bin/filter_pdb.py --chains ${chains} --input_dir filtered_query_pdbs --min_length 14
  python3 ${moduleDir}/bin/filter_pdb.py --chains ${chains} --input_dir filtered_target_pdbs --min_length 14

  foldseek easy-search filtered_query_pdbs/ filtered_target_pdbs/ ${output_dir}/foldseek_similarity.tsv temp \
          ${exhaustive_search ? '--exhaustive-search' : ''} \
          -e ${e} \
          --alignment-type ${alignment_type} \
          --format-output ${format_output} \
          -c ${c} \
          -s ${s}

  # Remove temporary folder
  rm -r filtered_query_pdbs filtered_target_pdbs
  """
}

workflow {
  FoldseekEasySearch(
    params.chains,
    [params.output_dir, params.query_pdb_dir, params.target_pdb_dir],
    params.exhaustive_search,
    params.e,
    params.alignment_type,
    params.format_output,
    params.c,
    params.s
  )
}
