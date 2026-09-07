import itertools
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import typer
import yaml
from humanize import naturaltime
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from sqlalchemy.exc import NoResultFound

from ovo.cli.common import console, OVOCliError

app = typer.Typer(pretty_exceptions_enable=False, help="Submit and manage OVO design workflows")


def _is_id_format(value: str) -> bool:
    """Check if a value looks like a UUID (ID format) rather than a human-readable name."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _try_get_by_id(db, model, value: str):
    """Try to look up a model instance by ID. Returns None if not found."""
    try:
        return db.get(model, id=value)
    except NoResultFound:
        return None


def _resolve_by_id(db, model, value: str, label: str):
    """Look up a model instance by ID. Raises OVOCliError if it looks like an ID but is not found."""
    result = _try_get_by_id(db, model, value)
    if result is None and _is_id_format(value):
        raise OVOCliError(f"{label} not found with ID: {value}")
    return result


def resolve_project(value: str):
    """Resolve a project by ID or name. Raises OVOCliError if not found or ambiguous."""
    from ovo import db
    from ovo.core.database.models import Project

    result = _resolve_by_id(db, Project, value, "Project")
    if result:
        return result
    projects = db.select(Project, name=value)
    if not projects:
        raise OVOCliError(f"Project not found: {value}")
    if len(projects) > 1:
        options = "\n  ".join(f"{p.id} (author: {p.author})" for p in projects)
        raise OVOCliError(f"Multiple projects found with name '{value}'. Use project ID to disambiguate:\n  {options}")
    return projects[0]


def resolve_round_ids(value: str, project_id: str = None) -> list[str]:
    """Resolve round IDs by ID or name. Raises OVOCliError if not found."""
    from ovo import db
    from ovo.core.database.models import Round

    result = _resolve_by_id(db, Round, value, "Round")
    if result:
        if project_id and result.project_id != project_id:
            raise OVOCliError(f"Round '{value}' belongs to a different project (expected project {project_id})")
        return [result.id]
    round_filter = {"name": value}
    if project_id:
        round_filter["project_id"] = project_id
    rounds = db.select(Round, **round_filter)
    if not rounds:
        raise OVOCliError(f"Round not found: {value}")
    return [r.id for r in rounds]


@app.command()
def names():
    """List all available workflow type names."""
    from ovo.core.database.models import WorkflowTypes

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Available workflow types", no_wrap=True)

    for wf_name in WorkflowTypes.get_design_workflow_types():
        table.add_row(wf_name)

    console.print(table)


@app.command()
def template(
    name: str = typer.Option(
        ..., "--name", help="Workflow type name (use 'ovo workflow names' to list available names)"
    ),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (prints to stdout if not specified)"),
):
    """Generate a YAML config template for a given workflow type.

    The generated template contains all parameter fields with their default values,
    ready to be customized and submitted via 'ovo workflow submit'.
    """
    from ovo.core.logic.bulk_submission_logic import get_bulk_config_template

    try:
        yaml_str = get_bulk_config_template(name)
    except ValueError as e:
        raise OVOCliError(str(e))

    if output:
        with open(output, "w") as f:
            f.write(yaml_str)
        console.print(f"[green]✔[/green] Template written to: {output}")
    else:
        sys.stdout.write(yaml_str)


@app.command()
def submit(
    config_file: str = typer.Argument(help="Path to YAML/JSON config file (same format as bulk submission)"),
    project: str = typer.Option(
        None, "--project", help="Project name or ID (creates if not found, uses personal project if not specified)"
    ),
    round_name: str = typer.Option(None, "--round", help="Round name or ID (creates new round if not found)"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key to use (see 'ovo scheduler list')"),
    resume_failed: bool = typer.Option(
        False, "--resume-failed", help="Resume previously failed jobs with the same pool name"
    ),
    return_existing: bool = typer.Option(
        False,
        "--return-existing",
        help="Return the existing pool instead of failing if a pool with the same name and params was already submitted",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Submit design workflows from a YAML/JSON config file.

    Reads a bulk submission config (same format as the Bulk Submission UI page),
    expands grid parameters, and submits each workflow to the scheduler.
    Each submission in the config needs a 'pool_name' for the pool to create.
    Results are stored in the database as DesignJob and Pool records.

    Input file paths in the config are resolved relative to the config file location.
    Files are uploaded to storage and paths are updated before submission.

    Prints the DesignJob ID for each submitted workflow to stdout.
    Use 'ovo workflow status <job_id>' to check progress.
    """
    from ovo import config as ovo_config, db
    from ovo.core.auth import get_username
    from ovo.core.database.models import Project as ProjectModel, Round
    from ovo.core.logic.bulk_submission_logic import (
        BulkSubmission,
        bulk_submit,
        import_bulk_config,
        resolve_input_paths,
        validate_submissions,
    )
    from ovo.core.utils.bulk_submission_utils import parse_bulk_config_yaml
    from ovo.core.logic.project_logic import get_or_create_personal_project, get_or_create_project
    from ovo.core.logic.round_logic import get_or_create_project_rounds

    # 1. Validate scheduler and read config file
    resolved_scheduler_key = scheduler_key or ovo_config.default_scheduler
    if resolved_scheduler_key not in ovo_config.schedulers:
        available = "\n  ".join(f"{k} ({v.name})" for k, v in ovo_config.schedulers.items())
        raise OVOCliError(f"Unknown scheduler: '{resolved_scheduler_key}'\n\nAvailable schedulers:\n  {available}")

    if not os.path.exists(config_file):
        raise OVOCliError(f"Config file not found: {config_file}")

    with open(config_file) as f:
        config_text = f.read()

    try:
        config_dict = parse_bulk_config_yaml(config_text)
    except yaml.YAMLError as e:
        raise OVOCliError(f"Failed to parse YAML config: {e}")

    # 2. Expand grid parameters into submissions
    try:
        submissions = import_bulk_config(config_dict)
    except ValueError as e:
        raise OVOCliError(f"Invalid config: {e}")

    if not submissions:
        raise OVOCliError("No workflows found in config")

    # Every submission needs its own pool name, there is no pool name option to fall back to here
    try:
        pool_names = BulkSubmission.get_pool_names(submissions)
    except ValueError as e:
        raise OVOCliError(f"{e}\nEach submission of the config needs a 'pool_name' for the pool it creates.")

    console.print(f"Parsed [bold]{len(submissions)}[/bold] workflow(s) from config")

    # 3. Resolve project and round
    if project:
        proj = _resolve_by_id(db, ProjectModel, project, "Project")
        if not proj:
            projects = db.select(ProjectModel, name=project)
            if projects:
                if len(projects) > 1:
                    options = "\n  ".join(f"{p.id} (author: {p.author})" for p in projects)
                    raise OVOCliError(
                        f"Multiple projects found with name '{project}'. Use project ID to disambiguate:\n  {options}"
                    )
                proj = projects[0]
            else:
                if not yes and not Confirm.ask(f"Project '{project}' does not exist. Create it?"):
                    raise SystemExit(0)
                proj = get_or_create_project(project)
    else:
        proj = get_or_create_personal_project()

    if round_name:
        proj_round = _resolve_by_id(db, Round, round_name, "Round")
        if proj_round:
            if proj_round.project_id != proj.id:
                raise OVOCliError(f"Round '{round_name}' belongs to a different project (expected project {proj.id})")
        else:
            try:
                proj_round = db.get(Round, name=round_name, project_id=proj.id)
            except NoResultFound:
                if not yes and not Confirm.ask(
                    f"Round '{round_name}' does not exist in project '{proj.name}'. Create it?"
                ):
                    raise SystemExit(0)
                proj_round = Round(name=round_name, project_id=proj.id, author=get_username())
                db.save(proj_round)
    else:
        # If not specified, use the last round (by creation date) or create a new one if none exist
        rounds = get_or_create_project_rounds(proj.id)
        proj_round = list(rounds.values())[-1]

    # Validate the whole batch before uploading or submitting anything, so it fails as a whole
    try:
        pool_names = validate_submissions(
            submissions, round_id=proj_round.id, return_existing=return_existing or resume_failed
        )
    except ValueError as e:
        raise OVOCliError(str(e))

    # 4. Resolve input file paths relative to config file directory
    try:
        resolve_input_paths(
            [submission.workflow for submission in submissions],
            project_id=proj.id,
            base_dir=os.path.dirname(os.path.abspath(config_file)),
        )
    except FileNotFoundError as e:
        raise OVOCliError(str(e))

    # 5. Summary and confirmation
    console.print("\nSubmission summary:")
    console.print(f"     Project: [bold]{proj.name}[/bold]")
    console.print(f"       Round: [bold]{proj_round.name}[/bold]")
    console.print(f"       Pools: [bold]{', '.join(pool_names)}[/bold]")
    console.print(f"   Scheduler: [bold]{resolved_scheduler_key}[/bold]")
    console.print(f"   Workflows: [bold]{len(submissions)}[/bold]")
    console.print("")

    if not yes:
        if not Confirm.ask("Proceed with submission?"):
            raise SystemExit(0)

    # 6. Submit each workflow
    def report(result) -> None:
        if result.success:
            console.print(
                f"[green]✔[/green] Submitted [bold]{result.pool_name}[/bold] "
                f"→ DesignJob [bold]{result.design_job_id}[/bold]"
            )
            console.print(f"Check status with: [bold]ovo workflow status {result.design_job_id}[/bold]")
            console.print(f"Monitor job grid tasks with: [bold]ovo workflow tasks {result.design_job_id}[/bold]")
            # Print job ID to stdout for scripting
            sys.stdout.write(f"{result.design_job_id}\n")
        else:
            console.print(f"[red]✘[/red] Failed to submit [bold]{result.pool_name}[/bold]: {result.error}")

    results = bulk_submit(
        submissions=submissions,
        scheduler_key=resolved_scheduler_key,
        round_id=proj_round.id,
        # Resuming a failed job requires looking up the existing pool of the same name
        return_existing=return_existing or resume_failed,
        resume_failed=resume_failed,
        callback=report,
    )
    errors = [f"Pool '{result.pool_name}': {result.error}" for result in results if not result.success]

    if errors:
        console.print(f"\n[red][bold]✘[/bold] {len(errors)}/{len(submissions)} workflow(s) failed to submit[/red]")
        sys.exit(1)
    else:
        console.print(f"\n[green][bold]✔[/bold] All {len(submissions)} workflow(s) submitted successfully[/green]")
        console.print("Check status with: [bold]ovo workflow status <job_id_or_pool>[/bold]")
        console.print(f"List all jobs with: [bold]ovo workflow list --project {proj.id}[/bold]")


