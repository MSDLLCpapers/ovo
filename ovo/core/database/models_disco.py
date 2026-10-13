import json
from copy import copy
from dataclasses import dataclass, field
from typing import Callable

from ovo.core.database import descriptors_refolding
from ovo.core.database.models import DesignWorkflow, WorkflowParams, WorkflowTypes, DesignJob, Design, Base, Threshold
from ovo.core.database.models_refolding import RefoldingSupportedDesignWorkflow, RefoldingWorkflow
from ovo.core.database.descriptors_refolding import REFOLDING_TESTS_BY_TYPE


@dataclass
class DiscoParams(WorkflowParams):
    # ligand in DISCO format: "CCD_<code>" (CCD code), a bare SMILES string, or "FILE_<path>" (uploaded file)
    ligand: str | None = None
    # storage path of an uploaded ligand file (set when ligand uses the "FILE_" mode)
    ligand_file_path: str | None = field(default=None, metadata=dict(show_to_user=False, storage_path=True))
    # protein chain length (number of masked "-" residues to generate)
    sequence_length: int = 100
    # user-specified raw DISCO input JSON (advanced mode); when set, it overrides the structured fields above
    custom_input_json: str | None = None
    # path to a pre-made DISCO input JSON in storage (escape hatch; the UI generates the JSON at submit time)
    input_json_path: str | None = field(default=None, metadata=dict(show_to_user=False, storage_path=True))
    # experiment preset: "designable" or "diverse"
    experiment: str = "designable"
    # compute effort: "max" (200 steps) or "fast" (100 steps)
    effort: str = "fast"
    # number of random seeds (designs) to generate
    num_designs: int = 5
    # additional LigandMPNN run parameters
    ligandmpnn_run_parameters: str = ""

    @classmethod
    def from_dict(cls, data):
        data = copy(data)
        return cls(**data)

    def validate(self):
        super().validate()
        if self.custom_input_json:
            # Advanced mode: the user supplies the full DISCO input JSON (a non-empty list of jobs).
            try:
                parsed = json.loads(self.custom_input_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Custom input JSON is not valid JSON: {e}") from e
            if not isinstance(parsed, list) or not parsed:
                raise ValueError("Custom input JSON must be a non-empty list of DISCO jobs")
        elif not self.input_json_path and self.sequence_length < 1:
            # A ligand is optional (no ligand = unconditional generation). When no pre-made input JSON is
            # provided, the UI generates one from sequence_length (and the optional ligand) at submit time.
            raise ValueError(f"sequence_length must be at least 1, got: {self.sequence_length}")
        if self.experiment not in ("designable", "diverse"):
            raise ValueError(f"experiment must be 'designable' or 'diverse', got: '{self.experiment}'")
        if self.effort not in ("max", "fast"):
            raise ValueError(f"effort must be 'max' or 'fast', got: '{self.effort}'")
        if self.num_designs < 1:
            raise ValueError(f"num_designs must be at least 1, got: {self.num_designs}")


@WorkflowTypes.register("DISCO design")
@dataclass
class DiscoWorkflow(DesignWorkflow, RefoldingSupportedDesignWorkflow):
    """Dataclass for DISCO sequence-structure co-design workflow."""

    disco_params: DiscoParams | None = field(default_factory=DiscoParams, metadata=dict(tool_name="DISCO"))

    # acceptance threshold values (descriptor key -> interval (min, max, enabled))
    acceptance_thresholds: dict[str, Threshold] = field(
        default_factory=lambda: {
            # Disco paper defined success (co-designability) as backbone RMSD < 2
            descriptors_refolding.BOLTZ_PRIMARY_DESIGN_RMSD.key: Threshold(max_value=2.0),
            descriptors_refolding.BOLTZ_PRIMARY_PLDDT.key: Threshold(min_value=0.8),
            # other thresholds from paper (A.10) https://arxiv.org/abs/2604.05181
            descriptors_refolding.BOLTZ_PRIMARY_PTM_SCORE.key: Threshold(min_value=0.7),
            descriptors_refolding.BOLTZ_PRIMARY_IPTM_SCORE.key: Threshold(min_value=0.7),
            descriptors_refolding.BOLTZ_PRIMARY_LIGAND_IPTM_SCORE.key: Threshold(min_value=0.7),
            descriptors_refolding.BOLTZ_PRIMARY_PROTEIN_IPTM_SCORE.key: Threshold(min_value=0.5),
            # TODO: what are good values for these? is this comparable to AF's PAE?
            # descriptors_refolding.BOLTZ_PRIMARY_PDE.key: Threshold(max_value=2.0),
            # descriptors_refolding.BOLTZ_PRIMARY_IPDE.key: Threshold(max_value=2.0),
        }
    )

    def get_pipeline_name(self) -> str:
        return "ovo.disco"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.design_logic_disco import prepare_disco_params

        return prepare_disco_params(self, workdir=workdir)

    def process_results(self, job: DesignJob, callback: Callable = None) -> list[Base]:
        from ovo.core.logic.design_logic_disco import process_workflow_results

        return process_workflow_results(job=job, callback=callback)

    def get_contig_indexes(self) -> list[int]:
        return [0]

    def get_refolding_design_type(self) -> str:
        return "scaffold"

    def get_refolding_designed_chains(self) -> list[str]:
        return ["A"]

    def get_refolding_native_pdb_path(self, contig_index: int) -> str | None:
        return None

    def get_refolding_design_paths(self, design_ids: list[str]) -> dict[str, str]:
        from ovo import db

        return {d.id: d.structure_path for d in db.select(Design, id__in=design_ids)}

    def get_skipped_threshold_keys(self) -> list[str]:
        skipped_keys = []

        if self.disco_params.ligand is None:
            for key in self.acceptance_thresholds.keys():
                if key.startswith("refolding|") and any(kw in key for kw in ["ligand", "iptm", "iplddt", "ipde"]):
                    skipped_keys.append(key)

        return skipped_keys

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single DISCO design structures in Streamlit."""
        from ovo.app.components.workflow_visualization_components import disco_design_visualization

        disco_design_visualization(design_id)
