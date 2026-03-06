#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

INPUT_DIR_QUERY=$(pwd)/query_pdb
INPUT_DIR_TARGET=$(pwd)/target_pdb
OUTPUT_DIR=$(pwd)/test-foldseek-results

OVO_MODULE_PATH=$(ovo module)
WORKFLOW_ROOT=$(realpath "../../")

# Nextflow configs
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
WORKFLOW_CONFIG=$WORKFLOW_ROOT/protein-clustering/nextflow.config
USER_CONFIG_DIR=$(python -c "from ovo import config; print(config.dir)")
USER_CONFIG=$USER_CONFIG_DIR/nextflow_local.config

# Remove previous run results
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

# Unzip input PDB files if any exist
unzip -o "../pdb_query" -d "$INPUT_DIR_QUERY"
unzip -o "../pdb_target" -d "$INPUT_DIR_TARGET"

# PDB txt file (query the same as target)
rm -f input.txt
for file in $INPUT_DIR_QUERY/*.pdb; do
  # extract id from filename
  id=$(basename "$file" .pdb)
  echo "$file" >> input.txt
done
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb input.txt  \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR \
  --n_neighbors 10,30,100 \
  --chains A \
  --workflow_name "foldseek" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG"

cat **/*final_clustering.csv

#  PDB txt file  (query pdbs against different target pdbs)
rm -f input_query.txt
for file in $INPUT_DIR_QUERY/*.pdb; do
  # extract id from filename
  id=$(basename "$file" .pdb)
  echo "$file" >> input_query.txt
done
rm -f input_target.txt
for file in $INPUT_DIR_TARGET/*.pdb; do
  # extract id from filename
  id=$(basename "$file" .pdb)
  echo "$file" >> input_target.txt
done
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb input_query.txt \
  --target_pdb input_target.txt \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR \
  --n_neighbors 10,30,100 \
  --chains A \
  --workflow_name "foldseek" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG"

cat **/*final_clustering.csv

# PDB dir (just query pdbs against itself)
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR_QUERY/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR \
  --n_neighbors 10,30,100 \
  --chains A \
  --workflow_name "foldseek" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG"

cat **/*final_clustering.csv

# PDB dir (query pdbs against different target pdbs)
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --query_pdb $INPUT_DIR_QUERY/ \
  --target_pdb $INPUT_DIR_TARGET/ \
  --code_dir "$(ovo module)" \
  --publish_dir $OUTPUT_DIR \
  --n_neighbors 10,30,100 \
  --chains A \
  --workflow_name "foldseek" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG"

cat **/*final_clustering.csv

# Clean up extracted PDB files
rm -f "$INPUT_DIR_QUERY"/*.pdb 
rm -f "$INPUT_DIR_TARGET"/*.pdb