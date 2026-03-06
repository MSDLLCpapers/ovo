from abc import ABC, abstractmethod
from typing import Type, TypeVar, Sequence

import pandas as pd

from ovo.core.database.models import Base
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
