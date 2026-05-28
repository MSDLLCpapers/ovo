import argparse

import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--similarity_csv", type=str, required=True, help="Input CSV file containing similarity data")
    parser.add_argument("--output_csv", type=str, required=True, help="Path to output CSV file")
    parser.add_argument(
        "--linkage_method",
        type=str,
        default="average",
        help="Linkage method for hierarchical clustering (default: average)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        required=True,
        help="Threshold for cutting the dendrogram (valid range 0.0-1.0 for distance matrices)",
    )
    parser.add_argument(
        "--criterion", type=str, default="distance", help="Criterion for cutting the dendrogram (default: distance)"
    )

    args = parser.parse_args()

    similarity_df = pd.read_csv(args.similarity_csv, index_col=0)

    # Convert to numpy array
    similarity_matrix = similarity_df.values

    # Handle case with 1 entry
    if similarity_matrix.shape[0] == 1:
        print("Only one entry found in similarity matrix, assigning it to cluster 1")
        output_df = pd.DataFrame({"ID": similarity_df.index, "Cluster": [1]})
        output_df.to_csv(args.output_csv, index=False)
        exit(0)

    # Convert distance matrix to condensed distance matrix (upper triangle only)
    # scipy requires condensed format for linkage
    condensed_distances = squareform(similarity_matrix, checks=False)

    # Perform hierarchical clustering
    linkage_matrix = linkage(condensed_distances, method=args.linkage_method)

    # Cut dendrogram at threshold to get cluster assignments
    cluster_labels = fcluster(linkage_matrix, t=args.threshold, criterion=args.criterion)

    # Reorder cluster labels such that cluster 1 corresponds to the largest cluster, cluster 2 to the second largest, etc.
    # Count cluster sizes and create size-based mapping
    cluster_counts = pd.Series(cluster_labels).value_counts().sort_values(ascending=False)
    size_based_mapping = {old_id: new_id for new_id, old_id in enumerate(cluster_counts.index, 1)}

    # Remap cluster labels so largest cluster = 1, second largest = 2, etc.
    cluster_labels = np.array([size_based_mapping[label] for label in cluster_labels])

    output_df = pd.DataFrame({"ID": similarity_df.index, "Cluster": cluster_labels})

    # Use closest member to cluster centroid (medoid) as representative structure
    cluster_representatives = []
    for cluster_id in output_df["Cluster"].unique():
        # Filter distance matrix to only this cluster's members
        cluster_mask = cluster_labels == cluster_id
        sub_distance_matrix = similarity_df[cluster_mask].T[cluster_mask].T

        # Find the member with lowest average distance to others (closest to centroid)
        representative_id = sub_distance_matrix.mean().idxmin()

        cluster_representatives.append({"Cluster": cluster_id, "Representative_ID": representative_id})

    cluster_representatives = pd.DataFrame(cluster_representatives)
    output_df = output_df.merge(cluster_representatives, on="Cluster")

    # Save cluster assignments to CSV
    output_df.to_csv(args.output_csv, index=False)
