import re
from dataclasses import dataclass, field
from typing import Callable, Optional

import pandas as pd

from ovo.core.database import descriptors_refolding, descriptors_rfdiffusion
from ovo.core.database.models import DesignWorkflow, WorkflowParams, WorkflowTypes, Design, Threshold, Base
from ovo.core.database.models_refolding import (
    RefoldingSupportedDesignWorkflow,
)
from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.residue_selection import (
    from_segments_to_hotspots,
    parse_partial_diffusion_binder_contig,
    create_partial_diffusion_binder_contig,
)

MODEL_WEIGHTS_SCAFFOLD = ["Base", "ActiveSite"]
MODEL_WEIGHTS_BINDER = ["Complex_base", "Complex_beta"]


@dataclass
class RFdiffusionParams(WorkflowParams):
    # path to input pdb in S3 or other storage backend
    input_pdb_paths: list[str] = field(default_factory=list, metadata=dict(show_to_user=False, storage_path=True))
    # contig strings
    contigs: list[str] = field(default_factory=list)
    # hotspot residues, comma-separated
    hotspots: str | None = None
    # model_weights
    model_weights: str | None = None
    # number of denoising timesteps
    timesteps: int = 50
    # use partial diffusion
    partial_diffusion: bool = False
    # number of backbone designs to generate
    num_designs: int = 10
    # enable cyclic offset to design macrocyclic peptides
    cyclic_offset: bool = False
    # Number of designs to be processed in batches
    batch_size: int = 50
    # Limit contig length to given value (123) or to given range (123-456, inclusive)
    contigmap_length: int | str | None = None
    # Inpaint (generate) sequence for these input structure regions, in this format: A10-20/B30-40/...
    inpaint_seq: str | None = None
    # Hard filters for backbone designs, applied before sequence design, e.g. "pydssp_helix_percent<50,N_contact_hotspots>=5"
    backbone_filters: str | None = None
    # Additional CLI params for RFdiffusion run_inference.py
    run_parameters: str = ""

    @property
    def input_pdb(self):
        return self.input_pdb_paths[0] if self.input_pdb_paths else None

    @input_pdb.setter
    def input_pdb(self, value):
        self.input_pdb_paths = [value]

    @property
    def contig(self):
        return self.contigs[0] if self.contigs else None

    @contig.setter
    def contig(self, value):
        self.contigs = [value] if value else []

    def validate(self):
        super().validate()
        if not self.input_pdb:
            raise ValueError("No input pdb provided")
        if not self.contig:
            raise ValueError("Please provide a contig")
        if "/0 " not in self.contig and " " in self.contig:
            raise ValueError(
                f'Spaces detected in contig specification, keep in mind that chain breaks are done by inserting "/0 ", found: "{self.contig}"'
            )
        if self.contigmap_length:
            assert isinstance(self.contigmap_length, (int, str)), (
                f"Expected int or str, got {self.contigmap_length} for contigmap_length"
            )
            assert (
                isinstance(self.contigmap_length, int)
                or re.fullmatch("[0-9]+", self.contigmap_length)
                or re.fullmatch("[0-9]+-[0-9]+", self.contigmap_length)
            ), f"Invalid contigmap_length, expected format 123 or 123-456, got: '{self.contigmap_length}'"
        if self.hotspots:
            assert isinstance(self.hotspots, str), f"Expected str for hotspots, got {type(self.hotspots).__name__}"
            if not all(re.fullmatch("[A-Z][0-9]+", hotspot) for hotspot in self.hotspots.split(",")):
                raise ValueError(f"Invalid hotspots format, expected 'A123,A124,A131', got: '{self.hotspots}'")
        if self.inpaint_seq:
            assert isinstance(self.inpaint_seq, str), (
                f"Expected str for inpaint_seq, got {type(self.inpaint_seq).__name__}"
            )
            if not all(re.fullmatch("[A-Z][0-9]+(-[0-9]+)?", segment) for segment in self.inpaint_seq.split("/")):
                raise ValueError(
                    f"Invalid inpaint_seq format, expected format 'A10-20/A22/B30-40', got: '{self.inpaint_seq}'"
                )
        if self.backbone_filters:
            assert isinstance(self.backbone_filters, str), (
                f"Expected str for backbone_filters, got {type(self.backbone_filters).__name__}"
            )
            for filter_expr in self.backbone_filters.split(","):
                match = re.fullmatch("([a-zA-Z0-9_]+)(<=|>=|=|<|>)([-]?[0-9]+(\\.[0-9]+)?)", filter_expr)
                if not match:
                    raise ValueError(
                        f"Invalid backbone_filters format, expected format 'pydssp_helix_percent<50,N_contact_hotspots>=5', got: '{self.backbone_filters}'"
                    )
                field, operator, value, _ = match.groups()
                if field not in descriptors_rfdiffusion.BACKBONE_METRIC_FIELD_NAMES:
                    raise ValueError(
                        f"Invalid backbone filter field '{field}', supported fields: {', '.join(descriptors_rfdiffusion.BACKBONE_METRIC_FIELD_NAMES)}"
                    )


