import re
import subprocess
from datetime import datetime

import typer
import os

from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from ovo.cli.common import console, OVOCliError, download_files, init_nextflow, print_ovo_logo
from ovo.core.configuration import (
    ConfigProps,
    DEFAULT_OVO_HOME,
    get_source_command,
    get_shell_config_path,
    save_default_config,
)
import shutil
from pathlib import Path

from ovo.core.utils.resources import RESOURCES_DIR

app = typer.Typer(pretty_exceptions_enable=False, help="OVO initialization commands")

TEMPLATES_DIR = Path(__file__).parent / "templates"

RFDIFFUSION_MODEL_FILES = [
    # URL, local path, hash (SHA256: calculate with "shasum -a 256 my_file" or "sha256sum my_file")
    (
        "https://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt",
        "rfdiffusion_models/Base_ckpt.pt",
        "0fcf7d7c32b4848030aca3a051e6768de194616f96ba6c38186351a33bfc6eca",
    ),
    (
        "https://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt",
        "rfdiffusion_models/Complex_base_ckpt.pt",
        "76e4e260aefee3b582bd76b77ab95d2592e64f00c51bf344968ab9239f3250bc",
    ),
    (
        "https://files.ipd.uw.edu/pub/RFdiffusion/f572d396fae9206628714fb2ce00f72e/Complex_beta_ckpt.pt",
        "rfdiffusion_models/Complex_beta_ckpt.pt",
        "5a0b1cafc23c60b1aabcec1e49391986ac4fd02cc1b6b4cc41714ca9fe882e9e",
    ),
    (
        "https://files.ipd.uw.edu/pub/RFdiffusion/5532d2e1f3a4738decd58b19d633b3c3/ActiveSite_ckpt.pt",
        "rfdiffusion_models/ActiveSite_ckpt.pt",
        "beca1f672049161df0bc6a2d2523828f19fd9c8a2b449988e246dde42e7ea986",
    ),
    (
        "https://files.ipd.uw.edu/pub/RFdiffusion/74f51cfb8b440f50d70878e05361d8f0/InpaintSeq_ckpt.pt",
        "rfdiffusion_models/InpaintSeq_ckpt.pt",
        "3b71b2b954e87d46b75a88ba64e0420fbf27f592604b10b6c3561b8c8ab70ab6",
    ),
]

ALPHAFOLD_MODEL_FILES = [
    (
        "https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar",
        "alphafold_models",
        "36d4b0220f3c735f3296d301152b738c9776d16981d054845a68a1370b26cfe3",
    )
]

ESM1V_MODEL_FILES = [
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_1.pt",
        "esm_models/esm1v_t33_650M_UR90S_1.pt",
        "9519ee60f1cddad3c101afb1f42612499e188534969c3f682e94850870f70433",
    ),
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_2.pt",
        "esm_models/esm1v_t33_650M_UR90S_2.pt",
        "5b7b095e8eafc53ccfe5994b954fb756bfe7a081f22b4caa1ed59b77b90bcf81",
    ),
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_3.pt",
        "esm_models/esm1v_t33_650M_UR90S_3.pt",
        "bc5cb2f2a1b35def284e2b2833ae58c803ca9c61b16b72c1dd54c54e76df0b67",
    ),
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_4.pt",
        "esm_models/esm1v_t33_650M_UR90S_4.pt",
        "44750a28c09f7ba9e7ccb7aeaba812cbbe90eb2a8a2c658dc5fa165f7090a15a",
    ),
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_5.pt",
        "esm_models/esm1v_t33_650M_UR90S_5.pt",
        "69ffd06be29aaaf105eda919f23e5ac4a6872e7907fbf1f087fd942abdb3adf7",
    ),
]

