import json

from ovo import *
import sys
from sqlalchemy.orm import Mapped
import typing
import os

# This should be executed with -i flag:
#   python -i scripts/migrate_dataclass.py DB_ENTITY FIELD_STORING_DATACLASS_VALUE
#   python -i scripts/migrate_dataclass.py Run workflow
# Or full command:
#   echo -e "def migrate(data):\n  data.pop('queued')\n\nrun(migrate)" | python -i scripts/migrate_dataclass.py DescriptorJob job_status


os.environ["OVO_STRICT_JSON"] = "1"  # raise exception when parsing fails


def get_all_annotations(cls):
    annotations = {}
    for base in cls.__mro__:  # Traverse the class hierarchy
        annotations.update(getattr(base, "__annotations__", {}))
    return annotations


def get_mapped_type(mapped_type):
    """Extracts the Python type from sqlalchemy Mapped[...]"""
    if typing.get_origin(mapped_type) is Mapped:
        return typing.get_args(mapped_type)[0]
    return mapped_type  # Fallback for non-Mapped types


assert len(sys.argv) == 3, "Usage: python -i scripts/migrate_dataclass.py MODEL_NAME FIELD_NAME"
model_name = sys.argv[1]
field_name = sys.argv[2]
Model = globals()[model_name]
if not hasattr(Model, field_name):
    raise ValueError(f"Model {model_name} has no field {field_name}")
# get from type hint annotation
type_annotations = get_all_annotations(Model)
if field_name not in type_annotations:
    raise ValueError(f"No type declared for field {field_name} in class {model_name}, got: {type_annotations}")
DataclassType = get_mapped_type(type_annotations[field_name])


def print_failed():
    # dict object_id -> update data dict
    object_ids = db.select_unique_values(Model, "id")
    print(f"Checking {len(object_ids)} {Model.__name__}.{field_name} objects...")
    for object_id in object_ids:
        try:
            db.get(Model, object_id)
        except Exception as e:
            print()
            print(f"Parsing error: {e}")
            # failed to parse, migrate the value
            data = json.loads(db.get_value(Model, field_name, id=object_id, raw=True))
            print(data)
            print()


def run(migrate_func=None, dry=False, all=False):
    # dict object_id -> update data dict
    num_updated = 0
    object_ids = db.select_unique_values(Model, "id")
    for object_id in object_ids:
        try:
            db.get(Model, object_id)
            should_migrate = False
        except Exception as e:
            should_migrate = True
            # failed to parse, migrate the value
            print(f"Migrating {model_name} {object_id} with error: {e}")
        if all or should_migrate:
            data_raw = db.get_value(Model, field_name, id=object_id, raw=True)
            if not data_raw:
                continue
            data = json.loads(data_raw)
            migrate_func(data)
            try:
                value = DataclassType.from_dict(data) if hasattr(DataclassType, "from_dict") else DataclassType(**data)
                print(data)
                if not dry:
                    db.save_value(Model, field_name, value, id=object_id)
            except Exception as e:
                print("Skipping failed migration:", e)
                continue
            num_updated += 1

    if not dry:
        print(f"Updated {num_updated} objects")
    else:
        print(f"Would update {num_updated} objects")


print_failed()

print("""

Migrate by defining a function:
def migrate(data):
    data['new_arg'] = data.pop('old_arg')

And calling:
run(migrate)

Or run(migrate, dry=True) to just print the migrated values
""")
