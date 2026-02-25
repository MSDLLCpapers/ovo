import glob
import os
import time

import jsonschema
import typer
import sys
from ovo.cli.common import console, OVOCliError
from ovo.core.scheduler import NextflowScheduler
from ovo.core.utils.param_validation import validate_params
from ovo.core.scheduler.simple_queue_mixin import SimpleQueueMixin
import re

app = typer.Typer(pretty_exceptions_enable=False, help="Schedule and monitor OVO jobs")


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    pipeline_name: str = typer.Argument(default=None, help="Pipeline to submit"),
    output: str = typer.Argument(default=None, help="Output directory"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
    link: bool = typer.Option(default=None, help="Do not copy output files, create a symlink instead"),
    ctx: typer.Context = typer.Option(None),
    help: bool | None = typer.Option(
        None,
        "--help",
        "-h",
        help="Show pipeline-specific help",
    ),
):
    """Run OVO job synchronously and save output to directory (shorhand for submit --sync)"""
    from ovo import config, get_scheduler

    resolved_scheduler_key = scheduler_key or config.default_scheduler
    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)
    usage = "Usage: ovo scheduler run PIPELINE_NAME OUTPUT_DIR [OPTIONS] [PARAMS]"
    if help is True:
        if pipeline_name:
            schema = scheduler.get_param_schema(pipeline_name=pipeline_name)
            console.print(format_help(schema))
            return
        else:
            console.print(usage)
            return
    if pipeline_name and (not output or output.startswith("--")):
        schema = scheduler.get_param_schema(pipeline_name=pipeline_name)
        error = f"Missing OUTPUT. {usage}"
        raise OVOCliError(format_help(schema) + f"\n\n[red][bold]✘[/bold] {error}[/red]")
    return submit(
        pipeline_name=pipeline_name,
        output=output,
        link=link,
        scheduler_key=scheduler_key,
        sync=True,
        ctx=ctx,
    )


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def submit(
    pipeline_name: str = typer.Argument(default=None, help="Pipeline to submit"),
    output: str = typer.Option(None, "--output", help="Custom output directory (requires --sync)"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
    sync: bool = typer.Option(default=None, help="Run nextflow process synchronously, waiting for completion"),
    link: bool = typer.Option(
        default=None, help="Do not copy output files, create a symlink instead (when --output is used)"
    ),
    ctx: typer.Context = typer.Option(None),
    help: bool | None = typer.Option(
        None,
        "--help",
        "-h",
        help="Show pipeline-specific help",
    ),
):
    """Submit a job through OVO scheduler"""
    from ovo import config, get_scheduler, storage
    from ovo.core.utils.formatting import parse_args

    resolved_scheduler_key = scheduler_key or config.default_scheduler
    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)

    usage = "Usage: ovo scheduler submit PIPELINE_NAME [OPTIONS] [PARAMS]"
    if help is True:
        if pipeline_name:
            schema = scheduler.get_param_schema(pipeline_name=pipeline_name)
            console.print(format_help(schema))
            return
        else:
            console.print(usage)
            return

    if not pipeline_name:
        available_paths = scheduler.get_pipeline_names()
        sep = "\n "
        raise OVOCliError(f"Pipeline name is required. Available pipelines: \n{sep}{sep.join(available_paths)}")

    extra_args = ctx.args if hasattr(ctx, "args") else []
    params = parse_args(extra_args)

    schema = scheduler.get_param_schema(pipeline_name=pipeline_name)

    if not params:
        error = "Provide pipeline parameters using --my_param value --other_param value"
        raise OVOCliError(format_help(schema) + f"\n\n[red][bold]✘[/bold] {error}[/red]")

    if schema:
        try:
            validate_params(params, schema)
        except jsonschema.ValidationError as e:
            error = f"Input parameters are invalid: {e.message}"
            if e.path:
                error += f" ({'.'.join(map(str, e.path))})"
            raise OVOCliError(format_help(schema) + f"\n\n[red][bold]✘[/bold] {error}[/red]")

    if output:
        if not sync:
            raise OVOCliError("Output directory can only be set with --sync option")
        if os.path.exists(output):
            raise OVOCliError(f"Output directory already exists: '{output}'")

    console.print(f"Submitting [bold]{pipeline_name}[/bold] with [bold]{resolved_scheduler_key}[/bold] scheduler:")
    max_key_length = max(len(key) for key in params.keys())
    for key, value in params.items():
        console.print(f" {key.rjust(max_key_length)}: [green]{value}[/green]")
    console.print("")

    submitted = scheduler.submit(
        pipeline_name=pipeline_name,
        params=params,
        submission_args=dict(sync=sync, resolve_relative_paths=True),
    )
    if sync:
        process, job_id = submitted
        console.print("")
        if process.returncode != 0:
            console.print(f"[bold][red]✘[/red] Pipeline failed with exit code {process.returncode}[/bold]")
            sys.exit(4)
        console.print("[bold][green]✔[/green] Pipeline finished successfully[/bold]")
        scheduler_output_dir = scheduler.get_output_dir(job_id=job_id)
        if output:
            console.print(f"Job output directory: {scheduler_output_dir}")
            console.print(f"Saving output...")
            storage.sync_directory(scheduler_output_dir, output, link=link)
            console.print(f"[green]✔[/green] Output saved to: {os.path.abspath(output)}")
        else:
            console.print(f"[green]✔[/green] Output saved to: {scheduler_output_dir}")
    else:
        job_id = submitted
        console.print("")
        console.print(f"Running in background, use --sync to run synchronously and wait for completion.")
        console.print(f"[green]✔[/green] Job submitted: [bold]{job_id}[/bold]")
        scheduler_arg = f"--scheduler {scheduler_key} " if scheduler_key else ""
        console.print(f"[green]✔[/green] Output directory: [bold]{scheduler.get_output_dir(job_id)}[/bold]")
        console.print(f"[green]✔[/green] Check status with: [bold]ovo scheduler status {scheduler_arg}{job_id}[/bold]")
    return job_id


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def jupyter(
    dirs: list[str] = typer.Argument(help="Directory to run from. Will be mounted inside the container."),
    env: str = typer.Option(
        default=None,
        help="Name of conda environment or container to run in, for example rfdiffusion. Runs in current environment if not specified.",
    ),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
    ip: str = typer.Option(default="0.0.0.0", help="Host to bind Jupyter server to"),
    port: int = typer.Option(default=8888, help="Port to bind Jupyter server to"),
    queue: str = typer.Option(
        default=None,
        help="Nextflow queue to use when submitting job (default queue is configured in the nextflow config of your scheduler)",
    ),
    cluster_options: str = typer.Option(default=None, help="Nextflow clusterOptions to use when submitting job"),
    run_parameters: str = typer.Option(default="", help="Additional commandline parameters to pass to Jupyter server"),
    timeout: int = typer.Option(default=3600, help="Timeout in seconds to wait for Jupyter server to start"),
    socket_dir: str = typer.Option(
        default=None,
        help="Directory where to create Jupyter socket file (if applicable). If not specified, defaults to /tmp/ovo-USERNAME",
    ),
):
    """Run JupyterLab server in a selected environment as a job using OVO scheduler"""
    from ovo import config, get_scheduler

    for i, d in enumerate(dirs):
        if d.startswith("-"):
            raise OVOCliError(f"Unexpected parameter {d}")
        if not os.path.exists(d):
            if i == 0:
                raise OVOCliError(f"Please pass a directory to run from, path does not exist: {d}")
            raise OVOCliError(
                f"Expected list of local directories to mount, got non-existent path: {d}. "
                f"If you wanted to specify an environment to run from, use --env option instead."
            )

    if not socket_dir:
        tmp_dir = os.environ.get("STMP") or "/tmp"
        socket_dir = os.path.join(tmp_dir, f"ovo-{os.environ.get('USER')}")
    os.makedirs(socket_dir, exist_ok=True)

    params = {
        "dirs": ",".join([os.path.abspath(d) for d in dirs]),
        "env": env,
        "ip": ip,
        "port": port,
    }
    if run_parameters:
        params["run_parameters"] = run_parameters
    if queue:
        params["queue"] = queue
    if cluster_options:
        params["cluster_options"] = cluster_options
    resolved_scheduler_key = scheduler_key or config.default_scheduler
    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)

    if not isinstance(scheduler, NextflowScheduler):
        raise NotImplementedError("Only NextflowScheduler currently supports Jupyter submission.")

    pipeline_name = "jupyterlab"
    console.print(
        f"Submitting [bold]{pipeline_name}[/bold] in [bold]{env or 'ovo'}[/bold] environment with [bold]{resolved_scheduler_key}[/bold] scheduler:"
    )
    max_key_length = max(len(key) for key in params.keys())
    for key, value in params.items():
        console.print(f" {key.rjust(max_key_length)}: [green]{value}[/green]")
    console.print("")

    # Additional params that should not be printed in the console
    params["socket_dir"] = os.path.abspath(socket_dir)

    job_id = scheduler.submit(
        pipeline_name=pipeline_name,
        params=params,
        submission_args=dict(sync=False, resolve_relative_paths=True),
    )
    # Wait for workdir
    workdir_prefix = None
    console.print("Waiting for Jupyter job to start...")
    for retry in range(timeout):
        time.sleep(1)
        if scheduler.get_result(job_id) is False:
            console.print(scheduler.get_log(job_id))
            console.print(f"[red][bold]✘[/bold] Jupyter job {job_id} failed[/red]")
            sys.exit(4)
        log = scheduler.get_log(job_id)
        # parse regex [5f/008512] Submitted process > JupyterLab
        if match := re.search(r"\[([^[]*)] Submitted process > JupyterLab", log or ""):
            workdir_prefix = match.group(1)
            break

    if not workdir_prefix:
        console.print(scheduler.get_log(job_id))
        console.print(
            f"[red][bold]✘[/bold] Failed to get Jupyter workdir for job {job_id}, please check job status[/red]"
        )
        sys.exit(4)

    workdir_glob = os.path.join(scheduler.workdir, f"work/{workdir_prefix}*")
    workdir = glob.glob(workdir_glob)
    if not workdir:
        console.print(f"[red][bold]✘[/bold] Failed to find Jupyter workdir: {workdir_glob}[/red]")
        sys.exit(4)
    workdir = workdir[0]

    console.print(f"Checking workdir {workdir} for Jupyter URL...")
    jupyter_url_lines = None
    hostname = None
    socket_file = None
    installing_jupyter = None
    log = None
    for retry in range(timeout):
        time.sleep(1)
        log_path = os.path.join(workdir, ".command.log")
        if scheduler.get_result(job_id) is False:
            # Job has failed, print log and exit
            if os.path.exists(log_path):
                with open(log_path) as f:
                    console.print(f.read())
            else:
                console.print(scheduler.get_log(job_id))
            console.print(f"[red][bold]✘[/bold] Jupyter job {job_id} failed[/red]")
            sys.exit(4)
        if not os.path.exists(log_path):
            # some executor jobs might create only a .command.err file before the job has finished
            err_path = os.path.join(workdir, ".command.err")
            if os.path.exists(err_path):
                # If .command.log doesn't exist but .command.err does, use it instead
                log_path = err_path
            else:
                # Log files not created yet, keep waiting
                continue
        with open(log_path) as f:
            log = f.read()
        if "Jupyter Lab not available" in log:
            if not installing_jupyter:
                console.print("Jupyter Lab not available in the environment, installing...")
                installing_jupyter = True
        jupyter_url_lines = [
            line
            for line in log.splitlines()
            if ("http://" in line or "https://" in line or "http+unix://" in line)
            and "token=" in line
            and "ServerApp" not in line
        ]
        if jupyter_url_lines:
            hostname_lines = [line for line in log.splitlines() if "JUPYTER_HOSTNAME:" in line]
            if hostname_lines:
                hostname = hostname_lines[-1].split("JUPYTER_HOSTNAME:")[-1].strip()
            socket_lines = [line for line in log.splitlines() if "JUPYTER_SOCKET:" in line]
            if socket_lines:
                socket_file = socket_lines[-1].split("JUPYTER_SOCKET:")[-1].strip()
            break

    if not jupyter_url_lines:
        console.print(log or scheduler.get_log(job_id))
        console.print(f"[red][bold]✘[/bold] Failed to get Jupyter URL for job {job_id}, please check job status[/red]")
        sys.exit(4)

    console.print(f"\n[green]✔[/green] Jupyter [bold]{env or 'ovo'}[/bold] environment is running at:")

    if socket_file:
        token = re.search(r"token=([^&\s]+)", str(jupyter_url_lines[0])).group(1)
        console.print(f"Socket file: {socket_file}")
        console.print(f"      Token: {token}")
    else:
        different_port = False
        for line in jupyter_url_lines:
            console.print(line)
            if str(port) not in line:
                different_port = True
        if different_port:
            console.print(
                f"\n[bold][red]Note![/red][/bold] JupyterLab is running on a different port! The requested port {port} was occupied.\n"
            )

    console.print("Tips:")
    console.print(" - Cmd/Ctrl + Double click the URL to open the link in your browser.")
    if hostname:
        remote = socket_file if socket_file else f"localhost:{port}"
        console.print(
            (
                "- Use SSH tunneling "
                if socket_file
                else f" - If the host is not directly accessible, use SSH tunneling "
            )
            + f"to forward your local port {port} to remote port or socket, for example:\n"
            f"   ssh -NTL {port}:{remote} {hostname}"
        )
    console.print(
        f" - Remember to stop the job when you're done using 'ovo scheduler cancel {job_id}'\n   or directly from JupyterLab using Server -> Shutdown"
    )