@app.command()
def status(
    job_or_pool: str = typer.Argument(help="Design job ID or pool ID"),
):
    """Check the status of a submitted design workflow job.

    Accepts either a design job ID or a pool ID. The command first tries to
    resolve the argument as a job ID, then as a pool ID.
    """
    from ovo import db
    from ovo.core.database.models import DesignJob, Pool
    from ovo.core.logic.design_logic import format_pool_status, get_log
    from ovo.core.logic.job_logic import update_job_status, format_job_duration

    # Try as job ID first
    design_job = _try_get_by_id(db, DesignJob, job_or_pool)
    if design_job:
        try:
            pool = db.get(Pool, design_job_id=design_job.id)
        except NoResultFound:
            raise OVOCliError(
                f"No pool associated with DesignJob {job_or_pool}. This indicates a database inconsistency — "
                f"every submitted job should have a pool."
            )
    else:
        # Try as pool ID
        pool = _try_get_by_id(db, Pool, job_or_pool)
        if not pool:
            raise OVOCliError(f"No design job or pool found with ID: {job_or_pool}")
        if not pool.design_job_id:
            raise OVOCliError(f"Pool '{pool.name}' has no associated design job")
        try:
            design_job = db.get(DesignJob, id=pool.design_job_id)
        except NoResultFound:
            raise OVOCliError(f"DesignJob {pool.design_job_id} referenced by pool '{pool.name}' not found")

    update_job_status(design_job)
    status_text = format_pool_status(design_job, pool.processed)

    # Display info
    console.print(f"  Job ID: [bold]{design_job.id}[/bold]")
    console.print(f"  Pool: [bold]{pool.name}[/bold] (id: {pool.id})")
    console.print(f"  Pool round: {pool.round_id}")
    console.print(f"  Workflow: {design_job.workflow.name}")
    console.print(f"  Scheduler: {design_job.scheduler_key} (job: {design_job.job_id})")
    started = (
        naturaltime(design_job.job_started_date_utc, when=datetime.now(timezone.utc).replace(tzinfo=None))
        if design_job.job_started_date_utc
        else "-"
    )
    console.print(f"  Started: {started}")
    console.print(f"  Duration: {format_job_duration(design_job)}")
    console.print(f"  Status: [bold]{status_text}[/bold]")

    log_text = get_log(design_job, tail=5)
    if log_text:
        console.print("\n  [dim]Log (last 5 lines):[/dim]")
        for line in log_text.splitlines():
            console.print(f"    {line}")

    console.print(f"\n  View tasks with: [bold]ovo workflow tasks {design_job.id}[/bold]")

    if design_job.job_result is None:
        sys.exit(3)
    elif design_job.job_result is False:
        sys.exit(4)
    elif not pool.processed:
        console.print(f"\n  Process results with: [bold]ovo workflow process {design_job.id}[/bold]")


