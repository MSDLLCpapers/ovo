import os
import uuid
from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field, asdict
from datetime import datetime
from datetime import timezone
from typing import Callable, List, Literal, Union

import pandas as pd
from sqlalchemy import String, Boolean, DateTime, func, Integer, UniqueConstraint, JSON
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import mapped_column

from ovo.core.database.encoder import DataclassType
from ovo.core.database.db_proxy import DBProxy
from ovo.core.scheduler.base_scheduler import Scheduler
from ovo.core.utils.formatting import generate_id
from ovo.core.utils.pdb import (
    get_sequences_from_pdb_str,
    ChainNotFoundError,
    get_standardized_remarks_from_pdb_str,
)
import json


class Base(MappedAsDataclass, DeclarativeBase, metaclass=DBProxy):
    """subclasses will be converted to dataclasses"""


class JobMixin(MappedAsDataclass):
    scheduler_key: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    job_started_date_utc: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    job_finished_date_utc: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)
    # None = in progress, True = success, False = failed
    job_result: Mapped[bool | None] = mapped_column(Boolean, default=None, nullable=True, index=True)
    warnings: Mapped[list[str]] = mapped_column(JSON, default_factory=list, nullable=False)


class MetadataMixin(MappedAsDataclass):
    author: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    created_date_utc: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
        default_factory=lambda: datetime.now(timezone.utc),
        server_default=func.datetime("now"),
    )


class UserSettings(Base):
    __tablename__ = "user_setting"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    last_project_id: Mapped[str] = mapped_column(String, default=None, nullable=True)