def format_help(schema):
    from ovo import config

    params_str = "Available schedulers:\n\n"
    for scheduler_key, scheduler_config in config.schedulers.items():
        params_str += (
            f" --scheduler {scheduler_key} ({scheduler_config.name}, args: {scheduler_config.submission_args})\n"
        )
    params_str += "\n"
    if schema:
        sep = "\n  "
        formatted_params = {
            key: f"--{key}: {value['description']}" + (f" (default {value['default']})" if value.get("default") else "")
            if value.get("description")
            else f"--{key}"
            for key, value in schema.get("properties", {}).items()
        }
        required_params = [formatted_params.get(key, f"--{key}") for key in schema.get("required", [])]
        if required_params:
            params_str += f"Required parameters:\n{sep}{sep.join(required_params)}\n\n"
        optional_params = [
            formatted_params[key]
            for key in schema.get("properties", {}).keys()
            if key not in schema.get("required", [])
        ]
        params_str += f"Optional parameters:\n{sep}{sep.join(optional_params) or 'None'}"
    return params_str.strip()


@app.command()
def status(
    job_id: str = typer.Argument(help="Job ID"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
):
    """Get job status"""
    from ovo import config, get_scheduler

    resolved_scheduler_key = scheduler_key or config.default_scheduler
    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)

    job_result = scheduler.get_result(job_id=job_id)
    if job_result is None:
        console.print(f"[bold]Job {job_id} is running[/bold]")
        sys.exit(3)
    elif job_result is False:
        console.print(f"[bold][red]✘[/red] Job {job_id} failed[/bold]")
        console.print(scheduler.get_log(job_id=job_id))
        sys.exit(4)
    else:
        console.print(f"[bold][green]✔[/green] Job {job_id} completed successfully[/bold]")
        console.print(f"Output directory: {scheduler.get_output_dir(job_id=job_id)}")


