#!/bin/bash

set -ex

# change to script dir
cd "$(dirname "$0")"

REFERENCE_FILES_DIR=$(python -c "from ovo import config; print(config.reference_files_dir)")
WORK_DIR=$(python -c "from ovo import config; print(config.dir)")/workdir/work
OVO_MODULE_PATH=$(ovo module)
DEFAULT_CONFIG=$OVO_MODULE_PATH/pipelines/nextflow_default.config
INPUT_DIR=$(pwd)/test-input-minibinder
OUTPUT_DIR=$(pwd)/test-results-minibinder

# change to work dir
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
# clear previous result
rm -rf *_mpnn

# Model type and weights are passed through run_parameters, see MPNN_WEIGHT_CONFIG
# and prepare_rfdiffusion_workflow_params()
base_run_parameters="--omit_AA \"CX\" --temperature 0.0001"

# ProteinMPNN
run_parameters="--model_type protein_mpnn --checkpoint_protein_mpnn \"model_params/proteinmpnn_v_48_020.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/protein_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# LigandMPNN
run_parameters="--model_type ligand_mpnn --checkpoint_ligand_mpnn \"model_params/ligandmpnn_v_32_010_25.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/ligand_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# SolubleMPNN
run_parameters="--model_type soluble_mpnn --checkpoint_soluble_mpnn \"model_params/solublempnn_v_48_020.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/soluble_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# PottsMPNN
run_parameters="--model_type protein_mpnn --checkpoint_protein_mpnn \"model_params/pottsmpnn_20.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/potts_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# Soluble PottsMPNN
run_parameters="--model_type protein_mpnn --checkpoint_protein_mpnn \"model_params/sol_pottsmpnn_20.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/soluble_potts_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# CyclicMPNN
run_parameters="--model_type protein_mpnn --checkpoint_protein_mpnn \"model_params/cyclicmpnn_48_010.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/cyclic_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

# HyperMPNN
run_parameters="--model_type protein_mpnn --checkpoint_protein_mpnn \"model_params/v48_030_epoch300_hyper.pt\" $base_run_parameters"
nextflow run ../../main.nf \
  -profile ${PROFILE:-conda,cpu_env} \
  -work-dir "$WORK_DIR" \
  -config "$DEFAULT_CONFIG" \
  --shared_modules "ovo:$OVO_MODULE_PATH" \
  --reference_files_dir "$REFERENCE_FILES_DIR" \
  --publish_dir $OUTPUT_DIR/hyper_mpnn \
  --pdb_path $INPUT_DIR \
  --num_seq_per_target 2 \
  --run_parameters "$run_parameters" \
  "$@"

ls -lR ${OUTPUT_DIR}/
