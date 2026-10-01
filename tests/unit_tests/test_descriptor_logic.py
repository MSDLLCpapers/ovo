import pandas as pd
import pytest

from ovo.core.database.models import Design, DesignChain, DesignSpec
from ovo.core.logic import descriptor_logic


def _design(design_id: str, chain_id: str, sequence: str) -> Design:
    return Design(
        id=f"ovo_testpool123_{design_id}",
        pool_id="testpool123",
        spec=DesignSpec(chains=[DesignChain(type="protein", chain_ids=[chain_id], sequence=sequence)]),
    )


def test_prepare_design_sequences_relabels_chains(tmp_path):
    """Designs with differently labelled designed chains should share a single canonical sequence column."""
    designs = [_design("rfd", "A", "MKFLKFSLL"), _design("bindcraft", "B", "MTEYKLVVV")]

    csv_path = descriptor_logic.prepare_design_sequences(
        designs,
        workdir=str(tmp_path),
        chains_by_design_id={designs[0].id: ["A"], designs[1].id: ["B"]},
    )

    df = pd.read_csv(csv_path, index_col="design_id")
    assert list(df.columns) == ["A"]
    assert not df["A"].isna().any()
    assert df["A"].to_dict() == {designs[0].id: "MKFLKFSLL", designs[1].id: "MTEYKLVVV"}


def test_prepare_design_sequences_without_chains_map(tmp_path):
    """Without a chains map, the original chain IDs are used as columns (each design only fills its own)."""
    designs = [_design("rfd", "A", "MKFLKFSLL"), _design("bindcraft", "B", "MTEYKLVVV")]

    csv_path = descriptor_logic.prepare_design_sequences(designs, workdir=str(tmp_path))

    df = pd.read_csv(csv_path, index_col="design_id")
    assert sorted(df.columns) == ["A", "B"]
    assert df.loc[designs[0].id, "A"] == "MKFLKFSLL"
    assert pd.isna(df.loc[designs[0].id, "B"])


def test_prepare_design_sequences_missing_chain(tmp_path):
    designs = [_design("rfd", "A", "MKFLKFSLL")]

    with pytest.raises(Exception, match="C"):
        descriptor_logic.prepare_design_sequences(
            designs, workdir=str(tmp_path), chains_by_design_id={designs[0].id: ["C"]}
        )
