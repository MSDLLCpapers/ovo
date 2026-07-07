import shutil
import warnings
import zipfile
import io
import pickle
import gzip
from typing import List, Literal

from urllib.parse import urlparse
from zipfile import ZipFile

from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor

import os
import tempfile
import weakref
from collections import OrderedDict
from ovo.core.aws import AWSSessionManager
from ovo.core.utils.formatting import get_hashed_path_for_bytes
import threading
from contextlib import contextmanager
from typing import Optional
import multiprocessing


class Storage:
    """Class for managing file storage in local filesystem or S3 bucket"""

    def __init__(
        self,
        storage_root: str,
        aws: AWSSessionManager | None,
        verbose: bool = False,
        num_copy_threads: int | None = None,
        archive_method: Literal["zip", None] = None,
        memory_cache_limit_bytes=50 * 1024 * 1024,
        disk_cache_limit_bytes=200 * 1024 * 1024,
        memory_cache_limit_per_file_bytes=5 * 1024 * 1024,
    ):
        self.storage_root: str = storage_root
        self.aws: AWSSessionManager | None = aws
        self.verbose = verbose
        self.num_copy_threads = num_copy_threads
        self.archive_method = archive_method
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
        # zip context
        self._zip_write_context: Optional[ZipWriteContext] = None
        self._zip_read_context: Optional[ZipReadContext] = None

    @contextmanager
    def archive_context(self, *extensions: str, delete_if_exists=False):
        """
        Activate an archive context for all store_...() calls
        for files ending with any of the provided extensions (or all files if not provided).
        Only one context may be active at a time.
        """
        if self.archive_method is None:
            yield
            return
        elif self.archive_method == "zip":
            if self._zip_write_context is not None:
                raise RuntimeError(f"Another zip_context is already active for {self._zip_write_context.extensions}")
            ctx = ZipWriteContext(*extensions, delete_if_exists=delete_if_exists)
            self._zip_write_context = ctx

            try:
                yield
            finally:
                self._zip_write_context = None
                ctx.close()
        else:
            raise ValueError(f"Invalid archive method configured: {self.archive_method}")

    def _get_zip_write_context(self, storage_abs_path: str) -> Optional["ZipWriteContext"]:
        """
        Return a ZipWriteContext to write to, else None. Raises RuntimeError if called from a different process.
        """
        ctx = self._zip_write_context
        if ctx is None:
            return None

        storage_scheme, *_ = self.parse_path(self.storage_root)
        if storage_scheme == "s3":
            return None

        if not ctx.accepts_path(storage_abs_path):
            return None

        return ctx

    @contextmanager
    def bulk_read_context(self):
        """Context manager for speeding up reading files from zip and other archives

        Each zip file is opened only once and reused for all reads within the context,
        and closed at the end of the context.
        """
        if self._zip_read_context is not None:
            # already in bulk read context, do nothing
            yield
            return
        ctx = ZipReadContext()
        self._zip_read_context = ctx
        try:
            yield
        finally:
            self._zip_read_context = None
            ctx.close()

    @contextmanager
    def _get_zip_read_file(self, zip_abs_path: str):
        """Return a ZipFile for reading, given its absolute path.

        If bulk_read_context is active, reuse the same ZipFile for the same zip_abs_path, otherwise open and close it for each read.
        """
        if self._zip_read_context is None:
            warnings.warn(
                "Accessing zip files without bulk_read_context may be slow, "
                "consider using 'with storage.bulk_read_context():' "
                "when reading multiple files from the same archive"
            )
            with ZipFile(zip_abs_path) as f:
                yield f
            return
        # bulk read context enabled, delegate to context
        with self._zip_read_context.get_zip_file(zip_abs_path) as f:
            yield f

    def _clear_temp_dir(self):
        self._temp_dir.cleanup()

    def _cache_exists(self, file_path):
        return file_path in self._cache_memory or file_path in self._cache_disk

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

    def _cache_store(self, file_path, content: str | bytes | None):
        if content is None:
            if file_path in self._cache_memory:
                self.memory_cache_size -= len(self._cache_memory[file_path])
                del self._cache_memory[file_path]
            if file_path in self._cache_disk:
                self.disk_cache_size -= os.path.getsize(self._cache_disk[file_path])
                os.remove(self._cache_disk[file_path])
                del self._cache_disk[file_path]
            return
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

    def clear_cache(self, storage_path: str):
        """Clear the cache for a specific file path"""
        abs_path = self.resolve_path(storage_path)
        self._cache_store(abs_path, None)

    @staticmethod
    def parse_path(path: str) -> tuple[str, str, str]:
        parsed = urlparse(str(path), allow_fragments=False)
        return parsed.scheme, parsed.netloc, parsed.path.lstrip("/")

    @staticmethod
    def _parse_zip_path(abs_path: str) -> tuple[str, str]:
        if not abs_path.startswith("zip://") or ":" not in abs_path.removeprefix("zip://"):
            raise ValueError(
                f"Invalid zip path, expected format: zip://path/to/zipfile.zip:internal/path/in/zip, got: {abs_path}"
            )
        zip_abs_path, arcpath = abs_path.removeprefix("zip://").split(":", 1)
        return zip_abs_path, arcpath

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
        elif scheme == "zip":
            zip_abs_path, arcpath = self._parse_zip_path(abs_path)
            if self._zip_write_context and self._zip_write_context.zip_files.get(zip_abs_path):
                raise ZipIsBeingWrittenError(
                    f"Cannot check existence of {storage_path} while the zip is still being written"
                )
            try:
                with self._get_zip_read_file(zip_abs_path) as zip_file:
                    try:
                        zip_file.getinfo(arcpath)
                        return True
                    except KeyError:
                        return False
            except FileNotFoundError:
                # The ZIP archive itself does not exist, so the file cannot exist.
                return False
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
        elif scheme == "zip":
            if self.verbose:
                print(f"Reading {storage_path} from ZIP")
            zip_abs_path, arcpath = self._parse_zip_path(abs_path)
            if self._zip_write_context and self._zip_write_context.zip_files.get(zip_abs_path):
                raise ZipIsBeingWrittenError(f"Cannot read {storage_path} while the zip is still being written")
            with self._get_zip_read_file(zip_abs_path) as zip_file:
                with zip_file.open(arcpath) as f:
                    content = f.read()
                    if cache_store:
                        self._cache_store(abs_path, content)
                    return content
        if self.verbose:
            print(f"Reading {storage_path} from FS")
        with open(abs_path, "rb") as f:
            content = f.read()
        if cache_store:
            self._cache_store(abs_path, content)
        return content

    def read_file_str(self, storage_path: str, cache_store: bool = True, decompress: bool = False) -> str:
        """Read the file from the source filesystem or from the source S3 bucket
        :param storage_path: relative (within storage root) or absolute path to the source file
        :param cache_store: if True, cache the file contents in memory/disk for faster subsequent reads
        :param decompress: if True, decompress the file contents using gzip before decoding
        """
        file_content = self.read_file_bytes(storage_path, cache_store=cache_store)
        if decompress:
            file_content = gzip.decompress(file_content)
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
        if scheme == "zip":
            abspath = os.path.join(self.storage_root, storage_path.removeprefix("zip://"))
            return f"zip://{abspath}"
        if not os.path.isabs(storage_path) and not scheme:
            # Convert relative path to absolute
            return os.path.join(self.storage_root, storage_path)
        return storage_path

    def _basename(self, path: str) -> str:
        """Get the base name (filename) from a path, supporting both regular paths and zip paths"""
        path = self.resolve_path(path)
        scheme, _, _ = self.parse_path(path)
        if scheme == "zip":
            _, arcpath = self._parse_zip_path(path)
            return os.path.basename(arcpath)
        else:
            return os.path.basename(path)

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
        storage_scheme, storage_bucket, storage_path = self.parse_path(storage_abs_path)
        source_scheme, source_bucket, source_path = self.parse_path(source_abs_path)

        if ctx := self._get_zip_write_context(storage_abs_path):
            arcname = os.path.basename(storage_abs_path)
            if source_scheme == "s3":
                content = self.read_file_bytes(source_abs_path)
                with ctx.get_zip_file(storage_abs_path) as f:
                    zip_rel_path = f.filename.removeprefix(self.storage_root).lstrip("/")
                    if self.verbose:
                        print(f"Writing {source_abs_path} to zip {zip_rel_path}:{arcname}")
                    f.writestr(arcname, content)
            else:
                with ctx.get_zip_file(storage_abs_path) as f:
                    zip_rel_path = f.filename.removeprefix(self.storage_root).lstrip("/")
                    if self.verbose:
                        print(f"Writing {source_abs_path} to zip {zip_rel_path}:{arcname}")
                    f.write(source_abs_path, arcname=arcname)
            return f"zip://{zip_rel_path}:{arcname}"

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

        if ctx := self._get_zip_write_context(storage_abs_path):
            arcname = os.path.basename(storage_abs_path)
            with ctx.get_zip_file(storage_abs_path) as f:
                zip_rel_path = f.filename.removeprefix(self.storage_root).lstrip("/")
                f.writestr(arcname, file_bytes)
            return f"zip://{zip_rel_path}:{arcname}"

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

    def get_project_path(
        self, project_id: str, pool_id: str = None, input_bytes: bytes = None, absolute: bool = False
    ) -> str:
        """Get the storage path for a project or a specific section within a project."""
        if pool_id:
            path = f"project/{project_id}/pools/{pool_id}"
        elif input_bytes:
            hash_str = get_hashed_path_for_bytes(input_bytes)
            path = f"project/{project_id}/inputs/{hash_str}"
        else:
            path = f"project/{project_id}"

        if absolute:
            return self.resolve_path(path)
        return path

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
        storage_rel_path = os.path.join(self.get_project_path(project_id, input_bytes=file_bytes), filename)
        return self.store_file_bytes(file_bytes, storage_rel_path)

    def create_zip(self, storage_paths_by_dir: dict[str, list[str]] | list[str], flatten: bool = False) -> bytes:
        """Create zip file
        :param storage_paths_by_dir: dictionary with the storage paths by directory ("" or None for root)
                                     or flat list of storage paths (will be stored in the root of the zip)
        :param flatten: if True, store all files in the root of the zip, add subdirectories as filename prefixes instead
        :return: zip content with the stored files
        """
        if isinstance(storage_paths_by_dir, list):
            storage_paths_by_dir = {"": storage_paths_by_dir}
        elif isinstance(storage_paths_by_dir, dict):
            for paths in storage_paths_by_dir.values():
                assert isinstance(paths, list), (
                    "storage_paths_by_dir must be a dictionary of lists, found value of type " + str(type(paths))
                )
                # Avoid overwriting files by mistake
                filenames = [self._basename(p) for p in paths]
                assert len(filenames) == len(set(filenames)), (
                    "Storing duplicate file paths in the same zip directory are not allowed: " + ", ".join(filenames)
                )

        else:
            raise ValueError(f"storage_paths_by_dir must be a dictionary or a list, got {type(storage_paths_by_dir)}")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            with ThreadPoolExecutor(self.num_copy_threads) as executor:
                # Fetch all files and collect their content
                futures = []
                for subdir, file_paths in storage_paths_by_dir.items():
                    for file_path in file_paths:
                        future = executor.submit(self.read_file_bytes, file_path, cache_store=False)
                        futures.append((future, subdir, file_path))

                # Process each future to write to ZIP file
                for future, subdir, file_path in futures:
                    filename = self._basename(file_path)
                    file_data = future.result()  # this will raise exception if any
                    # Write the file to the zip with the desired structure
                    if file_data and filename:
                        if subdir:
                            if flatten:
                                arcname = f"{subdir.replace('/', '_')}_{filename}"
                            else:
                                arcname = f"{subdir}/{filename}"
                        else:
                            arcname = filename
                        zip_file.writestr(arcname, file_data)
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

    def sync_files(
        self,
        storage_paths: list[str],
        local_destination_dir: str,
        preserve_subdirs=False,
        skip_outside_root=False,
        copy_full_archives=False,
    ):
        """Download/copy list of stored files to local directory
        :param storage_paths: list of files to be downloaded to destination directory
        :param local_destination_dir: path to destination directory (will be created if not exists)
        :param preserve_subdirs: if True (or if recursive=True), preserve subdirectories in the local destination directory
        :param skip_outside_root: if True, skip files found outside of storage root instead of raising an error (only applies when preserve_subdirs=True)
        :param copy_full_archives: if True, when a file is found to be within a zip archive, copy the entire archive to the destination directory instead of extracting just the file (only applies when preserve_subdirs=True)
        """
        if isinstance(storage_paths, str):
            storage_paths = [storage_paths]

        zip_paths_by_archive = {}
        if preserve_subdirs:
            filtered_storage_paths = []
            for i, path in enumerate(storage_paths):
                scheme, _, _ = self.parse_path(self.resolve_path(path))
                if scheme == "zip":
                    zip_abs_path, arcpath = self._parse_zip_path(self.resolve_path(path))
                    assert zip_abs_path.startswith(self.storage_root), (
                        f"Zip archive is outside of storage root: {zip_abs_path}"
                    )
                    zip_rel_path = os.path.relpath(zip_abs_path, self.storage_root)
                    if copy_full_archives:
                        # Do not copy individual file from the zip, instead copy the entire zip archive
                        if zip_rel_path not in filtered_storage_paths:
                            filtered_storage_paths.append(zip_rel_path)
                    else:
                        # Copy each individual file
                        zip_paths_by_archive.setdefault(zip_rel_path, []).append((arcpath, path))
                    continue

                if not scheme:
                    # when a path is local, make sure that it's within the storage root
                    if os.path.isabs(path) and path.startswith(self.storage_root):
                        # absolute path within storage root, convert to relative
                        path = os.path.relpath(path, self.storage_root)
                        filtered_storage_paths.append(path)
                        continue
                    if os.path.isabs(path) or not os.path.exists(os.path.join(self.storage_root, path)):
                        if skip_outside_root:
                            warnings.warn(f"Skipping file found outside of storage root: {path}")
                            continue
                        raise FileOutsideStorageRootError("Cannot export file found outside of storage root: " + path)
                assert not os.path.isabs(path) and ("://" not in path or path.startswith("zip://")), (
                    f"Expected relative paths when preserve_subdirs=True, got: {path}"
                )
                filtered_storage_paths.append(path)

        else:
            filtered_storage_paths = storage_paths

        os.makedirs(local_destination_dir, exist_ok=True)
        with ThreadPoolExecutor(self.num_copy_threads) as executor:
            futures = [
                executor.submit(
                    self.sync_file,
                    file_path,
                    os.path.join(local_destination_dir, file_path if preserve_subdirs else self._basename(file_path)),
                )
                for file_path in filtered_storage_paths
            ]
            for future in futures:
                future.result()

        for zip_rel_path, arcpaths in zip_paths_by_archive.items():
            os.makedirs(os.path.join(local_destination_dir, os.path.dirname(zip_rel_path)), exist_ok=True)
            with self.bulk_read_context():
                with zipfile.ZipFile(os.path.join(local_destination_dir, zip_rel_path), "w") as zip_file:
                    for arcpath, original_path in arcpaths:
                        content = self.read_file_bytes(original_path, cache_store=False)
                        zip_file.writestr(arcpath, content)

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
            filename = self._basename(storage_path)
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
                basenames = [self._basename(p) for p in storage_paths]
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

    def remove(self, storage_path: str):
        """Remove the file from storage"""
        self.clear_cache(storage_path)
        abs_path = self.resolve_path(storage_path)
        scheme, bucket, key = self.parse_path(abs_path)
        if scheme == "s3":
            try:
                self.aws.s3.delete_object(Bucket=bucket, Key=key)
            except ClientError as e:
                print("S3 ERROR", e, e.response)
                if e.response["Error"]["Code"] in ("NoSuchKey", "404", 404):
                    raise FileNotFoundError(f"File not found: {abs_path}") from e
                raise
        elif scheme == "zip":
            raise NotImplementedError("Removing files from zip archives is not supported yet")
        else:
            os.remove(abs_path)