@app.command()
def process(
    job_ids: list[str] = typer.Argument(help="Design job ID(s) to process results for"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for job to finish before processing"),
):
    """Process results of completed design workflow job(s).

    Downloads workflow results, creates Design and DescriptorValue records
    in the database, and marks the pool as processed.

    Accepts multiple job IDs to process in sequence.
    """
    from ovo import db
    from ovo.core.database.models import DesignJob, Design, Pool
    from ovo.core.logic.design_logic import process_results

    errors = []
    for job_id in job_ids:
        try:
            design_job = db.get(DesignJob, id=job_id)
        except NoResultFound:
            console.print(f"[red]✘[/red] DesignJob not found: {job_id}")
            errors.append(job_id)
            continue

        try:
            pool = db.get(Pool, design_job_id=design_job.id)
        except NoResultFound:
            console.print(f"[red]✘[/red] No pool associated with DesignJob {job_id} (database inconsistency)")
            errors.append(job_id)
            continue
        pool_label = pool.name

        if pool.processed:
            console.print(f"[dim]⏭[/dim]  {pool_label}: already processed, skipping")
            continue

        console.print(f"[bold]Processing {pool_label}...[/bold]")
        try:
            pool = process_results(design_job, wait=wait)
            num_designs = db.count(Design, pool_id=pool.id)
            console.print(f"[green]✔[/green] {pool_label}: processed, {num_designs} design(s) created")
        except ValueError as e:
            console.print(f"[red]✘[/red] {pool_label}: {e}")
            errors.append(job_id)

    if errors:
        console.print(f"\n[red][bold]✘[/bold] {len(errors)}/{len(job_ids)} job(s) failed to process[/red]")
        sys.exit(1)
    else:
        console.print(f"\n[green][bold]✔[/bold] All {len(job_ids)} job(s) processed successfully[/green]")


@app.command(name="list")
def list_jobs(
    project_name: str = typer.Option(None, "--project", help="Filter by project name or ID"),
    round_name: str = typer.Option(None, "--round", help="Filter by round name or ID"),
    pool_name: str = typer.Option(None, "--pool", help="Filter by pool name or ID"),
    author: str = typer.Option(None, "--author", help="Filter by author"),
    since: str = typer.Option(
        None, "--since", help="Show jobs started within this duration (e.g. '1h', '2d', '1d 5h 30m')"
    ),
    in_progress: bool = typer.Option(False, "--in-progress", help="Show only in-progress jobs"),
    done: bool = typer.Option(False, "--done", help="Show only done (completed and processed) jobs"),
    failed: bool = typer.Option(False, "--failed", help="Show only failed jobs"),
    update: bool = typer.Option(True, "--update/--no-update", help="Update job statuses before listing"),
):
    """List submitted design workflow jobs.

    At least one of --project, --round, or --pool must be provided.
    The --in-progress, --done and --failed flags can be combined, listing the jobs in any of those states.
    """
    from ovo import db
    from ovo.core.database.models import Pool, Round
    from ovo.core.logic.design_logic import (
        DONE_STATUS,
        FAILED_STATUS,
        READY_STATUS,
        count_designs_by_pool,
        format_pool_status,
        get_pool_jobs,
        update_job_statuses,
    )
    from ovo.core.logic.job_logic import format_job_duration
    from ovo.core.utils.formatting import parse_duration

    if not project_name and not round_name and not pool_name and not in_progress and not since:
        raise OVOCliError("At least one of --project, --round, --pool, --in-progress, or --since must be provided")

    # The job results the status flags select, combined with OR: --done --failed lists both
    selected_job_results = {
        job_result for job_result, selected in ((None, in_progress), (True, done), (False, failed)) if selected
    }

    # Resolve project name or ID
    project_id = None
    round_ids = None
    if project_name:
        project = resolve_project(project_name)
        project_id = project.id

    if round_name:
        round_ids = resolve_round_ids(round_name, project_id)

    # Resolve pool filter
    pool_filters = {}
    if pool_name:
        pool = _resolve_by_id(db, Pool, pool_name, "Pool")
        if pool:
            pool_filters["id"] = pool.id
        else:
            pool_filters["name"] = pool_name
    if author:
        pool_filters["author"] = author

    # The --since option is resolved to a filter on the jobs, the status flags are applied below
    job_filters = {}
    if since:
        try:
            seconds = parse_duration(since)
        except ValueError as e:
            raise OVOCliError(f"Invalid duration: {e}. Use combinations of d, h, m, s (e.g. '1d 5h 30m')")
        started_since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=seconds)
        job_filters["job_started_date_utc__gte"] = started_since

    jobs, pools_by_job_id = get_pool_jobs(
        project_id=project_id, round_ids=round_ids, job_filters=job_filters, **pool_filters
    )

    if update and (in_progress_jobs := [job for job in jobs if job.job_result is None]):
        # Updated before filtering on the status below, so a job that has finished since it was last
        # listed is reported as done or failed rather than as still in progress
        with console.status("Updating job statuses...") as spinner:
            num_updated = itertools.count(1)
            update_job_statuses(
                in_progress_jobs,
                callback=lambda job: spinner.update(
                    f"Updating job statuses... {next(num_updated)}/{len(in_progress_jobs)}"
                ),
            )

    # Filtered here rather than in the query above, so the statuses just updated are the ones filtered on
    if selected_job_results:
        jobs = [job for job in jobs if job.job_result in selected_job_results]

    if not jobs:
        console.print("No jobs found")
        return

    pools = [pools_by_job_id[job.id] for job in jobs]
    accepted_by_pool, total_by_pool = count_designs_by_pool([pool.id for pool in pools])

    # Look up round names
    round_ids = list({p.round_id for p in pools if p.round_id})
    rounds = db.select(Round, id__in=round_ids) if round_ids else []
    rounds_by_id = {r.id: r for r in rounds}

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Job ID", no_wrap=True)
    table.add_column("Author", no_wrap=True)
    table.add_column("Round", no_wrap=True)
    table.add_column("Pool", no_wrap=True)
    table.add_column("Workflow")
    table.add_column("Status")
    table.add_column("Duration")
    table.add_column("Designs")
    table.add_column("Started")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for job in jobs:
        pool = pools_by_job_id[job.id]
        round_obj = rounds_by_id.get(pool.round_id)
        status = format_pool_status(job, pool.processed, update_status=update) or "-"
        if "⏳" in status:
            status = f"[yellow]{status}[/yellow]"
        elif status == FAILED_STATUS:
            status = f"[red]{status}[/red]"
        elif status in (READY_STATUS, DONE_STATUS):
            status = f"[green]{status}[/green]"
        designs = f"{accepted_by_pool.get(pool.id, 0)}/{total_by_pool.get(pool.id, 0)}" if pool.processed else "-"
        table.add_row(
            job.id,
            pool.author or "-",
            round_obj.name if round_obj else (pool.round_id or "-"),
            pool.name,
            job.workflow.name,
            status,
            format_job_duration(job) or "-",
            designs,
            naturaltime(job.job_started_date_utc, when=now) if job.job_started_date_utc else "-",
        )

    # Use a wide console for table output to avoid column truncation in non-TTY environments (e.g. tests, pipes)
    table_console = Console(stderr=True, highlight=False, width=max(console.width, 200))
    table_console.print(table)