@dataclass
class ProteinMPNNParams(WorkflowParams):
    # number of sequences to generate per structure
    num_sequences: int = 5
    # number of fastrelax cycles (0 = no fastrelax)
    fastrelax_cycles: int = 0
    # amino acids to omit, comma-separated
    omit_aa: str = "CX"
    # sampling temperature (0 = greedy, 0.1 = default, higher is more random)
    sampling_temp: float | None = field(default=None, metadata={"show_to_user": True})
    # amino acid bias, for example F:1.5,K:-1.5 (positive = more likely, zero = neutral default, negative = less likely)
    bias_aa: str = ""
    # additional commandline run parameters
    run_parameters: str = ""

    def validate(self):
        super().validate()
        if self.fastrelax_cycles:
            assert self.fastrelax_cycles >= 0, "fastrelax_cycles must be non-negative"
            if self.num_sequences != 1:
                # TODO implement support for multiple sequences per cycle with fastrelax
                raise NotImplementedError(
                    "Please set num_sequences=1 when using fastrelax_cycles > 0. "
                    "Generating multiple sequences per cycle with fastrelax is not supported yet."
                )
            # help user use proper run params to avoid failing after RFdiffusion stage
            if "--" in self.run_parameters:
                raise ValueError("Please use arguments for dl_interface_design_extended.py (single dash)")
        else:
            # help user use proper run params to avoid failing after RFdiffusion stage
            if self.run_parameters and self.run_parameters[0] == "-" and self.run_parameters[1] != "-":
                raise ValueError("Please use arguments for ligandmpnn (double dash)")
            assert self.num_sequences >= 1, "num_sequences must be at least 1"
        if not self.sampling_temp:
            raise ValueError("Please provide a sampling temperature")
        if self.bias_aa:
            assert isinstance(self.bias_aa, str), f"Expected str for bias_aa, got {type(self.bias_aa).__name__}"
            if not all(re.fullmatch("[A-Z]:-?[0-9]+(\\.[0-9]+)?", bias) for bias in self.bias_aa.split(",")):
                raise ValueError(f"Invalid bias_aa format, expected format 'F:1.5,K:-1.5', got: '{self.bias_aa}'")


@dataclass
class RefoldingParams(WorkflowParams):
    # Refolding test to perform, for example 'af2_model_1_ptm_tt_3rec'
    primary_test: str = None
    # run ESMFold with fp16 precision
    esmfold_fp16: bool = False

    def validate(self):
        super().validate()
        if not self.primary_test:
            raise ValueError("Please select a refolding test to perform")
        if "," in self.primary_test:
            raise ValueError(f"Only a single refolding test can be selected, got: {self.primary_test}")


