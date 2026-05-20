#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"


MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR=$(pwd)/test-input
OUTPUT_DIR=$(pwd)/test-results

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous result
rm -rf rfdiffusion

nextflow run ../../main.nf \
  -stub \
  -process.containerOptions="-v \"$MODELS_DIR:$MODELS_DIR\"" \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --input_pdb "$INPUT_DIR/5ELI.pdb" \
  --input_json_path "$INPUT_DIR/test_input_settings.json" \
  --settings_advanced "$INPUT_DIR/custom_settings_advanced.json" \
  --settings_filters "$INPUT_DIR/custom_settings_filters.json" \
  --time_limit_seconds 120 \
  --publish_dir $OUTPUT_DIR \
  --reference_files_dir "$MODELS_DIR" \
  "$@"

ls -l contig1_batch1/*/
