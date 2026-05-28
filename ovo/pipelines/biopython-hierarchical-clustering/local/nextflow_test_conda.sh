#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

INPUT_ZIP=$(pwd)/input.zip
INPUT_DIR=$(pwd)/input
OUTPUT_DIR=$(pwd)/test-results

INTERFACE_RESIDUES_CSV=$(pwd)/interface_residues_input.csv
DSSP_CSV=$(pwd)/dssp_input.csv

unzip -o "$INPUT_ZIP"

OVO_MODULE_PATH=$(ovo module)
WORKFLOW_ROOT=$(realpath "../../")

# Nextflow configs
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
WORKFLOW_CONFIG=$WORKFLOW_ROOT/biopython-hierarchical-clustering/nextflow.config
USER_CONFIG_DIR=$(python -c "from ovo import config; print(config.dir)")
USER_CONFIG=$USER_CONFIG_DIR/nextflow_local.config

# Clean up old results
if ls $OUTPUT_DIR/searching_results/*csv 1> /dev/null 2>&1; then
    echo "Removing old csv files from $OUTPUT_DIR"
    rm $OUTPUT_DIR/searching_results/*csv
fi
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --output_dir searching_results \
  --input_pdb_dir "$INPUT_DIR" \
  --publish_dir "$OUTPUT_DIR" \
  --max-memory 8GB \
  --chains A \
  --cyclic false \
  --threshold 0.5 \
  --similarity_method sequence \
  --interface_residues_csv "$INTERFACE_RESIDUES_CSV" \
  --dssp_csv "$DSSP_CSV" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \

gunzip -c */*distance_matrix.csv.gz | head -n 10
gunzip -c */*clustering.csv.gz | head -n 10