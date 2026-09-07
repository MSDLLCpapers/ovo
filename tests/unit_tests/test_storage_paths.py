import pytest

from ovo.core.storage import Storage


@pytest.fixture(params=["/data/storage", "/data/storage/", "s3://my-bucket/ovo/storage/"])
def storage(request) -> Storage:
    """A Storage against a local and an S3 root, without connecting to anything."""
    return Storage(storage_root=request.param, aws=None)


def test_storage_root_must_be_absolute(storage):
    """A trailing slash is stripped, and a relative root (which the config resolves) is refused."""
    assert storage.storage_root == storage.storage_root.rstrip("/")

    with pytest.raises(AssertionError, match="must be an absolute path or a URI"):
        Storage(storage_root="./storage", aws=None)


def test_resolve_path_keeps_the_storage_root_scheme(storage):
    """A relative path resolves under the root, whether that root is a local path or an S3 URI."""
    resolved = storage.resolve_path("projects/p1/inputs/x.pdb")

    assert resolved == storage.storage_root + "/projects/p1/inputs/x.pdb"
    assert storage.is_storage_path("projects/p1/inputs/x.pdb")


def test_is_storage_path_rejects_traversal_out_of_the_storage_root(storage):
    """'..' segments are resolved before comparing, so they cannot point outside the root."""
    root = storage.storage_root

    assert not storage.is_storage_path("../../etc/passwd")
    assert not storage.is_storage_path("projects/../../../etc/passwd")
    assert not storage.is_storage_path(f"{root}/../../etc/passwd")
    assert not storage.is_storage_path("zip://../../secret.zip:x.pdb")
    # While a path that stays inside is still accepted
    assert storage.is_storage_path(f"{root}/projects/p1/../p2/x.pdb")
    assert storage.is_storage_path("zip://archives/a.zip:x.pdb")


def test_is_storage_path_rejects_other_locations(storage):
    assert not storage.is_storage_path("/etc/passwd")
    assert not storage.is_storage_path("s3://another-bucket/x.pdb")
