import pytest

from ovo import db
from ovo.core.database import Design
from ovo.core.logic import descriptor_logic
from ovo.core.utils.tests import TEST_SCHEDULER_KEY
from __MODULE_NAME__.models___MODULE_SUFFIX__ import __WORKFLOW_CLASS_NAME__


def test_full___MODULE_SUFFIX__(project_data):
    project, project_round, custom_pool = project_data

    # Use example designs
    designs = db.select(Design, pool_id=custom_pool.id)
    design_ids = [d.id for d in designs]

    workflow = __WORKFLOW_CLASS_NAME__(chains=["A"], design_ids=[design.id for design in designs], params={})
    # Submit workflow using Scheduler
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=workflow, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    # Sleep until workflow has finished and load the results from output folder to the DB
    descriptor_logic.process_results(descriptor_job)

    # Read descriptor values as a DataFrame
    values = descriptor_logic.get_wide_descriptor_table(design_ids=design_ids)
    print(values.to_dict(orient="records"))

    first_value = values.iloc[0]
    assert first_value["Polar SASA"] == pytest.approx(2998.54, rel=0.1)
    assert first_value["Non-polar SASA"] == pytest.approx(3583.39, rel=0.1)
