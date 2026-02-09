#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

REFERENCE_FILES_DIR=$(python -c "from ovo import config; print(config.reference_files_dir)")
WORK_DIR=$(python -c "from ovo import config; print(config.dir)")/workdir/work
OVO_MODULE_PATH=$(ovo module)
PLUGIN_MODULE_PATH=$(ovo module __MODULE_NAME__)
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
INPUT_DIR=$(pwd)/test-input
OUTPUT_DIR=$(pwd)/test-results

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous result
rm -rf contig1_batch1

nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --publish_dir $OUTPUT_DIR \
  --shared_modules "ovo:$OVO_MODULE_PATH,__MODULE_NAME__:$PLUGIN_MODULE_PATH" \
  --chains A \
  --input_pdb "$INPUT_DIR/" \
  $@

ls -lR contig1_batch1/*

head contig1_batch1/__MODULE_SUFFIX__.csv

