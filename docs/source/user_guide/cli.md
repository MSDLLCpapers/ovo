# OVO Command Line Interface

Everything that OVO can do from the web app can also be done from the terminal using the `ovo` command,
which is installed together with the `ovo` Python package. The CLI is useful for setting up OVO,
for scripted and reproducible design campaigns, and for running individual pipelines
without touching the OVO database.

```bash
ovo --help        # list all command groups
ovo workflow -h   # help of a command group
ovo workflow submit -h
```

The main CLI commands are organized into the following command groups:

| Command          | Purpose                                                                                     |
|------------------|---------------------------------------------------------------------------------------------|
| `ovo init`       | Set up the OVO home directory, reference files and execution environments                    |
| `ovo app`        | Run the Streamlit web application                                                           |
| `ovo workflow`   | Submit and manage design workflows – the same objects the web app creates (pools, designs)   |
| `ovo scheduler`  | Run individual Nextflow pipelines and manage their jobs, without creating database records   |

The distinction between `ovo workflow` and `ovo scheduler` is important:

- **`ovo workflow`** submits a *workflow*. Results are registered in the OVO database
  as a `Pool` with `Design` and descriptor records, and become visible in the web app.
  This is the CLI equivalent of the Bulk Submission page.
- **`ovo scheduler`** submits a *pipeline* directly to a [scheduler](schedulers.md).
  Output files are written to the job output directory, nothing is stored in the database.
  This is the low-level interface used for testing pipelines and for ad-hoc runs.

## Web application: `ovo app`


## Design workflows: `ovo workflow`

A design workflow submission is described by a **YAML config file** – the same format the
Bulk Submission page of the web app uses and exports. The typical CLI cycle is:
generate a template, edit it, submit it, watch the jobs, and process the results.

### 1. Pick a workflow type

```bash
ovo workflow names
```

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Available workflow types                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ BindCraft binder design                  │
│ RFdiffusion scaffold design              │
│ RFdiffusion binder design                │
│ RFdiffusion cyclic peptide binder design │
│ BindCraft cyclic peptide binder design   │
└──────────────────────────────────────────┘
```

The available types depend on the installed [plugins](../plugins/index.md).

### 2. Generate a config template

```bash
ovo workflow template --name "RFdiffusion binder design" -o my_binders.yaml
```

The template contains every parameter of the workflow type with its default value,
including the acceptance thresholds. Without `-o` it is printed to stdout.

### 3. Edit the config

Only the parameters you want to change need to be kept – the rest fall back to the defaults.
Each submission needs a `pool_name` for the pool it will create:

```yaml
submissions:
  - pool_name: My binders
    pool_description: First attempt against 6VES
    workflow:
      name: RFdiffusion binder design
      rfdiffusion_params:
        input_pdb_paths:
          - inputs/6VES.pdb    # relative to the config file location
        contigs:
          - A1-21/0 4-6
        model_weights: Complex_base
        num_designs: 10
      protein_mpnn_params:
        num_sequences: 5
        sampling_temp: 0.1
      refolding_params:
        primary_test: af2_model_1_multimer_tt_3rec
      target_chain: A
```

Input file paths are resolved relative to the directory of the config file and uploaded
to OVO storage before submission, so a config file plus its input files is a self-contained,
shareable description of a submission.

Any parameter can be turned into a **grid** to submit one pool per value combination.
The submission below expands into four workflows (2 × 2), each with its own pool named
`My binders Combo 1` … `Combo 4`:

```yaml
submissions:
  - pool_name: My binders
    workflow:
      name: RFdiffusion binder design
      rfdiffusion_params:
        input_pdb_paths:
          - inputs/6VES.pdb
        contigs:
          - A1-21/0 4-6
        timesteps:
          grid: [20, 50]
      protein_mpnn_params:
        num_sequences:
          grid: [2, 5]
