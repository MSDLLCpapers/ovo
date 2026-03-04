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
    return joined_embedding


def get_umap_embeddings(
    similarity_df: pd.DataFrame,
    query_column: str,
    target_column: str,
    score_column: str,
    n_neighbors: int = 50,
    n_components: int = 2,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    similarity_df: similarity DataFrame with columns containing columns specified by query_column, target_column, score_column
    query_column: name of the column with query IDs
    target_column: name of the column with target IDs
    score_column: name of the column with similarity scores
    n_neighbors: UMAP n_neighbors for balancing between local and global structure
    k: number of nearest neighbors to compute for each query (>= n_neighbors) in kNN
    metric: metric for NearestNeighbors ('cosine','euclidean', etc.)
    n_components: output embedding dimension
    """
    # remap IDs to contiguous integers
    idx = sorted(set(similarity_df[query_column]).union(set(similarity_df[target_column])))
    id_to_idx = {id_: i for i, id_ in enumerate(idx)}
    n = len(idx)

    indices = np.zeros((n, n_neighbors), dtype=np.int64)
    dists = np.zeros((n, n_neighbors), dtype=np.float32)
    for query_id, query_rows in similarity_df.groupby(query_column):
        top_rows = query_rows.sort_values(by=score_column, ascending=False).head(n_neighbors)
        top_target_ids = top_rows[target_column]
        top_scores = top_rows[score_column]
        if len(top_rows) < n_neighbors:
            # Pad with self-similarity if not enough neighbors
            pad_size = n_neighbors - len(top_rows)
            top_target_ids = pd.concat([pd.Series([query_id] * pad_size), top_target_ids])
            top_scores = pd.concat([pd.Series([1.0] * pad_size), top_scores])
        indices[id_to_idx[query_id]] = top_target_ids.apply(id_to_idx.get).to_numpy()
        dists[id_to_idx[query_id]] = np.clip(1 - top_scores.to_numpy(), 0, 1)

    # Pass precomputed knn to UMAP
    mapper = umap.UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        metric="precomputed",
        init="random",
        random_state=random_state,
        precomputed_knn=(indices, dists),
    )
    embedding = mapper.fit_transform(np.zeros((n, 1)))

    # Map embedding back to original query IDs
    df_embedding = pd.DataFrame(embedding, index=idx)
    df_embedding.rename(columns={0: f"umap_x_{n_neighbors}", 1: f"umap_y_{n_neighbors}"}, inplace=True)
    return df_embedding


def validate_neighbors_value(similarity_df: pd.DataFrame, n_neighbors, query_column: str = "query") -> list[str]:
    errors = []
    n_unique_queries = similarity_df[query_column].nunique()
    # Validate the number of input structures
    if n_unique_queries < 2:
        errors.append(f"Not enough unique queries passed (must be more than 2 - currently {n_unique_queries})")

    # Validate n_neighbors type
    if not n_neighbors.isdigit():
        errors.append(f"Invalid n_neighbors ({n_neighbors}): value must be integer.")
        return errors
    else:
        n_neighbors = int(n_neighbors)

    # Validate the n_neighbors value
    if n_neighbors < 2:
        errors.append("N_neighbors must be greater than 1")
    elif int(n_neighbors) > n_unique_queries:
        errors.append(f"N_neighbors ({n_neighbors}) exceeding possible neighbors ({n_unique_queries}).")

    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster_file", type=str, required=True)
    parser.add_argument("--similarity_file", type=str, required=True)
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
    parser.add_argument("--n_neighbors", type=str, required=True)
    parser.add_argument("--output_dir", type=str)
    options = parser.parse_args()

    os.mkdir(options.output_dir)

    if os.path.getsize(options.similarity_file) == 0:
        raise ValueError("Similarity file is empty")

    similarity_sep = "\t" if options.similarity_file.endswith(".tsv") else ","
    cluster_sep = "\t" if options.cluster_file.endswith(".tsv") else ","

    similarity_columns = options.similarity_file_columns.strip().split(",")
    cluster_columns = options.cluster_file_columns.strip().split(",")

    similarity_index_column = options.similarity_query_column
    cluster_index_column = options.clustering_index_column
    cluster_representative_column = options.clustering_repr_column

    score_col_idx = similarity_columns.index(options.similarity_score_column)

    # Read similarity file with or without header
    similarity_df = pd.read_csv(
        options.similarity_file,
        sep=similarity_sep,
        header=0 if options.similarity_file_has_header else None,
        dtype={score_col_idx: np.float32},
        names=None if options.similarity_file_has_header else similarity_columns,
    )

    # Read cluster file with or without header
    cluster_df = pd.read_csv(
        options.cluster_file,
        sep=cluster_sep,
        header=0 if options.cluster_file_has_header else None,
        names=None if options.cluster_file_has_header else cluster_columns,
    ).set_index(cluster_index_column)

    n_unique_queries = similarity_df[similarity_index_column].nunique()
    missing_ids = sorted(set(cluster_df.index) - set(similarity_df[similarity_index_column].unique()))
    if missing_ids:
        print(f"[Warning] {len(missing_ids)} design IDs are missing in the similarity file: {missing_ids}")
        print("Adding self-similarity entries for missing IDs.")
        # Add self-similarity entries for missing IDs
        similarity_df = pd.concat(
            [
                similarity_df,
                pd.DataFrame(
                    {
                        options.similarity_query_column: missing_ids,
                        options.similarity_target_column: missing_ids,
                        options.similarity_score_column: [1.0] * len(missing_ids),
                    }
                ),
            ]
        )
        n_unique_queries = similarity_df[similarity_index_column].nunique()

    # Compute embedding for each n_neighbor, handle failures without exceptions
    query_embeddings = []
    all_errors = []
    for n_neighbors in options.n_neighbors.split(","):
        error_messages = validate_neighbors_value(similarity_df, n_neighbors, query_column=similarity_index_column)
        embedding_df = None

        if not error_messages:
            # Compute embedding coords
            try:
                embedding_df = get_umap_embeddings(
                    similarity_df=similarity_df,
                    query_column=similarity_index_column,
                    target_column=options.similarity_target_column,
                    score_column=options.similarity_score_column,
                    n_neighbors=int(n_neighbors),
                    n_components=2,
                )
            except Exception as e:
                traceback.print_exc()
                error_messages = [str(e)]

        if embedding_df is None:
            nan_data = {
                f"umap_x_{n_neighbors}": [np.nan] * n_unique_queries,
                f"umap_y_{n_neighbors}": [np.nan] * n_unique_queries,
            }
            embedding_df = pd.DataFrame(nan_data, index=similarity_df[similarity_index_column].unique())
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
