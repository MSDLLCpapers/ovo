#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

WORKFLOW_ROOT=$(realpath "../../")

MODELS_DIR=${OVO_HOME:-~/ovo}/reference_files
WORK_DIR=${OVO_HOME:-~/ovo}/workdir/work
DEFAULT_CONFIG=$(pwd)/../../nextflow_default.config
OVO_MODULE_PATH=$(realpath "$PWD/../../../")
INPUT_DESIGNS=$(pwd)/test-input/scaffold/
NATIVE_PDB=$(pwd)/../lib/NO_FILE
OUTPUT_DIR=$(pwd)/test-results
CONFIG=$(pwd)/test.config

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous results
[ -e contig1_batch1 ] && rm -rf contig1_batch1

# PDB file
nextflow run ../../main.nf \
  -profile ${PROFILE:-docker,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --design_type scaffold \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --max_memory 8GB \
  --reference_files_dir "$MODELS_DIR" \
  --input_designs "$INPUT_DESIGNS" \
  --native_pdb "$NATIVE_PDB" \
  --batch_size 1 \
  --tests af2_model_1_ptm_nt_3rec,esmfold,boltz2_scaffold_nt \
  --publish_dir $OUTPUT_DIR \
  --chains A \
  $@

echo "Execution dir: $(pwd)"

head contig1_batch*/*.jsonl
