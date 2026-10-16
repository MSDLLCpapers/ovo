import logging

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from ovo import db
from ovo.core.database.models import BulkSubmissionDraftArtifact, DesignJob, Pool, Project, ProjectArtifact, Round
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.bulk_submission_utils import parse_bulk_config_yaml
from ovo.app.components.navigation import SUBMISSION_QUERY_PARAM
from ovo.app.components.submission_components import format_param_values
from ovo.app.utils.testing import hide_test_dialog, show_test_dialog
from ovo.core.logic.bulk_submission_logic import save_bulk_submission_draft
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
DRAFT_POOL_NAME_PREFIX = "test bulk draft"


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
        # Run after typing the name, the Create round button is disabled while the name is empty -
        # which it is whenever the last round of the project is not named "<something> <number>"
        at.text_input("round_name").set_value(round_name).run(timeout=TIMEOUT)
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

        # Save link dialog: saves the reviewed submission as a draft and shows its persistent link
        logger.info("Testing the save link dialog...")
        # Opening the dialog saves the draft, so the link is there to copy right away
        show_test_dialog(at, "save_link")
        asserts.assert_no_error_on_page(at, "in the save link dialog")

        drafts = db.select(
            ProjectArtifact,
            project_id=at.session_state.project.id,
            artifact_type=BulkSubmissionDraftArtifact.artifact_type,
        )
        asserts.assert_equal(1, len(drafts), "Test that opening the save link dialog saved one draft.")
        saved_artifact = drafts[0].artifact
        asserts.assert_equal(
            CONFIG_POOL_NAME,
            saved_artifact.config["submissions"][0]["pool_name"],
            "Test that the draft kept the config of the reviewed submission.",
        )
        assert not saved_artifact.is_submitted(), "The draft should not be submitted by saving its link"
        assert any(drafts[0].id in code.value for code in at.code), "The dialog should show the link of the draft"

        # Typing a note updates the draft that is already saved
        at.text_area("save_link_note").set_value("Please confirm").run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after typing a note")
        asserts.assert_equal(
            "Please confirm", db.get(ProjectArtifact, id=drafts[0].id).artifact.note, "Test that the note was saved."
        )
        hide_test_dialog(at, "save_link")

        num_jobs_before = len(mock_scheduler.jobs)
        at.button("bulk_submit_all").click().run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after submitting")

        # The draft the link was saved for records the job that was submitted from this page
        submitted_artifact = db.get(ProjectArtifact, id=drafts[0].id).artifact
        asserts.assert_equal("test_user", submitted_artifact.submitted_by, "Test that the draft was marked submitted.")
        asserts.assert_equal(1, len(submitted_artifact.design_job_ids), "Test the crosslink to the submitted job.")

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

    @pytest.mark.parametrize(
        "test_wrapper",
        [BULK_SUBMISSION_FILE],
        indirect=True,
    )
    def test_submit_saved_draft(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """Save a submission draft the way an agent would, then open its link and submit it."""
        at = test_wrapper
        at.run(timeout=TIMEOUT)
        project_id = at.session_state.project.id

        # A draft saved outside the app, e.g. by an agent preparing a submission for the user
        logger.info("Testing saving a submission draft...")
        draft_round = Round(project_id=project_id, name=f"Round for {DRAFT_POOL_NAME_PREFIX}", author="test_agent")
        db.save(draft_round)
        saved_submission = save_bulk_submission_draft(
            config_dict=parse_bulk_config_yaml(EXAMPLE_CONFIG.read_text()),
            project_id=project_id,
            round_id=draft_round.id,
            pool_name_prefix=DRAFT_POOL_NAME_PREFIX,
            note="Please confirm this submission",
            uploaded_files={"5ELI_A.pdb": EXAMPLE_INPUT_PDB.read_bytes()},
            author="test_agent",
        )
        artifact = saved_submission.artifact
        assert not artifact.is_submitted(), "A new draft should not be marked as submitted"
        asserts.assert_equal(1, len(artifact.input_paths), "Test that the input file was recorded on the draft.")
        assert artifact.input_paths[0] != "5ELI_A.pdb", "The uploaded input should have been stored in storage"
        asserts.assert_equal(
            artifact.input_paths,
            artifact.config["submissions"][0]["workflow"]["rfdiffusion_params"]["input_pdb_paths"],
            "Test that the saved config points at the stored input.",
        )

        # Opening the link restores the config and goes straight to the review step
        logger.info("Testing opening the submission draft link...")
        at.query_params[SUBMISSION_QUERY_PARAM] = saved_submission.id
        at.run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after opening the draft link")
        state = at.session_state.workflows[page_key]
        asserts.assert_equal(saved_submission.id, state.loaded_submission_id, "Test that the draft was loaded.")
        asserts.assert_equal(1, len(state.submissions), "Test that the draft config was parsed.")
        assert not state.uploaded_files, "The inputs of a draft are in storage, nothing has to be uploaded again"
        assert "Please confirm this submission" in [info.value for info in at.info], "The note should be shown"

        pool_name = f"{DRAFT_POOL_NAME_PREFIX} {CONFIG_POOL_NAME}"
        asserts.assert_equal(
            pool_name,
            at.table[0].value.loc[("Pool", "Name")].iloc[0],
            "Test that the review table shows the pool name of the draft.",
        )

        # The workflow summary of the submission is shown below the header, before it is submitted
        assert any("fixed segments" in markdown.value for markdown in at.markdown), (
            "The review step should show the workflow summary of the submission"
        )

        # Submitting records the jobs it created back on the draft
        logger.info("Testing submitting the draft...")
        num_jobs_before = len(mock_scheduler.jobs)
        at.button("bulk_submit_all").click().run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after submitting the draft")
        assert len(mock_scheduler.jobs) == num_jobs_before + 1, (
            f"Job should be scheduled with MockScheduler: {mock_scheduler}"
        )

        pool = db.get(Pool, name=pool_name)
        submitted_artifact = db.get(ProjectArtifact, id=saved_submission.id).artifact
        asserts.assert_equal(
            [pool.design_job_id], submitted_artifact.design_job_ids, "Test the crosslink to the submitted job."
        )
        asserts.assert_equal("test_user", submitted_artifact.submitted_by, "Test that the submitting user was saved.")
        assert not submitted_artifact.submission_errors, submitted_artifact.submission_errors

        # Opening the link again reports what it submitted instead of offering to submit it again
        at.switch_page(BULK_SUBMISSION_FILE)
        # Switching pages clears the query parameters, so the link is opened again from scratch
        at.query_params[SUBMISSION_QUERY_PARAM] = saved_submission.id
        at.run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after reopening the submitted draft link")
        assert any("already submitted by test_user" in warning.value for warning in at.warning), (
            f"Expected an already submitted warning, got: {[warning.value for warning in at.warning]}"
        )
        assert "bulk_submit_all" not in [button.key for button in at.button], (
            "A submitted draft should not offer to submit again until the user asks to"
        )

    @pytest.mark.parametrize(
        "test_wrapper",
        [BULK_SUBMISSION_FILE],
        indirect=True,
    )
    def test_submit_draft_after_switching_project(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """Switching project detaches the draft, so its project keeps it unsubmitted."""
        at = test_wrapper
        at.run(timeout=TIMEOUT)
        project_id = at.session_state.project.id

        draft_round = Round(project_id=project_id, name="Round for the detached draft", author="test_agent")
        db.save(draft_round)
        saved_submission = save_bulk_submission_draft(
            config_dict=parse_bulk_config_yaml(EXAMPLE_CONFIG.read_text()),
            project_id=project_id,
            round_id=draft_round.id,
            pool_name_prefix="test bulk detached",
            uploaded_files={"5ELI_A.pdb": EXAMPLE_INPUT_PDB.read_bytes()},
            author="test_agent",
        )
        at.query_params[SUBMISSION_QUERY_PARAM] = saved_submission.id
        at.run(timeout=TIMEOUT)
        asserts.assert_equal(
            saved_submission.id,
            at.session_state.workflows[page_key].loaded_submission_id,
            "Test that the draft was loaded.",
        )

        # Select another project, as the sidebar does, which keeps the state of this page
        other_project = Project(name="Other project of the detached draft", author="test_user")
        db.save(other_project)
        at.session_state.project = other_project
        at.run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after switching project")

        state = at.session_state.workflows[page_key]
        assert not state.saved_submission, "The draft of the other project should have been detached"
        assert any("no longer submitted as the draft" in info.value for info in at.info), (
            f"Expected a notice that the draft was detached, got: {[info.value for info in at.info]}"
        )

        # The config can still be submitted, it just creates a submission of the selected project
        num_jobs_before = len(mock_scheduler.jobs)
        at.button("bulk_submit_all").click().run(timeout=TIMEOUT)
        asserts.assert_no_error_on_page(at, "after submitting in the other project")
        assert len(mock_scheduler.jobs) == num_jobs_before + 1, (
            f"Job should be scheduled with MockScheduler: {mock_scheduler}"
        )
        pool = db.get(Pool, name=f"test bulk detached {CONFIG_POOL_NAME}")
        submitted_round = db.get(Round, id=db.get(Pool, id=pool.id).round_id)
        asserts.assert_equal(
            other_project.id, submitted_round.project_id, "Test that the submission went to the selected project."
        )

        draft_artifact = db.get(ProjectArtifact, id=saved_submission.id).artifact
        assert not draft_artifact.is_submitted(), "The draft of the other project should be left unsubmitted"
        assert not draft_artifact.design_job_ids, draft_artifact.design_job_ids


def test_format_param_values_marks_list_defaults():
    """A list parameter is labelled as the default when it matches it, see format_param_values."""
    values = pd.Series(
        {
            ("Interface analysis", "target_chains"): ["B"],
            ("Interface analysis", "binder_chains"): ["C"],
            ("Workflow", "type"): "Biotite interface analysis",
        },
        name="Value",
    )
    default_values = pd.Series(
        {
            ("Interface analysis", "target_chains"): ["B"],
            ("Interface analysis", "binder_chains"): ["B"],
            ("Workflow", "type"): "Biotite interface analysis",
        },
        name="Value",
    )

    formatted = format_param_values(values, default_values=default_values)

    assert formatted[("Interface analysis", "target_chains")] == ":grey[B (default)]"
    assert formatted[("Interface analysis", "binder_chains")] == "C"
    # The type is not labelled, even though every workflow of a type has the same one
    assert formatted[("Workflow", "type")] == "Biotite interface analysis"
