#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

WORKFLOW_ROOT=$(realpath "../../")

MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR=$(pwd)/test-input/partial_diff
OUTPUT_DIR=$(pwd)/test-results
CONFIG=$(pwd)/test.config

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous results
rm -rf batch1

nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --max_memory 8GB \
  --pdb_dir $INPUT_DIR \
  --publish_dir $OUTPUT_DIR \
  --relax_cycles 1 \
  --run_parameters " -debug " \
  "$@"

pwd
ls -l batch1/proteinmpnn_fastrelax/


