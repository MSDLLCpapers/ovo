nextflow.enable.dsl = 2

process JupyterLab {
    conda { params.env ? params.getSharedEnv("ovo.${params.env}", workflow.profile) : null }
    container (params.env ? "${ workflow.containerEngine in ['singularity', 'apptainer']
        ? params.ovo_container_dir + '/ovo-' + params.env
        : params.docker_repository + 'ovo-' + params.env }" : null)

    label "jupyter"
    cpus { params.cpus }
    memory { params.memory }
    queue { params.queue }
    clusterOptions { params.cluster_options }

    input:
      path dirs
      val ip
      val port
      val run_parameters
    script:
    """
    # Make sure python is available
    which python3
    PYTHON_BIN=\$(which python3)

    # Check if jupyter-lab is available in this environment, otherwise try to install it via pip
    if [ ! -f "\${PYTHON_BIN/python3/jupyter-lab}" ]; then
        # Make sure pip is available together with python
        if [ ! -f "\${PYTHON_BIN/python3/pip}" ]; then
            echo "This environment does not have pip installed next to python"
            echo \$PYTHON_BIN
            exit 2
        fi

        echo "Jupyter Lab not available in this environment, attempting to install via pip"
        pip install jupyterlab jupyterlab-lsp python-lsp-server
    fi

    echo "JUPYTER_HOSTNAME: \$(hostname -i 2>/dev/null || hostname)" >&2

    # Create symlink to root directory to enable LSP access to all files (as long as they are mounted in the container)
    ln -s / .lsp_symlink

    cat > README.md << EOF
# Hello from ${params.env || 'ovo'} environment!

This Jupyter Lab instance is running inside a Nextflow pipeline process.

Current work dir: \$(pwd)

EOF

    if [[ "${workflow.containerEngine in ['singularity', 'apptainer'] && !params.no_unix_sockets}" == "true" ]]; then
        mkdir -p "${params.socket_dir}"
        socket_file="${params.socket_dir}/\$(date +%Y%m%d-%H%M%S)"
        if [[ -f "\$socket_file" ]]; then
            socket_file="\${socket_file}-\$RANDOM"
        fi
        network_args="--sock \$socket_file"
        echo "JUPYTER_SOCKET: \$socket_file" >&2
    else
        network_args="--port ${port} ${workflow.containerEngine ? "--port-retries 0" : ""}"
    fi

    # Run Jupyter Lab
    jupyter-lab \
      --ip ${ip} \
      \$network_args \
      --allow-root \
      --ContentsManager.allow_hidden=True \
      --no-browser \
      ${run_parameters}
    """
}

// static data files are in nextflow.config
workflow {

    [
        'dirs',
    ].each { param ->
        params[param] = null
        if (!params[param]) {
            throw new IllegalArgumentException("Argument --${param} is required!")
        }
    }

    def dirs = params.dirs
        .split(',')
        .collect { it.trim() }
        .findAll { it } // removes empty strings
        .collect { file(it) }

    JupyterLab(
        Channel.from(dirs).collect(),
        params.ip,
        params.port,
        params.run_parameters
    )
}

