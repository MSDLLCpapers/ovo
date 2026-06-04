import os
import argparse
import traceback

import pandas as pd
import numpy as np
import umap


def join_embedding_with_cluster(
    similarity_df: pd.DataFrame, cluster_df: pd.DataFrame, cluster_repr_column: str = "cluster_repr"
) -> pd.DataFrame:
    joined_embedding = similarity_df.join(cluster_df, how="inner")
    # Add cluster_id column: assign a unique integer to each cluster_repr in order of decreasing cluster size (largest cluster gets ID 1)
    cluster_repr_to_id = {
        repr_: i for i, repr_ in enumerate(joined_embedding[cluster_repr_column].value_counts().index, start=1)
    }
    joined_embedding["cluster_id"] = joined_embedding[cluster_repr_column].map(cluster_repr_to_id)
    joined_embedding.rename(columns={cluster_repr_column: "cluster_repr"}, inplace=True)
    return joined_embedding


def get_umap_embeddings_from_long_format(
    df: pd.DataFrame,
    query_column: str,
    target_column: str,
    score_column: str,
    n_neighbors: int,
    is_similarity: bool = True,
    n_components: int = 2,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Create UMAP embeddings from long format similarity or distance data.
    Extracts kNN from the long format data and passes to UMAP.

    Args:
        df: DataFrame with query, target, score columns
        query_column: name of the query column
        target_column: name of the target column
        score_column: name of the score column
        n_neighbors: number of neighbors to retrieve for UMAP
        is_similarity: if True, data contains similarity scores (higher = more similar);
                      if False, data contains distances (lower = more similar)
        n_components: output embedding dimension
        random_state: random seed
    Returns:
        DataFrame with UMAP coordinates
    """
    # Remap IDs to contiguous integers
    idx = sorted(set(df[query_column]).union(set(df[target_column])))
    id_to_idx = {id_: i for i, id_ in enumerate(idx)}
    n = len(idx)

    indices = np.zeros((n, n_neighbors), dtype=np.int64)
    dists = np.zeros((n, n_neighbors), dtype=np.float32)

    for query_id, query_rows in df.groupby(query_column):
        # Sort: descending for similarity (highest first), ascending for distance (lowest first)
        top_rows = query_rows.sort_values(by=score_column, ascending=not is_similarity).head(n_neighbors)
        top_target_ids = top_rows[target_column]
        top_scores = top_rows[score_column]

        if len(top_rows) < n_neighbors:
            # Pad with self-score if not enough neighbors
            pad_size = n_neighbors - len(top_rows)
            top_target_ids = pd.concat([pd.Series([query_id] * pad_size), top_target_ids])
            # Pad with 1.0 for similarity (perfect match), 0.0 for distance (zero distance to self)
            pad_value = 1.0 if is_similarity else 0.0
            top_scores = pd.concat([pd.Series([pad_value] * pad_size), top_scores])

        indices[id_to_idx[query_id]] = top_target_ids.apply(id_to_idx.get).to_numpy()

        # Convert similarity to distance if needed, otherwise use scores as is
        if is_similarity:
            dists[id_to_idx[query_id]] = np.clip(1 - top_scores.to_numpy(), 0, 1)
        else:
            dists[id_to_idx[query_id]] = top_scores.to_numpy()

    # Create UMAP embeddings from precomputed kNN
    mapper = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric="precomputed",
        init="random",
        random_state=random_state,
        precomputed_knn=(indices, dists),
    )
    embedding = mapper.fit_transform(np.zeros((n, 1)))

    # Create DataFrame with original IDs as index
    df_embedding = pd.DataFrame(embedding, index=idx)
    df_embedding.rename(columns={0: f"umap_x_{n_neighbors}", 1: f"umap_y_{n_neighbors}"}, inplace=True)

    return df_embedding


def get_umap_embeddings_from_matrix(
    distance_matrix: pd.DataFrame,
    n_neighbors: int,
    n_components: int = 2,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Create UMAP embeddings from a full pairwise distance matrix.
    UMAP will internally compute kNN from the distance matrix.

    Args:
        distance_matrix: DataFrame with pairwise distances (square matrix)
        n_neighbors: UMAP n_neighbors for balancing between local and global structure
        n_components: output embedding dimension
        random_state: random seed
    Returns:
        DataFrame with UMAP coordinates
    """

    if n_neighbors >= len(distance_matrix):
        print(f"N_neighbors {n_neighbors} exceeds number of samples, setting to {len(distance_matrix) - 1}")

    mapper = umap.UMAP(
        n_neighbors=min(n_neighbors, len(distance_matrix) - 1),
        n_components=n_components,
        metric="precomputed",
        init="random",
        random_state=random_state,
    )
    embedding = mapper.fit_transform(distance_matrix.values)
    df_embedding = pd.DataFrame(embedding, index=distance_matrix.index)
    df_embedding.rename(columns={0: f"umap_x_{n_neighbors}", 1: f"umap_y_{n_neighbors}"}, inplace=True)
    return df_embedding


def validate_neighbors_value(n_neighbors: str) -> list[str]:
    """Validate there are enough neighbors for UMAP embedding and that n_neighbors is a valid integer."""
    errors = []

    # Validate n_neighbors type
    if not n_neighbors.isdigit():
        errors.append(f"Invalid n_neighbors ({n_neighbors}): value must be integer.")
        return errors
    else:
        n_neighbors_int = int(n_neighbors)

    # Validate the n_neighbors value
    if n_neighbors_int < 2:
        errors.append("N_neighbors must be greater than 1")

    return errors


def validate_matrix(matrix: pd.DataFrame, is_similarity: bool = True) -> list[str]:
    """
    Validate that the matrix has expected properties for similarity or distance matrix.

    Args:
        matrix: DataFrame with pairwise scores
        is_similarity: if True, expect similarity matrix; if False, expect distance matrix
    Returns:
        List of warning messages (empty if validation passes)
    Raises:
        ValueError: if matrix is not square (critical error)
    """
    warnings = []

    # Check if matrix is square - this is a critical error
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(
            f"Matrix must be square for pairwise distance/similarity computation. Got shape {matrix.shape}"
        )

    # Check diagonal values
    diagonal = np.diag(matrix.values)
    expected_diagonal = 1.0 if is_similarity else 0.0
    matrix_type = "similarity" if is_similarity else "distance"

    # Check if diagonal is close to expected value
    if not np.allclose(diagonal, expected_diagonal, atol=1e-6):
        unique_diag = np.unique(diagonal.round(6))
        warnings.append(
            f"Diagonal values unexpected for {matrix_type} matrix. "
            f"Expected {expected_diagonal}, found values: {unique_diag[:10]}"
        )

    # Check symmetry
    if not np.allclose(matrix.values, matrix.values.T, atol=1e-6):
        warnings.append("Matrix is not symmetric")

    # Check value range
    min_val = matrix.min().min()
    max_val = matrix.max().max()

    if is_similarity:
        # Similarity should be in [0, 1]
        if min_val < -1e-6 or max_val > 1 + 1e-6:
            warnings.append(f"Similarity values outside [0, 1] range: min={min_val:.6f}, max={max_val:.6f}")
    else:
        # Distance should be non-negative
        if min_val < -1e-6:
            warnings.append(f"Distance values are negative: min={min_val:.6f}")

    return warnings


def fill_missing_ids_in_matrix(
    matrix: pd.DataFrame, cluster_ids: list[str], is_similarity: bool = True
) -> pd.DataFrame:
    """
    Fill missing IDs in a pairwise matrix with appropriate self-scores.

    Args:
        matrix: DataFrame with IDs as index and columns
        cluster_ids: List of cluster IDs to check for
        is_similarity: if True, uses self-similarity = 1.0; if False, uses self-distance = 0.0
    Returns:
        Updated DataFrame with missing IDs filled
    """
    missing_ids = sorted(set(cluster_ids) - set(matrix.index))
    if missing_ids:
        matrix_type = "similarity" if is_similarity else "distance"
        print(f"[Warning] {len(missing_ids)} design IDs are missing in the {matrix_type} matrix: {missing_ids}")
        print(f"Adding self-{matrix_type} entries for missing IDs.")

        # Determine self-score and other-score based on matrix type
        if is_similarity:
            self_score = 1.0  # Perfect similarity with self
            other_score = 0.0  # No similarity with others (most dissimilar)
        else:
            self_score = 0.0  # Zero distance to self
            other_score = float("inf")  # Infinite distance to others (we'll use a large value)

        # Add missing IDs to matrix
        for missing_id in missing_ids:
            # Set very low similarity / very high distance to all other structures
            matrix.loc[missing_id, :] = other_score if not is_similarity else other_score
            matrix.loc[:, missing_id] = other_score if not is_similarity else other_score
            # Set perfect self-score
            matrix.loc[missing_id, missing_id] = self_score
    return matrix


def fill_missing_ids_in_similarity_long_format(
    df: pd.DataFrame,
    cluster_ids: list[str],
    query_column: str,
    target_column: str,
    score_column: str,
    is_similarity: bool = True,
) -> pd.DataFrame:
    """
    Fill missing IDs in long format pairwise score data.

    Args:
        df: DataFrame with query, target, score columns
        cluster_ids: List of cluster IDs to check for
        query_column: name of the query column
        target_column: name of the target column
        score_column: name of the score column
        is_similarity: if True, uses self-similarity = 1.0; if False, uses self-distance = 0.0
    Returns:
        Updated DataFrame with missing IDs filled
    """
    missing_ids = sorted(set(cluster_ids) - set(df[query_column].unique()))
    if missing_ids:
        matrix_type = "similarity" if is_similarity else "distance"
        print(f"[Warning] {len(missing_ids)} design IDs are missing in the {matrix_type} file: {missing_ids}")
        print(f"Adding self-{matrix_type} entries for missing IDs.")
        # Determine self-score based on matrix type
        self_score = 1.0 if is_similarity else 0.0
        # Add self-score entries for missing IDs
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    {
                        query_column: missing_ids,
                        target_column: missing_ids,
                        score_column: [self_score] * len(missing_ids),
                    }
                ),
            ]
        )
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster_file", type=str, required=True)
    parser.add_argument(
        "--similarity_file",
        type=str,
        required=True,
        help="File containing pairwise similarity or distance scores. Can be in long format (query, target, score) or matrix format (square matrix with IDs as index and columns). If the file is distance use --is_distance",
    )
    parser.add_argument("--cluster_file_columns", type=str, default="cluster_repr,cluster_member")
    parser.add_argument("--similarity_file_columns", type=str, required=True)
    parser.add_argument("--cluster_file_has_header", action="store_true", help="Set if cluster file has header row")
    parser.add_argument(
        "--similarity_file_has_header", action="store_true", help="Set if similarity file has header row"
    )
    parser.add_argument("--clustering_index_column", type=str, default="cluster_member")
    parser.add_argument("--clustering_repr_column", type=str, default="cluster_repr")
    parser.add_argument("--similarity_query_column", type=str, default="query")
    parser.add_argument("--similarity_target_column", type=str, default="target")
    parser.add_argument("--similarity_score_column", type=str, required=True)
    parser.add_argument(
        "--similarity_format",
        type=str,
        default="long",
        choices=["long", "matrix"],
        help="Format of similarity file: 'long' (query, target, score) or 'matrix' (NxN matrix)",
    )
    parser.add_argument(
        "--is_distance",
        action="store_true",
        help="Set if the input contains distance scores (lower = more similar). "
        "If not set, input is treated as similarity scores (higher = more similar).",
    )
    parser.add_argument("--n_neighbors", type=str, required=True)
    parser.add_argument("--output_dir", type=str)
    options = parser.parse_args()

    # Determine if input is similarity or distance
    is_similarity = not options.is_distance

    os.makedirs(options.output_dir, exist_ok=True)

    # For symlinks, follow to the target; for compressed files, check actual file size
    file_size = os.path.getsize(os.path.realpath(options.similarity_file))
    if file_size == 0:
        raise ValueError(f"Similarity file is empty: {options.similarity_file}")

    similarity_sep = "\t" if options.similarity_file.endswith(".tsv") else ","
    cluster_sep = "\t" if options.cluster_file.endswith(".tsv") else ","

    similarity_columns = options.similarity_file_columns.strip().split(",")
    cluster_columns = options.cluster_file_columns.strip().split(",")

    similarity_index_column = options.similarity_query_column
    similarity_target_column = options.similarity_target_column
    similarity_score_column = options.similarity_score_column
    cluster_index_column = options.clustering_index_column
    cluster_representative_column = options.clustering_repr_column

    # Read similarity file
    if options.similarity_format == "matrix":
        # For matrix format, read directly as matrix
        similarity_data = pd.read_csv(
            options.similarity_file,
            sep=similarity_sep,
            header=0 if options.similarity_file_has_header else None,
            index_col=0,
        )
        # For validation, we need to know unique queries
        similarity_index_column = similarity_data.index.name or "index"
    elif options.similarity_format == "long":
        # Handle column specifications
        if options.similarity_file_has_header:
            # File has header - use column names directly
            dtype_spec = {similarity_score_column: np.float32}
            names_spec = None
            header_spec = 0
        else:
            # File has no header - need explicit column names
            if not options.similarity_file_columns or options.similarity_file_columns.strip() == "":
                raise ValueError("similarity_file_columns must be provided when similarity_file_has_header is False")

            similarity_columns = options.similarity_file_columns.strip().split(",")
            score_col_idx = similarity_columns.index(similarity_score_column)
            dtype_spec = {score_col_idx: np.float32}
            names_spec = similarity_columns
            header_spec = None

        # Long format - read as DataFrame
        similarity_data = pd.read_csv(
            options.similarity_file,
            sep=similarity_sep,
            header=header_spec,
            dtype=dtype_spec,
            names=names_spec,
        )
    else:
        raise ValueError("Please use either 'long' or 'matrix' format")

    # Read cluster file with or without header
    cluster_df = pd.read_csv(
        options.cluster_file,
        sep=cluster_sep,
        header=0 if options.cluster_file_has_header else None,
        names=None if options.cluster_file_has_header else cluster_columns,
    ).set_index(cluster_index_column)
    cluster_ids = cluster_df.index.tolist()

    # Handle missing IDs in similarity data
    if options.similarity_format == "matrix":
        similarity_data = fill_missing_ids_in_matrix(similarity_data, cluster_ids, is_similarity)
    elif options.similarity_format == "long":
        similarity_data = fill_missing_ids_in_similarity_long_format(
            similarity_data,
            cluster_ids,
            similarity_index_column,
            similarity_target_column,
            similarity_score_column,
            is_similarity,
        )

    # Validate matrix format data
    if options.similarity_format == "matrix":
        validation_warnings = validate_matrix(similarity_data, is_similarity)
        if validation_warnings:
            print("[Validation Warnings]")
            for warning in validation_warnings:
                print(f"  - {warning}")

    # Get number of unique queries
    if options.similarity_format == "matrix":
        empty_index = similarity_data.index
    elif options.similarity_format == "long":
        if not similarity_index_column:
            raise ValueError("query_column is required for long format")
        empty_index = similarity_data[similarity_index_column].unique()
    else:
        raise ValueError("Please use either 'long' or 'matrix' format")

    # Compute embedding for each n_neighbor, handle failures without exceptions
    query_embeddings = []
    all_errors = []
    for n_neighbors in options.n_neighbors.split(","):
        error_messages = validate_neighbors_value(n_neighbors)
        all_errors.extend(error_messages)

        embedding_df = None

        if not error_messages:
            try:
                if options.similarity_format == "matrix":
                    distance_matrix = similarity_data.copy()
                    if is_similarity:
                        # Convert similarity to distance: distance = 1 - similarity
                        distance_matrix = 1 - distance_matrix
                        distance_matrix = distance_matrix.clip(lower=0)

                    embedding_df = get_umap_embeddings_from_matrix(
                        distance_matrix=distance_matrix,
                        n_neighbors=int(n_neighbors),
                    )
                elif options.similarity_format == "long":
                    # For long format, extract kNN and create UMAP embeddings
                    embedding_df = get_umap_embeddings_from_long_format(
                        df=similarity_data,
                        query_column=similarity_index_column,
                        target_column=similarity_target_column,
                        score_column=similarity_score_column,
                        n_neighbors=int(n_neighbors),
                        is_similarity=is_similarity,
                    )

            except Exception as e:
                traceback.print_exc()
                error_messages = [str(e)]

        if embedding_df is None:
            nan_data = {
                f"umap_x_{n_neighbors}": [np.nan] * len(empty_index),
                f"umap_y_{n_neighbors}": [np.nan] * len(empty_index),
            }
            embedding_df = pd.DataFrame(nan_data, index=empty_index)
        query_embeddings.append(embedding_df)
        all_errors.extend(error_messages)

    embedding_df = pd.concat(query_embeddings, axis=1)
    embedding_df["error"] = ";".join(list(set(all_errors)))

    joined_embedding_df = join_embedding_with_cluster(
        embedding_df, cluster_df, cluster_repr_column=cluster_representative_column
    )
    joined_embedding_df.reset_index(drop=False).rename(columns={"index": "id"}).to_csv(
        os.path.join(options.output_dir, "final_clustering.csv"), index=False
    )
