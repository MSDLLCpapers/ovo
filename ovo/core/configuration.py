import dataclasses
import json
import os
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path

import yaml
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ovo.cli.common import console, OVOCliError, OVONotInitializedError


class BaseConfigModel(BaseSettings):
    model_config = SettingsConfigDict(
        # Enable automatic type conversion for all child models
        from_attributes=True,
        # Raise error on fields that do not match the model
        extra="forbid",
        # Prefix for env vars - override any config value with OVO_SOME_FIELD_SUBFIELD=123
        env_prefix="OVO_",
    )


@dataclass
class DBConfig:
    url: str | None
    verbose: bool = False


@dataclass
class AWSConfig:
    region: str
    assume_role_arn: str


@dataclass
class StorageConfig:
    path: str | None
    verbose: bool = False
    aws: AWSConfig | None = field(default=None)
    num_copy_threads: int | None = None


@dataclass
class SchedulerConfig:
    type: str
    name: str
    workdir: str
    aws: AWSConfig | None = field(default=None)
    submission_args: dict = field(default_factory=dict)


@dataclass
class AuthConfig:
    # Users who can access Debug page and run commands on the server through the web UI
    admin_users: list[str] = field(default_factory=list)
    # Enable native Streamlit authentication
    streamlit_auth: bool = field(default=False)
    # Allow users to visit private projects if they have the link (containing the project UID)
    allow_private_project_link_access: bool = field(default=True)
    # Hide admin access warning if admin_users is set but no auth is configured
    hide_admin_warning: bool = field(default=False)
    # Always generate a required token to access the app
    always_require_token: bool = field(default=False)


@dataclass
class ConfigProps:
    pyrosetta_license: bool = False
    read_only: bool = False
    rfdiffusion_backbones_limit: int = 1000
    rfdiffusion_backbones_limit_admin: int = 5000
    mpnn_sequences_limit: int = 100


@dataclass
class TemplatesConfig:
    welcome: str | None = None
    welcome_appendix: str | None = None


class OVOConfig(BaseConfigModel):
    # Absolute path to config directory (not stored in YAML, initialized in load_config)
    dir: str = field()
    # Absolute path to reference files directory (model weights, etc)
    reference_files_dir: str = field()
    # Database instance that manages all interactions with the DB
    db: DBConfig = field(default_factory=DBConfig)
    # Authentication config
    auth: AuthConfig = field(default_factory=AuthConfig)
    # Storage instance that manages PDBs and other files
    storage: StorageConfig = field(default_factory=StorageConfig)
    # Key of the default scheduler to use for job submissions
    default_scheduler: str | None = None
    # Key of the local scheduler to use for local job submissions like RFdiffusion preview
    local_scheduler: str | None = None
    # Dictionary of scheduler instances (scheduler key -> instance) that enable scheduling jobs
    schedulers: dict[str, SchedulerConfig] = field(default_factory=dict)
    # Nextflow home directory
    nextflow_home: str = field(default="./nextflow")
    # Text content configuration
    templates: TemplatesConfig = field(default_factory=TemplatesConfig)
    # Remaining configuration settings
    props: ConfigProps = field(default_factory=ConfigProps)
    # Freeform plugin configuration (plugin module name -> config dict)
    plugins: dict[str, dict] = field(default_factory=dict)

    @model_validator(mode="after")
    def resolve_relative_paths(self):
        """Resolve relative paths to absolute paths based on config directory

        Config paths are stored as relative to config directory,
        but in the config object instance they are resolved to full absolute paths.
        """

        def make_absolute_if_relative(path: str) -> str:
            """Convert relative path to absolute by prepending home_dir"""
            if path and not os.path.isabs(path) and "://" not in path:
                return os.path.normpath(os.path.join(self.dir, path))
            return path

        # Resolve DB path
        if self.db.url.startswith("sqlite:///"):
            self.db.url = "sqlite:///" + make_absolute_if_relative(self.db.url.removeprefix("sqlite:///"))

        # Resolve absolute paths
        self.reference_files_dir = make_absolute_if_relative(self.reference_files_dir)
        self.storage.path = make_absolute_if_relative(self.storage.path)
        self.nextflow_home = make_absolute_if_relative(self.nextflow_home)
        for scheduler_name, scheduler_config in self.schedulers.items():
            scheduler_config.workdir = make_absolute_if_relative(scheduler_config.workdir)
            for path_arg in ["config"]:
                if path_arg in scheduler_config.submission_args:
                    scheduler_config.submission_args[path_arg] = make_absolute_if_relative(
                        scheduler_config.submission_args[path_arg]
                    )

        for templ_field in dataclasses.fields(self.templates):
            path = getattr(self.templates, templ_field.name)
            setattr(self.templates, templ_field.name, make_absolute_if_relative(path))

        return self

    @classmethod
    def default(cls, props: ConfigProps, default_profile=None, admin_users: list[str] = None) -> str:
        if default_profile is None:
            default_profile = "conda"
        props_rows = "\n".join(f"  {k}: {json.dumps(v)}" for k, v in props.__dict__.items())
        default_scheduler_key = f"local_{default_profile}"
        return f"""
db:
  url: sqlite:///ovo.db
  verbose: false
reference_files_dir: ./reference_files
nextflow_home: ./nextflow
auth:
  admin_users: {json.dumps(admin_users or [])}
  allow_private_project_link_access: true
storage:
  verbose: false
  path: ./storage
# Customize number of threads for parallel read/write operations on Storage such as sync_files, create_zip, ...
#  num_copy_threads: 16
# Example of a storage path on AWS S3:
#  path: s3://bucket-name/ovo/storage/
#  aws:
#    region: us-east-1
#    assume_role_arn: arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR-ROLE (or null if not assuming a different role)
props:
{props_rows}
default_scheduler: {default_scheduler_key}
local_scheduler: {default_scheduler_key}
schedulers:
  {default_scheduler_key}:
    name: Local with {default_profile}
    type: NextflowScheduler
    submission_args:
      # using CPU version of dependencies, remove 'cpu_env' if your local machine has a GPU
      profile: {default_profile},cpu_env
      max_memory: 8GB
      config: ./nextflow_local.config
    workdir: ./workdir
# Plugin-specific configuration can go here, for example:
# plugins:
#   ovo_plugin_name:
#     key: value
# Uncomment to customize web page content
# templates:
#     welcome: templates/welcome.md
#     welcome_appendix: templates/welcome_appendix.md
"""

    @staticmethod
    def default_nextflow_config():
        return """
process {
    // process settings
    
    executor = "local"  // Executor, for example "pbs", "slurm", ...
    
    beforeScript = ""   // Script to execute before each job, for example "module add singularity"
    queue = null        // Job queue, for example "long"
    
    // customize resources per process
    //withLabel: "colabdesign|rfdiffusion" {
    //    queue = 'gpu-t4'
    //    memory = '16 GB'
    //    cpus = 4
    //    // alternatively to memory and cpus, you can specify cluster job submission options directly
    //    // clusterOptions = "-l select=1:ncpus=4:mem=20gb"
    //}
}
//
//params {
//    // override default parameters here
//    foo = "bar"
//}
"""


