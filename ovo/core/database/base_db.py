from abc import ABC, abstractmethod
from typing import Type, TypeVar, Sequence

import pandas as pd

from ovo.core.database.models import Base, Labeling
from ovo.core.database.db_proxy import DBProxy

T = TypeVar("T", bound=Base)


class DBEngine(ABC):
    def init(self):
        pass

    @abstractmethod
    def save(self, obj: Base):
        raise NotImplementedError()

    @abstractmethod
    def save_all(self, objs: Sequence[Base]):
        raise NotImplementedError()

    @abstractmethod
    def remove(self, model: Type[T], *id_args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def save_value(self, model: Type[T], column: str, value, *id_args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def count(self, model: Type[T], field="id", **kwargs) -> Sequence[T]:
        raise NotImplementedError()

    @abstractmethod
    def count_distinct(self, model: Type[T], field="id", group_by=None, **kwargs) -> int:
        raise NotImplementedError()

    @abstractmethod
    def select(self, model: Type[T], limit: int = None, order_by=None, **kwargs) -> Sequence[T]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, model: Type[T], *id_args, **kwargs) -> T:
        raise NotImplementedError()

    @abstractmethod
    def get_value(self, model: Type[T], column: str, *id_args, raw=False, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def select_values(self, model: Type[T], column: str, order_by=None, **kwargs) -> list:
        raise NotImplementedError()

    @abstractmethod
    def select_dict(self, model: Type[T], key_column: str, value_column: str, order_by=None, **kwargs) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def select_unique_values(self, model: Type[T], column: str, **kwargs) -> set:
        raise NotImplementedError()

    @abstractmethod
    def select_descriptor_values(
        self, descriptor_key: str, design_ids: list[str], descriptor_job_id: str | None = None
    ) -> pd.Series:
        raise NotImplementedError()

    @abstractmethod
    def select_wide_descriptor_table(self, design_ids: list[str], descriptor_keys: list[str], **kwargs) -> pd.DataFrame:
        raise NotImplementedError()

    def __getattr__(self, name: str) -> DBProxy:
        """Enable accessing models as attributes of the DBEngine instance.

        For example instead of db.select(Design) you can do db.Design.select().
        """
        for mapper in Base.registry.mappers:
            cls = mapper.class_
            if cls.__name__ == name:
                return cls
        raise AttributeError(f"DB model or function {name} not available")

    @abstractmethod
    def add_label(self, label: str, design_ids: list[str], username: str, explanation: str | None = None):
        """Add a label to multiple designs.

        Args:
            label: The label to add
            design_ids: List of design IDs to add the label to
            username: The username of the person adding the label
            explanation: Optional explanation for adding the label (for audit/logging purposes)
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_label(self, label: str, design_ids: list[str], **kwargs):
        """Remove a label from multiple designs.

        Args:
            label: The label to remove
            design_ids: List of design IDs to remove the label from
        """
        raise NotImplementedError()

    @abstractmethod
    def remove_designs_labeling(self, labeling_id: int, design_ids: list[str]):
        """Remove a specific design labeling by its ID.

        Args:
            labeling_id: The ID of the design labeling to remove
            design_ids: List of design IDs to remove the labeling from
        """
        raise NotImplementedError()

    @abstractmethod
    def get_designs_with_all_labels(self, label_names: list[str], design_ids: list[str] = None) -> list[str]:
        """Get design IDs that have ALL of the specified labels.

        Args:
            label_names: List of label names that designs must have (ALL of them)
            design_ids: Optional list of design_ids to filter within (if None, searches all designs)

        Returns:
            List of design_ids that have all the specified labels
        """
        raise NotImplementedError()

    @abstractmethod
    def get_designs_with_any_labels(self, label_names: list[str], design_ids: list[str] = None) -> list[str]:
        """Get design IDs that have ANY of the specified labels.

        Args:
            label_names: List of label names that designs can have (ANY of them)
            design_ids: Optional list of design_ids to filter within (if None, searches all designs)

        Returns:
            List of design_ids that have at least one of the specified labels
        """
        raise NotImplementedError()

    @abstractmethod
    def get_labelings_for_design(self, design_id: str) -> list[Labeling]:
        """Get all labelings for a specific design using a single optimized query."""
        raise NotImplementedError()

    @abstractmethod
    def get_available_labels_for_design_ids(self, design_ids: list[str]) -> list[str]:
        """Get unique labels available for the given design IDs."""
        raise NotImplementedError()

    @abstractmethod
    def get_available_labels_for_pool_ids(self, pool_ids: list[str], **design_filters) -> list[str]:
        """Get unique labels available for designs in the given pool IDs.

        Args:
            pool_ids: List of pool IDs to get labels for
            **design_filters: Additional filters to apply to Design model (e.g., accepted=True)

        Returns:
            Sorted list of unique label strings available for designs in the specified pools
        """
        raise NotImplementedError()