@dataclass
class RFdiffusionWorkflow(DesignWorkflow, RefoldingSupportedDesignWorkflow):
    """Dataclass for RFdiffusion workflow."""

    # input parameters for RFdiffusion
    rfdiffusion_params: RFdiffusionParams | None = field(
        default_factory=RFdiffusionParams, metadata=dict(tool_name="RFdiffusion")
    )
    # input parameters for Protein MPNN
    protein_mpnn_params: ProteinMPNNParams | None = field(
        default_factory=ProteinMPNNParams, metadata=dict(tool_name="ProteinMPNN")
    )
    # input parameters for AlphaFold Initial Guess, ESMFold and other refolding test params
    refolding_params: RefoldingParams | None = field(
        default_factory=RefoldingParams, metadata=dict(tool_name="Refolding")
    )

    # UI state variables
    # User-provided PDB code (or filename in case of uploaded file)
    input_name: str | None = None
    # preview_job_id: job id of the submitted preview job
    preview_job_id: str | None = None
    # selected scaffolding segments or binder hotspots
    selected_segments: list[str] = None
    # IDs of designs used for partial diffusion (unless custom upload was used)
    # Corresponds to order of contigs in rfdiffusion_params.contigs field
    design_ids: list[str] = field(default_factory=list)

    def get_table_row(self, **kwargs) -> pd.Series:
        """Get all values of all param fields, skip fields with metadata.show_to_user=False, return pd.Series"""
        row = super().get_table_row(**kwargs)
        return pd.concat(
            [
                pd.Series(
                    {
                        ("Workflow", "input"): self.input_name,
                    },
                    **kwargs,
                ),
                row,
            ]
        )

    def get_input_pdb_path(self, contig_index=None):
        if contig_index is None:
            return self.rfdiffusion_params.input_pdb
        if contig_index == 0:
            return self.rfdiffusion_params.input_pdb_paths[0]
        has_multiple_inputs = len(self.rfdiffusion_params.input_pdb_paths) > 1
        has_multiple_contigs = len(self.rfdiffusion_params.contigs) > 1
        if has_multiple_inputs and has_multiple_contigs:
            assert len(self.rfdiffusion_params.input_pdb_paths) == len(self.rfdiffusion_params.contigs), (
                "When multiple input PDBs and multiple contigs are provided, "
                f"their counts must match. Got: {len(self.rfdiffusion_params.input_pdb_paths)} PDBs "
                f"and {len(self.rfdiffusion_params.contigs)} contigs."
            )
        if has_multiple_inputs:
            # When workflow has a single contig, the contig_index corresponds to PDB input index
            return self.rfdiffusion_params.input_pdb_paths[contig_index]
        else:
            # When workflow has multiple contigs, it must only have a single PDB input
            return self.rfdiffusion_params.input_pdb_paths[0]

    def get_contig(self, contig_index=0):
        return self.rfdiffusion_params.contigs[contig_index] if self.rfdiffusion_params.contigs else ""

    def set_contig(self, contig: str):
        self.rfdiffusion_params.contig = contig

    def get_hotspots(self):
        return self.rfdiffusion_params.hotspots

    def get_cyclic_offset(self):
        return self.rfdiffusion_params.cyclic_offset

    def get_selected_segments(self, inpainting=False):
        if inpainting:
            return self.rfdiffusion_params.inpaint_seq.split("/") if self.rfdiffusion_params.inpaint_seq else []
        else:
            return self.selected_segments or []

    def set_selected_segments(self, selection: list[str], inpainting=False):
        if inpainting:
            self.rfdiffusion_params.inpaint_seq = "/".join(selection) if selection else None
        else:
            self.selected_segments = selection

    def get_time_estimate(self, scheduler: Scheduler) -> str:
        total_designs = self.rfdiffusion_params.num_designs * len(self.rfdiffusion_params.contigs)
        STARTUP_TIME_MINUTES = scheduler.get_startup_time_minutes() * 3
        ONE_DESIGN_MINUTES = 2  # assuming that one full design takes this many minutes to complete
        estimated_minutes = STARTUP_TIME_MINUTES + total_designs * ONE_DESIGN_MINUTES
        estimated_hours = estimated_minutes / 60
        estimated_days = estimated_hours / 24

        if estimated_days > 1:
            final_estimation = f"{estimated_days:.1f} days"
        elif estimated_hours > 1:
            final_estimation = f"{estimated_hours:.1f} hours"
        else:
            final_estimation = f"{estimated_minutes:.1f} minutes"

        # FIXME improve time estimation based on chain length (quadratic?), number of contigs and batch size
        message = (
            f"The pipeline will generate and evaluate **{total_designs} backbone designs**. "
            f"For a structure of **~1000 residues**, the expected runtime is about **2 minutes** for 1 design. "
            f"The estimated total runtime including startup is **{final_estimation}**. "
        )
        if self.rfdiffusion_params.num_designs > self.rfdiffusion_params.batch_size:
            message += (
                f"Workflow will be parallelized in batches of {self.rfdiffusion_params.batch_size} designs, "
                f"each batch can run in parallel so the total runtime can be shortened dramatically."
            )
        return message

    def get_pipeline_name(self) -> str:
        return "ovo.rfdiffusion-end-to-end"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.design_logic_rfdiffusion import prepare_rfdiffusion_workflow_params

        return prepare_rfdiffusion_workflow_params(self, workdir=workdir)

    def process_results(self, job: "DesignJob", callback: Callable = None) -> list[Base]:
        """Process results of a successful workflow - download files from workdir,
        create Design and DescriptorValue objects"""
        from ovo.core.logic.design_logic_rfdiffusion import process_workflow_results

        return process_workflow_results(job=job, callback=callback)

    @classmethod
    def get_download_fields(cls):
        return {
            "RFdiffusion Input PDB": (RFdiffusionWorkflow, "rfdiffusion_params.input_pdb_paths"),
        }

    def get_refolding_design_paths(self, design_ids: list[str]) -> dict[str, str]:
        from ovo import db

        return {d.id: d.structure_path for d in db.select(Design, id__in=design_ids)}


