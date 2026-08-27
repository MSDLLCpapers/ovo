import os
from typing import Type, Sequence, Any
import pandas as pd

from sqlalchemy import create_engine, or_, func, case, text, distinct, inspect
from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy.orm.attributes import flag_modified

from ovo.core.database.base_db import T
from ovo.core.database.cache_clearing import CacheClearingEngine
from ovo.core.database.models import Base, DescriptorValue, Design, Labeling, DesignLabeling
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
            project_columns = [c["name"] for c in inspector.get_columns("project")]
            if "description" not in project_columns:
                print("Applying automigration: adding description to project", file=sys.stderr)
                session.execute(text("ALTER TABLE project ADD COLUMN description TEXT"))
                session.commit()
            user_setting_columns = [c["name"] for c in inspector.get_columns("user_setting")]
            if "last_project_id" in user_setting_columns and "props" not in user_setting_columns:
                print("Applying automigration: migrating last_project_id to props in user_setting", file=sys.stderr)
                # Add props column
                if self._db_url.startswith("postgresql://"):
                    session.execute(text("ALTER TABLE user_setting ADD COLUMN props JSONB NOT NULL DEFAULT '{}'"))
                    session.execute(
                        text(
                            "UPDATE user_setting SET props = "
                            "jsonb_build_object('ovo.last_project_id', last_project_id) "
                            "WHERE last_project_id IS NOT NULL"
                        )
                    )
                else:
                    session.execute(text("ALTER TABLE user_setting ADD COLUMN props TEXT NOT NULL DEFAULT '{}'"))
                    session.execute(
                        text(
                            "UPDATE user_setting SET props = "
                            "'{\"ovo.last_project_id\": \"' || last_project_id || '\"}' "
                            "WHERE last_project_id IS NOT NULL"
                        )
                    )
                session.commit()
            # Add index on descriptor_key if it doesn't exist
            descriptor_value_indexes = inspector.get_indexes("descriptor_value")
            has_descriptor_key_index = any(
                "descriptor_key" in idx.get("column_names", []) and len(idx.get("column_names", [])) == 1
                for idx in descriptor_value_indexes
            )
            if not has_descriptor_key_index:
                print(
                    f"Applying automigration: adding index on descriptor_key in descriptor_value",
                    file=sys.stderr,
                )
                row_count = session.execute(text("SELECT COUNT(*) FROM descriptor_value")).scalar()
                print(
                    f"Creating descriptor_key index on {row_count:,} rows...",
                    file=sys.stderr,
                )
                session.execute(
                    text("CREATE INDEX ix_descriptor_value_descriptor_key ON descriptor_value (descriptor_key)")
                )
                session.commit()
            # Add missing MetadataMixin columns to project artifact
            project_artifact_columns = [c["name"] for c in inspector.get_columns("project_artifact")]
            if "author" not in project_artifact_columns:
                row_count = session.execute(text("SELECT COUNT(*) FROM project_artifact")).scalar()
                if row_count == 0:
                    print("Applying automigration: adding metadata columns to project_artifact", file=sys.stderr)
                    session.execute(text("DROP TABLE project_artifact"))
                    session.commit()
                    Base.metadata.create_all(self._engine)
                else:
                    raise NotImplementedError(
                        "Automigration to add metadata columns to project_artifact "
                        "is not implemented for non-empty tables, manual migration is required. "
                        "\n"
                        "\nPlease consider renaming the existing project_artifact table, "
                        "restarting OVO to create a new one with the correct schema, and then migrating the data from the old table to the new one:"
                        "\n"
                        "\nALTER TABLE project_artifact RENAME TO project_artifact_old;"
                        "\nDROP INDEX IF EXISTS ix_project_artifact_project_id;"
                        "\nDROP INDEX IF EXISTS ix_project_artifact_artifact_type;"
                        "\nDROP INDEX IF EXISTS ix_project_artifact_descriptor_job_id;"
                        "\nDROP INDEX IF EXISTS ix_project_artifact_design_job_id;"
                        "\n"
                        "\nRestart OVO to create new project_artifact table with metadata columns."
                        "\nThen migrate data:"
                        "\n"
                        "\nINSERT INTO"
                        "\nproject_artifact("
                        "\n    id, project_id, artifact_type, descriptor_job_id,"
                        "\n    design_job_id, artifact, author, created_date_utc"
                        "\n)"
                        "\nSELECT"
                        "\nid, project_id, artifact_type, descriptor_job_id,"
                        "\ndesign_job_id, artifact, 'unknown', CURRENT_TIMESTAMP"
                        "\nFROM project_artifact_old;"
                    )

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
            order_by = [order_by]
        else:
            try:
                order_by = list(order_by)
            except:
                order_by = [order_by]
        # process an iterable of column names
        return [self._create_order_by_single(model, k) for k in order_by]

    def _create_order_by_single(self, model: Type[T], order_by):
        if isinstance(order_by, str):
            return getattr(model, order_by) if not order_by.startswith("-") else getattr(model, order_by[1:]).desc()
        else:
            # Assume that the caller passed an already constructed order_by expression, e.g. model.column.desc()
            return order_by

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
        self,
        design_ids: list[str],
        descriptor_keys: list[str],
        descriptor_job_id: str | dict[str, list[str]] | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Select values of multiple descriptors for multiple designs, returning a wide table with design_id as index and descriptor_keys as columns.

        :param design_ids: List of design IDs to select descriptors for
        :param descriptor_keys: List of descriptor keys to select
        :param descriptor_job_id: Optional descriptor job ID to filter by, or a dict mapping job ID to list of its descriptor keys that should be filtered by that job (if present in descriptor_keys).

        :return: A pandas DataFrame with design_id as index and descriptor_keys as columns, containing the descriptor values.
        """
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
                if isinstance(descriptor_job_id, dict):
                    # Different descriptor keys are filtered by different descriptor_job_ids
                    # create mapping: descriptor key -> job id
                    job_id_by_descriptor_key = {}
                    for job_id, keys in descriptor_job_id.items():
                        if isinstance(keys, str):
                            keys = [keys]
                        for key in keys:
                            assert isinstance(key, str), (
                                f"Expected descriptor key string, got {type(key).__name__}: {key}"
                            )
                            job_id_by_descriptor_key[key] = job_id
                    # create mapping: job id (or None) -> list of descriptor keys
                    descriptor_keys_by_job_id = {}
                    for descriptor_key in descriptor_keys:
                        job_id = job_id_by_descriptor_key.get(descriptor_key)
                        if job_id not in descriptor_keys_by_job_id:
                            descriptor_keys_by_job_id[job_id] = []
                        descriptor_keys_by_job_id[job_id].append(descriptor_key)

                    merged_result = None
                    for job_id, keys in descriptor_keys_by_job_id.items():
                        query = self._create_descriptor_query(session, batch, keys, job_id, **kwargs)
                        result = pd.DataFrame(query.all())
                        if merged_result is None:
                            merged_result = result
                        else:
                            merged_result = pd.merge(merged_result, result, on="design_id", how="outer")
                    merged_result = merged_result[["design_id"] + descriptor_keys]
                    results.append(merged_result)
                else:
                    query = self._create_descriptor_query(session, batch, descriptor_keys, descriptor_job_id, **kwargs)
                    results.append(pd.DataFrame(query.all()))
            session.close()
            df = pd.concat(results) if results else pd.DataFrame([])
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

    def _create_descriptor_query(
        self, session, design_ids: list[str], descriptor_keys: list[str], descriptor_job_id: str = None, **kwargs
    ):
        cases = [
            func.max(case((DescriptorValue.descriptor_key == key, DescriptorValue.value), else_=None)).label(key)
            for key in descriptor_keys
        ]
        query = (
            session.query(DescriptorValue.design_id, *cases)
            .filter(*self._create_filters(DescriptorValue, dict(design_id__in=design_ids)))
            .filter(*self._create_filters(DescriptorValue, kwargs))
            .group_by(DescriptorValue.design_id)
        )
        if descriptor_job_id is not None:
            # All descriptors are filtered by the same descriptor_job_id
            query = query.filter(DescriptorValue.descriptor_job_id == descriptor_job_id)
        return query

    def get_design_accepted_values(self, design_ids: list[str]):
        with self._create_session() as session:
            query = self._create_query(session, model=Design, columns=["id", "accepted"], id__in=design_ids)
            result = query.all()  # Returns list of tuples (id, accepted)

        series = pd.Series({design_id: value for design_id, value in result})
        return series.reindex(design_ids)

    def create_labeling(self, label: str, username: str, explanation: str | None = None) -> Labeling:
        """Create a new labeling."""
        self.check_read_only()

        labeling = Labeling(id=Labeling.generate_id(), label=label.strip(), author=username, explanation=explanation)
        self.save(labeling)
        return labeling

    def add_label(self, label: str, design_ids: list[str], username: str, explanation: str | None = None):
        """Add a label to multiple designs.

        Args:
            label: The label to add
            design_ids: List of design IDs to add the label to
            username: The username of the person adding the label
            explanation: Optional explanation for adding the label (for audit/logging purposes)
        """
        self.check_read_only()

        # Create Labeling
        labeling = self.create_labeling(label, username, explanation)

        # Add the labeling to the designs
        design_labelings = []
        for design_id in design_ids:
            design_labelings.append(DesignLabeling(design_id=design_id, labeling_id=labeling.id))

        self.save_all(design_labelings)
        return labeling

    def remove_label(self, label: str, design_ids: list[str], **kwargs):
        """Remove a label from multiple designs.

        Args:
            label: The label to remove
            design_ids: List of design IDs to remove the label from
        """
        self.check_read_only()

        # Get the labeling record(s) for the specified label and author
        # This assumes that the same label can be added multiple times by the same user with different explanations, and we want to remove all of them when removing a label.
        labelings = self.select(Labeling, label=label, **kwargs)

        if not labelings:
            return

        # Bulk delete associations
        labeling_ids = [labeling.id for labeling in labelings]
        with self._create_session() as session:
            session.query(DesignLabeling).filter(
                DesignLabeling.design_id.in_(design_ids), DesignLabeling.labeling_id.in_(labeling_ids)
            ).delete()
            session.commit()

        # If there are no more design_labeling associations for this labeling, we can remove the labeling record itself
        for labeling in labelings:
            remaining_associations = self.count(DesignLabeling, labeling_id=labeling.id)
            if remaining_associations == 0:
                self.remove(Labeling, id=labeling.id)

    def remove_designs_labeling(self, labeling_id: str, design_ids: list[str]):
        """Remove a specific design labeling by its ID.

        Args:
            labeling_id: The ID of the design labeling to remove
            design_ids: List of design IDs to remove the labeling from
        """
        self.check_read_only()

        with self._create_session() as session:
            session.query(DesignLabeling).filter(
                DesignLabeling.design_id.in_(design_ids), DesignLabeling.labeling_id == labeling_id
            ).delete(synchronize_session=False)
            session.commit()

        # Manually trigger cache clearing for DesignLabeling model
        self._clear_all_cache(DesignLabeling)

        remaining_associations = self.count(DesignLabeling, labeling_id=labeling_id)
        if remaining_associations == 0:
            self.remove(Labeling, id=labeling_id)

    def get_designs_with_all_labels(self, label_names: list[str], design_ids: list[str] = None) -> list[str]:
        """Get design IDs that have ALL of the specified labels using a single optimized query."""
        if not label_names:
            return design_ids or []

        with self._create_session() as session:
            # If no design_ids filter, run a single query
            if not design_ids:
                query = (
                    session.query(DesignLabeling.design_id)
                    .join(Labeling, DesignLabeling.labeling_id == Labeling.id)
                    .filter(Labeling.label.in_(label_names))
                    .group_by(DesignLabeling.design_id)
                    .having(func.count(func.distinct(Labeling.label)) == len(set(label_names)))
                )
                return [row[0] for row in query.all()]

            # Batch design_ids to avoid SQLite parameter limit
            design_ids = list(design_ids)
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )

            all_results = []
            for batch in batches:
                query = (
                    session.query(DesignLabeling.design_id)
                    .join(Labeling, DesignLabeling.labeling_id == Labeling.id)
                    .filter(Labeling.label.in_(label_names))
                    .filter(DesignLabeling.design_id.in_(batch))
                    .group_by(DesignLabeling.design_id)
                    .having(func.count(func.distinct(Labeling.label)) == len(set(label_names)))
                )
                all_results.extend([row[0] for row in query.all()])

            return all_results

    def get_designs_with_any_labels(
        self, label_names: list[str], design_ids: list[str] = None, author: str = None
    ) -> list[str]:
        """Get design IDs that have ANY of the specified labels using a single optimized query.

        Args:
            label_names: List of label names that designs can have (ANY of them)
            design_ids: Optional list of design_ids to filter within (if None, searches all designs)
            author: Optional author filter - only consider labels from this author
        """
        if not label_names:
            return design_ids or []

        with self._create_session() as session:
            # If no design_ids filter, run a single query
            if not design_ids:
                query = (
                    session.query(DesignLabeling.design_id)
                    .join(Labeling, DesignLabeling.labeling_id == Labeling.id)
                    .filter(Labeling.label.in_(label_names))
                )
                if author:
                    query = query.filter(Labeling.author == author)
                query = query.distinct()
                return [row[0] for row in query.all()]

            # Batch design_ids to avoid SQLite parameter limit
            design_ids = list(design_ids)
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )

            all_results = set()
            for batch in batches:
                query = (
                    session.query(DesignLabeling.design_id)
                    .join(Labeling, DesignLabeling.labeling_id == Labeling.id)
                    .filter(Labeling.label.in_(label_names))
                    .filter(DesignLabeling.design_id.in_(batch))
                )
                if author:
                    query = query.filter(Labeling.author == author)
                query = query.distinct()
                all_results.update([row[0] for row in query.all()])

            return list(all_results)

    def get_labelings_for_design(self, design_id: str) -> list[Labeling]:
        """Get all labelings for a specific design using a single optimized query."""
        if not design_id:
            return []

        with self._create_session() as session:
            query = (
                session.query(Labeling)
                .join(DesignLabeling, Labeling.id == DesignLabeling.labeling_id)
                .filter(DesignLabeling.design_id == design_id)
                .order_by(Labeling.created_date_utc)  # from least recent to most recent
            )
            return query.all()

    def get_labelings_for_design_ids(self, design_ids: list[str]) -> dict[str, list[Labeling]]:
        """Get all labelings of the given designs using a single query per batch of design IDs."""
        design_ids = list(design_ids)
        if not design_ids:
            return {}

        from collections import defaultdict

        with self._create_session() as session:
            # Batch design_ids to avoid SQLite parameter limit
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )

            labelings_by_design_id = defaultdict(list)
            for batch in batches:
                query = (
                    session.query(DesignLabeling.design_id, Labeling)
                    .join(Labeling, Labeling.id == DesignLabeling.labeling_id)
                    .filter(DesignLabeling.design_id.in_(batch))
                    .order_by(Labeling.created_date_utc)  # from least recent to most recent
                )
                for design_id, labeling in query.all():
                    labelings_by_design_id[design_id].append(labeling)

            return dict(labelings_by_design_id)

    def get_available_labels_for_design_ids(self, design_ids: list[str]) -> list[str]:
        """Get unique labels available for the given design IDs (union)."""
        if not design_ids:
            return []

        with self._create_session() as session:
            # Batch design_ids to avoid SQLite parameter limit
            design_ids = list(design_ids)
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )

            all_labels = set()
            for batch in batches:
                query = (
                    session.query(Labeling.label)
                    .join(DesignLabeling, Labeling.id == DesignLabeling.labeling_id)
                    .filter(DesignLabeling.design_id.in_(batch))
                    .distinct()
                )
                all_labels.update([row[0] for row in query.all()])

            return sorted(all_labels)

    def get_available_shared_labels_for_design_ids(self, design_ids: list[str], author: str = None) -> list[str]:
        """Get labels that are present on ALL of the given design IDs (intersection).

        Args:
            design_ids: List of design IDs
            author: Optional author filter - only return labels from this author
        """
        if not design_ids:
            return []

        design_ids = list(set(design_ids))

        with self._create_session() as session:
            # Batch design_ids to avoid SQLite parameter limit
            batches = (
                [design_ids]
                if not self._in_clause_items_limit
                else [
                    design_ids[i : i + self._in_clause_items_limit]
                    for i in range(0, len(design_ids), self._in_clause_items_limit)
                ]
            )

            # Collect label -> set of design_ids mappings across all batches
            from collections import defaultdict

            label_to_design_ids = defaultdict(set)

            for batch in batches:
                query = (
                    session.query(Labeling.label, DesignLabeling.design_id)
                    .join(DesignLabeling, Labeling.id == DesignLabeling.labeling_id)
                    .filter(DesignLabeling.design_id.in_(batch))
                )
                if author:
                    query = query.filter(Labeling.author == author)

                for label, design_id in query.all():
                    label_to_design_ids[label].add(design_id)

            # Filter to labels that appear on ALL design_ids
            shared_labels = [label for label, ids in label_to_design_ids.items() if len(ids) == len(design_ids)]

            return sorted(shared_labels)

    def get_available_labels_for_pool_ids(self, pool_ids: list[str], **design_filters) -> list[str]:
        """Get unique labels available for designs in the given pool IDs.

        Args:
            pool_ids: List of pool IDs to get labels for
            **design_filters: Additional filters to apply to Design model (e.g., accepted=True)

        Returns:
            Sorted list of unique label strings available for designs in the specified pools
        """
        if not pool_ids:
            return []

        with self._create_session() as session:
            query = (
                session.query(Labeling.label)
                .join(DesignLabeling, Labeling.id == DesignLabeling.labeling_id)
                .join(Design, DesignLabeling.design_id == Design.id)
                .filter(Design.pool_id.in_(pool_ids))
            )

            # Apply additional Design filters if provided
            if design_filters:
                query = query.filter(*self._create_filters(Design, design_filters))

            query = query.distinct()
            return sorted([row[0] for row in query.all()])
