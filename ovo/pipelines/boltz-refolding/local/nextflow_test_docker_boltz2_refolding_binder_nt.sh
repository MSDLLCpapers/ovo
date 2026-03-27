#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

MODULE_DIR=$(realpath "../")

MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DIR_PREFIX=$(pwd)/test-input
INPUT_DIR=${INPUT_DIR_PREFIX}/binder
TEMPLATE_PDB_NO_FILE="${INPUT_DIR_PREFIX}/references/NO_FILE"
OUTPUT_DIR=$(pwd)/test-results-binder-nt

# change to work dir
rm -rf "$OUTPUT_DIR"
mkdir "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

nextflow run ../../main.nf \
  -process.containerOptions="-v ${MODULE_DIR}:${MODULE_DIR}" \
  -profile ${PROFILE:-docker,cpu_env} \
  -work-dir "${WORK_DIR}" \
  -config "${DEFAULT_CONFIG}" \
  --shared_modules "ovo:${OVO_MODULE_PATH}" \
  --input_dir "${INPUT_DIR}" \
  --publish_dir "${OUTPUT_DIR}" \
  --reference_files_dir "${MODELS_DIR}" \
  --output_dir batch1 \
  --max-memory 16GB \
  --boltz_version boltz2_binder_nt \
  --design_type binder \
  --native_pdb "${TEMPLATE_PDB_NO_FILE}" \
  --run_parameters " --no-template --cyclic --designed_chains A " \
  $@

head batch1/boltz2_binder_nt/*/*.cif
