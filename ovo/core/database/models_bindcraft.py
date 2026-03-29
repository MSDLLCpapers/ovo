import os
from copy import copy
from dataclasses import dataclass, field
from typing import Callable

# from ovo import db
from ovo.core.database.models import DesignWorkflow, WorkflowParams, WorkflowTypes, DesignJob, Design, Base
from ovo.core.database.models_refolding import RefoldingSupportedDesignWorkflow
from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.residue_selection import from_segments_to_hotspots


@dataclass
class BindCraftParams(WorkflowParams):
    # path to input pdb in S3 or other storage backend
    input_pdb_path: str = field(default=None, metadata=dict(show_to_user=False, storage_path=True))
    # comma-separated target chain ids (for example "A,B")
    target_chains: str = None
    # minimum and maximum number of residues in designed binder
    binder_length: str = "70,150"
    # hotspot residues, comma-separated like A123,A124
    hotspots: str | None = None
    # run pipeline until given number of accepted designs are generated
    number_of_final_designs: int = 2
    # time limit in hours
    time_limit_hours: int = 24
    # filter (Default, Peptide, Relaxed, Peptide_Relaxed, None)
    filter_type: str = "Default"
    # design protocol (Default, Beta-sheet, Peptide)
    design_protocol: str = "Default"
    # interface protocol (AlphaFold2, MPNN)
    interface_protocol: str = "AlphaFold2"
    # template protocol (Default, Masked)
    template_protocol: str = "Default"
    # prediction protocol (Default, HardTarget)
    prediction_protocol: str = "Default"
    # dictionary with advanced settings that override default values
    # for example {"omit_AAs": ""}
    custom_advanced_settings: dict = None
    # dictionary with filter settings that override default values
    # for example {"1_pLDDT": {"threshold": 0.8, "higher": true}}
    custom_filter_settings: dict = None
    # Number of parallel replicas to run (default: 1). Each replica will stop when it reaches time_limit_seconds or when it generates the desired number of accepted designs.
    num_replicas: int = 1

    @classmethod
    def from_dict(cls, data):
        data = copy(data)
        return cls(**data)

    def validate(self):
        super().validate()
        if not self.input_pdb_path:
            raise ValueError("No input pdb provided")
        if not self.target_chains:
            raise ValueError("No target chains provided")
        if not self.binder_length:
            raise ValueError("No binder length provided")
        if not self.number_of_final_designs:
            raise ValueError("No number of final designs provided")
        if not self.binder_length.replace(",", "").isdigit():
            raise ValueError(f"Binder length should be 'length' or 'min,max', got: '{self.binder_length}'")
        if self.hotspots:
            # check if hotspots are in the form of A123,A124
            for hotspot in self.hotspots.split(","):
                if not hotspot:
                    raise ValueError(f"Invalid hotspot: {self.hotspots}")
                if not hotspot[0].isalpha():
                    raise ValueError(
                        f"Hotspot residue should be prefixed with chain ID (for example A123,A124), got: {self.hotspots}"
                    )
                if not any(hotspot.startswith(chain) for chain in self.target_chains.split(",")):
                    raise ValueError(f"Hotspot {hotspot} does not match selected target chains {self.target_chains}")


