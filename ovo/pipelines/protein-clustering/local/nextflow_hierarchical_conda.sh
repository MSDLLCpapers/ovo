#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

INPUT_ZIP=$(pwd)/input.zip
INPUT_DIR=$(pwd)/input
OUTPUT_DIR=$(pwd)/test-hierarchical-results

INTERFACE_RESIDUES_CSV=$(pwd)/interface_residues_input.csv
DSSP_CSV=$(pwd)/dssp_input.csv

unzip -o "$INPUT_ZIP"

OVO_MODULE_PATH=$(ovo module)
WORKFLOW_ROOT=$(realpath "../../")

# Nextflow configs
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
WORKFLOW_CONFIG=$WORKFLOW_ROOT/protein-clustering/nextflow.config
USER_CONFIG_DIR=$(python -c "from ovo import config; print(config.dir)")
USER_CONFIG=$USER_CONFIG_DIR/nextflow_local.config

# Remove previous run results and create directories
if ls $OUTPUT_DIR/*/*/*csv 1> /dev/null 2>&1; then
    echo "Removing old csv files from $OUTPUT_DIR"
    rm $OUTPUT_DIR/*/*/*csv
fi
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "=== Testing Hierarchical Clustering with Multiple Similarity Methods ==="

# Test 1: Sequence similarity clustering
echo "--- Test 1: Sequence Similarity ---"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR/sequence \
  --n_neighbors 2 \
  --chains A \
  --workflow_name "hierarchical" \
  --hierarchical_similarity_method "sequence" \
  --hierarchical_cyclic false \
  --hierarchical_linkage_method "average" \
  --hierarchical_threshold 0.5 \
  --hierarchical_criterion "distance" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \
  -resume

echo "--- Sequence clustering results ---"
cat sequence/**/final_clustering.csv | head -20

# Test 2: Secondary structure similarity clustering
echo "--- Test 2: Secondary Structure Similarity ---"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR/secondary_structure \
  --n_neighbors 2 \
  --chains A \
  --workflow_name "hierarchical" \
  --hierarchical_similarity_method "secondary_structure" \
  --hierarchical_dssp_csv "$DSSP_CSV" \
  --hierarchical_cyclic false \
  --hierarchical_linkage_method "average" \
  --hierarchical_threshold 0.2 \
  --hierarchical_criterion "distance" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \
  -resume

echo "--- Secondary structure clustering results ---"
cat secondary_structure/**/final_clustering.csv | head -20

# Test 3: Interface residues similarity clustering
echo "--- Test 3: Interface Residues Similarity ---"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR/interface_residues \
  --n_neighbors 2 \
  --chains A \
  --workflow_name "hierarchical" \
  --hierarchical_similarity_method "interface_residues" \
  --hierarchical_interface_residues_csv "$INTERFACE_RESIDUES_CSV" \
  --hierarchical_cyclic false \
  --hierarchical_linkage_method "ward" \
  --hierarchical_threshold 0.5 \
  --hierarchical_criterion "distance" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \
  -resume

echo "--- Interface residues clustering results ---"
cat interface_residues/**/final_clustering.csv | head -20

# Test 4: RMSD similarity clustering
echo "--- Test 4: RMSD Similarity ---"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR/rmsd \
  --n_neighbors 2 \
  --chains A \
  --workflow_name "hierarchical" \
  --hierarchical_similarity_method "rmsd" \
  --hierarchical_cyclic false \
  --hierarchical_linkage_method "complete" \
  --hierarchical_threshold 5.0 \
  --hierarchical_criterion "distance" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \
  -resume

echo "--- RMSD clustering results ---"
cat rmsd/**/final_clustering.csv | head -20

echo "=== All Hierarchical Clustering Tests Complete ==="
echo "Results saved in: $OUTPUT_DIR"
echo "Available test directories:"
ls -la $OUTPUT_DIR/

