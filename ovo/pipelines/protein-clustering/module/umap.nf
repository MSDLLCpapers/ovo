nextflow.enable.dsl = 2

process Umap {
    def containerName = "protein-cluster"
    conda { params.getSharedEnv("ovo.${containerName}", workflow.profile) }
    container "${ workflow.containerEngine in ['singularity', 'apptainer']
    ? params.ovo_container_dir + '/ovo-' + containerName
    : params.docker_repository + 'ovo-' + containerName }"

    label 'clustering_processing'

    publishDir "${ params.publish_dir }"
    input:
        path cluster_file
        path similarity_file
        val cluster_file_columns
        val similarity_file_columns
        val clustering_index_column
        val clustering_repr_column
        val similarity_query_column
        val similarity_target_column
        val similarity_score_column
        val n_neighbors
        val output_dir
    output:
        path "${output_dir}/final_clustering.csv", emit: umap_results
    script:
    """
    set -euxo pipefail

    python3 ${projectDir}/bin/clustering_similarity_processing.py \
        --cluster_file ${cluster_file} \
        --similarity_file ${similarity_file} \
        --cluster_file_columns "${cluster_file_columns}" \
        --similarity_file_columns "${similarity_file_columns}" \
        --clustering_index_column "${clustering_index_column}" \
        --clustering_repr_column "${clustering_repr_column}" \
        --similarity_query_column "${similarity_query_column}" \
        --similarity_target_column "${similarity_target_column}" \
        --similarity_score_column "${similarity_score_column}" \
        --n_neighbors ${n_neighbors} \
        --output_dir "${output_dir}"
    """
}