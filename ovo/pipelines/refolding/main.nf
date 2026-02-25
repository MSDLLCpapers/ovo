include { AlphaFoldInitialGuess } from '../alphafold-initial-guess'
include { ESMFold } from '../esmfold'

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
        cyclic
    main:
        def alphafold_tests = []
        def esmfold_tests = []

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
                    } else if (template == "nt") {
                      args += " --no-templates"
                      expected_design_type = "scaffold"
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

                    if (cyclic) {
                        args += " --cyclic"
                    }

                    args += " --num-recycles ${num_recycles}"

                    alphafold_tests.add([test, design_type, args])

                    break
                case "esmfold":
                    if (design_type != "scaffold") {
                        throw new IllegalArgumentException("ESMFold refolding currently only supports scaffold design_type, got: ${design_type}")
                    }
                    esmfold_tests.add([test, 4])
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
              batches.combine(Channel.fromList(alphafold_tests)).map { batch_name, batch_design_dir, native_pdb, test, design_type, args ->
                  [[
                    batch_name: batch_name,
                    test: test
                  ], native_pdb, batch_design_dir, design_type, args]
              },
              params.alphafold_models_path,
          )
          af2_pdb_dir = AlphaFoldInitialGuess.out.pdb_dir
          pdb_dir = af2_pdb_dir
        }

        esmfold_pdb_dir = null
        if (esmfold_tests) {
          ESMFold(
              batches.combine(Channel.fromList(esmfold_tests)).map { batch_name, batch_design_dir, native_pdb, test, num_recycles ->
                  [[
                    batch_name: batch_name,
                    test: test,
                  ], batch_design_dir, num_recycles]
              },
              params.esmfold_models_path,
              params.esmfold_fp16
          )
          esmfold_pdb_dir = ESMFold.out.pdb_dir
          pdb_dir = esmfold_pdb_dir
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
        'design_type'
    ]
    requiredParams.each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }
    indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
	def inputBatches
	def nativePdb = params.native_pdb ? params.native_pdb : "${projectDir}/lib/NO_FILE"
    if (params.input_designs.endsWith('.txt')) {
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
        throw new IllegalArgumentException("Input designs must be a pdb file, a directory ending with /, or a txt file (one path to pdb per line), got: ${params.input_designs}")
    }

    createDirs(inputBatches)

    Refolding(createDirs.out, params.tests, params.design_type, params.cyclic)
}

