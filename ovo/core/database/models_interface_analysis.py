from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, ClassVar

from ovo import ResidueNumberDescriptor
from ovo.app.utils.cached_db import get_cached_num_cyclic
from ovo.core.database import descriptors_rfdiffusion
from ovo.core.database.models import DescriptorWorkflow, WorkflowTypes, Design, Base, DescriptorJob, Descriptor


class InterfaceAnalysisWorkflow(DescriptorWorkflow, ABC):
    """Base class for interface analysis workflows. chains field = binder chain(s)."""

    interface_descriptors: ClassVar[list[Descriptor]] = []
    residue_number_descriptors: ClassVar[dict[str, tuple[ResidueNumberDescriptor, ResidueNumberDescriptor]]] = {}

    @classmethod
    @abstractmethod
    def from_ui(cls, design_ids: list[str]) -> list["InterfaceAnalysisWorkflow"]:
        raise NotImplementedError()


@WorkflowTypes.register("Biotite interface analysis")
@dataclass
class BiotiteInterfaceAnalysisWorkflow(InterfaceAnalysisWorkflow):
    interface_descriptors = [
        descriptors_rfdiffusion.N_HYDROGEN_BONDS,
        descriptors_rfdiffusion.N_SALT_BRIDGES,
        descriptors_rfdiffusion.N_PI_CATION_INTERACTIONS,
        descriptors_rfdiffusion.N_PI_STACKING_INTERACTIONS,
        descriptors_rfdiffusion.N_DISULFIDE_BONDS,
    ]
    residue_number_descriptors = {
        "Biotite all-atom (within 4.5Å)": (
            descriptors_rfdiffusion.BIOTITE_INTERFACE_TARGET_RESIDUES_AA,
            descriptors_rfdiffusion.BIOTITE_INTERFACE_BINDER_RESIDUES_AA,
        )
    }

    target_chains: List[str] = field(default_factory=lambda: ["B"])

    def get_pipeline_name(self) -> str:
        return "ovo.biotite-interface-metrics"

    def prepare_params(self, workdir: str) -> dict:
        from ovo import db
        from ovo.core.logic.descriptor_logic import prepare_design_structures

        designs = db.select(Design, id__in=self.design_ids)
        pdb_dir = prepare_design_structures(designs, workdir=workdir)
        return {
            "pdb_dir": pdb_dir,
            "binder_chain_id": self.chains[0],
            "target_chain_id": ",".join(self.target_chains),
        }

    def process_results(self, job: DescriptorJob, callback: Callable = None) -> list[Base]:
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            filenames={"biotite_interface_metrics|biotite": "biotite_interface_metrics"},
            design_id_mapping={did: did for did in self.design_ids},
        )
        return descriptor_values + [job]

    def validate(self):
        super().validate()
        if not self.chains:
            raise ValueError("At least one binder chain must be specified")
        if not self.target_chains:
            raise ValueError("At least one target chain must be specified")
        if len(self.target_chains) != 1:
            raise ValueError("Biotite interface analysis currently supports exactly one target chain")

    @classmethod
    def from_ui(cls, design_ids: list[str]) -> list["BiotiteInterfaceAnalysisWorkflow"]:
        import streamlit as st
        from ovo.app.components.input_components import get_default_target_chain, binder_chain_input

        n = len(design_ids)
        st.write(f"Submit Biotite interface analysis for {n:,} {'design' if n == 1 else 'designs'}")

        binder_chain = binder_chain_input(design_ids, key_prefix="biotite")
        if not binder_chain:
            return []

        target_chain_str = st.text_input(
            "Target chain",
            value=get_default_target_chain(binder_chain),
            help="Chain ID of the target protein in the PDB file",
            key="biotite_target_chain",
        ).strip()
        if not target_chain_str:
            st.warning("Please specify a target chain ID")
            return []

        return [
            cls(
                design_ids=design_ids,
                chains=[binder_chain],
                target_chains=[target_chain_str],
            )
        ]


