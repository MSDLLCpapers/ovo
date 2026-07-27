#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

INPUT_DIR=$(pwd)/test-input
OUTPUT_DIR=$(pwd)/test-results

WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
WORKFLOW_ROOT=$(realpath "../../")
MODULE_DIR=$(realpath "../")

# Nextflow configs
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
WORKFLOW_CONFIG=$WORKFLOW_ROOT/biotite-interface-metrics/nextflow.config
USER_CONFIG_DIR=$(python -c "from ovo import config; print(config.dir)")
USER_CONFIG=$USER_CONFIG_DIR/nextflow_local.config

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous result
rm -rf "batch1"

nextflow run ../../main.nf \
  -profile ${PROFILE:-docker,cpu_env} \
  -process.containerOptions="-v $MODULE_DIR:$MODULE_DIR" \
  --ovo_path "$OVO_MODULE_PATH" \
  --pdb_dir $INPUT_DIR \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  -config "$WORKFLOW_CONFIG" \
  -config "$USER_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --publish_dir $OUTPUT_DIR \
  --output_dir batch1 \
  --binder_chain A \
  --target_chain B \

cat batch1/biotite_interface_metrics.csv