@WorkflowTypes.register("RFdiffusion scaffold design")
@dataclass
class RFdiffusionScaffoldDesignWorkflow(RFdiffusionWorkflow):
    # acceptance threshold values (descriptor key -> interval (min, max, enabled))
    acceptance_thresholds: dict[str, Threshold] = field(
        default_factory=lambda: {
            descriptors_refolding.AF2_PRIMARY_PAE.key: Threshold(max_value=5.0),
            descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_NATIVE_MOTIF_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_PLDDT.key: Threshold(min_value=80),
            descriptors_refolding.ESMFOLD_PAE.key: Threshold(max_value=10.0, enabled=False),
            descriptors_refolding.ESMFOLD_DESIGN_BACKBONE_RMSD.key: Threshold(max_value=5.0, enabled=False),
            descriptors_refolding.ESMFOLD_PLDDT.key: Threshold(min_value=80, enabled=False),
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key: Threshold(enabled=False),
        }
    )

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import rfdiffusion_scaffold_design_visualization

        rfdiffusion_scaffold_design_visualization(design_id)

    @classmethod
    def visualize_single_design_sequences(self, design_id: str):
        from ovo.app.components.workflow_visualization_components import visualize_rfdiffusion_design_sequence

        visualize_rfdiffusion_design_sequence(design_id)

    def get_refolding_design_type(self) -> str:
        return "scaffold"

    def get_refolding_native_pdb_path(self, contig_index: int) -> str:
        # In binder design, we compare with fixed input motif from input PDB
        return self.get_input_pdb_path(contig_index=contig_index)


