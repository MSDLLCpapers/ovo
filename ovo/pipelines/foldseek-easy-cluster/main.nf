nextflow.enable.dsl = 2

process FoldseekEasyCluster {
  def containerName = "foldseek"
  conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
  container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"
  label = 'foldseek'

  publishDir { params.publish_dir }
  input:
    val chains
    tuple val(output_prefix), path(pdb_dir)
    val tmscore_threshold
    val c
    val alignment_type
    val min_seq_id
  output:
    path "*_cluster.tsv"  , emit: output_cluster_tsv
    path "*_all_seqs.fasta"  , emit: all_seq_fasta
    path "*_rep_seq.fasta"  , emit: rep_seq_fasta
  script:
  """
  set -euxo pipefail

  # Create a temporary directory for filtered PDBs
  mkdir -p filtered_pdbs

  # Copy PDB files to temporary directory
  cp ${pdb_dir}/*.pdb filtered_pdbs/

  # Filter the copied PDB files (not the originals)
  python3 ${moduleDir}/bin/filter_pdb.py --chains ${chains} --input_dir filtered_pdbs

  # Run foldseek on the filtered copies
  foldseek easy-cluster filtered_pdbs ${output_prefix} tmp \
    -c ${c} \
    --tmscore-threshold ${tmscore_threshold} \
    --alignment-type ${alignment_type} \
    --min-seq-id ${min_seq_id} 

  # Remove temporary folder
  rm -r filtered_pdbs
  """
}

workflow {
  FoldseekEasyCluster(params.chains,[params.output_prefix, params.pdb_dir], params.tmscore_threshold, params.c, params.alignment_type, params.min_seq_id)
}