class Project(Base, MetadataMixin):
    __tablename__ = "project"
    __table_args__ = (UniqueConstraint("name", "author", name="uq_project_name_author"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    # TODO should project names be unique? Or conditionally - if they are public?
    name: Mapped[str] = mapped_column(String, default=None, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)


class Round(Base, MetadataMixin):
    __tablename__ = "round"

    id: Mapped[str] = mapped_column(String, primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, default=None, nullable=False)
    description: Mapped[str] = mapped_column(String, default=None, nullable=True)


MODEL_WEIGHTS_SCAFFOLD = ["Base", "ActiveSite"]
MODEL_WEIGHTS_BINDER = ["Complex_base", "Complex_beta"]


@dataclass
class WorkflowParams:
    def validate(self):
        pass

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self, human_readable=False):
        data = asdict(self)
        if human_readable:
            data = {k: v for k, v in data.items() if self.__dataclass_fields__[k].metadata.get("show_to_user", True)}
        return data


@dataclass
class Threshold:
    # min value
    min_value: float | None = None
    # max value
    max_value: float | None = None
    # enabled flag
    enabled: bool = True

    def copy(self, **kwargs) -> "Threshold":
        copied = copy(self)
        for key, value in kwargs.items():
            setattr(copied, key, value)
        return copied

    def __eq__(self, other):
        # NOTE: Not checking type because it's broken by live-reload, check attributes instead
        if not hasattr(other, "min_value") or not hasattr(other, "max_value") or not hasattr(other, "enabled"):
            return False
        return self.min_value == other.min_value and self.max_value == other.max_value and self.enabled == other.enabled

    def format(self, descriptor_name: str = "") -> str | None:
        if self.min_value is None and self.max_value is not None:
            return f"{descriptor_name} ≤ {self.max_value:.3f}".strip()
        elif self.max_value is None and self.min_value is not None:
            return f"{descriptor_name} ≥ {self.min_value:.3f}".strip()
        elif self.min_value is not None and self.max_value is not None:
            if descriptor_name:
                return f"{descriptor_name} within {self.min_value:.3f} — {self.max_value:.3f}"
            else:
                return f"{self.min_value:.3f} — {self.max_value:.3f}"
        return None

    def get_bounds(
        self, descriptor: "NumericDescriptor", descriptor_values: pd.Series
    ) -> tuple[float | int, float | int] | None:
        """Get min, max bounds for the threshold for a specific set of designs, based on the descriptor values

        Can be used to plot the threshold on a histogram or scatter plot.

        :param descriptor: Descriptor object, used to get the min and max values if not set in the threshold
        :param descriptor_values: Series of descriptor values for the designs, used to determine the bounds
        :return: tuple of (min, max) bounds for the threshold, or None if no bounds are set
        """
        if self.min_value is None and self.max_value is None:
            return None
        # we will widen the range for integer values to make it clear that the value is included (we use >= and <=)
        is_int = all(int(v) == v for v in descriptor_values if not pd.isna(v))
        min_allowed, max_allowed = self.min_value, self.max_value
        # delta = 1.5 times the whole X range of the plot
        delta = (descriptor_values.max() - descriptor_values.min()) * 1.5 if not descriptor_values.empty else 1
        if min_allowed is None:
            # (-inf to threshold.max_value)
            if descriptor.min_value is not None:
                # if the descriptor has a defined min value we can start from there
                min_allowed = descriptor.min_value
            else:
                # otherwise we start at the max minus the width of the plot (we double the range)
                min_allowed = max_allowed - delta
            if not descriptor_values.empty and descriptor_values.min() < min_allowed:
                # expand the range further in case any actual values are even lower
                min_allowed = descriptor_values.min()
        elif max_allowed is None:
            # (threshold.min_value to +inf)
            if descriptor.max_value is not None:
                max_allowed = descriptor.max_value
            else:
                max_allowed = min_allowed + delta
            if not descriptor_values.empty and descriptor_values.max() > max_allowed:
                max_allowed = descriptor_values.max()
        else:
            # threshold.min_value to threshold.max_value, we are all set
            pass

        if is_int:
            min_allowed -= 0.5
            max_allowed += 0.5

        return min_allowed, max_allowed


class WorkflowTypes:
    # workflow name -> class
    _registry = {}

    @classmethod
    def register(cls, workflow_name=None):
        """Decorator to register a workflow class with a given name"""
        assert workflow_name is None or isinstance(workflow_name, str), (
            "Usage: WorkflowTypes.register(workflow_name=...) or @WorkflowTypes.register()"
        )

        def decorator(registered_class):
            # Use provided workflow name or "ovo_module ClassName" if not provided
            registered_class.name = workflow_name or f"{registered_class.__module__} {registered_class.__name__}"
            cls._registry[registered_class.name] = registered_class
            return registered_class

        return decorator

    @classmethod
    def exists(cls, workflow_name):
        """Check if a workflow type with the given name exists"""
        return workflow_name in cls._registry

    @classmethod
    def get(cls, workflow_name):
        """Get workflow class by name"""
        if workflow_name not in cls._registry:
            raise ValueError(
                f"Workflow type '{workflow_name}' is not registered, available types: {list(cls._registry.keys())}"
            )
        return cls._registry[workflow_name]

    @classmethod
    def get_subclass_names(cls, workflow_name) -> list[str]:
        """Get list of registered workflow names that are subclasses of the given workflow name (including itself)"""
        BaseWorkflowType = WorkflowTypes.get(workflow_name)
        workflow_names = [workflow_name]
        for n, WorkflowType in WorkflowTypes._registry.items():
            if n == workflow_name:
                # workflow_name is already included at the start of the list
                continue
            if WorkflowType.is_subclass(BaseWorkflowType):
                workflow_names.append(n)
        return workflow_names


@dataclass
class Workflow:
    # name is filled in by @WorkflowTypes.register decorator
    name: str = field(init=False)

    def is_instance(self, cls):
        """Safe isinstance that avoids error on objects loaded from Streamlit session state after live reload

        This solves the problem that sometimes is_instance returns false in our app
        even though the object actually is of that class.

        See documentation: https://docs.streamlit.io/develop/concepts/design/custom-classes
        And issue: https://github.com/streamlit/streamlit/issues/8180
        """
        return self.__class__.is_subclass(cls)

    @classmethod
    def is_subclass(cls, other_cls):
        """Safe issubclass that avoids error on objects loaded from Streamlit session state after live reload"""
        other_cls_name = f"{other_cls.__module__}.{other_cls.__name__}"
        this_class_and_superclass_names = [f"{c.__module__}.{c.__name__}" for c in cls.__mro__]
        return other_cls_name in this_class_and_superclass_names

    @classmethod
    def from_dict(cls, data):
        """Convert dict to Workflow object - NOTE: This method currently cannot be extended, the base class method will always be called! See db.encoder module"""

        data = copy(data)
        workflow_name = data["name"]
        if not WorkflowTypes.exists(workflow_name):
            return UnknownWorkflow(
                data=data,
                error=f"Workflow is not registered: '{workflow_name}'",
            )

        try:
            subclass = WorkflowTypes.get(workflow_name)
            for field_name, empty_params in subclass().get_param_fields().items():
                if data.get(field_name):
                    # instantiate params dataclasses from dicts
                    data[field_name] = type(empty_params).from_dict(data[field_name])

            # convert all thresholds to Threshold objects
            if "acceptance_thresholds" in data:
                for key, value in data["acceptance_thresholds"].items():
                    data["acceptance_thresholds"][key] = Threshold(**value)

            return subclass(**{k: v for k, v in data.items() if k not in ("name",)})
        except Exception as e:
            if os.getenv("OVO_STRICT_JSON", "").lower() in ("1", "true", "yes"):
                raise e
            return UnknownWorkflow(
                data=data,
                error=f"Unexpected error when loading workflow from DB, this might be due to changes to the schema. Migration steps might need to be applied. Error: {e}",
            )

    def get_param_fields(self, human_readable=False) -> dict[str, WorkflowParams]:
        """Get all ..._param fields, verify they are instances of WorkflowParams

        with human_readble=False, returns dict: field_name -> params instance
        with human_readble=True, returns dict: Tool name -> params instance
        """
        fields = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            if tool_name := field_def.metadata.get("tool_name"):
                assert value is not None, (
                    f"Params should be initialized with default factory, "
                    f"found None in {type(self).__name__}.{field_name}"
                )

                # NOTE: if this fails, it might also be due to live-reload,
                # we might need to adapt the logic to handle that
                assert isinstance(value, WorkflowParams), "Params should be instance of WorkflowParams"
                assert "__dataclass_fields__" in type(value).__dict__, (
                    f"WorkflowParams subclass should be decorated with @dataclass: {type(value).__name__}"
                )
                key = tool_name if human_readable else field_name
                fields[key] = value
            elif isinstance(value, WorkflowParams):
                raise ValueError(
                    f'Workflow param fields should be declared with field(metadata=dict(tool_name="...")) '
                    f"in {type(self).__name__}.{field_name}"
                )

        return fields

    def get_table_row(self, **kwargs) -> pd.Series:
        """Get all values of all param fields, skip fields with metadata.show_to_user=False, return pd.Series"""
        if param_fields := self.get_param_fields(human_readable=True):
            param_columns = {
                (tool_name, subfield_name): value
                for tool_name, params in param_fields.items()
                for subfield_name, value in params.to_dict(human_readable=True).items()
            }
        elif hasattr(self, "params") and isinstance(self.params, dict):
            field_def = self.__dataclass_fields__.get("params")
            if field_def and field_def.metadata and "tool_name" in field_def.metadata:
                tool_name = field_def.metadata["tool_name"]
            else:
                tool_name = "Params"
            param_columns = {(tool_name, k): v for k, v in self.params.items()}
        else:
            param_columns = {}
        return pd.Series(
            {
                ("Workflow", "type"): self.name,
                **param_columns,
            },
            **kwargs,
        )

    def validate(self):
        for field_name, params in self.get_param_fields().items():
            try:
                params.validate()
            except Exception as e:
                raise ValueError(f"Validation failed for workflow.{field_name} ({type(params).__name__}: {e}") from e

    def get_time_estimate(self, scheduler: Scheduler) -> str:
        return "Time estimate: No time estimate available for this workflow"

    @abstractmethod
    def get_pipeline_name(self) -> str:
        """Get name (for example ovo.rfdiffusion-end-to-end) or github URL of pipeline to be submitted for this workflow"""
        raise NotImplementedError()

    @abstractmethod
    def prepare_params(self, workdir: str) -> dict:
        """Submit the workflow to the scheduler and return the job id"""
        raise NotImplementedError()

    @abstractmethod
    def process_results(self, job: Union["DesignJob", "DescriptorJob"], callback: Callable = None) -> list[Base]:
        """Process results of a successful workflow - download files from workdir,
        create and return objects to be saved such as Designs and DescriptorValues"""
        raise NotImplementedError()

    @classmethod
    def get_download_fields(cls):
        return {
            "pdb files": (Design, "structure_path"),
        }


@dataclass
class DescriptorWorkflow(Workflow, ABC):
    chains: List[str] = field(default_factory=list)
    design_ids: List[str] = field(default_factory=list)

    def validate(self):
        super().validate()
        if not self.chains:
            raise ValueError("No chains provided")
        if not isinstance(self.chains, list):
            raise ValueError(
                f"DescriptorWorkflow.chains must be a list, got {self.chains} ({type(self.chains).__name__})"
            )
        if not self.design_ids:
            raise ValueError("No design IDs provided")


@WorkflowTypes.register("Design Descriptor Workflow")
@dataclass
class DesignDescriptorWorkflow(DescriptorWorkflow):
    """Placeholder DescriptorWorkflow used when the descriptors are generated by a design workflow"""

    design_job_id: str = field(default=None)


@dataclass
class DesignWorkflow(Workflow):
    # acceptance threshold values (descriptor key -> interval (min, max, enabled))
    acceptance_thresholds: dict[str, Threshold] = field(default_factory=dict)

    def get_table_row(self, **kwargs) -> pd.Series:
        """Get all values of all param fields, skip fields with metadata.show_to_user=False, return pd.Series"""
        row = super().get_table_row(**kwargs)
        from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY

        return pd.concat(
            [
                row,
                pd.Series(
                    {
                        ("Thresholds", ALL_DESCRIPTORS_BY_KEY[key].name): t.format()
                        for key, t in self.acceptance_thresholds.items()
                        if t.enabled
                    },
                    **kwargs,
                ),
            ]
        )

    def validate(self):
        super().validate()
        from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY

        for key, threshold in self.acceptance_thresholds.items():
            if not isinstance(threshold, Threshold):
                raise ValueError(
                    f"Acceptance threshold for {key} should be an instance of Threshold, got {threshold} ({type(threshold).__name__})"
                )
            if not isinstance(key, str):
                raise ValueError(f"Acceptance threshold key should be a string, got {key} ({type(key).__name__})")
            if key not in ALL_DESCRIPTORS_BY_KEY:
                raise ValueError(f"Unknown descriptor key '{key}' in acceptance thresholds")

    @classmethod
    def visualize_multiple_designs_structures(cls, design_ids: list[str]):
        """Visualize multiple design structures in Streamlit"""
        raise NotImplementedError()

    @classmethod
    def visualize_single_design_structures(cls, design_id: str):
        """Visualize single design structures in Streamlit"""
        from ovo.app.components.workflow_visualization_components import visualize_design_structure

        visualize_design_structure(design_id)

    @classmethod
    def visualize_single_design_sequences(self, design_id: str):
        from ovo.app.components.workflow_visualization_components import visualize_design_sequence

        visualize_design_sequence(design_id)

    def get_relevant_descriptor_keys(self) -> list[str]:
        """Get list of descriptor keys that are of interest for this workflow

        Used to determine which descriptors to show in the Explorer table

        By default, we return all descriptors included in the accepted_thresholds field for this workflow (even disabled ones)
        """
        return list(self.acceptance_thresholds.keys())


@WorkflowTypes.register("Unknown Workflow")
class UnknownWorkflow(DesignWorkflow, DescriptorWorkflow):
    """Unknown workflow type, used when the workflow type is not recognized or not registered

    This can happen when a plugin is uninstalled.
    """

    # Avoid saving this class to DB, handled by DataclassEncoder
    __do_not_serialize__ = True
    # Raw data dict as stored in the workflow column
    data: dict = None
    # Explanation for why this workflow couldn't be loaded
    error: str = None

    def __init__(self, data: dict, error: str):
        self.data = data
        self.error = error
        # inherit all fields from DesignWorkflow and DescriptorWorkflow, combined inheritance doesn't seem to do the trick
        self.acceptance_thresholds = {}
        self.chains = []
        self.design_ids = []


class DesignJob(Base, MetadataMixin, JobMixin):
    __tablename__ = "design_job"

    id: Mapped[str] = mapped_column(String, primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    workflow: Mapped[DesignWorkflow] = mapped_column(DataclassType(Workflow), default=None, nullable=False)


class Pool(Base, MetadataMixin):
    __tablename__ = "pool"
    __table_args__ = (UniqueConstraint("name", "round_id", name="uq_pool_name_round"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=None)
    round_id: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    design_job_id: Mapped[str] = mapped_column(String, default=None, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String, default=None, nullable=False)
    description: Mapped[str] = mapped_column(String, default=None, nullable=True)
    # flag used to easily recognize a pool that has just finished but has not been processed yet
    # (job_result = True and processed = False)
    processed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @classmethod
    def generate_id(cls):
        return generate_id(previous_ids=Pool.select_unique_values("id"))


DesignChainType = Literal["protein", "dna", "rna", "ligand"]


x = {
    "id": "asdads",
    "spec": {
        "chains": [
            {"chain_ids": ["H"], "sequence": "QVQLV..."},
            {"chain_ids": ["L"], "sequence": "EIVL..."},
        ]
    },
    "structure_path": "asdasd/asdad",
}


@dataclass
class DesignChain:
    # Chain type: protein/dna/rna/ligand
    type: DesignChainType
    # Chain ID(s) for this chain in the PDB file
    # One chain or multiple chain IDs in case of multiple identical chains
    chain_ids: list[str]
    # Sequence (amino acid, DNA or RNA)
    sequence: str = None
    # SMILES string to define a ligand molecule
    smiles: str = None
    # CCD string to define a ligand molecule
    ccd: str = None
    # Contig string for this chain compatible with RFdiffusion motif scaffolding
    # Chains correspond to chains in input structure
    # May or may not contain the chain break suffix (/0)
    # Example: C123-456/10-10/C567-890/20-20/0
    contig: str = None
    # Macrocyclic chain
    cyclic: bool = False


@dataclass
class DesignSpec:
    chains: list[DesignChain]

    def get_chain(self, chain_id: str):
        for chain in self.chains:
            if chain_id in chain.chain_ids:
                return chain
        raise KeyError(f"Chain {chain_id} not found in design spec")

    @classmethod
    def from_pdb_str(cls, pdb_data: str, chains: list[str], cyclic=False):
        sequences = get_sequences_from_pdb_str(pdb_data, chains=chains)
        remarks = get_standardized_remarks_from_pdb_str(pdb_data)
        contig_by_chain = {}
        if remarks and remarks.get("Chains") and remarks.get("Standardized contig"):
            contig_chains = remarks["Standardized contig"].split()
            chains_list = remarks["Chains"].split()
            assert len(chains_list) == len(contig_chains)
            contig_by_chain = dict(zip(chains_list, contig_chains))
        return cls(
            chains=[
                DesignChain(
                    # TODO assuming all chains are protein, add support for ligands, dna, rna
                    type="protein",
                    # TODO enable detecting symmetric chains and using multiple chain ids here
                    chain_ids=[chain_id],
                    sequence=sequence,
                    contig=contig_by_chain.get(chain_id),
                    cyclic=cyclic,
                )
                for chain_id, sequence in sequences.items()
            ]
        )

    @classmethod
    def from_dict(cls, data):
        chains = [DesignChain(**chain_data) for chain_data in data.pop("chains")]
        return cls(chains=chains, **data)


class Design(Base):
    __tablename__ = "design"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    pool_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    structure_path: Mapped[str] = mapped_column(String, default=None, nullable=True, info=dict(storage_path=True))
    structure_descriptor_key: Mapped[str] = mapped_column(String, default=None, nullable=True)
    accepted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    spec: Mapped[DesignSpec] = mapped_column(DataclassType(DesignSpec), default=None, nullable=False)
    # This should be used when aligning design to its input - in case of multiple inputs
    contig_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __post_init__(self):
        assert self.pool_id, "pool_id must be set for Design"
        assert "_" not in self.pool_id, f"pool_id cannot contain underscores, got: {self.pool_id}"
        assert self.id, "id must be set for Design"
        if not self.id.startswith(f"ovo_{self.pool_id}_"):
            raise ValueError(f"Design ID '{self.id}' from pool '{self.pool_id}' must start with 'ovo_{self.pool_id}_'")

    @classmethod
    def design_id_to_pool_id(cls, design_id: str) -> str:
        """Get Pool ID from Design ID (ovo_xyz_1234 -> xyz)"""
        assert design_id.startswith("ovo_"), f"Invalid design ID '{design_id}'"
        assert design_id.count("_") >= 2, f"Invalid design ID '{design_id}'"
        return design_id.split("_")[1]

    @classmethod
    def from_pdb_file(
        cls,
        storage,
        filename: str,
        pdb_str: str,
        chains: list[str],
        project_id: str,
        pool_id: str,
        id: str = None,
        **kwargs,
    ):
        basename, file_extension = os.path.splitext(filename)
        if id is None:
            id = f"ovo_{pool_id}_{basename}"

        try:
            spec = DesignSpec.from_pdb_str(pdb_str, chains=chains)
        except ChainNotFoundError as e:
            raise ValueError(f"File '{filename}' does not contain requested chain '{e}'") from e

        return cls(
            id=id,
            pool_id=pool_id,
            spec=spec,
            structure_path=storage.store_file_str(
                pdb_str, os.path.join("project", project_id, "pools", pool_id, "designs", f"{id}.pdb")
            ),
            **kwargs,
        )


class DescriptorJob(Base, MetadataMixin, JobMixin):
    __tablename__ = "descriptor_job"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=None)
    project_id: Mapped[str] = mapped_column(String, default=None, nullable=False, index=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    workflow: Mapped[DescriptorWorkflow] = mapped_column(DataclassType(Workflow), default=None, nullable=False)

    @classmethod
    def generate_id(cls, tries=100):
        """Generate unique UID shortened for memory efficiency in descriptor_value table"""
        for length in range(6, 10):
            for i in range(tries):
                new_id = str(uuid.uuid4()).replace("-", "")[:length]
                try:
                    DescriptorJob.get(id=new_id)
                except NoResultFound:
                    return new_id
        raise ValueError(f"Failed to generate unique id of length {length} after {tries} tries")


class DescriptorValue(Base):
    __tablename__ = "descriptor_value"

    design_id: Mapped[str] = mapped_column(String, primary_key=True)
    descriptor_key: Mapped[str] = mapped_column(String, primary_key=True)
    descriptor_job_id: Mapped[str] = mapped_column(String, primary_key=True)
    # Comma-separated list of chain IDs for which this descriptor value applies
    # Can be same or a subset of descriptor_job.workflow.chains
    chains: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String, nullable=True)


class ArtifactTypes:
    # artifact type -> class
    _registry = {}

    @classmethod
    def register(cls):
        """Decorator to register an Artifact class"""

        def decorator(registered_class):
            artifact_type = f"{registered_class.__module__}.{registered_class.__qualname__}"
            cls._registry[artifact_type] = registered_class
            registered_class.artifact_type = artifact_type
            return registered_class

        return decorator

    @classmethod
    def exists(cls, artifact_type):
        """Check if an artifact of the given type exists"""
        return artifact_type in cls._registry

    @classmethod
    def get(cls, artifact_type):
        """Get artifact class by type string"""
        if artifact_type not in cls._registry:
            raise ValueError(
                f"Artifact type '{artifact_type}' is not registered, available types: {list(cls._registry.keys())}"
            )
        return cls._registry[artifact_type]


@dataclass
class Artifact(ABC):
    # artifact_type is filled in by @ArtifactTypes.register decorator
    artifact_type: str = field(init=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        data_copy = copy(data)
        artifact_type: str = data_copy.pop("artifact_type")
        if not ArtifactTypes.exists(artifact_type):
            raise ValueError(f"Artifact type '{artifact_type}' is not registered")
        ArtifactSubclass = ArtifactTypes.get(artifact_type)
        try:
            return ArtifactSubclass(**data_copy)
        except TypeError as e:
            return UnknownArtifact(
                data=data,
                error=f"Unexpected error when loading artifact from DB, this might be due to changes to the schema. Migration steps might need to be applied. Error: {e}",
            )

    @abstractmethod
    def get_storage_paths(self) -> list[str]:
        raise NotImplementedError()


@dataclass
class UnknownArtifact(Artifact):
    """Unknown artifact type, used when the artifact type is not recognized or not registered

    This can happen when a plugin is uninstalled.
    """

    # Avoid saving this class to DB, handled by DataclassEncoder
    __do_not_serialize__ = True
    # Raw data dict as stored in the artifact column
    data: dict = None
    # Explanation for why this artifact couldn't be loaded
    error: str = None

    def __init__(self, data: dict, error: str):
        self.data = data
        self.error = error

    def get_storage_paths(self) -> list[str]:
        return []


class ProjectArtifact(Base):
    __tablename__ = "project_artifact"
    id: Mapped[str] = mapped_column(String, primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, nullable=False, default=None, index=True)
    artifact_type: Mapped[str] = mapped_column(String, nullable=False, default=None, index=True)
    descriptor_job_id: Mapped[str] = mapped_column(String, nullable=True, default=None, index=True)
    design_job_id: Mapped[str] = mapped_column(String, nullable=True, default=None, index=True)
    artifact: Mapped[Artifact] = mapped_column(DataclassType(Artifact), default=None, nullable=False)


@dataclass
class Descriptor(ABC):
    # Human-readable name of the descriptor
    name: str = None
    # Description of the descriptor
    description: str = None
    # Tool name (seq_composition, esm_1v,...)
    tool: str = None
    # Short machine-readable column name for the descriptor (sequence_composition|length, esm1v|native_seq_avg_softmax, ...)
    key: str = None

    def serialize(self, value):
        """Serialize a value into a number or string so that it can be stored in the DB"""
        return value

    def deserialize(self, value):
        """De-serialize a value stored in the DB into a meaningful object in python"""
        return value


@dataclass
class NumericDescriptor(Descriptor, ABC):
    # Comparison type (higher_is_better, lower_is_better, does_not_apply)
    comparison: str = None
    # Minimum value for the descriptor
    min_value: float = None
    # Maximum value for the descriptor
    max_value: float = None
    # Value above/below which the descriptor is considered a warning
    warning_value: float = None
    # Value above/below which the descriptor is considered an error
    error_value: float = None
    # Unit, e.g. "Å", "Å²", "kcal/mol"
    unit: str = None
    # Predefined color scale - see get_descriptor_cmap() function
    color_scale: str = None

    def get_plot_range(self, values: pd.Series, padding=0.05) -> tuple[float, float] | None:
        """Return range for the plot based on min_value, max_value with additional padding"""
        min_value = self.min_value if self.min_value is not None else values.min()
        if not pd.isna(values.min()) and values.min() < min_value:
            min_value = values.min()
        max_value = self.max_value if self.max_value is not None else values.max()
        if not pd.isna(values.max()) and values.max() > max_value:
            max_value = values.max()
        padding_value = (max_value - min_value) * padding
        return min_value - padding_value, max_value + padding_value

    def format(self, value):
        if pd.isna(value):
            return None
        unit_suffix = f" {self.unit}" if self.unit else ""
        try:
            if int(value) == value:
                return str(int(value)) + unit_suffix
        except:
            pass
        if isinstance(value, str):
            return value
        return f"{value:.2f}" + unit_suffix


@dataclass
class NumericGlobalDescriptor(NumericDescriptor):
    """Descriptor storing a number for the whole molecule"""

    pass


@dataclass
class NumericResidueDescriptor(NumericDescriptor):
    """Descriptor storing a number for each residue in a protein chain"""

    pass


@dataclass
class StringGlobalDescriptor(Descriptor):
    """Descriptor storing a string label for the whole molecule"""

    pass


@dataclass
class StringResidueDescriptor(Descriptor):
    """Descriptor storing a string for multiple residues, as a {resid -> string} dictionary,
    stored in the DB as a JSON-encoded string."""

    def serialize(self, value):
        """Serialize a value into a number or string so that it can be stored in the DB"""
        assert isinstance(value, dict), (
            f"Expected dict when serializing {self.name}, got value {value} ({type(value).__name__})"
        )
        return json.dumps(value)

    def deserialize(self, value):
        """De-serialize a value stored in the DB into a meaningful object in python"""
        return json.loads(value)


@dataclass
class CategoricalResidueDescriptor(Descriptor):
    """Descriptor storing a category label for each residue in a protein chain,
    each category represented by a letter.

    Annotation for the whole chain is saved as a single string,
    each category represented by a letter (key in category_labels),
    for example "EEEHHH---HHH" for DSSP secondary structure annotation.
    """

    # map from letter to category label (H -> Helix)
    category_labels: dict[str] = field(default_factory=dict)


@dataclass
class ResidueNumberDescriptor(Descriptor):
    """Descriptor storing list of residue numbers as a value, for example A123,A124,A202"""

    pass


@dataclass
class FileDescriptor(Descriptor):
    """Descriptor storing a Storage file path as a value"""

    pass


@dataclass
class StructureFileDescriptor(FileDescriptor):
    """Descriptor storing a structure file path as a value (PDB, mmCIF)"""

    structure_type: Literal["backbone_design", "sequence_design", "prediction", "experimentally_resolved"] = None
    b_factor_value: Literal["plddt", "fractional_plddt"] = None


# include all models
__all__ = [
    "Base",
    "JobMixin",
    "MetadataMixin",
    "UserSettings",
    "Project",
    "Round",
    "WorkflowParams",
    "Threshold",
    "WorkflowTypes",
    "Workflow",
    "DescriptorWorkflow",
    "DesignDescriptorWorkflow",
    "DesignWorkflow",
    "UnknownWorkflow",
    "DesignJob",
    "Pool",
    "DesignChainType",
    "DesignChain",
    "DesignSpec",
    "Design",
    "DescriptorJob",
    "DescriptorValue",
    "Descriptor",
    "NumericDescriptor",
    "NumericGlobalDescriptor",
    "NumericResidueDescriptor",
    "StringGlobalDescriptor",
    "StringResidueDescriptor",
    "CategoricalResidueDescriptor",
    "ResidueNumberDescriptor",
    "FileDescriptor",
    "StructureFileDescriptor",
    "DataclassType",
    "Artifact",
    "UnknownArtifact",
    "ArtifactTypes",
    "ProjectArtifact",
]