@WorkflowTypes.register("BindCraft binder design")
@dataclass
class BindCraftBinderDesignWorkflow(DesignWorkflow, RefoldingSupportedDesignWorkflow):
    """Dataclass for BindCraft binder design workflow."""

    # input parameters for BindCraft
    bindcraft_params: BindCraftParams | None = field(
        default_factory=BindCraftParams, metadata=dict(tool_name="BindCraft")
    )

    # UI state variables
    # User-provided PDB code (or filename in case of uploaded file)
    input_name: str | None = None
    # selected binder hotspots, synchronized with bindcraft_params.hotspots
    selected_segments: list[str] | None = None
    # dict chains, key: chain, value: contig, e.g. {A: A1-100/102-110/112-130, B: B23-202}
    chains: dict | None = None

    def get_input_pdb_paths(self):
        return [self.get_input_pdb_path()]

    def get_input_pdb_path(self):
        return self.bindcraft_params.input_pdb_path

    def get_selected_segments(self):
        return self.selected_segments or []

    def set_selected_segments(self, segments: list[str]):
        self.selected_segments = segments
        self.bindcraft_params.hotspots = from_segments_to_hotspots(segments)

    def get_pipeline_name(self) -> str:
        return "ovo.bindcraft"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.design_logic_bindcraft import prepare_bindcraft_params

        return prepare_bindcraft_params(self, workdir=workdir)

    def process_results(self, job: DesignJob, callback: Callable = None) -> list[Base]:
        """Process results of a successful workflow - download files from workdir,
        create Design and DescriptorValue objects"""
        from ovo.core.logic.design_logic_bindcraft import process_workflow_results

        return process_workflow_results(job=job, callback=callback)

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import bindcraft_binder_design_visualization

        bindcraft_binder_design_visualization(design_id)

    @classmethod
    def get_download_fields(cls):
        return {
            "BindCraft Input PDB": (BindCraftBinderDesignWorkflow, "bindcraft_params.input_pdb_path"),
            "BindCraft design": (Design, "structure_path"),
        }

    def get_settings_paths(self):
        ovo_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "resources"))
        bindcraft_resources_path = os.path.join(ovo_resources_path, "bindcraft")

        # Logic to determine protocol tags
        if self.bindcraft_params.design_protocol == "Default":
            design_protocol_tag = "default_4stage_multimer"
        elif self.bindcraft_params.design_protocol == "Beta-sheet":
            design_protocol_tag = "betasheet_4stage_multimer"
        elif self.bindcraft_params.design_protocol == "Peptide":
            design_protocol_tag = "peptide_3stage_multimer"
        else:
            raise ValueError(f"Unsupported design protocol {self.bindcraft_params.design_protocol}")

        if self.bindcraft_params.interface_protocol == "AlphaFold2":
            interface_protocol_tag = ""
        elif self.bindcraft_params.interface_protocol == "MPNN":
            interface_protocol_tag = "_mpnn"
        else:
            raise ValueError(f"Unsupported interface protocol {self.bindcraft_params.interface_protocol}")

        if self.bindcraft_params.template_protocol == "Default":
            template_protocol_tag = ""
        elif self.bindcraft_params.template_protocol == "Masked":
            template_protocol_tag = "_flexible"
        else:
            raise ValueError(f"Unsupported template protocol {self.bindcraft_params.template_protocol}")

        if self.bindcraft_params.design_protocol == "Peptide":
            prediction_protocol_tag = ""
        else:
            if self.bindcraft_params.prediction_protocol == "Default":
                prediction_protocol_tag = ""
            elif self.bindcraft_params.prediction_protocol == "HardTarget":
                prediction_protocol_tag = "_hardtarget"
            else:
                raise ValueError(f"Unsupported prediction protocol {self.bindcraft_params.prediction_protocol}")

        # Final advanced settings path
        advanced_settings_filename = (
            design_protocol_tag + interface_protocol_tag + template_protocol_tag + prediction_protocol_tag + ".json"
        )
        advanced_settings_path = os.path.join(bindcraft_resources_path, "settings_advanced", advanced_settings_filename)

        if self.bindcraft_params.filter_type == "Default":
            filter_filename = "default_filters.json"
        elif self.bindcraft_params.filter_type == "Peptide":
            filter_filename = "peptide_filters.json"
        elif self.bindcraft_params.filter_type == "Relaxed":
            filter_filename = "relaxed_filters.json"
        elif self.bindcraft_params.filter_type == "Peptide_Relaxed":
            filter_filename = "peptide_relaxed_filters.json"
        elif self.bindcraft_params.filter_type == "None":
            filter_filename = "no_filters.json"
        else:
            raise ValueError(f"Unsupported filter type: {self.bindcraft_params.filter_type}")

        filter_settings_path = os.path.join(bindcraft_resources_path, "settings_filters", filter_filename)

        return advanced_settings_path, filter_settings_path

    def get_refolding_designed_chains(self) -> list[str]:
        return ["B"]

    def get_refolding_native_pdb_path(self, contig_index: int) -> str:
        return self.get_input_pdb_path()

    def get_refolding_design_paths(self, design_ids: list[str]) -> dict[str, str]:
        from ovo import db

        # In BindCraft binder design, we assume the designed structure is the predicted structure, so return design structure paths for all design ids
        design_paths = db.select_dict(Design, "id", "structure_path", id__in=design_ids)
        return design_paths

    def get_refolding_design_type(self) -> str:
        return "binder"
