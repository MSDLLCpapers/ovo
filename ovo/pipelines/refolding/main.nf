include { AlphaFoldInitialGuess } from '../alphafold-initial-guess'
include { ESMFold } from '../esmfold'
include { BoltzRefolding } from '../boltz-refolding'

process createDirs {
    executor 'local'
    input:
        tuple val(batch_name), path(design_paths), path(native_pdb)
    output:
        tuple val(batch_name), path("designs"), path(native_pdb)
    script:
    """
        mkdir designs
        cp ${design_paths} designs
    """
}

workflow Refolding {
    take:
        batches
        tests
        design_type
    main:
        def alphafold_tests = []
        def esmfold_tests = []
        def boltz_tests = []

        for (t in (tests ? tests.split(',') : [])) {
            def test = t // avoid groovy closure capture issue
            switch (test) {
                case ~/af2_.*/:
                    def matcher = (test =~ /af2_model_([0-9]_[a-z]+)_([a-z]+)_([0-9]+)rec/)

                    if (!matcher.matches()) {
                        throw new IllegalArgumentException("Test '${test}' does not match expected pattern: af2_model_<model>_<template>_<n>rec")
                    }

                    def (model, template, num_recycles) = matcher[0][1..3]

                    def args = ""
                    def expected_design_type = null
                    if (template == "ft") {
                      // default scaffold
                      expected_design_type = "scaffold"
                    } else if (template == "tt") {
                      // default binder
                      expected_design_type = "binder"
                    } else if (template == "binderalone") {
                      // binder alone, no template
                      args += " --no-templates --no-initial-guess --binder-alone "
                      expected_design_type = "binder"
                    } else if (template == "nt") {
                      args += " --no-templates"
                      expected_design_type = "scaffold"
                    } else if (template == "seq") {
                      // sequence only, no structure input at all
                      expected_design_type = "sequence"
                    } else if (template == "tbt") {
                      args += " --use-binder-template"
                      expected_design_type = "binder"
                    } else if (template == "ct") {
                      args += " --use-binder-template --use-interface-template"
                      expected_design_type = "binder"
                    } else {
                      throw new IllegalArgumentException("Unexpected template ${template} in test ${test}")
                    }

                    if (expected_design_type != design_type) {
                      throw new IllegalArgumentException("Design type ${design_type} incompatible with template ${template} in test ${test}, the test only supports design_type=${expected_design_type}")
                    }

                    if (model == "1_ptm") {
                      // default
                    } else if (model == "1_multimer") {
                      args += " --multimer"
                    } else {
                      throw new IllegalArgumentException("Unexpected model ${model} in test ${test}")
                    }

                    args += " --num-recycles ${num_recycles}"

                    alphafold_tests.add([test, design_type, args])

                    break
                case "esmfold":
                    if (design_type != "scaffold") {
                        throw new IllegalArgumentException("ESMFold refolding currently only supports scaffold design_type, got: ${design_type}")
                    }
                    def args = ""
                    // args += " --num-recycles ${num_recycles} "

                    esmfold_tests.add([test, args])
                    break
                case ~"boltz.*":
                    def version = null
                    def template = null
                    def args = ""
                    def expected_design_type = null

                    // Match naming convention: boltz<1|2>_<scaffold|binder>_<nt|tt|alone>
                    def matcher_new = (test =~ /boltz([12])_(scaffold|binder)_(nt|tt|alone)/)

                    if (matcher_new.matches()) {
                        def design_type_suffix
                        (version, design_type_suffix, template) = matcher_new[0][1..3]

                        // Validate design type matches suffix
                        if (design_type_suffix != design_type) {
                            throw new IllegalArgumentException("Design type ${design_type} does not match test name ${test} (expected ${design_type_suffix})")
                        }

                        // Set template args based on suffix
                        if (template == "nt") {
                            args += " --no-template "
                        } else if (template == "alone") {
                            // binder alone, no target and no template
                            if (design_type != "binder") {
                                throw new IllegalArgumentException("Template type 'alone' (binder alone) only valid for binder design_type, got: ${design_type}")
                            }
                            args += " --no-template --binder-alone "
                        } else if (template == "tt") {
                            if (design_type != "binder") {
                                throw new IllegalArgumentException("Template type 'tt' (target template) only valid for binder design_type, got: ${design_type}")
                            }
                            // Use target template (default behavior, no special args needed)
                        }
                    } else {
                        throw new IllegalArgumentException("Test '${test}' does not match expected pattern: boltz<1|2>_<scaffold|binder>_<nt|tt|alone>")
                    }

                    boltz_tests.add([test, design_type, args])
                    break
                default:
                    throw new IllegalArgumentException("Unknown refolding test: ${test}")
            }
        }

        pdb_dir = null
        af2_pdb_dir = null
        if (alphafold_tests) {
          println "AlphaFold2 tests:"
          alphafold_tests.each { println it }

          AlphaFoldInitialGuess(
              batches.combine(Channel.fromList(alphafold_tests)).map { batch, test, design_type, args ->
                  [[
                    batch_name: batch.batch_name,
                    test: test
                  ],
                  batch.native_pdb,
                  batch.batch_design_dir,
                  design_type,
                  args + (batch.cyclic ? " --cyclic " :  "") + " --designed_chains ${batch.designed_chains} "
                  ]
              },
              params.alphafold_models_path,
          )
          af2_pdb_dir = AlphaFoldInitialGuess.out.pdb_dir
          pdb_dir = af2_pdb_dir
        }

        esmfold_pdb_dir = null
        if (esmfold_tests) {
          ESMFold(
              batches.combine(Channel.fromList(esmfold_tests)).map { batch, test, args ->
                  [[
                    batch_name: batch.batch_name,
                    test: test,
                  ], 
                  batch.batch_design_dir, 
                  args + " --chain ${batch.designed_chains} " + (params.esmfold_fp16 ? " --fp16 " : "")
                  ]
              },
              params.esmfold_models_path
          )
          esmfold_pdb_dir = ESMFold.out.pdb_dir
          pdb_dir = esmfold_pdb_dir
        }

        if (boltz_tests) {
          BoltzRefolding(
              // batches.combine(Channel.fromList(boltz_tests)).map { batch_name, batch_design_dir, native_pdb, test, design_type, args ->
              batches.combine(Channel.fromList(boltz_tests)).map { batch, test, design_type, args ->
                  [[
                    batch_name: batch.batch_name,
                    test: test
                  ], 
                  batch.batch_design_dir, 
                  batch.native_pdb, 
                  design_type, 
                  args + (batch.cyclic ? " --cyclic " :  "") + " --designed_chains ${batch.designed_chains} "
                  ]
              },
              params.boltz_models_path
          )
        }
        // TODO add RMSD calculation step based on param with yaml rmsd specs
    emit:
      pdb_dir = pdb_dir // pdb_dir is a shorthand when running only one refolding test
      af2_pdb_dir = af2_pdb_dir
      esmfold_pdb_dir = esmfold_pdb_dir
}

