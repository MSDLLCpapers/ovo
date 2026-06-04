#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

MODELS_DIR=${OVO_HOME:-~/ovo_config}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo_config}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
LOCAL_OVERRIDE=$(pwd)/test_override.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR=$(pwd)/test-input
OUTPUT_DIR=$(pwd)/test-results-binder

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous result
#rm -rf $OUTPUT_DIR

nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --num_designs 1 \
  --contig "A25-35/0 10-15" \
  --input_structure_path "$INPUT_DIR/5ELI.pdb" \
  --publish_dir $OUTPUT_DIR \
  --reference_files_dir "$MODELS_DIR" \
  --hotspot "A31,A33" \
  --run_parameters " inference_sampler.num_timesteps=10 " \
  "$@"

ls -l rfdiffusion3/*/

#  --run_parameters " inference_sampler.step_scale=3 inference_sampler.gamma_0=0.2 " \
  #--spec_overrides '{\"select_hotspots\": {\"A31\": \"BKBN\", \"A33\": \"ALL\"}, \"unindex\": \"A55,A59\", \"length\": \"80-180\", \"infer_ori_strategy\": \"com\"}' \
  #--contig "A30-50/0 10" \
