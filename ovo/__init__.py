from ovo.core.database import *
from ovo.core.storage import Storage
from ovo.core.aws import AWSSessionManager
from ovo.core.scheduler import *
from ovo.core.auth import get_username
from ovo.core.configuration import (
    load_config,
    DEFAULT_OVO_HOME,
    GLOBAL_OVO_HOME,
    get_shell_config_path,
    get_source_command,
)
from ovo.core.plugins import plugin_modules
from ovo.cli.common import console, OVONotInitializedError

# note: ovo.core.logic modules are imported at the bottom to avoid circular dependencies
from rich.panel import Panel
import os
import sys
import importlib.metadata

__version__ = importlib.metadata.version("ovo")

try:
    if sys.platform == "win32":
        console.print(
            Panel.fit(
                "[bold red]⚠️  WARNING: Windows Detected ⚠️[/bold red]\n\n"
                "[yellow]OVO workflows use Nextflow which is not supported on Windows.[/yellow]\n"
                "[yellow]Please use Linux or macOS, or run OVO in WSL2 (Windows Subsystem for Linux) to enable submitting workflows.[/yellow]",
                border_style="red",
                title="[bold red]Platform Warning[/bold red]",
            )
        )

    config = load_config(home_dir=GLOBAL_OVO_HOME or os.getenv("OVO_HOME") or DEFAULT_OVO_HOME)

    db = SqlDBEngine(db_url=config.db.url, verbose=config.db.verbose, read_only=config.props.read_only)
    db.init()

    storage = Storage(
        storage_root=config.storage.path,
        verbose=config.storage.verbose,
        aws=AWSSessionManager(
            assume_role=config.storage.aws.assume_role_arn,
            region_name=config.storage.aws.region,
        )
        if config.storage.aws
        else None,
        num_copy_threads=config.storage.num_copy_threads,
    )

    os.environ["NXF_HOME"] = config.nextflow_home

    schedulers: dict[str, Scheduler] = {}
    # make sure default scheduler is first in the dict
    sorted_scheduler_configs = sorted(
        config.schedulers.items(), key=lambda p: p[0] == config.default_scheduler, reverse=True
    )
    for scheduler_key, scheduler_config in sorted_scheduler_configs:
        if scheduler_config.type not in SchedulerTypes.REGISTERED_CLASSES:
            raise ValueError(
                f"Scheduler type '{scheduler_config.type}' found in config is not registered in this OVO server, make sure it was registered and imported. Supported schedulers: {SchedulerTypes.REGISTERED_CLASSES.keys()}"
            )
        init_args = {}
        if scheduler_config.aws:
            init_args["aws"] = AWSSessionManager(
                assume_role=scheduler_config.aws.assume_role_arn, region_name=scheduler_config.aws.region
            )
        SchedulerClass = SchedulerTypes.REGISTERED_CLASSES[scheduler_config.type]
        schedulers[scheduler_key] = SchedulerClass(
            name=scheduler_config.name,
            workdir=scheduler_config.workdir,
            reference_files_dir=config.reference_files_dir,
            allow_submit=True,
            submission_args=scheduler_config.submission_args,
            **init_args,
        )

    if not config.default_scheduler or config.default_scheduler not in schedulers:
        raise ValueError(f"default_scheduler '{config.default_scheduler}' not found, please check your config file.")

    if not config.local_scheduler or config.local_scheduler not in schedulers:
        raise ValueError(f"local_scheduler '{config.local_scheduler}' not found, please check your config file.")

    default_scheduler = schedulers[config.default_scheduler]
    local_scheduler = schedulers[config.local_scheduler]

    def get_scheduler(scheduler_key: str) -> Scheduler:
        if scheduler_key not in schedulers:
            raise ValueError(
                f"Scheduler '{scheduler_key}' is not registered in this OVO server, "
                f"registered schedulers: {schedulers.keys()}"
            )
        return schedulers[scheduler_key]

    # Load plugin modules to register their classes, use reload to support streamlit live reload
    for submodule_name in plugin_modules:
        submodule = importlib.import_module(submodule_name)
        importlib.reload(submodule)

    # Additional imports at the bottom to avoid circular dependencies
    from ovo.core.logic import design_logic, descriptor_logic, job_logic, project_logic, import_export_logic

except OVONotInitializedError as e:
    if ("init" in sys.argv and "home" in sys.argv) or "-h" in sys.argv or "--help" in sys.argv:
        # Ignore initialization error if we are initializing the home dir
        pass
    else:
        if os.getenv("OVO_HOME"):
            message = str(e)
        else:
            message = "\nPlease initialize OVO using [bold]ovo init home[/bold] or set [green]OVO_HOME[/green] env var."
            if shell_config_path := get_shell_config_path():
                with open(shell_config_path, "r") as f:
                    contents = f.read()
                if "OVO_HOME" in contents:
                    message = (
                        f"\n[green]OVO_HOME[/green] env variable not set.\nLooks like you have already initialized OVO and added [green]OVO_HOME[/green] "
                        f"to your {os.path.basename(shell_config_path)}, please run:\n" + get_source_command()
                    )
        console.print(Panel.fit(message, title="⚠️  OVO not initialized", border_style="red"))
        sys.exit(2)