ESM_IF_MODEL_FILES = [
    (
        "https://dl.fbaipublicfiles.com/fair-esm/models/esm_if1_gvp4_t16_142M_UR50.pt",
        "esm_models/esm_if1_gvp4_t16_142M_UR50.pt",
        "be4ba36edec22a9bfaa4946ff6b2815f1f19d8a3d7e0eada8b796d5a0eae9fd4",
    )
]

BOLTZ_MODEL_FILES = {
    (
        "https://huggingface.co/boltz-community/boltz-1/resolve/main/boltz1_conf.ckpt",
        "boltz_models/boltz1_conf.ckpt",
        "fea245d912c570ec117b2277c2719f312a6fc109c07b6f6ef741690ee775c2f5",
    ),
    (
        "https://huggingface.co/boltz-community/boltz-1/resolve/main/ccd.pkl",
        "boltz_models/ccd.pkl",
        "2d3b2f03a3c5665944adba51e33263511e51b21c9cd05d902f9c4b7c1e58d2f4",
    ),
}


@app.command()
def home(
    home_dir: str | None = typer.Argument(None, help="OVO home directory"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirm all without prompting"),
    no_env: bool = typer.Option(False, "--no-env", help="Do not set OVO_HOME in shell .bashrc/.zshrc file"),
    default_profile: str = typer.Option(None, "--profile", help="Default nextflow profile to use in default scheduler"),
):
    """Initialize the OVO home directory"""

    console.print("[bold]OVO initialization[/bold]")

    if home_dir is None:
        console.print("""
[bold]Create OVO home directory[/bold]

This directory will contain all OVO files:

- [bold]config.yml[/bold][gray]______[/gray]configuration file
- [bold]ovo.db[/bold][gray]__________[/gray]SQLite database (stored as a single file)
- [bold]workdir[/bold][gray]_________[/gray]Working directory for Nextflow workflows
- [bold]storage[/bold][gray]_________[/gray]PDB design files and other permanent results
- [bold]reference_files[/bold][gray]_[/gray]Downloaded model weights and other reference files

All paths can be customized later in the [bold]config.yml[/bold] file.
""")
        home_dir = yes or Prompt.ask(
            prompt="Enter path, or press [bold]Enter[/bold] to select the default",
            default=os.getenv("OVO_HOME", DEFAULT_OVO_HOME),  # Use OVO_HOME env var if set already
        )

    home_dir = os.path.abspath(os.path.expanduser(home_dir))

    while os.path.exists(home_dir):
        if yes:
            raise FileExistsError(f"Home directory already exists: {home_dir}")
        # show error f"Home directory already exists: {home_dir}"
        console.print(f"[red]Error:[/red] Home directory already exists: [bold]{home_dir}[/bold]")
        home_dir = Prompt.ask("Please choose a different path for the new OVO Home directory")
        home_dir = os.path.abspath(os.path.expanduser(home_dir))

    if not yes and home_dir != DEFAULT_OVO_HOME:
        if not Confirm.ask(f"Confirm directory: [bold]{home_dir}[/bold]"):
            console.print("Aborted")
            raise typer.Exit()

    if not default_profile:
        default_profile = "conda"
        if not yes:
            console.print("""
    OVO uses Nextflow to run workflows and manage software environments.
    How do you want the default OVO scheduler to manage dependencies?""")
            default_profile = Prompt.ask(
                "\nSelect profile, or press [bold]Enter[/bold] to select the default",
                choices=["conda", "singularity", "apptainer", "docker", "podman"],
                default=default_profile,
            )

    # ask about using conda when docker is not on PATH
    if not shutil.which(default_profile):
        console.print(
            f"[yellow]WARNING:[/yellow] {default_profile} not found on PATH, please make sure to install or activate {default_profile} or change the default scheduler profile (docker, singularity, apptainer, ...)"
        )

    config_props = ConfigProps()
    config_props.pyrosetta_license = yes or Confirm.ask(
        "\nEnable fastrelax? In case of commercial use, this requires a PyRosetta license"
    )

    admin_users = []
    if os.environ.get("USER"):
        # we don't want to flood the user with too many questions, enable by default
        admin_users.append(os.environ["USER"])

    os.makedirs(home_dir, exist_ok=True)

    config_path = save_default_config(
        home_dir=home_dir,
        config_props=config_props,
        default_profile=default_profile,
        admin_users=admin_users,
    )

    console.print(f"\n[green]✔[/green] Initialized OVO config: [bold]{config_path}[/bold]")

    if home_dir != DEFAULT_OVO_HOME and not no_env:
        console.print("\nYou will need to set the OVO_HOME environment variable to use this home directory.")
        export_command = f'export OVO_HOME="{home_dir}"'

        if (shell_config_path := get_shell_config_path()) and (
            yes or Confirm.ask(f"\nAdd the OVO_HOME dir to {shell_config_path}?")
        ):
            with open(shell_config_path, "a") as f:
                f.write(f"\n{export_command}")
            console.print(f"\n✔ Added to {shell_config_path}. Restart your terminal or run:")
            console.print(get_source_command())
        else:
            console.print("\nPlease set this environment variable manually:")
            console.print(f"[bold green]{export_command}[/bold green]")

    console.print("\nNext step: Initialize the preview workflow using [bold]ovo init preview[/bold]")


@app.command()
def preview():
    """Initialize nextflow, reference files and environment for the RFdiffusion preview workflow"""
    from ovo import config, local_scheduler

    # Initialize nextflow
    console.print("[bold]Initializing nextflow...[/bold]")
    init_nextflow()
    console.print("[bold][green]✔[/green] Nextflow initialized successfully[/bold]")

    # Download RFdiffusion base model weights
    download_files(destination_dir=config.reference_files_dir, file_list=RFDIFFUSION_MODEL_FILES)

    # Submit RFdiffusion preview (which also initializes the RFdiffusion conda environment)
    ovo_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources"))
    process, job_id = local_scheduler.submit(
        "rfdiffusion-backbone",
        params={
            "contig": "A82-87/10/A92-97",
            "input_pdb": os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb"),
            "num_designs": 1,
            "run_parameters": "diffuser.T=2",
        },
        submission_args=dict(sync=True),
    )
    process.wait()
    if process.returncode == 0:
        console.print("[bold][green]✔[/green] RFdiffusion preview completed successfully[/bold]")
        console.print("Example unconditional design output saved to:")
        console.print(local_scheduler.get_output_dir(job_id))
    else:
        console.print("RFdiffusion workflow [red]FAILED[/red], please see errors above")
        exit(process.returncode)

    console.print("\nNext step: Set up end-to-end RFdiffusion workflow using [bold]ovo init rfdiffusion[/bold]")
    console.print("           Or already explore OVO web app using [bold]ovo app[/bold]")


@app.command()
def rfdiffusion(scheduler: str = None):
    """Initialize nextflow, reference files and environment for the RFdiffusion end-to-end workflow"""
    from ovo import config, get_scheduler

    # Initialize nextflow
    init_nextflow()

    # Download RFdiffusion base model weights
    download_files(destination_dir=config.reference_files_dir, file_list=RFDIFFUSION_MODEL_FILES)

    # Download AlphaFold weights
    download_files(destination_dir=config.reference_files_dir, file_list=ALPHAFOLD_MODEL_FILES)

    scheduler = get_scheduler(scheduler_key=scheduler or config.default_scheduler)

    # Submit RFdiffusion scaffold end-to-end workflows
    ovo_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources"))
    process, job_id = scheduler.submit(
        "rfdiffusion-end-to-end",
        params={
            "rfdiffusion_contig": "A82-87/10/A92-97",
            "rfdiffusion_input_pdb": os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb"),
            "rfdiffusion_num_designs": 1,
            "rfdiffusion_run_parameters": "diffuser.T=2",
            "mpnn_num_sequences": 2,
            "design_type": "scaffold",
            "refolding_tests": "af2_model_1_ptm_ft_1rec",
        },
        submission_args=dict(sync=True),
    )
    process.wait()
    if process.returncode == 0:
        console.print("[bold][green]✔[/green] RFdiffusion scaffold preview completed successfully[/bold]")
        console.print("Example scaffold design output saved to:")
        console.print(scheduler.get_output_dir(job_id))
    else:
        console.print("RFdiffusion workflow [red]FAILED[/red], please see errors above")
        exit(process.returncode)

    # Submit RFdiffusion binder end-to-end workflow with LigandMPNN
    process, job_id = scheduler.submit(
        "rfdiffusion-end-to-end",
        params={
            "rfdiffusion_contig": "A20-130/0 10",
            "rfdiffusion_input_pdb": os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb"),
            "rfdiffusion_num_designs": 1,
            "rfdiffusion_run_parameters": "diffuser.T=15",
            "mpnn_num_sequences": 2,
            "mpnn_fastrelax_cycles": 0,
            "disable_pyrosetta_scoring": not config.props.pyrosetta_license,
            "design_type": "binder",
            "refolding_tests": "af2_model_1_multimer_tt_3rec",
        },
        submission_args=dict(sync=True),
    )
    process.wait()
    if process.returncode == 0:
        console.print("[bold][green]✔[/green] RFdiffusion binder preview completed successfully[/bold]")
        console.print("Example binder design output saved to:")
        console.print(scheduler.get_output_dir(job_id))
    else:
        console.print("RFdiffusion workflow [red]FAILED[/red], please see errors above")
        exit(process.returncode)

    if config.props.pyrosetta_license:
        # Submit RFdiffusion binder end-to-end workflow with FastRelax
        process, job_id = scheduler.submit(
            "rfdiffusion-end-to-end",
            params={
                "rfdiffusion_contig": "A20-130/0 10",
                "rfdiffusion_input_pdb": os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb"),
                "rfdiffusion_num_designs": 1,
                "rfdiffusion_run_parameters": "diffuser.T=15",
                "mpnn_fastrelax_cycles": 1,
                "design_type": "binder",
                "refolding_tests": "af2_model_1_multimer_tt_3rec",
            },
            submission_args=dict(sync=True),
        )
        process.wait()
        if process.returncode == 0:
            console.print("[bold][green]✔[/green] RFdiffusion binder preview completed successfully[/bold]")
            console.print("Example binder design output saved to:")
            console.print(scheduler.get_output_dir(job_id))
        else:
            console.print("RFdiffusion workflow [red]FAILED[/red], please see errors above")
            exit(process.returncode)

    console.print("\nNext step: Run OVO web app using [bold]ovo app[/bold]")


@app.command()
def proteinqc(
    tool_keys: str = typer.Option(
        "all",
        "--tools",
        help="Comma-separated list of ProteinQC tools to use, or 'all' to use all available tools (supported by the scheduler)",
    ),
    scheduler: str = None,
):
    """Initialize nextflow, reference files and environment for the ProteinQC workflow"""
    from ovo import config, get_scheduler
    from ovo.core.database.models_proteinqc import PROTEINQC_TOOLS, ESM_1V, ESM_IF
    from ovo.core.logic.proteinqc_logic import get_available_tools

    # Initialize nextflow
    init_nextflow()

    scheduler = get_scheduler(scheduler_key=scheduler or config.default_scheduler)

    if tool_keys != "all":
        tool_keys = tool_keys.split(",")
        all_tools_by_key = {tool.tool_key: tool for tool in PROTEINQC_TOOLS}
        tools = []
        for key in tool_keys:
            if key not in all_tools_by_key:
                raise OVOCliError(
                    f"Invalid ProteinQC tool '{key}', available tools: {','.join(all_tools_by_key.keys())}"
                )
            tools.append(all_tools_by_key[key])
    else:
        tools = get_available_tools(PROTEINQC_TOOLS, scheduler)
        tool_keys = [tool.tool_key for tool in tools]

    # Download ESM1v weights
    if ESM_1V in tools:
        download_files(destination_dir=config.reference_files_dir, file_list=ESM1V_MODEL_FILES)

    # Download ESM-IF weights
    if ESM_IF in tools:
        download_files(destination_dir=config.reference_files_dir, file_list=ESM_IF_MODEL_FILES)

    # Submit ProteinQC workflow
    ovo_resources_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources"))
    input_path = os.path.join(ovo_resources_path, "examples/inputs/5ELI_A.pdb")

    chains = ["A"]
    process, job_id = scheduler.submit(
        "proteinqc",
        params={
            "input_pdb": input_path,
            "tools": ",".join(tool_keys),
            "chains": ",".join(chains),
        },
        submission_args=dict(sync=True),
    )
    process.wait()
    if process.returncode == 0:
        console.print("[bold][green]✔[/green] ProteinQC completed successfully[/bold]")
        console.print("Example ProteinQC output saved to:")
        console.print(scheduler.get_output_dir(job_id))
    else:
        console.print("ProteinQC workflow [red]FAILED[/red], please see errors above")
        exit(process.returncode)


@app.command()
def plugin():
    """Create a new OVO plugin directory"""

    with console.screen():
        console.show_cursor(True)
        print_ovo_logo(padding="")
        console.print("[bold]Welcome to the OVO plugin wizard![/bold]")
        console.print("This wizard will help you create a new OVO plugin directory structure.")
        console.print("=" * console.size.width)
        console.print("")

        module_name = Prompt.ask("Enter the plugin module name (such as ovo_my_plugin)")
        while not module_name.startswith("ovo_"):
            console.print("[red]Please use a module name starting with ovo_[/red]")
            module_name = Prompt.ask("Enter the plugin module name (such as ovo_my_plugin)")
        module_suffix = module_name.removeprefix("ovo_")

        plugin_dir = os.path.abspath(module_name)

        if os.path.exists(plugin_dir):
            raise FileExistsError(f"Plugin directory already exists: {plugin_dir}")

        while not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", module_name):
            console.print("[red]Invalid module name, must be a valid Python identifier[/red]")
            module_name = Prompt.ask("Enter the plugin module name (such as ovo_my_plugin)")

        console.print("")
        table = Table(show_lines=True)
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        table.add_row("ui", "Plugin without any workflows")
        table.add_row("descriptor", "Workflow that produces only Descriptor objects ")
        table.add_row("design", "COMING SOON - Workflow that produces a Pool with Design and Descriptor objects")

        console.print(table)
        console.print("")

        # Ask the user to pick
        plugin_template = Prompt.ask(
            "Enter your choice",
            choices=["ui", "descriptor", "design"],
        )

        console.print(f"You picked: [bold green]{plugin_template}[/bold green]\n")

        files = [
            {
                "path": "README.md",
                "description": "Plugin README file",
                "content": TEMPLATES_DIR / "README.md",
            },
            {
                "path": "pyproject.toml",
                "description": "Plugin package metadata and configuration enabling pip install",
                "content": TEMPLATES_DIR / "plugin_pyproject.toml",
            },
            {
                "path": ".gitignore",
                "description": "Declares files to be ignored by git",
                "content": f"""
*.egg-info
/build
/work
.DS_Store
*.pyc
test-results
/.idea
/.vscode
__pycache__/
.env
""",
            },
            {
                "path": "MANIFEST.in",
                "description": "Declare non-code files to include the package distribution",
                "content": f"""
# Include only specific file types
recursive-include {module_name} *

prune **/test-results

prune **/node_modules

prune {module_name}/pipelines/*/local

# Patterns to exclude from any directory
global-exclude *~
global-exclude *.pyc
global-exclude *.pyo
global-exclude .git
global-exclude .DS_Store
global-exclude .ipynb_checkpoints
global-exclude *.map
""",
            },
        ]

        variables = {
            "__MODULE_NAME__": module_name,
            "__MODULE_SUFFIX__": module_suffix,
            "__PACKAGE_NAME__": module_name.replace("_", "-"),
        }

        if plugin_template == "ui":
            files.extend(
                [
                    {
                        "path": f"{module_name}/__init__.py",
                        "description": "Plugin module entry point that registers the plugin capabilities in OVO",
                        "content": f'''
plugin = dict(
    pages = {{
        # "Tool name": [
        #     dict(page="my_module.my_page", title="🔥 My plugin page")
        # ],
    }},
    design_views = {{
        "🔥 My design view": "{module_name}.design_view_{module_suffix}:{module_name}_fragment",
    }},
    # descriptors = "{module_name}.descriptors_{module_suffix}",
    # modules = [
    #     "{module_name}.models_{module_suffix}",
    # ]
)
''',
                    },
                    {
                        "path": f"{module_name}/design_view_{module_suffix}.py",
                        "description": "Placeholder 'design view', will appear as a new tab on the Designs page",
                        # read using Path, ../templates/alignment_design_view.py from current file
                        "content": TEMPLATES_DIR / "alignment_design_view.py",
                    },
                ]
            )
        elif plugin_template == "descriptor":
            workflow_class_name = Prompt.ask(
                "Enter the workflow subclass name (ending with Workflow such as SomeToolWorkflow)"
            )
            if not re.match(r"^[A-Z][a-zA-Z0-9]+Workflow$", workflow_class_name):
                console.print("[red]Invalid workflow class name, please use CamelCase ending with Workflow[/red]")
                workflow_class_name = Prompt.ask("Enter the workflow subclass name")

            pipeline_name = Prompt.ask("Enter the pipeline name (kebab-case such as some-tool)")
            if not re.match(r"[a-z0-9-]+$", pipeline_name):
                console.print("[red]Invalid pipeline name, please use lowercase and dashes[/red]")
                pipeline_name = Prompt.ask("Enter the pipeline name")

            variables["__WORKFLOW_CLASS_NAME__"] = workflow_class_name
            variables["__PIPELINE_NAME__"] = pipeline_name

            files.extend(
                [
                    {
                        "path": f"{module_name}/__init__.py",
                        "description": "Plugin module entry point that registers the plugin capabilities in OVO",
                        "content": f'''
plugin = dict(
    pages = {{
        # "Tool name": [
        #     dict(page="{module_name}.my_page", title="💥 My plugin page")
        # ],
    }},
    design_views = {{
        "💥 My Method": "{module_name}.design_view_{module_suffix}:{module_name}_fragment",
    }},
    descriptors = "{module_name}.descriptors_{module_suffix}",
    modules = [
        "{module_name}.models_{module_suffix}",
    ]
)
''',
                    },
                    {
                        "path": f"{module_name}/descriptors_{module_suffix}.py",
                        "description": "Declaration of Descriptor objects that store metadata about descriptor values",
                        "content": TEMPLATES_DIR / "descriptor_plugin/descriptors_example.py",
                    },
                    {
                        "path": f"{module_name}/design_view_{module_suffix}.py",
                        "description": "Web interface for submission and result visualization implemented using Streamlit",
                        "content": TEMPLATES_DIR / "descriptor_plugin/design_view_example.py",
                    },
                    {
                        "path": f"{module_name}/envs/{module_suffix}.yml",
                        "description": "Conda environment definition for an example tool",
                        "content": TEMPLATES_DIR / "descriptor_plugin/envs/mytool.yml",
                    },
                    {
                        "path": f"{module_name}/models_{module_suffix}.py",
                        "description": "Workflow subclass definition storing workflow parameters and processing logic",
                        "content": TEMPLATES_DIR / "descriptor_plugin/models_example.py",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/main.nf",
                        "description": "Nextflow pipeline definition example",
                        "content": TEMPLATES_DIR / "descriptor_plugin/pipelines/example/main.nf",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/bin/example.py",
                        "description": "Example Python script used in the workflow",
                        "content": TEMPLATES_DIR / "descriptor_plugin/pipelines/example/bin/example.py",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/nextflow.config",
                        "description": "Nextflow pipeline default parameter configuration",
                        "content": TEMPLATES_DIR / "descriptor_plugin/pipelines/example/nextflow.config",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/nextflow_schema.json",
                        "description": "Nextflow pipeline parameter schema declaring available parameters",
                        "content": TEMPLATES_DIR / "descriptor_plugin/pipelines/example/nextflow_schema.json",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/local/nextflow_test.sh",
                        "description": "Nextflow pipeline test script",
                        "content": TEMPLATES_DIR / "descriptor_plugin/pipelines/example/local/nextflow_test.sh",
                    },
                    {
                        "path": f"tests/test_{module_suffix}_workflow.py",
                        "description": "End-to-end test of the workflow that verifies results in the OVO database",
                        "content": TEMPLATES_DIR / "descriptor_plugin/test_example.py",
                    },
                    {
                        "path": f"{module_name}/pipelines/{pipeline_name}/local/test-input/5ELI_A.pdb",
                        "content": RESOURCES_DIR / "examples/inputs/5ELI_A.pdb",
                    },
                    {
                        "path": "tests/conftest.py",
                        "content": f'''
import pytest
from ovo.core.utils.tests import create_test_project_data


@pytest.fixture(scope="session")
def project_data():
    """Create one project, project_round, and pool for the entire test run."""
    return create_test_project_data()
''',
                    },
                ]
            )
        else:
            raise OVOCliError("Only 'descriptor' and 'ui' plugin templates are implemented so far")

        console.print("")
        run_git_init = Confirm.ask("Run 'git init' in the plugin directory?", default=True)

        if Confirm.ask("Add MIT license file?", default=True):
            author_name = Prompt.ask("Enter author name for license (Your Name)")
            files.append(
                {
                    "path": "LICENSE",
                    "description": "MIT License file",
                    "content": TEMPLATES_DIR / "LICENSE_MIT.txt",
                }
            )
            variables["__AUTHOR_NAME__"] = author_name
            variables["__YEAR__"] = str(datetime.now().year)

        console.print("")

    # All parameters ready, create plugin directory
    # create module and __init__.py file
    os.makedirs(plugin_dir)
    module_dir = os.path.join(plugin_dir, module_name)
    os.mkdir(module_dir)

    console.print("")
    console.print("=" * console.size.width)

    for file_dict in files:
        full_path = os.path.join(plugin_dir, file_dict["path"])
        content = file_dict["content"]
        if isinstance(content, Path):
            content = content.read_text()
        content = content.lstrip()
        for pattern, value in variables.items():
            content = content.replace(pattern, value)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wt") as f:
            f.write(content)

    tree = Tree(module_name)
    nodes = {(): tree}

    for item in sorted(files, key=lambda f: f["path"]):
        parts = Path(item["path"]).parts

        for i, part in enumerate(parts[:-1]):
            key = parts[: i + 1]
            if key not in nodes:
                nodes[key] = nodes[parts[:i]].add(part)

        nodes[parts[:-1]].add(f"{parts[-1]} [grey50]{item.get('description', '')}[/grey50]")

    console.print("")
    console.print(tree)

    console.print("\n[green]✔[/green] Created new plugin directory:")
    console.print(f"[bold]{plugin_dir}[/bold]")

    if run_git_init:
        console.print("")
        subprocess.run(["git", "init", plugin_dir], check=True)

    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"\n# Use pip install -e to install in editable/development mode")
    console.print(f"pip install -e {plugin_dir}")

    console.print(f"\nSee the plugin development guide at:")
    console.print("https://ovo.dichlab.org/docs/developer_guide/plugin_development.html")


if __name__ == "__main__":
    app()