workflow {
    def requiredParams = [
        'input_designs',
        'tests',
        'design_type',
        'designed_chains'
    ]
    requiredParams.each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }
    indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
	def inputBatches
	def batches
	def nativePdb = params.native_pdb ? params.native_pdb : "${projectDir}/lib/NO_FILE"
    if (params.input_designs.endsWith('.csv')) {
        // Sequence csv input, divide rows into batches (chunk files keep the .csv extension).
        // The csv chunk is passed directly as the design input, no design structure directory is needed.
        batches = Channel
          .fromPath(params.input_designs)
          .splitText(by: params.batch_size, file: true, keepHeader: true)
          .merge(indexes, { design_csv, idx -> ["contig1_batch${idx}", design_csv, nativePdb] })
    } else if (params.input_designs.endsWith('.txt')) {
        inputBatches = Channel
          .fromList(file(params.input_designs).readLines())
          .collate(params.batch_size)
          .merge(indexes, { design_paths, idx -> ["contig1_batch${idx}", design_paths, nativePdb] })
    } else if (params.input_designs.endsWith('/')) {
        // PDB directory, divide into batches
        inputBatches = Channel
          .fromPath(params.input_designs + '*.pdb')
          .collate(params.batch_size)
          .merge(indexes, { design_paths, idx -> ["contig1_batch${idx}", design_paths, nativePdb] })
    } else if (params.input_designs.endsWith('.pdb')) {
        // single PDB input, create one batch
        inputBatches = Channel
          .fromPath(params.input_designs)
          .map( design_path -> ["contig1_batch1", design_path, nativePdb] )
    } else {
        throw new IllegalArgumentException("Input designs must be a pdb file, a directory ending with /, a txt file (one path to pdb per line), or a csv file of sequences, got: ${params.input_designs}")
    }

    if (inputBatches) {
        createDirs(inputBatches)
        batches = createDirs.out
    }

    Refolding(
      batches.map({ batch_name, batch_design_dir, native_pdb -> [
        batch_name: batch_name,
        batch_design_dir: batch_design_dir,
        native_pdb: native_pdb,
        designed_chains: params.designed_chains,
        cyclic: params.cyclic
      ]}),
      params.tests,
      params.design_type
    )
}
