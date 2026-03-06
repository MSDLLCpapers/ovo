import os

import pytest

from ovo import storage
from ovo.core.storage import ZipIsBeingWrittenError
from unittest.mock import patch


def test_storage_zip_context():
    # force zip context for testing
    with patch.object(storage, "archive_method", "zip"):
        with storage.archive_context(".txt", delete_if_exists=True):
            path1 = storage.store_file_bytes(b"TEST1", "test/path/test1.txt")
            path2 = storage.store_file_bytes(b"TEST2", "test/path/test2.foo")
            path3 = storage.store_file_bytes(b"TEST3", "test/path/test3.txt")
            path4 = storage.store_file_bytes(b"TEST4", "test/another/test4.txt")

        assert path1 == "zip://test/path.zip:test1.txt"
        assert path2 == "test/path/test2.foo"
        assert path3 == "zip://test/path.zip:test3.txt"
        assert path4 == "zip://test/another.zip:test4.txt"

        assert os.path.exists(os.path.join(storage.storage_root, "test/path.zip"))
        assert os.path.exists(os.path.join(storage.storage_root, "test/another.zip"))
        assert os.path.exists(os.path.join(storage.storage_root, "test/path/test2.foo"))

        # test bulk read
        with storage.bulk_read_context():
            assert storage.read_file_bytes(path1) == b"TEST1"
            assert storage.read_file_bytes(path3) == b"TEST3"
            assert storage.read_file_bytes(path4) == b"TEST4"
            assert len(storage._zip_read_context.zip_files) == 2
        assert storage._zip_read_context is None

        # test regular read
        assert storage.read_file_bytes(path1) == b"TEST1"
        assert storage.read_file_bytes(path2) == b"TEST2"
        assert storage.read_file_bytes(path3) == b"TEST3"
        assert storage.read_file_bytes(path4) == b"TEST4"

        # test file exists
        assert storage.file_exists(path1)

        # test with no extensions
        with storage.archive_context(delete_if_exists=True):
            path1 = storage.store_file_bytes(b"TEST1", "test/path/test1.txt")

        assert path1 == "zip://test/path.zip:test1.txt"
        assert storage.read_file_bytes(path1) == b"TEST1"


def test_storage_reading_from_zip_when_being_written_raises_error():
    # force zip context for testing
    with patch.object(storage, "archive_method", "zip"):
        with pytest.raises(ZipIsBeingWrittenError):
            with storage.archive_context(".txt", delete_if_exists=True):
                path1 = storage.store_file_bytes(b"TEST1", "test/new/path/test1.txt")
                assert storage.read_file_bytes(path1) == b"TEST1"
