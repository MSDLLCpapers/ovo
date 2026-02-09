import sys
import time
import traceback

from rich.console import Console
import requests
import os
import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn, TimeRemainingColumn
import shutil
import tarfile


console = Console(stderr=True, highlight=False)


class OVOCliError(Exception):
    pass


class OVONotInitializedError(OVOCliError):
    pass


def calculate_file_hash(filename, hash_algorithm="sha256"):
    hash_func = hashlib.new(hash_algorithm)
    with open(filename, "rb") as f:
        while chunk := f.read(8192):  # Read the file in chunks
            hash_func.update(chunk)
    return hash_func.hexdigest()


def download_file(url, file_path, file_hash, progress, task):
    progress.console.print(f"Downloading [gray]{url}[/gray] to [gray]{file_path}[/gray]")
    filename = os.path.basename(file_path)

    if os.path.exists(file_path):
        if os.path.isdir(file_path) or calculate_file_hash(file_path) == file_hash:
            progress.console.print(f"[green]Skipping {filename}, file already exists.[/green]")
            progress.update(task, advance=1)
            return
        progress.console.print(f"[yellow]File {filename} exists but hash mismatch. Redownloading...[/yellow]")

    unpack_path = None
    if url.endswith(".tar") and not filename.endswith(".tar"):
        # treat file_path as directory
        assert "." not in filename, f"Filename should be a directory or end with .tar: {filename}"
        unpack_path = file_path
        file_path = file_path + ".tmp"

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))  # Get file size from headers
    with open(file_path, "wb") as file:
        progress.update(task, total=total_size)
        for data in response.iter_content(chunk_size=1024):  # Download in chunks
            file.write(data)
            progress.update(task, advance=len(data))

    # Verify the hash of the downloaded file
    downloaded_hash = calculate_file_hash(file_path)
    if downloaded_hash == file_hash:
        console.print(f"[green]Downloaded {filename} successfully and hash matches![/green]")
    else:
        raise ValueError(
            f"[red]Hash mismatch for {filename}! Expected: {file_hash}, Got: {downloaded_hash} in:[/red] {file_path}"
        )

    if unpack_path is not None:
        # unpack file_path into unpack_path
        tmp_path = unpack_path + "_temp"
        os.makedirs(tmp_path, exist_ok=True)
        with tarfile.open(file_path, "r:*") as tar_ref:
            tar_ref.extractall(tmp_path)
        # move to final path only when successful
        shutil.move(tmp_path, unpack_path)


def download_files(destination_dir: str, file_list: list[tuple[str, str, str]]):
    """Download files in parallel using ThreadPoolExecutor."""

    try:
        # Create progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
        ) as progress:
            tasks = []

            # Initialize download tasks
            for url, file_name, file_hash in file_list:
                file_path = os.path.join(destination_dir, file_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                task = progress.add_task(f"Downloading {file_name}", total=1)  # total is set later
                tasks.append((url, file_path, file_hash, progress, task))

            # Use ThreadPoolExecutor to download files concurrently
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for url, file_path, file_hash, progress, task in tasks:
                    futures.append(executor.submit(download_file, url, file_path, file_hash, progress, task))

                # Wait for all threads to finish
                for future in futures:
                    future.result()
    except Exception as e:
        time.sleep(3)  # short delay to wait for progress bar to flush
        traceback.print_exc()
        console.print(f"\n[red]Error during download:[/red] {e}\n")
        console.print("\nPlease try again, or download the files manually:\n")
        for url, file_path, file_hash, progress, task in tasks:
            console.print(f'wget {url} -O "{file_path}"')
        console.print("")
        sys.exit(2)


def run_nextflow(args: list[str]):
    if shutil.which("nextflow") is None:
        raise OVOCliError("nextflow binary should be available on PATH or in current environment")

    process = subprocess.run(["nextflow"] + args, capture_output=True, text=True)

    # Check for non-zero return code
    if process.returncode != 0:
        if (
            "Nextflow needs a Java virtual machine to run" in process.stderr
            or "java.lang.UnsupportedClassVersionError" in process.stderr
        ):
            raise OVOCliError(
                "Nextflow requires recent Java to run, please install Java 17+ (Java 21-24 recommended). Common ways to install: conda install -c conda-forge openjdk / apt install openjdk-21-jdk / brew install openjdk@21. When working on HPC, activate a recent Java module (module avail java; module load java/version)"
            )
        else:
            # Raise a custom error if the problem is something else
            error = process.stderr.strip() or process.stdout.strip()
            raise OVOCliError(f"Error running Nextflow: {error}")

    return process.stdout


def init_nextflow():
    return run_nextflow(["-h"])


def print_ovo_logo(padding="    "):
    from ovo import __version__

    version = f"Version [green]{__version__}[/green]"
    console.print(f"""
{padding}  ▄▀▀█▄  ▄▖   ▄▄  ▄▀▀█▄   
{padding} █    █▄ █▌   ██ █▄▀▄▀█▄  
{padding}█     ██  █▌ ██ █     ██  
{padding} ▀▄▄▄█▀    ███   ▀▄▄▄█▀   
{padding}{version.rjust(39)}
""")
