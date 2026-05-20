import datetime

import pytest

from ovo import db
from ovo.core.database import Design
from ovo.core.database.models_proteinqc import ProteinQCWorkflow
from ovo.core.logic import descriptor_logic
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_full_proteinqc(project_data):
    project, project_round, custom_pool = project_data

    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    proteinqc: ProteinQCWorkflow = ProteinQCWorkflow(
        chains=["A"],
        design_ids=[design.id for design in designs],
        tools=[
            "seq_composition",
            "dssp",
            "proteinsol",
            "esm_if",
        ],
    )
    proteinqc.validate()
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=proteinqc, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)
    values = descriptor_logic.get_wide_descriptor_table(design_ids=design_ids)
    print(values.to_dict(orient="records"))
    first_value = values.iloc[0]
    assert first_value["ESM-IF likelihood"] == pytest.approx(0.3369, rel=0.01)
    assert first_value["Sequence solubility (scaled)"] == pytest.approx(0.457, rel=0.01)
    assert first_value["DSSP Beta Sheet %"] > 40
    assert first_value["Sequence length"] > 0