DEFAULT_OVO_HOME = os.path.abspath(os.path.expanduser("~/ovo/"))
GLOBAL_OVO_HOME = None
site_packages_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
global_config_flag = os.path.join(site_packages_dir, "ovo.global_config")
if os.path.exists(global_config_flag):
    with open(global_config_flag) as f:
        GLOBAL_OVO_HOME = f.read().strip() or None

# Self-consistency check that default values are valid
default_data = yaml.safe_load(StringIO(OVOConfig.default(props=ConfigProps())))
default_data["dir"] = DEFAULT_OVO_HOME
OVOConfig.model_validate(default_data)


def save_global_home_dir(home_dir: str):
    # Ensure the directory is writable before attempting to write
    home_dir_path = os.path.dirname(global_config_flag)
    if not os.access(home_dir_path, os.W_OK):
        raise OVOCliError(f"Cannot write to the package directory: {home_dir_path}. Insufficient permissions.")
    try:
        with open(global_config_flag, "wt") as f:
            f.write(os.path.abspath(home_dir) + "\n")
    except OSError as e:
        raise OVOCliError(f"Failed to write global config flag at {global_config_flag}: {e}")


def get_shell_config_path():
    """Get path to .bashrc or .zshrc based on the current shell."""
    shell = os.path.basename(os.environ.get("SHELL", ""))
    home = str(Path.home())
    config_path = None
    if "zsh" in shell:
        config_path = os.path.join(home, ".zshrc")
    elif "bash" in shell:
        config_path = os.path.join(home, ".bashrc")
    if config_path and os.path.exists(config_path):
        return config_path
    return None


def get_source_command():
    """Print the command for the user to source the shell config file."""
    shell_config_path = get_shell_config_path()
    command = f"\n[bold]source {shell_config_path}[/bold] # load env variables"
    if active_env := os.getenv("CONDA_DEFAULT_ENV"):
        command += f"\n[bold]conda activate {active_env}[/bold] # re-activate this environment"
    return command


def load_config(home_dir: str) -> OVOConfig:
    """Load OVOConfig from config dir config.yml"""

    config_path = os.path.join(home_dir, "config.yml")

    if not os.path.exists(home_dir) or not os.path.exists(config_path):
        # Config dir does not exist yet, print error and exit
        if home_dir != DEFAULT_OVO_HOME:
            # Custom OVO_HOME set but invalid
            if not os.path.exists(home_dir):
                raise OVONotInitializedError(f"OVO_HOME directory set but is not accessible: {home_dir}")
            else:
                raise OVONotInitializedError(f"OVO config file not found in OVO_HOME: {home_dir}")
        else:
            # Default OVO_HOME, raise not initialized error
            raise OVONotInitializedError("OVO not initialized")

    console.print(f"[bold]OVO home[/bold] [green]{home_dir}[/green]")

    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
        data["dir"] = os.path.abspath(home_dir)

    config = OVOConfig(**data)

    if config.props.read_only:
        console.print("[blue][bold]Running in read-only mode[/bold] (configured in config.yml props.read_only)[/blue]")

    return config


def save_default_config(
    home_dir, config_props: ConfigProps, default_profile: str = None, admin_users: list[str] = None
) -> str:
    config_path = os.path.join(home_dir, "config.yml")

    with open(config_path, "w") as f:
        f.write(OVOConfig.default(props=config_props, default_profile=default_profile, admin_users=admin_users))

    with open(os.path.join(home_dir, "nextflow_local.config"), "w") as f:
        f.write(OVOConfig.default_nextflow_config())

    return config_path
