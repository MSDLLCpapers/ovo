import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from ovo.core.database import descriptors_refolding, descriptors_rfdiffusion
from ovo.core.database.models import (
    AlignmentOption,
    DesignWorkflow,
    WorkflowParams,
    WorkflowTypes,
    Design,
    Threshold,
    Base,
    DesignJob,
)
from ovo.core.database.models_refolding import (
    RefoldingSupportedDesignWorkflow,
    RefoldingWorkflow,
)
from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.residue_selection import (
    from_segments_to_hotspots,
    parse_partial_diffusion_binder_contig,
    create_partial_diffusion_binder_contig,
    parse_contig_for_input_structure,
    parse_contig_for_output_structure,
)

# Valid keys for RFD3 DesignInputSpecification (from rfd3.inference.input_parsing).
# Canonical source: ovo/pipelines/rfdiffusion3-backbone/bin/build_input_json.py
# Used for early validation of user-provided spec overrides.
RFD3_SPEC_FIELDS = {
    "input",
    "atom_array_input",
    "contig",
    "unindex",
    "length",
    "ligand",
    "cif_parser_args",
    "extra",
    "dialect",
    "select_fixed_atoms",
    "select_unfixed_sequence",
    "select_buried",
    "select_partially_buried",
    "select_exposed",
    "select_hbond_acceptor",
    "select_hbond_donor",
    "select_hotspots",
    "redesign_motif_sidechains",
    "symmetry",
    "ori_token",
    "infer_ori_strategy",
    "plddt_enhanced",
    "is_non_loopy",
    "partial_t",
}

MODEL_WEIGHTS_SCAFFOLD = ["Base", "ActiveSite"]
MODEL_WEIGHTS_BINDER = ["Complex_base", "Complex_beta"]


@dataclass(frozen=True)
class MPNNWeightSpec:
    """Specification for MPNN model weights.

    Attributes:
        display_name: Human-readable name shown in UI
        model_type: LigandMPNN model type (protein_mpnn, ligand_mpnn, soluble_mpnn, etc.)
        checkpoint_path: Checkpoint file name (e.g. "proteinmpnn_v_48_010.pt"). None means use LigandMPNN default.
    """

    display_name: str
    model_type: str
    checkpoint_path: str | None


