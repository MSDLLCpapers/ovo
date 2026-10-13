#!/bin/bash
set -ex

cd "$(dirname "$0")"

REFERENCE_FILES_DIR=${OVO_HOME:-~/ovo_config}/reference_files
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
WORK_DIR=${OVO_HOME:-~/ovo_config}/workdir/work
INPUT_DIR=$(pwd)/test-input
INPUT_FILE_NAME="ADP_ccd_100.json"
OUTPUT_DIR=$(pwd)/test-results

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
rm -rf "batch1"

# if singularity is available, use it
command -v singularity && PROFILE=singularity

nextflow run ../../main.nf \
  -profile ${PROFILE:-docker,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --input_json "${INPUT_DIR}/${INPUT_FILE_NAME}" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --num_designs "1" \
  --publish_dir "$OUTPUT_DIR" \
  --experiment "designable" \
  --effort "fast" \
  "$@"

ls -lR ${OUTPUT_DIR}/batch1/
