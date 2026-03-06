nextflow.enable.dsl = 2

include { FoldseekEasySearch } from '../foldseek-easy-search'
include { FoldseekEasyCluster } from '../foldseek-easy-cluster'
include { Umap } from './module/umap.nf'
include { createInputFolders as createInputFoldersQuery } from './module/createInputFolders.nf'
include { createInputFolders as createInputFoldersTarget } from './module/createInputFolders.nf'



workflow FoldseekClustering {
  take:
    query_pdb_dir
    target_pdb_dir
    n_neighbors
    output_dir
    chains
  main:
    //  Getting information about the foldseek similarity search
    println "1. Running foldseek similarity search"
    def search_input = query_pdb_dir.combine(target_pdb_dir).map {
            query_dir, target_dir -> tuple(output_dir, query_dir, target_dir)
        }
    def output_columns = "query,target,${params.foldseek_embedding_metric}"
    foldseek_similarity_search = FoldseekEasySearch(
        chains,
        search_input,
        params.foldseek_exhaustive_search,
        params.foldseek_e,
        params.foldseek_alignment_type,
        output_columns,
        params.foldseek_c,
        params.foldseek_s
    )

    println "2. Running foldseek clustering"
    // Run clustering on query set only
    def clustering_input = query_pdb_dir.map {
        query_dir -> tuple(output_dir, query_dir)
    }
    foldseek_clustering = FoldseekEasyCluster(
        chains,
        clustering_input,
        params.foldseek_tmscore_threshold,
        params.foldseek_c,
        params.foldseek_alignment_type,
        params.foldseek_min_seq_id
    )

    println "3. Running foldseek visualization"
    umap_results = Umap(
        foldseek_clustering.output_cluster_tsv,
        foldseek_similarity_search.similarity_tsv,
        "cluster_repr,cluster_member",
        output_columns,
        "cluster_member",
        "cluster_repr",
        "query",
        "target",
        params.foldseek_embedding_metric,
        n_neighbors,
        output_dir,
    )
}

workflow {
    [
        'query_pdb',
        'n_neighbors',
        'chains',
        'workflow_name'
    ].each { param ->
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }

    println "Nextflow version: ${nextflow.version}"
    println "Running Protein Clustering"

    def pdbPathsQuery
    if (params.query_pdb.endsWith('.txt')) {
        pdbPathsQuery = Channel.fromList(file(params.query_pdb).readLines())
    } else if (params.query_pdb.endsWith('.pdb')) {
        pdbPathsQuery = Channel.fromPath(params.query_pdb)
    } else if (params.query_pdb.endsWith('/')) {
        pdbPathsQuery = Channel.fromPath(params.query_pdb + '*.pdb')
    } else {
        throw new IllegalArgumentException("Input file must be a .txt file with a list of .pdb files, or a directory ending with /, got: ${params.query_pdb}")
    }
    // Group all files into a single query folder
    def pdbsQueryGrouped = pdbPathsQuery.collect()
    query_pdb_dir = createInputFoldersQuery(pdbsQueryGrouped, "query_pdb_dir")

    // When target is not set, the pipeline continues with comparing the pdbs with themselves
    if (!params.target_pdb) {
        params.target_pdb = params.query_pdb
        target_pdb_dir = query_pdb_dir
    } else {
        def pdbPathsTarget
        if (params.target_pdb.endsWith('.txt')) {
            pdbPathsTarget = Channel.fromList(file(params.target_pdb).readLines())
        } else if (params.target_pdb.endsWith('.pdb')) {
            pdbPathsTarget = Channel.fromPath(params.target_pdb)
        } else if (params.target_pdb.endsWith('/')) {
            pdbPathsTarget = Channel.fromPath(params.target_pdb + '*.pdb')
        } else {
            throw new IllegalArgumentException("Input file must be .txt file with a list of .pdb files, or a directory ending with /, got: ${params.target_pdb}")
        }

        // Group all files into a single target folder
        def pdbsTargetGrouped = pdbPathsTarget.collect()
        target_pdb_dir = createInputFoldersTarget(pdbsTargetGrouped, "target_pdb_dir")
    }
    // No processing in batches of chosen size: foldseek easy-cluster and easy-search need all structures in one batch: continue with default out folder
    output_dir = "contig1_batch1"

    // Run the selected workflow
    if (params.workflow_name == 'foldseek') {
        FoldseekClustering(query_pdb_dir.pdb_dir, target_pdb_dir.pdb_dir, params.n_neighbors, output_dir, params.chains)
    } else {
        throw new IllegalArgumentException("Workflow name ${params.workflow_name} not recognized!")
    }
}