# MPNN weight configuration: key -> MPNNWeightSpec
MPNN_WEIGHT_CONFIG: dict[str, MPNNWeightSpec] = {
    # Built-in LigandMPNN models - SolubleMPNN variants
    "soluble_mpnn": MPNNWeightSpec("SolubleMPNN: default, 0.2 Å noise", "soluble_mpnn", "solublempnn_v_48_020.pt"),
    "soluble_mpnn_002": MPNNWeightSpec("SolubleMPNN: 0.02 Å noise", "soluble_mpnn", "solublempnn_v_48_002.pt"),
    "soluble_mpnn_010": MPNNWeightSpec("SolubleMPNN: 0.1 Å noise", "soluble_mpnn", "solublempnn_v_48_010.pt"),
    "soluble_mpnn_030": MPNNWeightSpec("SolubleMPNN: 0.3 Å noise", "soluble_mpnn", "solublempnn_v_48_030.pt"),
    # Built-in LigandMPNN models - ProteinMPNN variants
    "protein_mpnn": MPNNWeightSpec("ProteinMPNN: default, 0.2 Å noise", "protein_mpnn", "proteinmpnn_v_48_020.pt"),
    "protein_mpnn_002": MPNNWeightSpec("ProteinMPNN: 0.02 Å noise", "protein_mpnn", "proteinmpnn_v_48_002.pt"),
    "protein_mpnn_010": MPNNWeightSpec("ProteinMPNN: 0.1 Å noise", "protein_mpnn", "proteinmpnn_v_48_010.pt"),
    "protein_mpnn_030": MPNNWeightSpec("ProteinMPNN: 0.3 Å noise", "protein_mpnn", "proteinmpnn_v_48_030.pt"),
    # Built-in LigandMPNN models - LigandMPNN variants
    "ligand_mpnn": MPNNWeightSpec("LigandMPNN: default, 0.1 Å noise", "ligand_mpnn", "ligandmpnn_v_32_010_25.pt"),
    "ligand_mpnn_005": MPNNWeightSpec("LigandMPNN: 0.05 Å noise", "ligand_mpnn", "ligandmpnn_v_32_005_25.pt"),
    "ligand_mpnn_020": MPNNWeightSpec("LigandMPNN: 0.2 Å noise", "ligand_mpnn", "ligandmpnn_v_32_020_25.pt"),
    "ligand_mpnn_030": MPNNWeightSpec("LigandMPNN: 0.3 Å noise", "ligand_mpnn", "ligandmpnn_v_32_030_25.pt"),
    # Built-in LigandMPNN models - Membrane MPNN (only 0.2Å available)
    "per_residue_membrane_mpnn": MPNNWeightSpec(
        "ProteinMPNN with per-residue membrane label: default, 0.2 Å noise",
        "per_residue_label_membrane_mpnn",
        "per_residue_label_membrane_mpnn_v_48_020.pt",
    ),
    "global_membrane_mpnn": MPNNWeightSpec(
        "ProteinMPNN with global membrane label: default, 0.2 Å noise",
        "global_label_membrane_mpnn",
        "global_label_membrane_mpnn_v_48_020.pt",
    ),
    # Additional models bundled with the LigandMPNN fork
    "pottsmpnn_20": MPNNWeightSpec("PottsMPNN: 0.2 Å noise, no MSA", "protein_mpnn", "pottsmpnn_20.pt"),
    "pottsmpnn_30": MPNNWeightSpec("PottsMPNN: default, 0.3 Å noise, no MSA", "protein_mpnn", "pottsmpnn_30.pt"),
    "sol_pottsmpnn_20": MPNNWeightSpec("Soluble PottsMPNN: 0.2 Å noise, no MSA", "protein_mpnn", "sol_pottsmpnn_20.pt"),
    "sol_pottsmpnn_30": MPNNWeightSpec(
        "Soluble PottsMPNN: default, 0.3 Å noise, no MSA", "protein_mpnn", "sol_pottsmpnn_30.pt"
    ),
    "cyclicmpnn_48_010": MPNNWeightSpec("CyclicMPNN: 0.1 Å noise", "protein_mpnn", "cyclicmpnn_48_010.pt"),
    "hypermpnn_002": MPNNWeightSpec("HyperMPNN: 0.02 Å noise", "protein_mpnn", "v48_002_epoch240_hyper.pt"),
    "hypermpnn_010": MPNNWeightSpec("HyperMPNN: 0.1 Å noise", "protein_mpnn", "v48_010_epoch300_hyper.pt"),
    "hypermpnn_020": MPNNWeightSpec("HyperMPNN: default, 0.2 Å noise", "protein_mpnn", "v48_020_epoch300_hyper.pt"),
    "hypermpnn_030": MPNNWeightSpec("HyperMPNN: 0.3 Å noise", "protein_mpnn", "v48_030_epoch300_hyper.pt"),
}


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
    # Backbone generator model: "rfdiffusion" (v1) or "rfdiffusion3"
    backbone_generator: str = "rfdiffusion"
    # RFD3 InputSpec fields (ignored for RFD1)
    rfd3_unindex: str | None = None  # unindexed motif, contig string e.g. "A244,A274,A320"
    rfd3_select_fixed_atoms: str | None = None  # fixed atoms override, contig string e.g. "A244:TIP,A274:BKBN"
    rfd3_select_hotspots: str | None = None  # atom-level hotspots dict JSON e.g. '{"E64": "CD2,CZ", "E88": "CG,CZ"}'
    rfd3_ligand: str | None = None  # ligand CCD names e.g. "HAX,OAA"
    # rfd3_length: str | None = None  # total length constraint e.g. "100-150" or "120"
    rfd3_infer_ori_strategy: str | None = None  # override auto-derived infer_ori_strategy: "hotspots" or "com"
    rfd3_is_non_loopy: bool | None = None  # True = prefer helices/sheets, fewer loops. Default True for binder design.
    rfd3_ori_token: str | None = None  # explicit ORI token [x,y,z] e.g. "10.5,20.3,15.1"
    # number of designs to run in parallel within each RFdiffusion3 batch,
    # set to >1 for speedup when using GPU and generating many designs
    rfd3_inner_batch_size: int = 1
    rfd3_spec_overrides: str | None = (
        None  # additional arbitrary JSON overrides for RFD3 InputSpec, applied on top of named params
    )
    # Skip RFdiffusion backbone design, use custom backbone input from the given directory,
    # .zip file, or list of .pdb paths
    custom_backbones: str | list[str] = field(default=None, metadata=dict(storage_path=True))

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

    def to_dict(self, human_readable=False):
        super_dict = super().to_dict(human_readable=human_readable)
        if human_readable and self.custom_backbones and not self.contigs:
            # When reviewing parameters and custom backbone dir is used,
            # only show that custom backbone dir and no other parameters.
            # Contigs are kept when provided, they define which residues are redesigned.
            return {k: v for k, v in super_dict.items() if k in ("custom_backbones", "hotspots")}
        return super_dict

    def validate(self):
        super().validate()
        if not self.input_pdb and not self.custom_backbones:
            raise ValueError("No input pdb provided")
        if not isinstance(self.contigs, list):
            if isinstance(self.contigs, str):
                raise ValueError(
                    "Contigs must be provided as a list of strings, not a single string. For bulk grid submission, provide a list of lists."
                )
            raise ValueError(f"Expected list, got {type(self.contigs).__name__}: {self.contigs}")
        for contig in self.contigs:
            if "/0 " not in contig and " " in contig:
                raise ValueError(
                    f'Spaces detected in contig specification, keep in mind that chain breaks are done by inserting "/0 ", found: "{contig}"'
                )
            # verify that contig can be parsed
            _parsed_contig = parse_contig_for_input_structure(contig)
            if not (_parsed_contig or self.rfd3_unindex):
                raise ValueError(
                    f"Contig must contain at least one fixed segment or unindexed residues must be specified, got: '{contig=}' and '{self.rfd3_unindex=}'"
                )

        if self.hotspots:
            assert isinstance(self.hotspots, str), f"Expected str for hotspots, got {type(self.hotspots).__name__}"
            if not all(re.fullmatch("[A-Z][0-9]+", hotspot) for hotspot in self.hotspots.split(",")):
                raise ValueError(f"Invalid hotspots format, expected 'A123,A124,A131', got: '{self.hotspots}'")
            hotspot_positions = self.hotspots.split(",")
            for contig in self.contigs:
                contig_segments = [f"{s.chain}{s.start}-{s.end}" for s in parse_contig_for_input_structure(contig)]
                contig_positions = from_segments_to_hotspots(contig_segments).split(",")
                hotspots_missing_in_contig = set(hotspot_positions).difference(set(contig_positions))
                if hotspots_missing_in_contig:
                    raise ValueError(
                        f"Hotspot positions {hotspots_missing_in_contig} are not included in contig segments {contig_segments}. "
                        f"Please make sure that all hotspots are included in the contig segments."
                    )
        if self.custom_backbones:
            # Do not validate if this stage is skipped
            return
        if not self.contig:
            raise ValueError("Please provide a contig")
        for contig in self.contigs:
            all_segments = parse_contig_for_input_structure(contig, include_generated=True)
            if not any(s.start is None for s in all_segments):
                raise ValueError(
                    f"Contig must contain at least one generated region (e.g. '10' or '10-20'), got: '{contig}'"
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
        if self.inpaint_seq:
            assert isinstance(self.inpaint_seq, str), (
                f"Expected str for inpaint_seq, got {type(self.inpaint_seq).__name__}"
            )
            if not all(re.fullmatch("[A-Z][0-9]+(-[0-9]+)?", segment) for segment in self.inpaint_seq.split("/")):
                raise ValueError(
                    f"Invalid inpaint_seq format, expected format 'A10-20/A22/B30-40', got: '{self.inpaint_seq}'"
                )
            if self.backbone_generator == "rfdiffusion3":
                raise ValueError(
                    "Inpainting is not supported by RFdiffusion3, please use RFdiffusion1 instead, or remove the inpaint_seq regions"
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
        if self.backbone_generator not in ("rfdiffusion", "rfdiffusion3"):
            raise ValueError(
                f"backbone_generator must be 'rfdiffusion' or 'rfdiffusion3', got: '{self.backbone_generator}'"
            )
        if self.backbone_generator == "rfdiffusion3":
            if self.rfd3_inner_batch_size < 1:
                raise ValueError(f"rfd3_inner_batch_size must be >= 1, got: {self.rfd3_inner_batch_size}")
            if self.rfd3_unindex:
                unindex_residues = [r.strip() for r in self.rfd3_unindex.split(",") if r.strip()]
                if not all(re.fullmatch("[A-Z][0-9]+", r) for r in unindex_residues):
                    raise ValueError(
                        f"Invalid rfd3_unindex format, expected 'A244,A274,A320', got: '{self.rfd3_unindex}'"
                    )
                for contig in self.contigs:
                    fixed_residues: set[str] = set()
                    for seg in parse_contig_for_input_structure(contig):
                        for resnum in range(seg.start, seg.end + 1):
                            fixed_residues.add(f"{seg.chain}{resnum}")
                    overlap = sorted(set(unindex_residues) & fixed_residues)
                    if overlap:
                        raise ValueError(
                            f"Unindexed residues {overlap} also appear inside the contig fixed segments. "
                            f"Each residue must be either in the contig or in the unindexed list, not both."
                        )
            if self.rfd3_select_hotspots:
                try:
                    parsed_hotspots = json.loads(self.rfd3_select_hotspots)
                    if not isinstance(parsed_hotspots, dict):
                        raise ValueError('rfd3_select_hotspots must be a JSON dict, e.g. {"E64": "CD2,CZ"}')
                except json.JSONDecodeError as e:
                    raise ValueError(f"rfd3_select_hotspots is not valid JSON: {e}") from e
            if self.rfd3_infer_ori_strategy and self.rfd3_infer_ori_strategy not in ("hotspots", "com"):
                raise ValueError(
                    f"rfd3_infer_ori_strategy must be 'hotspots' or 'com', got: '{self.rfd3_infer_ori_strategy}'"
                )
            if self.rfd3_ori_token:
                parts = self.rfd3_ori_token.split(",")
                if len(parts) != 3:
                    raise ValueError(
                        f"rfd3_ori_token must be 3 comma-separated floats (x,y,z), got: '{self.rfd3_ori_token}'"
                    )
                try:
                    [float(p) for p in parts]
                except ValueError:
                    raise ValueError(
                        f"rfd3_ori_token must be 3 comma-separated floats (x,y,z), got: '{self.rfd3_ori_token}'"
                    )
            if self.rfd3_spec_overrides:
                try:
                    parsed = json.loads(self.rfd3_spec_overrides)
                    if not isinstance(parsed, dict):
                        raise ValueError("rfd3_spec_overrides must be a JSON object (dict)")
                except json.JSONDecodeError as e:
                    raise ValueError(f"rfd3_spec_overrides is not valid JSON: {e}") from e
                unknown_keys = set(parsed.keys()) - RFD3_SPEC_FIELDS
                if unknown_keys:
                    raise ValueError(
                        f"Unknown InputSpec keys in rfd3_spec_overrides: {', '.join(sorted(unknown_keys))}. "
                        f"Valid keys: {', '.join(sorted(RFD3_SPEC_FIELDS))}"
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
    sampling_temp: float = field(default=0.1, metadata={"show_to_user": True})
    # amino acid bias, for example F:1,K:-1 (positive = more likely, zero = neutral default, negative
    # = less likely). MPNN samples from softmax((logits + bias) / sampling_temp), so a bias of 1 or 2
    # is a moderate nudge rather than a hard rule, see MPNN_BIAS_LEVELS for measured effects
    bias_aa: str = ""
    # additional commandline run parameters
    run_parameters: str = ""
    # MPNN weights key from MPNN_WEIGHT_CONFIG
    # Note that only some are supported when fastrelax is enabled
    mpnn_weights_key: str = "soluble_mpnn"

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
        if self.sampling_temp is None:
            raise ValueError("Please provide a sampling temperature")
        assert self.sampling_temp >= 0, "sampling_temp must be non-negative"
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

    def to_dict(self, clean: bool = False) -> dict:
        data = super().to_dict(clean=clean)
        if clean:
            for ui_state_field in ("input_name", "preview_job_id", "selected_segments", "design_ids"):
                data.pop(ui_state_field, None)
        return data

    def get_table_row(self, **kwargs) -> pd.Series:
        """Get all values of all param fields, skip fields with metadata.show_to_user=False, return pd.Series"""
        row = super().get_table_row(**kwargs)
        if self.rfdiffusion_params.backbone_generator == "rfdiffusion":
            # hide RFD3 params when using RFD1
            row = row[row.index.map(lambda col: not str(col[1]).startswith("rfd3_"))]
        if self.rfdiffusion_params.backbone_generator == "rfdiffusion3":
            # hide RFD1 params when using RFD3
            row = row[row.index.map(lambda col: col != ("RFdiffusion", "model_weights"))]
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

    def get_contig_indexes(self) -> list[int]:
        return list(range(len(self.rfdiffusion_params.contigs)))

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
            **super().get_download_fields(),
            "RFdiffusion Input PDB": (RFdiffusionWorkflow, "rfdiffusion_params.input_pdb_paths"),
        }

    def get_refolding_design_paths(self, design_ids: list[str]) -> dict[str, str]:
        from ovo import db

        return {d.id: d.structure_path for d in db.select(Design, id__in=design_ids)}

    def get_refolding_native_pdb_path(self, contig_index: int) -> str:
        return self.get_input_pdb_path(contig_index=contig_index)

    def get_skipped_threshold_keys(self) -> list[str]:
        """Get descriptor keys from acceptance_thresholds that will (most likely) not be available
        and will be skipped during processing.

        Used to skip showing these thresholds in the UI (acceptance threshold settings and summary table).
        """
        skipped_keys = []

        # Skip all refolding descriptors that are not provided by the selected refolding test
        refolding_descriptor_key_prefix = (
            RefoldingWorkflow.get_descriptor_key_prefix(self.refolding_params.primary_test, primary=True)
            if self.refolding_params.primary_test
            else ()
        )
        skipped_keys += [
            key
            for key in self.acceptance_thresholds.keys()
            if key.startswith("refolding|") and not key.startswith(refolding_descriptor_key_prefix)
        ]

        # Skip hotspot contact descriptor if no hotspots are provided
        skipped_keys += [
            key
            for key in self.acceptance_thresholds.keys()
            if key == descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS.key and not self.rfdiffusion_params.hotspots
        ]

        return skipped_keys


@WorkflowTypes.register("RFdiffusion scaffold design")
@dataclass
class RFdiffusionScaffoldDesignWorkflow(RFdiffusionWorkflow):
    # acceptance threshold values (descriptor key -> interval (min, max, enabled))
    acceptance_thresholds: dict[str, Threshold] = field(
        default_factory=lambda: {
            # AF2 refolding
            descriptors_refolding.AF2_PRIMARY_PAE.key: Threshold(max_value=5.0),
            descriptors_refolding.AF2_PRIMARY_DESIGN_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_NATIVE_MOTIF_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_PLDDT.key: Threshold(min_value=80),
            # ESMFold refolding
            descriptors_refolding.ESMFOLD_PAE.key: Threshold(max_value=10.0),
            descriptors_refolding.ESMFOLD_DESIGN_BACKBONE_RMSD.key: Threshold(max_value=5.0),
            descriptors_refolding.ESMFOLD_PLDDT.key: Threshold(min_value=80),
            # Boltz refolding
            descriptors_refolding.BOLTZ_PRIMARY_PDE.key: Threshold(max_value=10.0),
            descriptors_refolding.BOLTZ_PRIMARY_PLDDT.key: Threshold(min_value=0.8),
            descriptors_refolding.BOLTZ_PRIMARY_DESIGN_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.BOLTZ_PRIMARY_NATIVE_MOTIF_RMSD.key: Threshold(max_value=2.0),
            # Added but disabled by default
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key: Threshold(enabled=False),
        }
    )

    @classmethod
    def get_alignment_options(cls, design: Design, chain_ids: list[str]) -> dict[str, AlignmentOption]:
        """Add aligning on the scaffolded motif, the part of the design that comes from the input structure"""
        options = super().get_alignment_options(design, chain_ids)
        contig = " ".join(chain.contig for chain in design.spec.chains if chain.contig)
        if not contig:
            return options

        motif_mapping = [
            (segment.chain, list(range(segment.start, segment.end + 1)))
            for segment in parse_contig_for_output_structure(contig)
            # only segments taken from the input structure are the motif, the rest was generated
            if segment.input_chain and segment.chain in chain_ids
        ]
        if motif_mapping:
            # the motif is only a few residues, aligning on all of their atoms is more precise than on Cα only
            options["On motif"] = AlignmentOption(motif_mapping, representation="cartoon+ball-and-stick", all_atom=True)
        return options

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import rfdiffusion_scaffold_design_visualization

        rfdiffusion_scaffold_design_visualization(design_id)

    @classmethod
    def visualize_single_design_sequences(self, design_id: str):
        from ovo.app.components.workflow_visualization_components import visualize_rfdiffusion_design_sequence

        visualize_rfdiffusion_design_sequence(design_id)

    @classmethod
    def visualize_summary(cls, jobs: list[DesignJob]):
        from ovo.app.components.workflow_summary import rfdiffusion_scaffold_workflow_summary

        rfdiffusion_scaffold_workflow_summary(jobs)

    def get_refolding_design_type(self) -> str:
        return "scaffold"

    def get_refolding_designed_chains(self) -> list[str]:
        # TODO: fix for symmetric designs with multiple contigs, currently we just assume chain A is designed
        return ["A"]


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
            # AF2 refolding
            descriptors_refolding.AF2_PRIMARY_IPAE.key: Threshold(max_value=10.0),
            descriptors_refolding.AF2_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.AF2_PRIMARY_PLDDT_BINDER.key: Threshold(min_value=80),
            # Boltz refolding
            descriptors_refolding.BOLTZ_PRIMARY_IPDE.key: Threshold(max_value=10.0),
            descriptors_refolding.BOLTZ_PRIMARY_TARGET_ALIGNED_BINDER_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.BOLTZ_PRIMARY_BINDER_PLDDT.key: Threshold(min_value=0.8),
            # Rosetta scoring
            descriptors_rfdiffusion.PYROSETTA_DDG.key: Threshold(max_value=-30.0),
            # Hotspot contacts - will be disabled if hotspots are not provided
            descriptors_rfdiffusion.N_CONTACTS_TO_HOTSPOTS.key: Threshold(min_value=2),
            # Added but disabled by default
            descriptors_rfdiffusion.PYROSETTA_CMS.key: Threshold(enabled=False),
            descriptors_rfdiffusion.PYROSETTA_SAP_SCORE.key: Threshold(enabled=False),
            descriptors_rfdiffusion.PYROSETTA_BUNS.key: Threshold(enabled=False, max_value=4),
            descriptors_rfdiffusion.RADIUS_OF_GYRATION.key: Threshold(enabled=False),
            descriptors_refolding.AF2_PRIMARY_BINDER_PAE.key: Threshold(max_value=5.0, enabled=False),
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
            # when redesigning only A1 and A3-7 in a peptide of 12 residues,
            # segments=["A1-1", "A3-7"] -> binder_contig="1-1/A2-2/5-5/A8-12"
            # an empty selection keeps the whole binder fixed, segments=[] -> binder_contig="A1-12",
            # which cannot be submitted - the input is skipped, see get_submitted_contig_indexes
            binder_length, _ = parse_partial_diffusion_binder_contig(self.get_binder_contig(contig_index=contig_index))
            self.set_binder_contig(
                create_partial_diffusion_binder_contig(redesigned_segments=segments, binder_length=binder_length),
                contig_index=contig_index,
            )
        else:
            # Hotspots
            super().set_selected_segments(segments)
            # Convert from segments to hotspots
            self.rfdiffusion_params.hotspots = from_segments_to_hotspots(segments)

    def split_contig(self, contig_index=0) -> tuple[str, str]:
        """Split the contig of an input into its binder part and its target part.

        Which part is which is not positional: the binder comes first under partial diffusion and
        second in de novo binder design, so it is recognized as the generated part - the one with a
        segment that has no chain. Under partial diffusion all of it can be fixed, when nothing is
        selected for redesign, and it is then recognized by its chain, which partial diffusion
        requires to be A (see :func:`parse_partial_diffusion_binder_contig`).

        :return: (binder contig, target contig), both "" if there is no contig yet
        """
        contig = self.get_contig(contig_index=contig_index)
        if not contig:
            return "", ""

        subcontigs = [subcontig.removesuffix("/0") for subcontig in contig.split()]
        assert len(subcontigs) == 2, f"Expected a binder chain and target chain in contig, got: {contig}"

        is_binder = [any(segment[0].isnumeric() for segment in subcontig.split("/")) for subcontig in subcontigs]
        if not any(is_binder) and self.rfdiffusion_params.partial_diffusion:
            is_binder = [all(segment[0] == "A" for segment in subcontig.split("/")) for subcontig in subcontigs]
        assert sum(is_binder) == 1, f"Expected exactly one binder contig and one target contig, got: {contig}"

        binder_index = is_binder.index(True)
        return subcontigs[binder_index], subcontigs[1 - binder_index]

    def get_target_contig(self, contig_index=0):
        return self.split_contig(contig_index=contig_index)[1]

    def get_binder_contig(self, contig_index=0):
        return self.split_contig(contig_index=contig_index)[0]

    def get_skipped_contig_indexes(self) -> list[int]:
        """Get the indexes of the inputs that have no residues selected for redesign.

        Only partial diffusion can end up like that, by deselecting every residue of a binder. There
        is nothing to submit for such an input, so it is left out of the submission rather than
        dropped from the workflow, which would lose the selections made in it - see
        :meth:`drop_skipped_inputs`.
        """
        if not self.rfdiffusion_params.partial_diffusion:
            return []
        return [
            contig_index
            for contig_index in self.get_contig_indexes()
            if not self.get_selected_segments(contig_index=contig_index, partial_diffusion=True)
        ]

    def drop_skipped_inputs(self) -> "RFdiffusionBinderDesignWorkflow":
        """Return the workflow to submit, without the inputs that have no residues to redesign.

        Returns this same workflow when there are none, so that the submitted workflow is a copy only
        when it has to be. See :meth:`get_skipped_contig_indexes`.
        """
        skipped_contig_indexes = set(self.get_skipped_contig_indexes())
        if not skipped_contig_indexes:
            return self

        workflow = deepcopy(self)
        params = workflow.rfdiffusion_params
        if len(params.input_pdb_paths) == len(params.contigs):
            # One input per contig, so the inputs of the skipped contigs go as well - a workflow with
            # several contigs for a single input keeps it, see get_input_pdb_path
            params.input_pdb_paths = [
                input_pdb_path
                for contig_index, input_pdb_path in enumerate(params.input_pdb_paths)
                if contig_index not in skipped_contig_indexes
            ]
        if isinstance(params.custom_backbones, list):
            # Sequence redesign of the inputs, each custom backbone has its own contig
            assert len(params.custom_backbones) == len(params.contigs), (
                f"Expected one custom backbone for each contig, got {len(params.custom_backbones)} "
                f"backbones and {len(params.contigs)} contigs"
            )
            params.custom_backbones = [
                custom_backbone
                for contig_index, custom_backbone in enumerate(params.custom_backbones)
                if contig_index not in skipped_contig_indexes
            ]
        params.contigs = [
            contig for contig_index, contig in enumerate(params.contigs) if contig_index not in skipped_contig_indexes
        ]
        return workflow

    def set_binder_contig(self, binder_contig: str, contig_index: int = 0):
        target_contig = self.get_target_contig(contig_index=contig_index)
        assert target_contig, "Target contig must be set before setting binder contig"
        self.rfdiffusion_params.contigs[contig_index] = binder_contig + "/0 " + target_contig

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import rfdiffusion_binder_design_visualization

        rfdiffusion_binder_design_visualization(design_id)

    @classmethod
    def visualize_summary(cls, jobs: list[DesignJob]):
        from ovo.app.components.workflow_summary import rfdiffusion_binder_design_workflow_summary

        rfdiffusion_binder_design_workflow_summary(jobs)

    def get_refolding_design_type(self) -> str:
        return "binder"

    def get_refolding_designed_chains(self) -> list[str]:
        # In binder design, we assume the binder is always chain A
        return ["A"]