@app.command()
def cancel(
    job_id: str = typer.Argument(help="Job ID"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
):
    """Cancel job execution"""
    from ovo import config, get_scheduler

    resolved_scheduler_key = scheduler_key or config.default_scheduler
    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)

    console.print(f"Cancelling job [bold]{job_id}[/bold] with scheduler [bold]{resolved_scheduler_key}[/bold]")
    scheduler.cancel(job_id=job_id)
    console.print(f"[green]✔[/green] Job cancelled")


@app.command()
def download(
    job_id: str = typer.Argument(help="Job ID"),
    output: str = typer.Argument(help="Output directory"),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key"),
):
    """Download job output files into a directory"""
    from ovo import config, get_scheduler, storage

    resolved_scheduler_key = scheduler_key or config.default_scheduler

    status(job_id=job_id, scheduler_key=resolved_scheduler_key)

    scheduler = get_scheduler(scheduler_key=resolved_scheduler_key)
    scheduler_output_dir = scheduler.get_output_dir(job_id=job_id)

    console.print(f"Job output directory: {scheduler_output_dir}")
    console.print(f"Saving output to: [bold]{output}[/bold]")
    storage.sync_directory(scheduler_output_dir, output, link=True)
    console.print(f"Output saved to: {os.path.abspath(output)}")


