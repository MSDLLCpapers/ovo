import datetime

import pandas as pd
import pytest

from ovo import db, schedulers
from ovo.core.database import Design
from ovo.core.database.models_proteinqc import ProteinQCWorkflow
from ovo.core.logic import descriptor_logic, design_logic
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_full_proteinqc_sequence_only(project_data):
    project, project_round, _ = project_data

    sequence_pool = db.Pool(
        id=db.Pool.generate_id(),
        round_id=project_round.id,
        name="Sequence Pool",
        author="test",
    )
    db.save(sequence_pool)
    designs = design_logic.create_designs_from_dataframe(
        df=pd.read_csv(RESOURCES_DIR / "examples/inputs/sample_designs.csv"),
        id_column="design_id",
        column_chains={"A": "A", "B": "B"},
        pool_id=sequence_pool.id,
    )
    db.save_all(designs)
    design_ids = [d.id for d in designs]

    proteinqc: ProteinQCWorkflow = ProteinQCWorkflow(
        chains=["A", "B"],
        design_ids=[design.id for design in designs],
        tools=["seq_composition", "proteinsol"],
        batch_size=2,
    )
    proteinqc.validate()

    params = proteinqc.prepare_params(workdir=schedulers[TEST_SCHEDULER_KEY].workdir)
    assert params["input_pdb"].endswith(".csv"), "Should prepare a csv file when using sequence-only tools"
    prepared_df = pd.read_csv(params["input_pdb"], index_col=0)
    assert prepared_df.index.tolist() == design_ids, "Prepared CSV should have design IDs as index"
    assert prepared_df["A"].tolist() == [d.spec.get_chain("A").sequence for d in designs], (
        "Prepared CSV should contain the correct sequences"
    )
    assert prepared_df["B"].tolist() == [d.spec.get_chain("B").sequence for d in designs], (
        "Prepared CSV should contain the correct sequences"
    )

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=proteinqc, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)
    values = descriptor_logic.get_wide_descriptor_table(design_ids=design_ids)
    print(values.to_dict(orient="records"))
    assert len(values) == 3
    assert len(values["Sequence length"].dropna()) == 3, "Sequence length should be computed for all designs"

    first_value = values.iloc[0]
    assert first_value["Sequence solubility (scaled)"] == pytest.approx(0.545, rel=0.01)
    assert first_value["Sequence length"] == sum(len(c.sequence) for c in designs[0].spec.chains)
