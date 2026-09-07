import pandas as pd
import pytest

from ovo.core.logic.pool_logic import PoolUpload


def test_pool_upload_requires_exactly_one_input():
    """Nothing is created when neither or both of the two upload shapes are given."""
    with pytest.raises(ValueError, match="either structure_files or dataframe"):
        PoolUpload(project_id="p", pool_name="pool", round_id="r").validate()

    with pytest.raises(ValueError, match="either structure_files or dataframe"):
        PoolUpload(
            project_id="p",
            pool_name="pool",
            round_id="r",
            structure_files=["some_file"],
            chains="A",
            dataframe=pd.DataFrame({"id": ["a"], "heavy": ["AAA"]}),
        ).validate()


def test_pool_upload_rejects_chains_with_dataframe():
    """The chains of a table upload come from column_chains, so a chains argument is an error."""
    upload = PoolUpload(
        project_id="p",
        pool_name="pool",
        round_id="r",
        dataframe=pd.DataFrame({"id": ["a"], "heavy": ["AAA"]}),
        id_column="id",
        column_chains={"heavy": "A"},
        chains="A",
    )

    with pytest.raises(ValueError, match="chains cannot be combined with dataframe"):
        upload.validate()

    assert upload.get_chains() == [], "A table upload has no chains until its designs are built"


def test_pool_upload_requires_a_round():
    with pytest.raises(ValueError, match="round_id"):
        PoolUpload(project_id="p", pool_name="pool", structure_files=["some_file"], chains="A").validate()


def test_pool_upload_get_chains():
    """The chains of a structure upload are accepted in every form the front-ends collect them in."""

    def upload(chains) -> PoolUpload:
        return PoolUpload(project_id="p", pool_name="pool", round_id="r", structure_files=["some_file"], chains=chains)

    assert upload("A").get_chains() == ["A"]
    assert upload("AB").get_chains() == ["A", "B"]
    assert upload("A, B").get_chains() == ["A", "B"]
    assert upload(["A", "B"]).get_chains() == ["A", "B"]
    assert upload(["AB"]).get_chains() == ["A", "B"]

    with pytest.raises(ValueError, match="Invalid chains 'a1'"):
        upload("a1").validate()
    with pytest.raises(ValueError, match="chains is required"):
        upload("").validate()

    # A list is validated the same way as the string form, and always parses into single letters
    with pytest.raises(ValueError, match=r"Invalid chains \['a', 'B'\]"):
        upload(["a", "B"]).validate()
    with pytest.raises(ValueError, match=r"Invalid chains \[1\]"):
        upload([1]).get_chains()
