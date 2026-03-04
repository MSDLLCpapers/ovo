import os
from typing import Type, Sequence, Any
import pandas as pd

from sqlalchemy import create_engine, or_, func, case, text, distinct, inspect
from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy.orm.attributes import flag_modified

from ovo.core.database.base_db import T
from ovo.core.database.cache_clearing import CacheClearingEngine
from ovo.core.database.models import Base, DescriptorValue, Design
import sys


class SqlDBEngine(CacheClearingEngine):
    def __init__(self, db_url: str, verbose: bool = False, read_only: bool = False):
        if verbose:
            print("Connecting to", db_url, file=sys.stderr)
        self._db_url = db_url
        self._engine = create_engine(db_url, echo=verbose)
        self._read_only = read_only
        self._in_clause_items_limit = None
        if self._db_url.startswith("sqlite://"):
            # Sqlite IN clause is limited to 250k items (as of 2025)
            self._in_clause_items_limit = 200000

    def init(self):
        if self._db_url.startswith("sqlite:///"):
            db_path = self._db_url.removeprefix("sqlite:///")
            if not os.path.exists(db_path):
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Create the table(s)
        Base.metadata.create_all(self._engine)
        self.automigrate()

    def automigrate(self):
        with self._create_session() as session:
            inspector = inspect(self._engine)
            descriptor_job_columns = [c["name"] for c in inspector.get_columns("descriptor_job")]
            if "project_id" not in descriptor_job_columns and "round_id" in descriptor_job_columns:
                print("Applying automigration: adding project_id to descriptor_job", file=sys.stderr)
                session.execute(text("ALTER TABLE descriptor_job ADD COLUMN project_id VARCHAR"))
                # create index on project_id
                session.execute(text("CREATE INDEX ix_descriptor_job_project_id ON descriptor_job (project_id)"))
                # fill existing rows with project_id based on descriptor_job.round_id = round.id -> round.project_id
                session.execute(
                    text(
                        "UPDATE descriptor_job SET project_id = "
                        "(SELECT project_id FROM round WHERE round.id = descriptor_job.round_id)"
                    )
                )
                session.commit()
                session.execute(text("DROP INDEX IF EXISTS ix_descriptor_job_round_id"))
                session.execute(text("ALTER TABLE descriptor_job DROP COLUMN round_id"))
                session.commit()

    def _create_session(self) -> Session:
        return Session(bind=self._engine, expire_on_commit=False)

    def _check_updated(self, obj: Base):
        for field, value in obj.__dict__.items():
            if hasattr(value, "is_changed_hash"):
                if value.is_changed_hash():
                    flag_modified(obj, field)

    def check_read_only(self):
        if self._read_only:
            raise RuntimeError("Ovo is running in read-only mode, write operations are not allowed.")

    def save(self, obj: Base):
        self.check_read_only()
        super().save(obj)
        with self._create_session() as session:
            self._check_updated(obj)
            session.add(obj)
            session.commit()

    def save_all(self, objs: Sequence[Base]):
        self.check_read_only()
        super().save_all(objs)
        with self._create_session() as session:
            for obj in objs:
                self._check_updated(obj)
            session.add_all(objs)
            session.commit()

    def remove(self, model: Type[T], *id_args, **kwargs):
        self.check_read_only()
        super().remove(model, *id_args, **kwargs)
        assert id_args or kwargs, "At least one filter must be provided for remove operation"
        with self._create_session() as session:
            self._create_query(session, model=model, id_args=id_args, **kwargs).delete()
            session.commit()

    def save_value(self, model: Type[T], column: str, value, **kwargs):
        self.check_read_only()
        super().save_value(model, column, value, **kwargs)
        assert kwargs, "At least one filter must be provided for save_value operation"
        with self._create_session() as session:
            session.query(model).filter(*self._create_filters(model, kwargs)).update({column: value})
            session.commit()

    def select(self, model: Type[T], limit: int = None, order_by=None, **kwargs) -> Sequence[T]:
        with self._create_session() as session:
            return self._create_query(session, model=model, order_by=order_by, limit=limit, **kwargs).all()

    def count(self, model: Type[T], **kwargs) -> int:
        with self._create_session() as session:
            return self._create_query(session, model=model, **kwargs).count()

    def count_distinct(self, model: Type[T], field="id", group_by=None, **kwargs) -> int | dict[Any, int]:
        with self._create_session() as session:
            if group_by:
                if isinstance(group_by, str):
                    group_by = [group_by]
                group_by_fields = [getattr(model, column) for column in group_by]
                query = (
                    session.query(*(group_by_fields + [func.count(distinct(getattr(model, field)))]))
                    .filter(*self._create_filters(model, kwargs))
                    .group_by(*group_by_fields)
                )
                return {(row[0] if len(row) == 2 else tuple(row[:-1])): row[-1] for row in query.all()}
            else:
                return self._create_query(session, model=model, columns=[field], **kwargs).distinct().count()

    def _create_query(self, session, model: Type[T], columns=None, order_by=None, limit=None, id_args=None, **kwargs):
        if id_args:
            assert len(id_args) == 1, "Only one positional argument is allowed"
            kwargs["id"] = id_args[0]
        if columns:
            query = session.query(*[getattr(model, column) for column in columns])
        elif hasattr(model, "__mapper__") and model.__mapper__.polymorphic_on is not None:
            query = session.query(with_polymorphic(model, "*"))
        else:
            query = session.query(model)
        return (
            query.filter(*self._create_filters(model, kwargs))
            .order_by(*self._create_order_by(model, order_by))
            .limit(limit)
        )

    def _create_order_by(self, model: Type[T], order_by):
        if order_by is None:
            return []
        if isinstance(order_by, str):
            return [self._create_order_by_single(model, order_by)]
        return [self._create_order_by_single(model, k) for k in order_by]

    def _create_order_by_single(self, model: Type[T], order_by):
        return getattr(model, order_by) if not order_by.startswith("-") else getattr(model, order_by[1:]).desc()

    def _create_filters(self, model: Type[T], kwargs):
        filters = []
        for k, v in kwargs.items():
            # Handle or conditions
            if k == "_or":
                or_conditions = []
                for condition in v:
                    for or_k, or_v in condition.items():
                        or_conditions.append(getattr(model, or_k) == or_v)
                filters.append(or_(*or_conditions))
            # Handle in conditions
            elif k.endswith("__in"):
                descriptor_key = k[:-4]  # Remove the '__in' suffix
                filters.append(getattr(model, descriptor_key).in_(v))
            elif k.endswith("__ne"):
                descriptor_key = k[:-4]
                filters.append(getattr(model, descriptor_key) != v)
            else:
                filters.append(getattr(model, k) == v)
        return filters

    def get(self, model: Type[T], *id_args, **kwargs) -> T:
        with self._create_session() as session:
            return self._create_query(session, model=model, id_args=id_args, **kwargs).one()

    def get_value(self, model: Type[T], column: str, *id_args, raw=False, **kwargs):
        with self._create_session() as session:
            query = self._create_query(session, model=model, columns=[column], id_args=id_args, **kwargs)
            if raw:
                # Fetch raw DB column value, useful for fetching values that are now incompatible due to changes in models
                query = query.with_entities(text(column))
            return query.one()[0]

    def select_values(self, model: Type[T], column: str, order_by=None, **kwargs) -> list:
        with self._create_session() as session:
            return [
                row[0]
                for row in self._create_query(session, model=model, columns=[column], order_by=order_by, **kwargs).all()
            ]

    def select_dict(self, model: Type[T], key_column: str, value_column: str, order_by=None, **kwargs) -> dict:
        with self._create_session() as session:
            return {
                row[0]: row[1]
                for row in self._create_query(
                    session, model=model, columns=[key_column, value_column], order_by=order_by, **kwargs
                )
            }

    def select_unique_values(self, model: Type[T], column: str, **kwargs) -> set:
        with self._create_session() as session:
            return set(
                row[0]
                for row in self._create_query(
                    session,
                    model=model,
                    columns=[column],
                    **kwargs,
                ).all()
            )

    def select_dataframe(
        self, model: Type[T], index_col: str = "id", order_by=None, limit="unset", **kwargs
    ) -> pd.DataFrame:
        if limit == "unset":
            if not kwargs:
                raise ValueError(
                    "select_dataframe requires passing a filter, a limit, or explicit unlimited query limit=None to avoid fetching too many rows"
                )
            limit = None
        with self._create_session() as session:
            query = self._create_query(session, model=model, limit=limit, order_by=order_by, **kwargs)
            return pd.read_sql_query(query.statement, query.session.bind, index_col=index_col)

    def select_descriptor_values(
        self, descriptor_key: str, design_ids: list[str], descriptor_job_id: str | None = None
    ) -> pd.Series:
        """Select values of a single descriptor for multiple designs."""
        # TODO this does not handle the case when a descriptor was computed multiple times for the same design and descriptor_job_id is not provided
        #  same as in select_wide_descriptor_table below
        with self._create_session() as session:
            assert isinstance(descriptor_key, str), (
                f"Expected descriptor_key to be string, got {type(descriptor_key).__name__}"
            )
            values = {}
            design_ids = list(design_ids)
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )
            for batch in batches:
                query = (
                    session.query(DescriptorValue.design_id, DescriptorValue.value)
                    .filter(DescriptorValue.descriptor_key == descriptor_key)
                    .filter(*self._create_filters(DescriptorValue, dict(design_id__in=batch)))
                )
                if descriptor_job_id is not None:
                    query = query.filter(DescriptorValue.descriptor_job_id == descriptor_job_id)
                values.update({design_id: value for design_id, value in query})
            series = pd.Series(values)
            try:
                # Try converting whole array to numbers.
                # If any value is not a number, keep it as array of strings.
                # This mimics original behavior of to_numeric(errors="ignore").
                series = pd.to_numeric(series)
            except ValueError:
                pass
            # Reindex to keep the original order, adding NaN for missing designs
            return series.reindex(design_ids)

    def select_design_descriptors(
        self, design_id: str, descriptor_keys: list[str], descriptor_job_id: str | None = None
    ) -> pd.Series:
        """Select values of multiple descriptors for a single design."""
        # TODO this does not handle the case when a descriptor was computed multiple times for the same design and descriptor_job_id is not provided
        #  same as in select_wide_descriptor_table below
        with self._create_session() as session:
            for key in descriptor_keys:
                assert isinstance(key, str), f"Expected collection of descriptor key strings, got {type(key).__name__}"
            query = (
                session.query(DescriptorValue.descriptor_key, DescriptorValue.value)
                .filter(DescriptorValue.design_id == design_id)
                .filter(*self._create_filters(DescriptorValue, {"descriptor_key__in": descriptor_keys}))
            )
            if descriptor_job_id is not None:
                query = query.filter(DescriptorValue.descriptor_job_id == descriptor_job_id)
            result = query.all()
            series = pd.Series({descriptor_key: value for descriptor_key, value in result})
            try:
                # Try converting whole array to numbers.
                # If any value is not a number, keep it as array of strings.
                # This mimics original behavior of to_numeric(errors="ignore").
                series = pd.to_numeric(series)
            except ValueError:
                pass
            return series.reindex(descriptor_keys)

    def select_wide_descriptor_table(
        self, design_ids: list[str], descriptor_keys: list[str], descriptor_job_id: str | None = None, **kwargs
    ) -> pd.DataFrame:
        # TODO this does not handle the case when a descriptor was computed multiple times for the same design and descriptor_job_id is not provided
        #  this can happen when we implement multiple descriptor jobs with different settings.
        #  To solve this, some descriptor job key could be incorporated in the column name or used as a filter.
        with self._create_session() as session:
            for key in descriptor_keys:
                assert isinstance(key, str), f"Expected collection of descriptor keys strings, got {type(key).__name__}"
            design_ids = list(design_ids)
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )
            results = []
            for batch in batches:
                cases = [
                    func.max(case((DescriptorValue.descriptor_key == key, DescriptorValue.value), else_=None)).label(
                        key
                    )
                    for key in descriptor_keys
                ]

                query = (
                    session.query(DescriptorValue.design_id, *cases)
                    .filter(*self._create_filters(DescriptorValue, dict(design_id__in=batch)))
                    .filter(*self._create_filters(DescriptorValue, kwargs))
                    .group_by(DescriptorValue.design_id)
                )
                if descriptor_job_id is not None:
                    query = query.filter(DescriptorValue.descriptor_job_id == descriptor_job_id)
                results += query.all()
            session.close()
            df = pd.DataFrame(results)
            if not df.empty:
                df = df.set_index("design_id")
            # remove columns with no values
            df = df.dropna(axis=1, how="all")
            for col in df.columns:
                try:
                    # Try converting whole array to numbers.
                    # If any value is not a number, keep it as array of strings.
                    # This mimics original behavior of to_numeric(errors="ignore").
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass
            return df.reindex(design_ids)

    def get_design_accepted_values(self, design_ids: list[str]):
        with self._create_session() as session:
            query = self._create_query(session, model=Design, columns=["id", "accepted"], id__in=design_ids)
            result = query.all()  # Returns list of tuples (id, accepted)

        series = pd.Series({design_id: value for design_id, value in result})
        return series.reindex(design_ids)
