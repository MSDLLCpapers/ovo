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
	'rfdiffusion_num_designs',
	'rfdiffusion_contig',
	'rfdiffusion_input_pdb',
]
requiredParams.each { param ->
    params[param] = null
    if (!params[param]) {
        throw new IllegalArgumentException("Argument --${param} is required!")
    }
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
        throw new IllegalArgumentException("Input file must be a .pdb file, a .txt file with a list of .pdb files, got: ${params.input_pdb}")
    }
    def contigs = params.rfdiffusion_contig.split(',')
	if (pdb_inputs.size() != contigs.size()) {
		if (pdb_inputs.size() == 1) {
			// use same pdb for all contigs
			pdb_inputs = (1..contigs.size()).collect { pdb_inputs[0] }
		} else {
			throw new IllegalArgumentException("There should be one input pdb for each contig (${contigs.size()}), or one input pdb, got ${pdb_inputs.size()}: ${params.rfdiffusion_input_pdb}")
		}
	}
	def batches = (1..pdb_inputs.size()).collectMany {
		i -> (1..params.rfdiffusion_num_designs).collate(params.batch_size).withIndex().collect {
			items, j -> ["contig${i}_batch${j+1}", pdb_inputs[i-1], contigs[i-1], items.size()]
		}
	}

	println "Batches:"
	batches.each { println it }

	def backbone_standardized_pdb_dir
	if (params.backbone_generator == "rfdiffusion3") {
        RFdiffusion3(
            Channel.fromList(batches),
            params.rfdiffusion3_models_path,
            params.hotspot,
            false,
            params.rfdiffusion_run_parameters,
            params.rfdiffusion3_spec_overrides
        )
        backbone_standardized_pdb_dir = RFdiffusion3.out.standardized_pdb_dir
    } else {
        RFdiffusion(
            Channel.fromList(batches),
            params.rfdiffusion_models_path,
            params.hotspot,
            false,
            params.save_traj,
            params.rfdiffusion_run_parameters
        )
        backbone_standardized_pdb_dir = RFdiffusion.out.standardized_pdb_dir
    }

    // TODO Here we assume that the rfdiffusion file produces a single binder chain (A) and single target chain (B)
    def updatedHotspots = params.hotspot ? params.hotspot.split(',').collect { r -> "B" + r.trim().substring(1) }.join(',') : ""
    BackboneMetrics(
        backbone_standardized_pdb_dir,
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
        Channel.fromList(batches).join(mpnn_out).map({
            batch_name, pdb_input, contig, size, mpnn_pdb_dir -> [
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

