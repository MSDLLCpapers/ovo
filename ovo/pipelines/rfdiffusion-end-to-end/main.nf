include { RFdiffusion } from params.getSharedPipelinePath("ovo.rfdiffusion-backbone")
include { RFdiffusion3 } from params.getSharedPipelinePath("ovo.rfdiffusion3-backbone")
include { LigandMpnn } from params.getSharedPipelinePath("ovo.ligandmpnn-sequence-design")
include { ProteinMPNN_Fast_Relax } from params.getSharedPipelinePath("ovo.proteinmpnn-fastrelax")
include { BackboneMetrics } from params.getSharedPipelinePath("ovo.backbone-metrics")
include { PyRosettaInterfaceMetrics } from params.getSharedPipelinePath("ovo.pyrosetta-interface-metrics")
include { ProteinQC } from params.getSharedPipelinePath("ovo.proteinqc")
include { Refolding } from params.getSharedPipelinePath("ovo.refolding")

def requiredParams = [
	'design_type',
	'rfdiffusion_input_pdb',
]
requiredParams.each { param ->
    params[param] = null // this sets null as default, to avoid printing warning
    if (!params[param]) {
        throw new IllegalArgumentException("Argument --${param} is required!")
    }
}
if (!params.custom_backbones && !params.rfdiffusion_contig) {
    throw new IllegalArgumentException("One of --rfdiffusion_contig or --custom_backbones must be provided!")
}


