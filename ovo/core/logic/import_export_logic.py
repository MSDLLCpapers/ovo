import os
import shutil
import tempfile
from dataclasses import is_dataclass, fields

from sqlalchemy.orm import make_transient

from ovo import db, storage, config
from ovo.core.configuration import ConfigProps, load_config, save_default_config
from ovo.core.database import SqlDBEngine, DBEngine, DataclassType
from ovo.core.database.descriptors import ALL_DESCRIPTORS_BY_KEY
from ovo.core.database.models import (
    Project,
    Round,
    Pool,
    Design,
    DesignJob,
    DescriptorJob,
    DescriptorValue,
    FileDescriptor,
    ProjectArtifact,
)
from ovo.core.storage import Storage
from ovo.core.utils.formatting import safe_filename

# Configuration for import/export operations (Project handled separately)
IMPORT_EXPORT_CONFIGS = [
    {"model_class": Round, "filter": lambda o: dict(project_id__in=[p.id for p in o["project"]])},
    {"model_class": Pool, "filter": lambda o: dict(round_id__in=[r.id for r in o["round"]])},
    {"model_class": Design, "filter": lambda o: dict(pool_id__in=[p.id for p in o["pool"]])},
    {
        "model_class": DesignJob,
        "filter": lambda o: dict(id__in=[p.design_job_id for p in o["pool"] if p.design_job_id is not None]),
    },
    {"model_class": DescriptorJob, "filter": lambda o: dict(project_id__in=[p.id for p in o["project"]])},
    {
        "model_class": DescriptorValue,
        "filter": lambda o: dict(descriptor_job_id__in=[j.id for j in o["descriptor_job"]]),
    },
    {"model_class": ProjectArtifact, "filter": lambda o: dict(project_id__in=[p.id for p in o["project"]])},
]


def find_storage_path_fields(cls, prefix: str = "") -> list[str]:
    result = []
    if not is_dataclass(cls):
        return result

    for f in fields(cls):
        field_name = f.name
        path = f"{prefix}.{field_name}" if prefix else field_name
        metadata = f.metadata or {}

        # Check if it's a nested dataclass
        if is_dataclass(f.default) or (callable(f.default_factory) and is_dataclass(f.default_factory())):
            sub_cls = f.default if is_dataclass(f.default) else f.default_factory()
            result.extend(find_storage_path_fields(type(sub_cls), prefix=path))

        # Add to result only if metadata has storage_path=True
        elif metadata.get("storage_path") is True:
            result.append(path)

    return result


