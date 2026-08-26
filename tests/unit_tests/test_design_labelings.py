from datetime import datetime, timedelta, timezone

import pytest

from ovo import db
from ovo.core.database.models import DesignLabeling, Labeling

DESIGN_IDS = ["ovo_lbl_001", "ovo_lbl_002", "ovo_lbl_003"]


@pytest.fixture
def labelings() -> list[Labeling]:
    """Create two labels, the first design has both of them, the second one has one and the third none."""
    created_date_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    good = Labeling(
        id="lbl_good", label="Good", explanation="Good design", author="test_user", created_date_utc=created_date_utc
    )
    interesting = Labeling(
        id="lbl_interesting",
        label="Interesting",
        author="test_user",
        created_date_utc=created_date_utc + timedelta(minutes=1),
    )
    db.save_all([good, interesting])
    db.save_all(
        [
            DesignLabeling(design_id=DESIGN_IDS[0], labeling_id=interesting.id),
            DesignLabeling(design_id=DESIGN_IDS[0], labeling_id=good.id),
            DesignLabeling(design_id=DESIGN_IDS[1], labeling_id=good.id),
        ]
    )
    yield [good, interesting]
    for design_id in DESIGN_IDS:
        db.remove(DesignLabeling, design_id=design_id)
    db.remove(Labeling, id=good.id)
    db.remove(Labeling, id=interesting.id)


def test_get_labelings_for_design_ids(labelings):
    good, interesting = labelings
    labelings_by_design_id = db.get_labelings_for_design_ids(DESIGN_IDS)

    # Designs without any labels are not included, labels are ordered from least to most recent
    assert {
        design_id: [labeling.label for labeling in design_labelings]
        for design_id, design_labelings in labelings_by_design_id.items()
    } == {
        DESIGN_IDS[0]: [good.label, interesting.label],
        DESIGN_IDS[1]: [good.label],
    }
    # The explanations are needed for the label comments in the Excel export
    assert labelings_by_design_id[DESIGN_IDS[0]][0].explanation == good.explanation

    # Same values as when querying the designs one by one
    for design_id in DESIGN_IDS:
        assert [labeling.id for labeling in labelings_by_design_id.get(design_id, [])] == [
            labeling.id for labeling in db.get_labelings_for_design(design_id)
        ]

    assert db.get_labelings_for_design_ids([]) == {}


def test_get_labelings_for_design_ids_batched(labelings, monkeypatch):
    """Design IDs are batched to avoid the SQLite parameter limit."""
    expected = db.get_labelings_for_design_ids(DESIGN_IDS)
    monkeypatch.setattr(db, "_in_clause_items_limit", 1)
    batched = db.get_labelings_for_design_ids(DESIGN_IDS)

    assert {
        design_id: [labeling.id for labeling in design_labelings] for design_id, design_labelings in batched.items()
    } == {design_id: [labeling.id for labeling in design_labelings] for design_id, design_labelings in expected.items()}