@app.command()
def tasks(
    job_id: str = typer.Argument(help="Design job ID"),
):
    """List tasks of a design workflow job."""
    import pandas as pd

    from ovo import db
    from ovo.core.database.models import DesignJob
    from ovo.core.logic.design_logic import get_tasks

    try:
        design_job = db.get(DesignJob, id=job_id)
    except NoResultFound:
        raise OVOCliError(f"DesignJob not found: {job_id}")

    df = get_tasks(design_job)
    if df is None or df.empty:
        console.print("[dim]No tasks available[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    for col in df.columns:
        table.add_column(str(col), no_wrap=(col == "task_id"))

    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            val = "-" if pd.isna(row[col]) else str(row[col])
            if col == "status":
                if val == "COMPLETED":
                    val = f"[green]{val}[/green]"
                elif val == "FAILED":
                    val = f"[red]{val}[/red]"
                elif val in ("RUNNING", "SUBMITTED"):
                    val = f"[yellow]{val}[/yellow]"
            values.append(val)
        table.add_row(*values)

    console.print(table)
    console.print(f"\nView task log with: [bold]ovo workflow log {job_id} --task <task_id>[/bold]")


@app.command()
def log(
    job_id: str = typer.Argument(help="Design job ID"),
    task_id: str = typer.Option(None, "--task", help="Task ID within the job"),
    tail: int = typer.Option(None, "--tail", "-n", help="Show only the last N lines"),
):
    """View the execution log of a design workflow job."""
    from ovo import db
    from ovo.core.database.models import DesignJob
    from ovo.core.logic.design_logic import get_log

    try:
        design_job = db.get(DesignJob, id=job_id)
    except NoResultFound:
        raise OVOCliError(f"DesignJob not found: {job_id}")

    log_text = get_log(design_job, task_id=task_id, tail=tail)
    if log_text:
        sys.stdout.write(log_text)
        if not log_text.endswith("\n"):
            sys.stdout.write("\n")
    else:
        console.print("[dim]No log available[/dim]")


if __name__ == "__main__":
    app()