@WorkflowTypes.register("PyRosetta interface analysis")
@dataclass
class PyRosettaInterfaceAnalysisWorkflow(InterfaceAnalysisWorkflow):
    interface_descriptors = [
        descriptors_rfdiffusion.PYROSETTA_DDG,
        descriptors_rfdiffusion.PYROSETTA_CMS,
        descriptors_rfdiffusion.PYROSETTA_SAP_SCORE,
        descriptors_rfdiffusion.PYROSETTA_BUNS,
        descriptors_rfdiffusion.PYROSETTA_BUNS_PERCENT,
    ]
    residue_number_descriptors = {
        "PyRosetta all-atom (within 4.5Å)": (
            descriptors_rfdiffusion.PYROSETTA_INTERFACE_TARGET_RESIDUES_AA,
            descriptors_rfdiffusion.PYROSETTA_INTERFACE_BINDER_RESIDUES_AA,
        )
    }

    target_chains: List[str] = field(default_factory=lambda: ["B"])
    relax: bool = True

    def get_pipeline_name(self) -> str:
        return "ovo.pyrosetta-interface-metrics"

    def prepare_params(self, workdir: str) -> dict:
        from ovo import db
        from ovo.core.logic.descriptor_logic import prepare_design_structures

        designs = db.select(Design, id__in=self.design_ids)
        pdb_dir = prepare_design_structures(designs, workdir=workdir)
        return {
            "pdb_dir": pdb_dir,
            "relax": self.relax,
            "binder_chain": self.chains[0],
            "target_chain": ",".join(self.target_chains),
        }

    def process_results(self, job: DescriptorJob, callback: Callable = None) -> list[Base]:
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values, read_per_design_files
        from ovo.core.database.descriptors_rfdiffusion import FASTRELAX_STRUCTURE_PATH

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            filenames={"pyrosetta_interface_metrics|pyrosetta": "pyrosetta_interface_metrics"},
            design_id_mapping={did: did for did in self.design_ids},
        )

        if self.relax:
            descriptor_values += read_per_design_files(
                descriptor_job=job,
                design_id_mapping={did: did for did in self.design_ids},
                design_files={
                    "relaxed_pdb/{}_relaxed.pdb": (
                        "structures",
                        "_pyrosetta_relaxed.pdb",
                        FASTRELAX_STRUCTURE_PATH.key,
                    ),
                },
                callback=callback,
            )

        return descriptor_values + [job]

    def validate(self):
        super().validate()
        if not self.chains:
            raise ValueError("At least one binder chain must be specified")
        if not self.target_chains:
            raise ValueError("At least one target chain must be specified")
        if len(self.target_chains) != 1:
            raise ValueError("PyRosetta interface analysis currently supports exactly one target chain")

    @classmethod
    def supports_cyclic(cls):
        return False

    @classmethod
    def from_ui(cls, design_ids: list[str]) -> list["PyRosettaInterfaceAnalysisWorkflow"]:
        import streamlit as st
        from ovo.app.components.input_components import get_default_target_chain, binder_chain_input

        n = len(design_ids)
        st.write(f"Submit PyRosetta interface analysis for {n:,} {'design' if n == 1 else 'designs'}")

        if not cls.supports_cyclic() and get_cached_num_cyclic(design_ids):
            raise ValueError("Cyclic peptides are not supported by this workflow.")

        binder_chain = binder_chain_input(design_ids, key_prefix="pyrosetta")
        if not binder_chain:
            return []

        target_chain_str = st.text_input(
            "Target chain",
            value=get_default_target_chain(binder_chain),
            help="Chain ID of the target protein in the PDB file",
            key="pyrosetta_target_chain",
        ).strip()
        if not target_chain_str:
            st.warning("Please specify a target chain ID")
            return []

        relax = st.checkbox(
            "Relax structures before scoring",
            value=PyRosettaInterfaceAnalysisWorkflow.relax,  # default value
            help="Run FastRelax on interface side chains before computing metrics. More accurate but significantly slower.",
            key="pyrosetta_relax",
        )

        return [
            cls(
                design_ids=design_ids,
                chains=[binder_chain],
                target_chains=[target_chain_str],
                relax=relax,
            )
        ]
