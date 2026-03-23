import enum
import json
from dataclasses import is_dataclass, asdict
from pathlib import Path

from sqlalchemy import TypeDecorator, String


class DataclassEncoder(json.JSONEncoder):
    """Simple JSON encoder that encodes dataclasses and enums."""

    def default(self, o):
        if hasattr(o, "__do_not_serialize__") and o.__do_not_serialize__:
            raise ValueError(f"Objects of type {type(o).__name__} cannot be updated in the database.")
        if is_dataclass(o):
            return asdict(o)
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