@WorkflowTypes.register("RFdiffusion binder design")
@dataclass
class RFdiffusionBinderDesignWorkflow(RFdiffusionWorkflow):
    # Workflow-specific parameters
    # length of the binder
    binder_length: str | None = None
    # dict chains, key: chain, value: contig, e.g. {A: A1-100/102-110/112-130, B: B23-202}
    chains: dict | None = None
    # start residue of the trimmed chain
    start_res_trimmed_chain: int | None = None
    # end residue of the trimmed chain
    end_res_trimmed_chain: int | None = None
    # chain ID of the target chain
    target_chain: str | None = None
    # acceptance threshold values (descriptor key -> interval (min, max, enabled))
    acceptance_thresholds: dict[str, Threshold] = field(
        default_factory=lambda: {
            descriptors_refolding.AF2_PRIMARY_IPAE.key: Threshold(max_value=10.0),
            descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_PLDDT_BINDER.key: Threshold(min_value=80),
            descriptors_rfdiffusion.PYROSETTA_DDG.key: Threshold(max_value=-30.0),
            descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS.key: Threshold(min_value=1, enabled=False),
            descriptors_refolding.AF2_PRIMARY_BINDER_PAE.key: Threshold(max_value=5.0, enabled=False),
            descriptors_rfdiffusion.PYROSETTA_CMS.key: Threshold(enabled=False),
            descriptors_rfdiffusion.PYROSETTA_SAP_SCORE.key: Threshold(enabled=False),
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key: Threshold(enabled=False),
        }
    )

    def get_target_chain(self):
        return self.target_chain

    def get_target_trim_boundary(self):
        return self.start_res_trimmed_chain, self.end_res_trimmed_chain

    def get_selected_segments(self, contig_index=0, partial_diffusion=False):
        if partial_diffusion:
            # get REDESIGNED segments from binder contig as they correspond to positions in binder chain A
            # default case for a peptide of 12 residues is simply binder_contig="12-12" turned into ["A1-12"]
            # or when redesigning only A1 and A3-7 in a peptide of 12 residues, this would be
            # binder_contig="1-1/A2-2/5-5/A8-12" turned into ["A1-1", "A3-7"]
            binder_contig = self.get_binder_contig(contig_index=contig_index)
            binder_length, designed_segments = parse_partial_diffusion_binder_contig(binder_contig)
            return designed_segments
        else:
            return super().get_selected_segments()

    def set_selected_segments(self, segments: list[str], contig_index=0, partial_diffusion=False):
        if partial_diffusion:
            # create contig from REDESIGNED segments as they correspond to positions in binder chain A
            # default case for a peptide of 12 residues:
            # segments=[] -> binder_contig="12-12"
            # or when redesigning only A1 and A3-7 in a peptide of 12 residues,
            # segments=["A1-1", "A3-7"] -> binder_contig="1-1/A2-2/5-5/A8-12"
            binder_length, _ = parse_partial_diffusion_binder_contig(self.get_binder_contig(contig_index=contig_index))
            self.set_binder_contig(
                create_partial_diffusion_binder_contig(redesigned_segments=segments, binder_length=binder_length)
            )
        else:
            # Hotspots
            super().set_selected_segments(segments)
            # Convert from segments to hotspots
            self.rfdiffusion_params.hotspots = from_segments_to_hotspots(segments)

    def get_target_contig(self, contig_index=0):
        contig = self.get_contig(contig_index=0)
        if not contig:
            return ""
        subcontigs = contig.split()
        # make sure that target contig is fixed
        assert len(subcontigs) == 2, f"Expected a binder chain and target chain in contig, got: {contig}"
        assert all(segment[0].isalpha() for segment in subcontigs[1].split("/")), (
            f"Expected contig in format 'DESIGN/0 TARGET', got: {contig}"
        )
        return subcontigs[1]

    def get_binder_contig(self, contig_index=0):
        contig = self.get_contig(contig_index=0)
        if not contig:
            return ""
        subcontigs = contig.split()
        assert len(subcontigs) == 2, f"Expected a binder chain and target chain in contig, got: {contig}"
        # make sure that target contig is fixed (binder contig should be designed but not necessarily - e.g. in partial diffusion)
        assert all(segment[0].isalpha() for segment in subcontigs[1].split("/")), (
            f"Expected contig in format 'DESIGN/0 TARGET', got: {contig}"
        )
        return subcontigs[0].removesuffix("/0")

    def set_binder_contig(self, binder_contig: str, contig_index: int = 0):
        target_contig = self.get_target_contig()
        assert target_contig, "Target contig must be set before setting binder contig"
        self.rfdiffusion_params.contigs[contig_index] = binder_contig + "/0 " + target_contig

    @classmethod
    def visualize_multiple_designs_structures(cls, design_ids: list[str]):
        """Visualize multiple design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import (
            rfdiffusion_multiple_binder_designs_visualization,
        )

        rfdiffusion_multiple_binder_designs_visualization(design_ids)

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import rfdiffusion_binder_design_visualization

        rfdiffusion_binder_design_visualization(design_id)

    def get_refolding_design_type(self) -> str:
        return "binder"

    def get_refolding_native_pdb_path(self, contig_index: int) -> Optional[str]:
        # In binder design, we don't compare with fixed input motif, so return None
        return None