def export_import_project(
    source_db: DBEngine,
    source_storage: Storage,
    dest_db: DBEngine,
    dest_dir: str,
    project_id: str = None,
    check_conflicts=True,
    count_only=False,
    accepted_only=False,
) -> dict:
    """
    Unified function to copy a project from source database/storage to destination database/storage.

    Args:
        source_db: Database engine to read from
        dest_db: Database engine to write to
        project_id: ID of the project to copy (if None, copy all projects)
        source_storage: Storage instance to read files from
        dest_dir: Destination storage directory
        check_conflicts: Whether to check for ID conflicts in destination database
        count_only: If True, only count entities without copying them
        accepted_only: Only include accepted Designs

    Returns:
        dict: Summary with counts of copied entities
    """

    # Get the project from source database
    projects = source_db.select(Project, **(dict(id=project_id) if project_id else dict()))

    # Check for Project ID conflicts if requested (but not when only counting)
    if check_conflicts and not count_only and dest_db.count(Project, id__in=[p.id for p in projects]):
        existing_projects = dest_db.select(Project, id__in=[p.id for p in projects])
        names = ", ".join(f"{project.name} ({project.id})" for project in existing_projects)
        raise ValueError(f"Project already exists in the database: {names}")

    # Collect all storage file paths
    storage_paths = []
    all_objects = {"project": projects}
    counts = {
        "project": len(all_objects["project"]),
    }

    # Build all_objects using the configuration-driven approach
    for entity_config in IMPORT_EXPORT_CONFIGS:
        model_class = entity_config["model_class"]
        table_name = model_class.__tablename__

        filter_dict = entity_config["filter"](all_objects)

        if accepted_only:
            # Filter for accepted designs and their descriptors
            if model_class is Design:
                filter_dict["accepted"] = True
            if model_class is DescriptorValue:
                filter_dict["design_id__in"] = [d.id for d in all_objects["design"]]

        # Use the filter function to get filter dict and fetch objects
        print(f"Fetching {model_class.__name__} from DB for export")
        all_objects[table_name] = source_db.select(model_class, **filter_dict)
        print(f" Fetched {len(all_objects[table_name]):,} {model_class.__name__} objects")

        # Update counts
        counts[table_name] = len(all_objects[table_name])

        # Check for conflicts if requested and model has an id field and we have objects (but not when only counting)
        if check_conflicts and not count_only and hasattr(model_class, "id") and all_objects[table_name]:
            print("- Checking for conflicts...")
            obj_ids = [obj.id for obj in all_objects[table_name]]
            if dest_db.count(model_class, id__in=obj_ids):
                existing_ids = [obj.id for obj in dest_db.select(model_class, id__in=obj_ids)]
                raise ValueError(
                    f"{len(existing_ids):,} {model_class.__name__} objects already exist in the database: {existing_ids}"
                )

        # Collect storage files from objects
        for column in model_class.__table__.columns:
            # Inspect all columns marked with storage_path=True
            if column.info.get("storage_path"):
                for obj in all_objects[table_name]:
                    if file_path := getattr(obj, column.name, None):
                        storage_paths.append(file_path)
            # Inspect all fields marked with storage_path=True inside nested dataclass columns
            if isinstance(column.type, DataclassType):
                subclasses = set(
                    type(getattr(obj, column.name, None))
                    for obj in all_objects[table_name]
                    if getattr(obj, column.name, None)
                )
                for path_field in sorted(set(field for cls in subclasses for field in find_storage_path_fields(cls))):
                    for obj in all_objects[table_name]:
                        v = getattr(obj, column.name, None)
                        for field_name in path_field.split("."):
                            v = getattr(v, field_name, None)
                        if v is not None:
                            if isinstance(v, str):
                                storage_paths.append(v)
                            elif isinstance(v, list):
                                storage_paths.extend(v)
                            else:
                                raise ValueError(
                                    f"Unsupported storage path field type {type(v)} in {model_class.__name__}.{column.name}.{path_field}"
                                )

        if table_name == DescriptorValue.__tablename__:
            for obj in all_objects[table_name]:
                if ALL_DESCRIPTORS_BY_KEY.get(obj.descriptor_key) and isinstance(
                    ALL_DESCRIPTORS_BY_KEY[obj.descriptor_key], FileDescriptor
                ):
                    storage_paths.append(obj.value)

        if table_name == ProjectArtifact.__tablename__:
            for obj in all_objects[table_name]:
                if obj.artifact:
                    artifact_paths = obj.artifact.get_storage_paths()
                    storage_paths.extend([p for p in artifact_paths if p])

    print("All entities fetched from DB!")
    counts["storage_file"] = len(storage_paths)

    # If only counting, return counts
    if count_only:
        return counts

    # Copy storage files
    print(f"Copying {len(storage_paths):,} storage files...")
    source_storage.sync_files(storage_paths=storage_paths, local_destination_dir=dest_dir, preserve_subdirs=True)
    print("Storage copied successfully!")

    # Copy all objects to destination database
    print("Inserting entities to DB...")
    for project in projects:
        # handle project name conflicts
        while dest_db.count(Project, name=project.name, author=project.author):
            project.name = f"{project.name} (Copy)"

    for table_name, objects in all_objects.items():
        for obj in objects:
            make_transient(obj)
        dest_db.save_all(objects)
    print("Entities inserted successfully!")

    return counts


