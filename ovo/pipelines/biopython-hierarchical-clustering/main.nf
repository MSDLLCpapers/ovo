nextflow.enable.dsl = 2

process DistanceMatrix {
  def containerName = "python-structure"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label = 'distance-matrix'

  publishDir { params.publish_dir }
  input:
    val chains
    tuple val(output_dir), path(input_pdb_dir)
    val cyclic
    val similarity_method
    path dssp_csv, stageAs: 'dssp_input.csv'  // Make it optional
    path interface_residues_csv, stageAs: 'interface_residues_input.csv'  // Make it optional
  output:
    path "${output_dir}/${similarity_method}_distance_matrix.csv.gz" , emit: distance_matrix_csv
  script:
  def dssp_arg = (similarity_method == "secondary_structure" && dssp_csv.exists()) ? "--dssp_csv ${dssp_csv}" : ""
  def interface_residues_arg = (similarity_method == "interface_residues" && interface_residues_csv.exists()) ? "--interface_residues_csv ${interface_residues_csv}" : ""

  """
  set -euxo pipefail

  # Create output directory
  mkdir -p "${output_dir}"

  # Calculate distance matrix
  python3 ${moduleDir}/bin/calculate_distance_matrix.py \
    --input_dir "${input_pdb_dir}" \
    --output_matrix "${output_dir}/${similarity_method}_distance_matrix.csv.gz" \
    --chains "${chains}" \
    --method "${similarity_method}" \
    --cyclic ${cyclic} \
    ${dssp_arg} \
    ${interface_residues_arg}

  """
}

process HierarchicalClustering {
  def containerName = "python-structure"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label = 'hierarchical-clustering'

  publishDir { params.publish_dir }
  input:
    val output_dir
    path distance_matrix_csv
    val similarity_method
    val linkage_method
    val threshold
    val criterion
  output:
    path "${output_dir}/${similarity_method}_clustering.csv.gz"  , emit: similarity_clustering_csv
  script:
  """
  set -euxo pipefail

  # Create output directory
  mkdir -p "${output_dir}"

  python3 ${moduleDir}/bin/hierarchical_clustering.py \
    --similarity_csv "${distance_matrix_csv}" \
    --output_csv "${output_dir}/${similarity_method}_clustering.csv.gz" \
    --linkage_method "${linkage_method}" \
    --threshold "${threshold}" \
    --criterion "${criterion}"
  """
}

workflow {
  dssp_file = params.dssp_csv ? file(params.dssp_csv) : file('NO_FILE')
  interface_residues_file = params.interface_residues_csv ? file(params.interface_residues_csv) : file('NO_FILE')

  distance_output = DistanceMatrix(
    params.chains,
    [params.output_dir, params.input_pdb_dir],
    params.cyclic,
    params.similarity_method,
    dssp_file,
    interface_residues_file
  )

  HierarchicalClustering(
    params.output_dir,
    distance_output.distance_matrix_csv,
    params.similarity_method,
    params.linkage_method,
    params.threshold,
    params.criterion
  )
}