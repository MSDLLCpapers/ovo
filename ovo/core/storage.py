import shutil
import zipfile
import io
import pickle
from typing import List

from urllib.parse import urlparse
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor

import os
import tempfile
import weakref
from collections import OrderedDict
from ovo.core.aws import AWSSessionManager
from ovo.core.utils.formatting import get_hashed_path_for_bytes


class Storage:
    """Class for managing file storage in local filesystem or S3 bucket"""

    def __init__(
        self,
        storage_root: str,
        aws: AWSSessionManager | None,
        verbose: bool = False,
        num_copy_threads: int | None = None,
        memory_cache_limit_bytes=50 * 1024 * 1024,
        disk_cache_limit_bytes=200 * 1024 * 1024,
        memory_cache_limit_per_file_bytes=5 * 1024 * 1024,
    ):
        self.storage_root: str = storage_root
        self.aws: AWSSessionManager | None = aws
        self.verbose = verbose
        self.num_copy_threads = num_copy_threads
        # caching
        self.memory_cache_limit = memory_cache_limit_bytes
        self.disk_cache_limit = disk_cache_limit_bytes
        self.memory_cache_limit_per_file_bytes = memory_cache_limit_per_file_bytes
        self._cache_memory = OrderedDict()  # LRU cache for memory
        self._cache_disk = OrderedDict()  # LRU cache for disk
        self.memory_cache_size = 0
        self.disk_cache_size = 0
        self._temp_dir = tempfile.TemporaryDirectory()
        weakref.finalize(self, self._clear_temp_dir)

    def _clear_temp_dir(self):
        self._temp_dir.cleanup()

    def _cache_read(self, file_path):
        if file_path in self._cache_memory:
            self._cache_memory.move_to_end(file_path)  # Mark as recently used
            return self._cache_memory[file_path]
        if file_path in self._cache_disk:
            with open(self._cache_disk[file_path], "rb") as f:
                content = f.read()
            self._cache_memory[file_path] = content
            self.memory_cache_size += len(content)
            while self.memory_cache_size > self.memory_cache_limit and self._cache_memory:
                old_file, old_content = self._cache_memory.popitem(last=False)
                self.memory_cache_size -= len(old_content)
            return content
        return None

    def _cache_store(self, file_path, content: str | bytes):
        if len(content) <= self.memory_cache_limit_per_file_bytes:
            # Cache recent files in memory (unless they are too big)
            self._cache_memory[file_path] = content
            self.memory_cache_size += len(content)
            while self.memory_cache_size > self.memory_cache_limit and self._cache_memory:
                old_file, old_content = self._cache_memory.popitem(last=False)
                self.memory_cache_size -= len(old_content)
        scheme, netloc, relative_path = self.parse_path(file_path)
        if not scheme:
            # Do not use disk cache for files that are already local
            return
        assert relative_path in os.path.abspath(relative_path), (
            f"Invalid path {relative_path}"
        )  # make sure path doesn't contain '../'
        disk_file_path = os.path.join(self._temp_dir.name, relative_path)
        os.makedirs(os.path.dirname(disk_file_path), exist_ok=True)
        with open(disk_file_path, "wb") as f:
            f.write(content)
        self._cache_disk[file_path] = disk_file_path
        self.disk_cache_size += os.path.getsize(disk_file_path)
        while self.disk_cache_size > self.disk_cache_limit and self._cache_disk:
            old_file, old_disk_path = self._cache_disk.popitem(last=False)
            self.disk_cache_size -= os.path.getsize(old_disk_path)
            os.remove(old_disk_path)

    @staticmethod
    def parse_path(path: str) -> tuple[str, str, str]:
        parsed = urlparse(str(path), allow_fragments=False)
        return parsed.scheme, parsed.netloc, parsed.path.lstrip("/")

    def list_dir(self, abs_path: str, only_dir=False, recursive=False) -> list[str]:
        """List all files in the directory, return list of paths relative to provided path
        :param abs_path: path to the source directory
        :param only_dir: if True, only list directories, if False, list all files
        :param recursive: if True, list all files in the directory recursively (relative to provided path)
        :return: list of files in the directory
        """
        abs_path = self.resolve_path(abs_path)

        scheme, bucket, prefix = self.parse_path(abs_path)
        if scheme == "s3":
            prefix = prefix.rstrip("/") + "/"
            objects = []

            if recursive:
                paginator = self.aws.s3.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                    if "CommonPrefixes" in page and only_dir:
                        objects += [cp["Prefix"][len(prefix) : -1] for cp in page["CommonPrefixes"]]
                    if "Contents" in page and not only_dir:
                        objects += [obj["Key"][len(prefix) :] for obj in page["Contents"] if obj["Key"] != prefix]
            else:
                try:
                    response = self.aws.s3.list_objects_v2(
                        Bucket=bucket, Prefix=prefix.rstrip("/") + "/", Delimiter="/"
                    )
                except ClientError as e:
                    print(e)
                    raise

                if "CommonPrefixes" in response:
                    objects += [
                        os.path.basename(content["Prefix"].rstrip("/"))
                        for content in response["CommonPrefixes"]
                        if content["Prefix"] != prefix
                    ]

                if "Contents" in response and not only_dir:
                    objects += [
                        os.path.basename(content["Key"].rstrip("/"))
                        for content in response["Contents"]
                        if content["Key"] != prefix
                    ]

            return objects

        if not os.path.exists(abs_path):
            return []

        if recursive:
            if only_dir:
                return sorted(
                    os.path.join(root, d).removeprefix(abs_path.rstrip("/") + "/")
                    for root, dirs, files in os.walk(abs_path, followlinks=True)
                    for d in dirs
                )
            else:
                return sorted(
                    os.path.join(root, filename).removeprefix(abs_path.rstrip("/") + "/")
                    for root, dirs, files in os.walk(abs_path, followlinks=True)
                    for filename in files
                )
        else:
            if only_dir:
                return sorted([d for d in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, d))])
            else:
                return sorted(os.listdir(abs_path))

    def file_exists(self, storage_path) -> bool:
        """Search for the file in the local filesystem or in the S3 bucket
        :param storage_path: relative (within storage root) or absolute path to the source file
        :return: True if the file exists, False otherwise
        """
        abs_path = self.resolve_path(storage_path)

        scheme, bucket, key = self.parse_path(abs_path)
        if scheme == "s3":
            try:
                self.aws.s3.head_object(Bucket=bucket, Key=key)
                return True
            except ClientError as e:
                # Check if the error is "Not Found"
                if e.response["Error"]["Code"] in ("NoSuchKey", "404", 404):
                    return False
                else:
                    print("S3 ERROR", e, e.response)
                    raise e
        return os.path.exists(abs_path)

    def read_file_bytes(self, storage_path, cache_store: bool = True) -> bytes:
        abs_path = self.resolve_path(storage_path)

        # Check if the file is in memory cache
        content = self._cache_read(abs_path)
        if content is not None:
            if self.verbose:
                print(f"Reading {storage_path} from cache")
            return content

        # Read file contents from s3 or disk
        scheme, bucket, key = self.parse_path(abs_path)
        if scheme == "s3":
            try:
                if self.verbose:
                    print(f"Reading {storage_path} from s3")
                response = self.aws.s3.get_object(Bucket=bucket, Key=key)
                content = response["Body"].read()
                if cache_store:
                    self._cache_store(abs_path, content)
            except ClientError as e:
                print("S3 ERROR", e, e.response)
                if e.response["Error"]["Code"] in ("NoSuchKey", "404", 404):
                    raise FileNotFoundError(f"File not found: {abs_path}") from e
                raise
            return content

        if self.verbose:
            print(f"Reading {storage_path} from FS")
        with open(abs_path, "rb") as f:
            content = f.read()
        if cache_store:
            self._cache_store(abs_path, content)
        return content

    def read_file_str(self, storage_path: str, cache_store: bool = True) -> str:
        """Read the file from the source filesystem or from the source S3 bucket"""
        file_content = self.read_file_bytes(storage_path, cache_store=cache_store)
        return file_content.decode()

    def read_file_pickle(self, storage_path: str):
        """Read the file from the source filesystem or from the source S3 bucket
        and parse it as a pickle."""
        file_content = self.read_file_bytes(storage_path)
        return pickle.loads(file_content)

    def resolve_path(self, storage_path: str) -> str:
        """Resolve the storage path to an absolute path in the local filesystem or S3 bucket.
        :param storage_path: relative (within storage root) or absolute path to the source file
        :return: absolute path to the file in the local filesystem or S3 bucket
        """
        scheme, _, _ = self.parse_path(storage_path)
        if not os.path.isabs(storage_path) and not scheme:
            # Convert relative path to absolute
            return os.path.join(self.storage_root, storage_path)
        return storage_path

    def store_file_path(self, source_abs_path: str, storage_rel_path: str, overwrite: bool = True) -> str:
        """Store the file in the local filesystem or in the S3 bucket
        :param source_abs_path: abs path (or s3 URI) to the source file
        :param storage_rel_path: path to the storage file
        :param overwrite: if True, overwrite the file if it exists

        :return: relative path to the stored file
        """

        if not overwrite and self.file_exists(storage_rel_path):
            return storage_rel_path

        storage_abs_path = self.resolve_path(storage_rel_path)
        source_scheme, source_bucket, source_path = self.parse_path(source_abs_path)
        storage_scheme, storage_bucket, storage_path = self.parse_path(storage_abs_path)
        if source_scheme == "s3":
            if self.verbose:
                print(f"Downloading {source_abs_path} to {storage_abs_path}")
            if storage_scheme == "s3":
                self.aws.s3.copy_object(
                    CopySource=os.path.join(source_bucket, source_path), Bucket=storage_bucket, Key=storage_path
                )
                return storage_rel_path
            os.makedirs(os.path.dirname(storage_abs_path), exist_ok=True)
            try:
                self.aws.s3.download_file(Bucket=source_bucket, Key=source_path, Filename=storage_abs_path)
            except ClientError as e:
                print("S3 ERROR", e, e.response)
                if e.response["Error"]["Code"] in ("NoSuchKey", "404", 404):
                    raise FileNotFoundError(f"File not found: s3://{source_bucket}/{source_path}") from e
                raise
            return storage_rel_path
        else:
            if self.verbose:
                print(f"Downloading {source_abs_path} to {storage_abs_path}")
            os.makedirs(os.path.dirname(storage_abs_path), exist_ok=True)
            shutil.copy(source_abs_path, storage_abs_path)
            return storage_rel_path

    def store_file_bytes(self, file_bytes: bytes, storage_rel_path: str, overwrite: bool = True) -> str:
        """Store the file string in the source filesystem or source S3 bucket
        :param file_bytes: file bytes to store
        :param storage_rel_path: relative path to the storage file
        :param overwrite: if True, overwrite the file if it exists
        :returns: relative path to the stored file
        """

        if not overwrite and self.file_exists(storage_rel_path):
            return storage_rel_path

        storage_abs_path = self.resolve_path(storage_rel_path)
        storage_scheme, storage_bucket, storage_path = self.parse_path(storage_abs_path)
        if storage_scheme == "s3":
            if self.verbose:
                print(f"Uploading content to {storage_abs_path}")
            self.aws.s3.put_object(
                Body=file_bytes,
                Bucket=storage_bucket,
                Key=storage_path,
            )
        else:
            if self.verbose:
                print(f"Storing content to {storage_abs_path}")
            os.makedirs(os.path.dirname(storage_abs_path), exist_ok=True)
            with open(storage_abs_path, "wb") as f:
                f.write(file_bytes)

        return storage_rel_path

    def store_file_str(self, file_str: str, storage_rel_path: str, overwrite: bool = True) -> str:
        """Store the file string in the source filesystem or source S3 bucket
        :param file_str: file string to store
        :param storage_rel_path: relative path to the storage file
        :param overwrite: if True, overwrite the file if it exists
        """
        return self.store_file_bytes(file_str.encode(), storage_rel_path, overwrite=overwrite)

    def store_input(
        self,
        project_id: str,
        file_path: str = None,
        file_bytes: bytes = None,
        file_str: str = None,
        filename: str = None,
    ) -> str:
        """Store the file string in the source filesystem or source S3 bucket

        :param project_id: project ID
        :param file_path: path to the source file (when loading from path)
        :param file_bytes: file bytes to store (when loading from bytes)
        :param file_str: file string to store (when loading from string)
        :param filename: filename to use when storing the file (required when loading from bytes or string)
        """
        if file_path:
            assert file_bytes is None and file_str is None, "Provide only one of file_path, file_bytes, or file_str"
            if filename is None:
                filename = os.path.basename(file_path)
            # consider the input path to be relative to current dir, not the storage dir (useful in Jupyter)
            file_path = os.path.abspath(file_path)
            file_bytes = self.read_file_bytes(file_path)
        elif file_bytes is not None:
            assert file_str is None, "Provide only one of file_bytes or file_str"
            assert filename is not None, "filename must be provided when loading from bytes"
        elif file_str is not None:
            assert filename is not None, "filename must be provided when loading from string"
            file_bytes = file_str.encode()
        hash_str = get_hashed_path_for_bytes(file_bytes)
        storage_rel_path = os.path.join("project", project_id, "inputs", hash_str, filename)
        return self.store_file_bytes(file_bytes, storage_rel_path)

    def create_zip(self, storage_paths_by_dir: dict[str, list[str]]) -> bytes:
        """Create zip file
        :param storage_paths_by_dir: dictionary with the storage paths by directory
        :return: zip content with the stored files
        """

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            with ThreadPoolExecutor(self.num_copy_threads) as executor:
                # Fetch all files and collect their content
                futures = {
                    (file_path, executor.submit(self.read_file_bytes, file_path, cache_store=False)): dir_model
                    for dir_model, file_paths in storage_paths_by_dir.items()
                    for file_path in file_paths
                }

                # Process each future to write to ZIP file
                for (file_path, future), subdir in futures.items():
                    filename = os.path.basename(file_path)
                    file_data = future.result()  # this will raise exception if any
                    # Write the file to the zip with the desired structure
                    if file_data and filename:
                        zip_file.writestr(f"{subdir}/{filename}", file_data)
        zip_buffer.seek(0)
        return zip_buffer.read()

    def sync_file(self, storage_path: str, local_destination_path: str, link: bool = False):
        """Download/copy stored file to local directory
        :param storage_path: path to the stored file
        :param local_destination_path: path to the destination file
        :param link: if True, and if supported, create a symbolic link to the file instead of copying it
        """
        storage_path = self.resolve_path(storage_path)
        scheme, _, _ = self.parse_path(storage_path)
        os.makedirs(os.path.dirname(local_destination_path), exist_ok=True)
        if not scheme:
            # local to local copy
            if link:
                os.symlink(storage_path, local_destination_path)
            else:
                shutil.copy(storage_path, local_destination_path)
            return

        try:
            content = self.read_file_bytes(storage_path, cache_store=False)
        except IsADirectoryError:
            raise ValueError(f"Use sync_directory to sync a directory, got: {storage_path}")
        with open(local_destination_path, "wb") as f:
            f.write(content)

    def sync_files(self, storage_paths: list[str], local_destination_dir: str, preserve_subdirs=False):
        """Download/copy list of stored files to local directory
        :param storage_paths: list of files to be downloaded to destination directory
        :param local_destination_dir: path to destination directory (will be created if not exists)
        :param preserve_subdirs: if True (or if recursive=True), preserve subdirectories in the local destination directory
        """
        if isinstance(storage_paths, str):
            storage_paths = [storage_paths]

        if preserve_subdirs:
            for path in storage_paths:
                assert not os.path.isabs(path) and "://" not in path, (
                    f"Expected relative paths when preserve_subdirs=True, got: {path}"
                )

        os.makedirs(local_destination_dir, exist_ok=True)
        with ThreadPoolExecutor(self.num_copy_threads) as executor:
            futures = [
                executor.submit(
                    self.sync_file,
                    file_path,
                    os.path.join(local_destination_dir, file_path if preserve_subdirs else os.path.basename(file_path)),
                )
                for file_path in storage_paths
            ]
            for future in futures:
                future.result()

    def is_local_path(self, path):
        scheme, netloc, relative_path = self.parse_path(path)
        return not scheme

    def sync_directory(self, source_dir: str, local_destination_dir: str, link=False):
        """Download/copy directory to local directory
        :param source_dir: source directory, path should be absolute or relative to storage root
        :param local_destination_dir: path to destination directory (will be created if not exists)
        :param link: Use symbolic links instead of copying files when possible.
        """
        source_dir = self.resolve_path(source_dir)
        if link and self.is_local_path(source_dir):
            os.symlink(source_dir, local_destination_dir)
            return

        os.makedirs(local_destination_dir, exist_ok=True)
        with ThreadPoolExecutor(self.num_copy_threads) as executor:
            futures = [
                executor.submit(
                    self.sync_file, os.path.join(source_dir, file_path), os.path.join(local_destination_dir, file_path)
                )
                for file_path in self.list_dir(source_dir, recursive=True)
            ]
            for future in futures:
                future.result()

    def prepare_workflow_input(
        self, storage_path: str, workdir: str, input_bytes: bytes = None, name: str = None, custom_hash: str = None
    ) -> str:
        """Prepare workflow input files for submission by storing them in the provided scheduler workdir
        under unique hashes based on each file's contents.

        :param storage_path: path to the stored file
        :param workdir: destination (working directory of the scheduler)
        :param input_bytes: optional - do not read the storage_path, instead use the provided bytes
        :param name: optional - rename the file to provided name (without extension, original extension will be appended)
        :param custom_hash: use custom hash for the subdirectory name instead of using a generated hash of file contents
        """

        # TODO implement logic to avoid copying file if it's already accessible to the scheduler
        #  Two caveats:
        #  - The default scheduler.workdir points to a subdirectory different than the storage directory, for example ovo/workdir vs ovo/storage,
        #    so something like if storage_path.startswith(workdir) would not work
        #  - If name param is passed, we need to rename the file anyway - maybe a symlink would need to be created in that case

        if input_bytes is None:
            input_bytes = self.read_file_bytes(storage_path)

        if custom_hash is None:
            custom_hash = get_hashed_path_for_bytes(input_bytes)

        workdir_scheme, workdir_bucket, workdir_prefix = self.parse_path(workdir)

        if name is None:
            filename = os.path.basename(storage_path)
        else:
            filename = name + os.path.splitext(storage_path)[-1]

        if workdir_scheme == "s3":
            input_path = os.path.join("inputs", custom_hash, filename)
            input_prefix = os.path.join(workdir_prefix, input_path)
            s3_input_path = os.path.join(workdir, input_path)

            if self.file_exists(s3_input_path):
                return s3_input_path

            if self.verbose:
                print(f"Uploading {storage_path} to {s3_input_path}")

            self.aws.s3.put_object(Body=input_bytes, Bucket=workdir_bucket, Key=input_prefix)
            return s3_input_path
        else:
            input_dir = os.path.join(workdir, "inputs", custom_hash)
            os.makedirs(input_dir, exist_ok=True)
            input_path = os.path.join(input_dir, filename)

            if self.file_exists(input_path):
                return input_path

            with open(input_path, "wb") as f:
                f.write(input_bytes)
            return input_path

    def prepare_workflow_inputs(
        self,
        storage_paths: list[str],
        workdir: str,
        names: List[str] = None,
        return_paths=False,
        single_directory=False,
    ) -> str | list[str]:
        """
        Prepare workflow input files for submission by storing them in the provided scheduler workdir
        under unique hashes based on each file's contents.

        Each file will be stored in a separate subdirectory based on a hash of the file contents.
        This is useful when the same file can be submitted multiple times in different sets of files but should only be stored once.

        When return_paths=False (default), returns a txt file with the final file paths (or directly the file path in case of single input file).
        When return_paths=True, returns list of file paths.
        When single_directory=True, creates single directory and returns its path. Requires filenames to be unique.

        :param storage_paths: list of files to be downloaded to destination directory
        :param workdir: destination (working directory of the scheduler)
        :param names: rename each file to provided name (list of names of same length as storage_paths, without file extension, original extension will be added)
        """

        if single_directory:
            # Name subdirectory based on hash of paths to input files (not their contents)
            # This assumes that once files have been stored in storage, their content does not change
            custom_hash = get_hashed_path_for_bytes("_".join(storage_paths).encode())

            if names is not None:
                assert len(set(names)) == len(names), f"Names must be unique when single_directory=True, got: {names}"
            else:
                basenames = [os.path.basename(p) for p in storage_paths]
                assert len(set(basenames)) == len(basenames), (
                    f"Filenames must be unique when single_directory=True, got: {basenames}"
                )
        else:
            custom_hash = None

        if names is None:
            names = [None] * len(storage_paths)
        else:
            if len(names) != len(storage_paths):
                raise ValueError(
                    f"Mismatch between number of names ({len(names)}) and number of paths ({len(storage_paths)}). Ensure that each path has a corresponding name."
                )

        paths = [
            self.prepare_workflow_input(storage_path, workdir=workdir, name=name, custom_hash=custom_hash)
            for storage_path, name in zip(storage_paths, names)
        ]
        if single_directory:
            if not paths:
                raise ValueError("No paths to be prepared")
            subdirs = [path.rsplit("/", 1)[0] for path in paths]
            assert len(set(subdirs)) == 1, f"Expected all files to be in a single directory, got: {paths}"
            return subdirs[0] + "/"
        elif return_paths:
            return paths
        elif len(paths) == 1:
            # single input, return the file path directly without wrapping into a txt file
            return paths[0]
        else:
            # prepare txt file with one path per line
            return self.prepare_workflow_input(
                storage_path="input_pdb_paths.txt", workdir=workdir, input_bytes="\n".join(paths).encode("utf-8")
            )