workflow {
	if (params.rfdiffusion_run_parameters.contains('hotspot_res')) {
        throw new IllegalArgumentException("RFdiffusion hotspot_res should not be provided in --rfdiffusion_run_parameters but as --hotspot.")
	}
	def pdb_inputs
    if (params.rfdiffusion_input_pdb.endsWith('.txt')) {
        pdb_inputs = file(params.rfdiffusion_input_pdb).readLines()
    } else if (params.rfdiffusion_input_pdb.endsWith('.pdb')) {
        pdb_inputs = [params.rfdiffusion_input_pdb]
    } else {
        throw new IllegalArgumentException("Input file must be a .pdb file, a .txt file with a list of .pdb files, got: ${params.rfdiffusion_input_pdb}")
    }
    def batches
    if (params.custom_backbones) {
      println "Using custom backbones from directory: ${params.custom_backbones}"

      if (pdb_inputs.size() > 1) {
          throw new IllegalArgumentException("When using --custom_backbones, only one input pdb should be provided, got ${pdb_inputs.size()}: ${params.rfdiffusion_input_pdb}")
      }
      def backbone_paths
      if (params.custom_backbones.endsWith('.txt')) {
          backbone_paths = Channel.fromList(file(params.custom_backbones).readLines())
      } else if (params.custom_backbones.endsWith('.pdb')) {
          backbone_paths = Channel.fromPath(params.custom_backbones)
      } else if (params.custom_backbones.endsWith('.zip')) {
          backbone_paths = UnpackBackbones(Channel.fromPath(params.custom_backbones))
      } else if (params.custom_backbones.endsWith('/')) {
          backbone_paths = Channel.fromPath(params.custom_backbones + '*.pdb')
      } else {
          throw new IllegalArgumentException("Input file must be a .pdb file, a .txt file with a list of .pdb files, or a directory ending with /, got: ${params.custom_backbones}")
      }
      def file_list = backbone_paths.collate(params.batch_size)
      indexes = Channel.of(1..(1000000.intdiv(params.batch_size)))
      CreateBackboneFolders(
        file_list.merge(indexes, { files, idx -> ["contig1_batch${idx}", files] })
      )

      batches = file_list.merge(indexes, { _, idx -> ["contig1_batch${idx}", pdb_inputs[0]] })
      backbones_dir = CreateBackboneFolders.out.pdb_dir
    } else {
      def contigs = "${params.rfdiffusion_contig}".split(",")
      if (pdb_inputs.size() != contigs.size()) {
          if (pdb_inputs.size() == 1) {
              // use same pdb for all contigs
              pdb_inputs = (1..contigs.size()).collect { pdb_inputs[0] }
          } else {
              throw new IllegalArgumentException("There should be one input pdb for each contig (${contigs.size()}), or one input pdb, got ${pdb_inputs.size()}: ${params.rfdiffusion_input_pdb}")
          }
      }

      def rfd_input_batches = (1..pdb_inputs.size()).collectMany {
          i -> (1..params.rfdiffusion_num_designs).collate(params.batch_size).withIndex().collect {
              items, j -> ["contig${i}_batch${j+1}", pdb_inputs[i-1], contigs[i-1], items.size()]
          }
      }
      batches = Channel.fromList(rfd_input_batches.collect {
        batch -> [batch[0], batch[1]] // only keep batch name and pdb input for downstream steps
      })

      println "Generating RFdiffusion batches:"
      rfd_input_batches.each { println it }

      if (params.backbone_generator == "rfdiffusion") {
        RFdiffusion(
            Channel.fromList(rfd_input_batches),
            params.rfdiffusion_models_path,
            params.hotspot,
            false,
            params.save_traj,
            params.rfdiffusion_run_parameters
        )
        backbones_dir = RFdiffusion.out.standardized_pdb_dir
      } else if (params.backbone_generator == "rfdiffusion3") {
        RFdiffusion3(
            Channel.fromList(rfd_input_batches),
            params.foundry_models_path,
            params.hotspot,
            false,
            params.rfdiffusion_run_parameters,
            params.rfdiffusion3_spec_overrides
        )
        backbones_dir = RFdiffusion3.out.standardized_pdb_dir
      }
    }

    // TODO Here we assume that the rfdiffusion file produces a single binder chain (A) and single target chain (B)
    def updatedHotspots = params.hotspot ? params.hotspot.split(',').collect { r -> "B" + r.trim().substring(1) }.join(',') : ""
    BackboneMetrics(
        backbones_dir,
        updatedHotspots,
        false,
        params.backbone_filters
    )

    if (params.mpnn_fastrelax_cycles) {
        if (params.design_type != "binder") {
            throw new IllegalArgumentException("-mpnn_fastrelax_cycles are only supported for binder design")
        }
        if (params.mpnn_num_sequences != 1){
            println("NOTE: Ignoring --mpnn_num_sequences=${params.mpnn_num_sequences} when running fastrelax, generating ${params.mpnn_fastrelax_cycles} cycles instead")
        }
        ProteinMPNN_Fast_Relax(
            BackboneMetrics.out.filtered_pdb_dir,
            params.mpnn_fastrelax_cycles,
            params.mpnn_run_parameters
        )
        mpnn_out = ProteinMPNN_Fast_Relax.out.pdb_dir
        relax_before_ddg = false
    } else {
        LigandMpnn(
            BackboneMetrics.out.filtered_pdb_dir,
            params.mpnn_num_sequences,
            params.mpnn_run_parameters
        )
        mpnn_out = LigandMpnn.out.standardized_pdb_dir
        relax_before_ddg = true
    }

    ProteinQC(
        mpnn_out,
        ['seq_composition'],
        'A'
    )

    Refolding(
        batches.join(mpnn_out).map({
            batch_name, pdb_input, mpnn_pdb_dir -> [
                batch_name: batch_name,
                batch_design_dir: mpnn_pdb_dir,
                native_pdb: pdb_input,
                designed_chains: params.refolding_chains,
            ]
        }),
        params.refolding_tests,
        params.design_type,
    )

    if (!params.disable_pyrosetta_scoring && params.design_type == "binder") {
        PyRosettaInterfaceMetrics(
            mpnn_out,
            relax_before_ddg
        )
    }
}


process CreateBackboneFolders {
    executor 'local'
    publishDir { params.publish_dir }

    input:
        tuple val (batch_name), path (inputs)
    output:
        tuple val(batch_name), path("${batch_name}/custom_backbones/"), emit: pdb_dir
    script:
    """
        mkdir -p "${batch_name}/custom_backbones/"
        cp ${inputs} "${batch_name}/custom_backbones/"
    """
}

process UnpackBackbones {
    executor 'local'

    input:
    path zipfile

    output:
    path "pdbs/*.pdb"

    script:
    """
    mkdir pdbs
    unzip -qq ${zipfile} '*.pdb' -d pdbs
    """
}
