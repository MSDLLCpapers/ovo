import logging

import pytest
from pytest_mock import MockerFixture

from ovo import db
from ovo.core.database.models import DesignJob, Pool
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.app.utils.testing import hide_test_dialog, show_test_dialog
from ovo.core.logic.round_logic import get_or_create_project_rounds
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.constants import TIMEOUT, BULK_SUBMISSION_FILE
from tests.unit_tests.utils.rfdiffusion_utils import click_nav_button, pools_tab_contain_pools

logger = logging.getLogger(__name__)

page_key = BULK_SUBMISSION_FILE

# The same config the CLI submit integration test uses, so both front-ends are driven by one input
EXAMPLE_CONFIG = RESOURCES_DIR / "examples/inputs/5ELI_A_hairpin_scaffold.yaml"
EXAMPLE_INPUT_PDB = RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"

POOL_NAME_PREFIX = "test bulk"
CONFIG_POOL_NAME = "CLI hairpin scaffold test"


class TestBulkSubmission:
    """Bulk submission page tests: upload an input, paste a config, submit it."""

    @pytest.mark.parametrize(
        "test_wrapper",
        [BULK_SUBMISSION_FILE],
        indirect=True,
    )
    def test_submit_example_config(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """Submit the example bulk config through the page, all the way to the scheduler."""
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Files step — upload the input structure that the config references by filename
        logger.info("Testing file upload step...")
        at.file_uploader("bulk_upload_single").set_value(
            [("5ELI_A.pdb", EXAMPLE_INPUT_PDB.read_bytes(), "chemical/x-pdb")]
        ).run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "file upload step")
        assert "5ELI_A.pdb" in at.session_state.workflows[page_key].uploaded_files

        # Config step — paste the config and check that it parses into one submission
        click_nav_button(at)
        logger.info("Testing config step...")
        at.text_area[0].set_value(EXAMPLE_CONFIG.read_text()).run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "config step")

        state = at.session_state.workflows[page_key]
        asserts.assert_equal(1, len(state.submissions), "Test that the config parsed into one submission.")
        submission = state.submissions[0]
        asserts.assert_equal(CONFIG_POOL_NAME, submission.pool_name, "Test that the pool name was read.")
        asserts.assert_equal(
            "RFdiffusion scaffold design", submission.workflow.name, "Test that the workflow type was read."
        )
        assert submission.workflow.rfdiffusion_params.contigs == ["A111-114/10/A117-119"]
        assert submission.workflow.rfdiffusion_params.num_designs == 1

        # Review step — submit into a new round, so the Jobs page afterwards shows only this job
        click_nav_button(at)
        logger.info("Testing review & submit step...")
        show_test_dialog(at, "create_round")
        round_name = f"Round for {POOL_NAME_PREFIX}"
        at.text_input("round_name").set_value(round_name)
        at.button("create_round").click().run(timeout=TIMEOUT)
        rounds_by_id = get_or_create_project_rounds(project_id=at.session_state.project.id)
        assert round_name in [project_round.name for project_round in rounds_by_id.values()], (
            "Test that the round was created."
        )
        hide_test_dialog(at, "create_round")

        # The typed name is a prefix of the pool name from the config
        at.text_input("input_pool_name").set_value(POOL_NAME_PREFIX).run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "review & submit step")

        pool_name = f"{POOL_NAME_PREFIX} {CONFIG_POOL_NAME}"
        review_table = at.table[0].value
        asserts.assert_equal(
            pool_name,
            review_table.loc[("Pool", "Name")].iloc[0],
            "Test that the review table shows the prefixed pool name.",
        )

        num_jobs_before = len(mock_scheduler.jobs)
        at.button("bulk_submit_all").click().run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after submitting")

        assert len(mock_scheduler.jobs) == num_jobs_before + 1, (
            f"Job should be scheduled with MockScheduler: {mock_scheduler}"
        )
        asserts.assert_equal("⏳️ Jobs", at.title[0].value, "Page should switch to Jobs")
        asserts.assert_equal("Submitted 1 job(s) successfully", at.success[0].value, "Success message should be shown")
        pools_tab_contain_pools(at, [pool_name])

        # The submitted workflow keeps the config params, with the uploaded input resolved to storage
        pool = db.get(Pool, name=pool_name)
        design_job = db.get(DesignJob, id=pool.design_job_id)
        workflow = design_job.workflow
        asserts.assert_equal("RFdiffusion scaffold design", workflow.name, "Test the submitted workflow type.")
        assert workflow.rfdiffusion_params.contigs == ["A111-114/10/A117-119"]
        assert workflow.rfdiffusion_params.timesteps == 1
        assert workflow.protein_mpnn_params.num_sequences == 2
        input_pdb_paths = workflow.rfdiffusion_params.input_pdb_paths
        assert len(input_pdb_paths) == 1, f"Expected one input path, got {input_pdb_paths}"
        assert input_pdb_paths[0].endswith("5ELI_A.pdb"), f"Unexpected input path: {input_pdb_paths[0]}"
        assert input_pdb_paths[0] != "5ELI_A.pdb", "The uploaded input should have been stored in storage"
