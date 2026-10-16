import enum
import json
from dataclasses import fields, is_dataclass
from pathlib import Path

import pandas as pd
from sqlalchemy import TypeDecorator, String


class DataclassEncoder(json.JSONEncoder):
    """Simple JSON encoder that encodes dataclasses and enums.

    Dataclass fields are serialized in the order the dataclass declares them, except for the names
    a class lists in ``__serialize_last__``, which go last. Declared once on a base class and
    inherited, since a field declared on a base class otherwise comes before every field of its
    subclasses - which puts a long shared field such as ``DesignWorkflow.acceptance_thresholds``
    above the parameters that identify the workflow.
    """

    def default(self, o):
        if hasattr(o, "__serialize_field__") and o.__serialize_field__:
            return getattr(o, o.__serialize_field__)
        if isinstance(o, pd.DataFrame):
            # Use the pandas JSON writer rather than to_dict to ensure JSON serializability -
            # records can contain values that json.dumps cannot handle (pd.Timestamp, pd.NaT,
            # numpy scalars), which fails when saving to the Postgres DB
            return json.loads(o.to_json(orient="records", date_format="iso"))
        if is_dataclass(o):
            # The field values are returned as they are, rather than converted by dataclasses.asdict,
            # so that json recurses back into this method for each nested dataclass and orders its
            # fields the same way
            serialize_last = getattr(o, "__serialize_last__", ())
            ordered = sorted(fields(o), key=lambda f: f.name in serialize_last)
            return {f.name: getattr(o, f.name) for f in ordered}
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, Path):
            return str(o.resolve())
        return super().default(o)


class DataclassType(TypeDecorator):
    """SQLA Type decorator to serialize dataclasses"""

    impl = String
    cache_ok = True

    def __init__(self, base_cls):
        super().__init__()
        self.base_cls = base_cls

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value, cls=DataclassEncoder)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # PostgreSQL JSONB returns dict directly, SQLite returns JSON string
        if isinstance(value, dict):
            result = value  # PostgreSQL case
        else:
            result = json.loads(value)  # SQLite case
        if hasattr(self.base_cls, "from_dict"):
            return self.base_cls.from_dict(result)
        return self.base_cls(**result)