def export_project(project_id: str, output_zip_path: str = None, accepted_only: bool = False) -> str:
    """
    Export a single project and all associated data to a ZIP file containing
    ovo.db (SQLite database), storage subdirectory with all files, and config.yml.

    Args:
        project_id: ID of the project to export
        output_zip_path: Optional output zip path. Temporary file path will be used if not provided.
        accepted_only: Only export Designs that are accepted.

    Returns:
        str: Path to the exported ZIP file
    """

    # Get the project to verify it exists and get its name
    project = db.get(Project, project_id)

    # Create temporary directory for export
    with tempfile.TemporaryDirectory() as temp_root:
        temp_home = os.path.join(temp_root, safe_filename(project.name))
        os.makedirs(temp_home, exist_ok=True)

        # Add minimal config file
        save_default_config(temp_home, config_props=ConfigProps(read_only=True))

        # Create new SQLite database using SqlDBEngine
        export_db_path = os.path.join(temp_home, "ovo.db")
        export_db = SqlDBEngine(db_url=f"sqlite:///{export_db_path}")
        export_db.init()

        # Use unified function to copy project data
        counts = export_import_project(
            source_db=db,
            source_storage=storage,
            dest_db=export_db,
            dest_dir=os.path.join(temp_home, "storage"),
            project_id=project_id,
            accepted_only=accepted_only,
            check_conflicts=False,  # No need to check conflicts when exporting
        )

        if not project.public:
            print("NOTE: Project is private but will be exported as public!")
            export_db.save_value(Project, "public", True, id=project.id)

        # Add a README file
        readme_content = f"""
        OVO Project Export
    
        Project: {project.name}
    
        Contents:
        - ovo.db: SQLite database with all project data
        - storage/: Directory containing all project files with relative paths
        - config.yml: Minimal configuration file template
    
        To import this data:
        1. Use the Import & Export admin page in OVO
        2. Upload this ZIP file
        3. The system will restore the project data and files
        
        To preview this data:
        1. Unpack this ZIP file
        2. set OVO_HOME environment variable to the unpacked directory path
        3. run "ovo app"
    
        Export Summary:
        - Rounds: {counts["round"]}
        - Pools: {counts["pool"]}
        - Designs: {counts["design"]}
        - Storage files: {counts["storage_file"]}
        - Descriptor value: {counts["descriptor_value"]}
        - Project artifacts: {counts["project_artifact"]}
    """.lstrip()

        with open(os.path.join(temp_home, "README.txt"), "wt") as f:
            f.write(readme_content)

        # Create the final ZIP file
        print("Creating ZIP archive...")
        temp_zip_path = temp_root.removesuffix("/") + ".zip"
        shutil.make_archive(
            temp_zip_path.removesuffix(".zip"),  # archive path (without file extension)
            "zip",  # archive format
            temp_root,  # directory to archive
        )

    if output_zip_path:
        shutil.move(temp_zip_path, output_zip_path)
        return output_zip_path

    # Return path to the temporary ZIP file - should be deleted by the caller!
    return temp_zip_path


def import_project(home_dir: str, project_id: str = None, count_only=False) -> dict[str, int]:
    """
    Import project from extracted directory.

    Args:
        home_dir: Path to extracted directory containing ovo.db, storage files and config.yml
        project_id: ID of the project to import (if None, import all projects)

    Returns:
        counts: number of
    """

    # Load config from the extracted directory
    source_config = load_config(home_dir)

    # Use unified function to copy project data (no metadata transform)
    return export_import_project(
        source_db=SqlDBEngine(db_url=source_config.db.url),
        source_storage=Storage(storage_root=source_config.storage.path, aws=None),
        dest_db=db,
        dest_dir=config.storage.path,
        project_id=project_id,
        check_conflicts=True,
        count_only=count_only,
    )