```

A single config can hold multiple `submissions` entries, mixing workflow types.

### 4. Submit

```bash
ovo workflow submit my_binders.yaml --project "Binder campaign" --round "Round 1"
```

| Option              | Description                                                                              |
|---------------------|------------------------------------------------------------------------------------------|
| `--project`         | Project name or ID, created after confirmation if it does not exist (personal project by default) |
| `--round`           | Round name or ID, created after confirmation if it does not exist (last round by default) |
| `--scheduler`       | Scheduler key to submit to, see `ovo scheduler list` (`default_scheduler` by default)     |
| `--resume-failed`   | Resume a failed job for an existing pool with the same name and parameters instead of failing |
| `--return-existing` | Return an existing pool only when the same name and parameters were already submitted      |
| `--yes`, `-y`       | Skip all confirmation prompts, for non-interactive use                                    |

The whole batch is validated before anything is uploaded or submitted, so a config with a
mistake in the last entry fails without submitting the first ones. After a summary and
confirmation, each workflow is submitted and its `DesignJob` ID is printed to stdout.

### 5. Monitor the jobs

```bash
ovo workflow status <job_id>          # status of a single job (accepts a pool ID too)
ovo workflow tasks <job_id>           # individual grid tasks of the job and their status
ovo workflow log <job_id>             # workflow execution log
ovo workflow log <job_id> --task <task_id> --tail 50
```

To see many jobs at once, use `ovo workflow list` with at least one of
`--project`, `--round`, `--pool`, `--in-progress` or `--since`:

```bash
ovo workflow list --project "Binder campaign"
ovo workflow list --round "Round 1" --in-progress
ovo workflow list --since "1d 5h" --done --failed
ovo workflow list --project "Binder campaign" --author jdoe --no-update
```

Job statuses are refreshed from the scheduler before listing; use `--no-update` for a fast,
read-only listing. Projects, rounds and pools can be referenced either by name or by ID.

### 6. Process the results

A finished job still needs its results *processed*: output files are copied to OVO storage
and `Design` and descriptor records are created in the database
(see [Schedulers](schedulers.md) for details of this step).

```bash
ovo workflow process <job_id> [<job_id> ...]   # waits for the job to finish
ovo workflow process <job_id> --no-wait        # fail instead of waiting if still running
```

Already processed pools are skipped, so the command is safe to re-run.
Once processed, the designs are visible in the web app and counted in the
"Designs" column of `ovo workflow list`.

## Pipelines: `ovo scheduler`

These commands drive the [scheduler](schedulers.md) layer directly: they run a single Nextflow
pipeline with the parameters you give them and write the results to the job output directory,
without creating any database records. This makes them useful for verifying an installation,
developing pipelines, and one-off runs whose results you only want as files.
The typical cycle is: pick a scheduler and a pipeline, run it, and collect the output.

### 1. Pick a scheduler

```bash
ovo scheduler list
```

The command lists the keys of all schedulers from the OVO config, their user-friendly names and
their submission arguments (Nextflow profile, config file, HealthOmics role, …), with the
`default_scheduler` marked. Every command of this group accepts `--scheduler <key>` to use a
scheduler other than the default one.

### 2. Pick a pipeline

Pipeline names are the pipeline directories shipped with OVO and its plugins (plugin pipelines are
prefixed with the module name, e.g. `ovo_mytool.some-tool`). Run `submit` or `run` without a pipeline name
to list them all:

```bash
ovo scheduler submit
```

Each pipeline declares its parameters in a `nextflow_schema.json` file. Adding `--help` after a
pipeline name renders that schema as help text – required and optional parameters with their
descriptions and defaults:

```bash
ovo scheduler run rfdiffusion-end-to-end --help
```

The same help is printed whenever a submission is rejected, so a missing or invalid parameter
shows the list of valid ones together with the error.

### 3. Run the pipeline

`run` executes the pipeline in the foreground, streaming the Nextflow output to the terminal,
and copies the results into the given output directory:

```bash
ovo scheduler run rfdiffusion-end-to-end \
  ./example \
  --design_type scaffold \
  --rfdiffusion_input_pdb 5ELI.pdb \
  --rfdiffusion_num_designs 1 \
  --rfdiffusion_contig A111-114/10/A117-119 \
  --refolding_tests af2_model_1_ptm_ft_3rec
```

Pipeline parameters follow the positional arguments as `--param value` pairs and are validated
against the pipeline schema before submission. A parameter without a value is a boolean flag,
values containing spaces need quoting (`--run_parameters "diffuser.T=20"`), and relative input
paths are resolved against the current directory.

| Option          | Description                                                                        |
|-----------------|------------------------------------------------------------------------------------|
| `--scheduler`   | Scheduler key to run on, see `ovo scheduler list` (`default_scheduler` by default)   |
| `run OUTPUT_DIR` | `run` takes the custom output directory as its second positional argument and always waits | 
| `submit --sync`  | Wait for completion instead of running in the background                         |
| `submit --output`| Custom output directory; requires `--sync`                                   |
| `--link`         | Symlink output files into the selected output directory instead of copying them |
| `--help`, `-h`  | Show the parameters of the given pipeline                                           |

### 4. Manage background jobs

`submit` without `--sync` starts the job in the background and prints its scheduler job ID.
Use that ID directly with `status`, `download`, or `cancel`; there is no need to capture it in
an intermediate variable. The results stay in the scheduler workdir – for the Nextflow scheduler in
`<workdir>/execdir/<job_id>/output/` – until you download them.

```bash
ovo scheduler submit proteinqc --input_pdb 5ELI.pdb --tools all --chains A
ovo scheduler status <job_id>           # state, output directory, and the log if it failed
ovo scheduler download <job_id> ./results
ovo scheduler cancel <job_id>           # terminate a running job
```

`status` reports the state through its exit code as well (`3` while running, `4` on failure),
so it can be polled from a script. `download` checks the status first and refuses to download
from a job that is unfinished or failed.

### Interactive JupyterLab sessions

`ovo scheduler jupyter` submits a JupyterLab server as a job, giving you an interactive session
inside one of the pipeline environments – for example on a GPU node of an HPC cluster:

```bash
ovo scheduler jupyter ./my_analysis_dir --env rfdiffusion --port 8888
```

The positional arguments are the local directories to mount, `--env` selects the Conda environment
or container (the current environment if omitted). 

`--queue` / `--cluster-options` are passed
on to the executor to request a specific partition or GPU. The command waits for the server to
start and prints its URL (or socket file and token when running in a container) together with the
`ssh -NTL` command for port forwarding if the node is not directly reachable. 

The session keeps
occupying the node until you stop it with `ovo scheduler cancel <job_id>` or from the JupyterLab
*Server → Shutdown* menu.

### Queue workers

When a scheduler is configured with a `queue` submission argument, its jobs are queued instead of
started immediately, and executed by worker processes. This limits how many jobs run concurrently
on one machine and allows pinning workers to specific GPUs:

```bash
ovo scheduler worker -n 2                                # start the queue server and 2 workers
CUDA_VISIBLE_DEVICES=1 ovo scheduler worker --connect     # add a worker to a running queue
```


## Exit codes

The commands that report job state use distinct exit codes, so shell scripts can react to them:

| Code | Meaning                                                                    |
|------|----------------------------------------------------------------------------|
| `0`  | Success                                                                    |
| `1`  | One or more workflows failed to submit or process (`ovo workflow submit`, `process`) |
| `3`  | Job is still running (`ovo workflow status`, `ovo scheduler status`)        |
| `4`  | Job failed (`ovo workflow status`, `ovo scheduler status`, `ovo scheduler run`) |

```