class ZipWriteContext:
    def __init__(self, *extensions: str, delete_if_exists: bool = False):
        if extensions and isinstance(extensions[0], list):
            raise ValueError(f"Got list, expected individual string arguments for file extensions")
        self.extensions = tuple(extensions)
        self.zip_files: dict[str, ZipFile] = {}
        self.zip_locks = {}
        self.lock = threading.Lock()
        self.process_name = multiprocessing.current_process().name
        self.delete_if_exists = delete_if_exists

    def close(self):
        for zip_file in self.zip_files.values():
            zip_file.close()

    @contextmanager
    def get_zip_file(self, storage_abs_path: str):
        """Return a ZipFile for writing to the provided storage path.

        Will keep the file open until the whole context is closed, allowing multiple files to be written to the same zip file without reopening it.

        Given a storage path (e.g. "/path/to/storage/dir/file.txt"), return a ZipFile object for writing to "ovo/storage/dir.zip"

        Raises RuntimeError if called from a different process (please use a thread pool for parallelism).
        """
        dir_path = os.path.dirname(storage_abs_path)

        current_process = multiprocessing.current_process().name
        if current_process != self.process_name:
            raise RuntimeError(
                f"Storage zip write context created in process '{self.process_name}' "
                f"cannot be used from process '{current_process}'. Please use a thread pool for parallelism instead."
            )
        zip_file_path = dir_path.rstrip("/") + ".zip"
        if zip_file_path not in self.zip_locks:
            with self.lock:
                if zip_file_path not in self.zip_locks:  # double check inside lock
                    self.zip_locks[zip_file_path] = threading.Lock()
        # only one thread can write to the same zip file at a time
        with self.zip_locks[zip_file_path]:
            if zip_file_path not in self.zip_files:
                os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
                if not self.delete_if_exists and os.path.exists(zip_file_path):
                    # Note we are defensive here to make sure that users do not delete previous storage files by mistake
                    raise FileExistsError(
                        f"Zip file already exists: {zip_file_path}. Use delete_if_exists=True to allow recreating archive."
                    )
                self.zip_files[zip_file_path] = ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED)
            # yield without closing (will be closed when whole ZipWriteContext is closed)
            yield self.zip_files[zip_file_path]

    def accepts_path(self, storage_abs_path: str) -> bool:
        assert os.path.isabs(storage_abs_path), f"Expected absolute path, got: {storage_abs_path}"

        if self.extensions and not storage_abs_path.endswith(self.extensions):
            return False

        dir_path = os.path.dirname(storage_abs_path)
        if not dir_path:
            # do not zip files in the root directory
            return False
        return True


class ZipReadContext:
    def __init__(self):
        self.zip_files: dict[str, ZipFile] = {}
        self.lock = threading.Lock()

    def close(self):
        for zip_file in self.zip_files.values():
            zip_file.close()

    @contextmanager
    def get_zip_file(self, zip_abs_path: str):
        """Return a ZipFile for reading from the provided zip file path.

        Will keep the file open until the whole context is closed, allowing multiple files to be read from the same zip file without reopening it.

        Raises RuntimeError if called from a different process (please use a thread pool for parallelism).
        """
        # reuse opened ZipFile if already opened, otherwise open it and keep it open
        if zip_abs_path not in self.zip_files:
            with self.lock:
                if zip_abs_path not in self.zip_files:  # double check inside lock
                    self.zip_files[zip_abs_path] = ZipFile(zip_abs_path)
        # yield without closing, it will be closed when whole ZipReadContext is closed
        yield self.zip_files[zip_abs_path]


class ZipIsBeingWrittenError(Exception):
    pass


class FileOutsideStorageRootError(Exception):
    pass
