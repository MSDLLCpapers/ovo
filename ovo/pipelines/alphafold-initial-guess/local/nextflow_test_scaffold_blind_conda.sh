#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

WORKFLOW_ROOT=$(realpath "../../")

MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR=$(pwd)/test-input/scaffold
NATIVE_PDB=$(pwd)/test-input/1A4I.pdb
OUTPUT_DIR=$(pwd)/test-results
CONFIG=$(pwd)/test.config

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous results
rm -rf batch1

# PDB file
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --max_memory 8GB \
  --design_type scaffold \
  --reference_files_dir "$MODELS_DIR" \
  --pdb_dir $INPUT_DIR \
  --native_pdb $NATIVE_PDB \
  --publish_dir $OUTPUT_DIR \
  --run_parameters "--no-templates --no-initial-guess" \
  $@

ls -lR batch1

cat batch1/initial_guess.jsonl