@app.command()
def worker(
    num_workers: int = typer.Option(1, "-n", "--workers", help="Number of worker threads"),
    connect: bool = typer.Option(
        False,
        "--connect",
        help="Connect to existing queue server instead of starting a new one. Enables running workers with different ENV vars such as CUDA_VISIBLE_DEVICES.",
    ),
    scheduler_key: str = typer.Option(None, "--scheduler", help="Scheduler key to use"),
    host: str = typer.Option(None, "--host", help="Run server on custom host (override config)"),
    port: int = typer.Option(None, "--port", help="Run server on custom port (override config)"),
):
    """Start queue and worker server to process jobs of a scheduler specified with queue submission arg in OVO config"""
    from ovo import config, get_scheduler
    import threading

    resolved_scheduler_key = scheduler_key or config.default_scheduler

    scheduler: SimpleQueueMixin = get_scheduler(scheduler_key=resolved_scheduler_key)

    if connect:
        # Connect mode: use already running queue
        queue = scheduler.connect_to_queue(host=host, port=port)
    else:
        # Start server in the background
        queue, serve_forever = scheduler.create_queue_server(host=host, port=port)
        threading.Thread(target=serve_forever, daemon=True).start()

    # Start workers
    threads = []
    for i in range(num_workers):
        t = threading.Thread(target=scheduler.queue_worker, args=(queue, i + 1))
        t.start()
        threads.append(t)

    # Keep main thread alive if connecting, or join worker threads
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        for n in range(num_workers + 100):
            # Send shutdown signal to workers, up to 10 extra in case some were executed independently
            queue.put(None)
        # TODO this actually doesn't seem to work,
        #  workers exit immediately even if nextflow run is still in progress
        print("\nWaiting for workers to finish their task, use Ctrl+C again to force shutdown...")
        for t in threads:
            t.join()


if __name__ == "__main__":
    app()
