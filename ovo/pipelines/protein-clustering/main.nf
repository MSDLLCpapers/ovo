nextflow.enable.dsl = 2

include { FoldseekEasySearch } from '../foldseek-easy-search'
include { FoldseekEasyCluster } from '../foldseek-easy-cluster'
include { Umap } from './module/umap.nf'
include { createInputFolders as createInputFoldersQuery } from './module/createInputFolders.nf'
include { createInputFolders as createInputFoldersTarget } from './module/createInputFolders.nf'
include { DistanceMatrix } from '../biopython-hierarchical-clustering/main.nf'
include { HierarchicalClustering } from '../biopython-hierarchical-clustering/main.nf'


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
        params.foldseek_s,
        params.foldseek_prefilter_mode
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
        foldseek_clustering.output_cluster_tsv, // cluster_file
        foldseek_similarity_search.similarity_tsv, // similarity_file
        "cluster_repr,cluster_member", // cluster_file_columns
        output_columns, // similarity_file_columns
        "cluster_member", // clustering_index_column
        "cluster_repr", // clustering_repr_column
        "query", // similarity_query_column
        "target", // similarity_target_column
        params.foldseek_embedding_metric, // similarity_score_column
        "long",  // similarity_format
        false, // is_distance (foldseek outputs similarity)
        n_neighbors, // n_neighbors
        output_dir, // output_dir
    )
}

workflow HierarchicalClusteringWorkflow {
  take:
    query_pdb_dir
    output_dir
  main:
    dssp_file = params.hierarchical_dssp_csv ? file(params.hierarchical_dssp_csv) : file('NO_FILE')
    interface_residues_file = params.hierarchical_interface_residues_csv ? file(params.hierarchical_interface_residues_csv) : file('NO_FILE')

    // Create the input tuple for DistanceMatrix
    distance_input = query_pdb_dir.map { pdb_dir -> 
        tuple(output_dir, pdb_dir) 
    }

    distance_output = DistanceMatrix(
        params.chains,
        distance_input,
        params.hierarchical_cyclic,
        params.hierarchical_similarity_method,
        dssp_file,
        interface_residues_file
    )

   clustering_output = HierarchicalClustering(
        output_dir,
        distance_output.distance_matrix_csv,
        params.hierarchical_similarity_method,
        params.hierarchical_linkage_method,
        params.hierarchical_threshold,
        params.hierarchical_criterion
    )

    umap_results = Umap(
        clustering_output.similarity_clustering_csv, // cluster_file
        distance_output.distance_matrix_csv, // distance_file
        "",  // cluster_file_columns
        "",  // similarity_file_columns
        "ID", // clustering_index_column
        "Representative_ID", // clustering_repr_column
        "", // similarity_query_column - not used for matrix format
        "", // similarity_target_column - not used for matrix format
        "", // similarity_score_column - not used for matrix format
        "matrix",  // similarity_format
        true, // is_distance (hierarchical clustering outputs distance matrices)
        params.n_neighbors, // n_neighbors
        output_dir // output_dir
    )
}

workflow {
    // Common required parameters
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
    
    // Workflow-specific validation
    if (params.workflow_name == 'foldseek') {
        // Foldseek workflow uses query_pdb input
    } else if (params.workflow_name == 'hierarchical') {
        // Hierarchical workflow requires similarity method
        if (params.hierarchical_similarity_method == null) {
            throw new IllegalArgumentException("Argument --hierarchical_similarity_method is required for hierarchical clustering workflow!")
        }
        
        // Method-specific validation
        if (params.hierarchical_similarity_method == 'secondary_structure' && !params.hierarchical_dssp_csv) {
            throw new IllegalArgumentException("--hierarchical_dssp_csv is required for secondary_structure similarity method!")
        }
        if (params.hierarchical_similarity_method == 'interface_residues' && !params.hierarchical_interface_residues_csv) {
            throw new IllegalArgumentException("--hierarchical_interface_residues_csv is required for interface_residues similarity method!")
        }
    } else {
        throw new IllegalArgumentException("Workflow name ${params.workflow_name} not recognized! Supported: foldseek, hierarchical")
    }

    println "Nextflow version: ${nextflow.version}"
    println "Running Protein Clustering with workflow: ${params.workflow_name}"

    // Set output directory
    output_dir = "contig1_batch1"

    def pdbPathsQuery
    if (params.query_pdb.endsWith('.txt')) {
        pdbPathsQuery = Channel.fromList(file(params.query_pdb).readLines())
    } else if (params.query_pdb.endsWith('.pdb')) {
        pdbPathsQuery = Channel.fromPath(params.query_pdb)
    } else if (params.query_pdb.endsWith('/')) {
        pdbPathsQuery = Channel.fromPath(params.query_pdb + '*.pdb')
    } else if (params.query_pdb.endsWith('.csv')) {
        pdbPathsQuery = Channel.fromPath(params.query_pdb)
    } else {
        throw new IllegalArgumentException("Input file must be a .pdb file, a .csv file with sequences, a .txt file with a list of .pdb files, or a directory ending with /, got: ${params.query_pdb}")
    }
    // Group all files into a single query folder
    def pdbsQueryGrouped = pdbPathsQuery.collect()
    query_pdb_dir = createInputFoldersQuery(pdbsQueryGrouped, "query_pdb_dir")

    // Run the selected workflow
    if (params.workflow_name == 'foldseek') {
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
        
        FoldseekClustering(query_pdb_dir.pdb_dir, target_pdb_dir.pdb_dir, params.n_neighbors, output_dir, params.chains)
        
    } else if (params.workflow_name == 'hierarchical') {
        HierarchicalClusteringWorkflow(query_pdb_dir.pdb_dir, output_dir)
    } else {
        throw new IllegalArgumentException("Workflow name ${params.workflow_name} not recognized! Supported: foldseek, hierarchical")
    }
}
