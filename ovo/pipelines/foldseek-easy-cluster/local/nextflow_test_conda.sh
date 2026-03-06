#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

INPUT_DIR=$(pwd)/test-input
OUTPUT_DIR=$(pwd)/test-results

OVO_MODULE_PATH=$(ovo module)
WORKFLOW_ROOT=$(realpath "../../")

# Nextflow configs
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
WORKFLOW_CONFIG=$WORKFLOW_ROOT/foldseek-easy-cluster/nextflow.config
USER_CONFIG_DIR=$(python -c "from ovo import config; print(config.dir)")
USER_CONFIG=$USER_CONFIG_DIR/nextflow_local.config

# change to work dir
rm -rf "$OUTPUT_DIR"
mkdir "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  --ovo_path "$OVO_MODULE_PATH" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --output_prefix clustering_results \
  --pdb_dir $INPUT_DIR \
  --publish_dir $OUTPUT_DIR \
  --max-memory 8GB \
  --chains A \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG"

head *_cluster.tsv
