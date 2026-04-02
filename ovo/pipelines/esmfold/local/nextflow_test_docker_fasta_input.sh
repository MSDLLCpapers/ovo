#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

MODULE_DIR=$(realpath "../")

MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR=$(pwd)/test-input-fasta
PUBLISH_DIR=$(pwd)/test-results
OUTPUT_DIR="batch1"

# change to work dir
rm -rf "$PUBLISH_DIR"
mkdir "$PUBLISH_DIR"
cd "$PUBLISH_DIR"

nextflow run ../../main.nf \
  -process.containerOptions="-v $MODULE_ROOT:$TEST_MODULE_ROOT" \
  -profile ${PROFILE:-docker,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --input_path $INPUT_DIR \
  --output_dir $OUTPUT_DIR \
  --publish_dir $PUBLISH_DIR \
  --reference_files_dir "$MODELS_DIR"

