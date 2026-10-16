import logging

import pytest
from pytest_mock import MockerFixture

from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.constants import TIMEOUT, DISCO_DESIGN_FILE
from tests.unit_tests.utils.rfdiffusion_utils import click_nav_button, review_and_submit_tab
from ovo.app.utils.testing import show_test_dialog

logger = logging.getLogger(__name__)

page_key = DISCO_DESIGN_FILE


class TestDiscoDesign:
    """DISCO ligand design page tests."""

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_ccd_ligand_and_submit(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Intro tab — skip to settings
        click_nav_button(at)

        # Settings tab: create a round so a pool can be submitted
        show_test_dialog(at, "create_round")
        # Run after typing the name, the Create round button is disabled while the name is empty -
        # which it is whenever the last round of the project is not named "<something> <number>"
        at.text_input("round_name").set_value("DISCO round").run(timeout=TIMEOUT)
        at.button("create_round").click().run(timeout=TIMEOUT)

        pool_name = "DISCO CCD test"
        at.text_input("input_pool_name").set_value(pool_name).run(timeout=TIMEOUT)

        # Ligand: CCD code mode is the default radio option
        at.text_input("disco_ccd_code").set_value("ATP").run(timeout=TIMEOUT)
        at.number_input("disco_sequence_length").set_value(100).run(timeout=TIMEOUT)
        at.number_input("disco_num_designs").set_value(1).run(timeout=TIMEOUT)

        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.ligand == "CCD_ATP"
        assert workflow.disco_params.sequence_length == 100

        # The generated JSON should be shown on the page
        assert any("CCD_ATP" in code.value for code in at.code), "Generated JSON should contain the CCD ligand"
        asserts.assert_no_error_on_page(at, "settings tab")

        # Review tab + submit
        click_nav_button(at)
        review_and_submit_tab(at, mock_scheduler, pool_name)

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_smiles_ligand(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        click_nav_button(at)

        # Switch ligand mode to SMILES
        at.radio("disco_ligand_mode").set_value("SMILES").run(timeout=TIMEOUT)
        at.text_input("disco_smiles").set_value("CC(=O)Oc1ccccc1C(=O)O").run(timeout=TIMEOUT)

        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.ligand == "CC(=O)Oc1ccccc1C(=O)O"
        assert workflow.disco_params.ligand_file_path is None
        asserts.assert_no_error_on_page(at, "settings tab")

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_unconditional_no_ligand(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        click_nav_button(at)

        # Switch ligand mode to "No ligand (unconditional)"
        at.radio("disco_ligand_mode").set_value("No ligand (unconditional)").run(timeout=TIMEOUT)

        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.ligand is None
        assert workflow.disco_params.ligand_file_path is None
        # No warning should be shown in unconditional mode
        assert not at.warning, f"Unexpected warning in unconditional mode: {[w.value for w in at.warning]}"
        # Generated JSON should contain only a protein chain (no ligand entity)
        assert any('"proteinChain"' in code.value for code in at.code)
        assert not any('"ligand"' in code.value for code in at.code)
        asserts.assert_no_error_on_page(at, "settings tab")

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_settings_preserved_after_review(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        click_nav_button(at)

        # CCD ligand survives going to review and back
        at.text_input("disco_ccd_code").set_value("ATP").run(timeout=TIMEOUT)
        at.number_input("disco_sequence_length").set_value(150).run(timeout=TIMEOUT)
        click_nav_button(at)
        click_nav_button(at, key="back_button_top")
        assert at.text_input("disco_ccd_code").value == "ATP"
        assert at.number_input("disco_sequence_length").value == 150
        assert at.session_state.workflows[page_key].disco_params.ligand == "CCD_ATP"

        # SMILES ligand survives going to review and back
        at.radio("disco_ligand_mode").set_value("SMILES").run(timeout=TIMEOUT)
        at.text_input("disco_smiles").set_value("CC(=O)Oc1ccccc1C(=O)O").run(timeout=TIMEOUT)
        click_nav_button(at)
        click_nav_button(at, key="back_button_top")
        assert at.radio("disco_ligand_mode").value == "SMILES"
        assert at.text_input("disco_smiles").value == "CC(=O)Oc1ccccc1C(=O)O"

        # Unconditional mode survives even though the ligand is empty
        at.radio("disco_ligand_mode").set_value("No ligand (unconditional)").run(timeout=TIMEOUT)
        click_nav_button(at)
        click_nav_button(at, key="back_button_top")
        assert at.radio("disco_ligand_mode").value == "No ligand (unconditional)"

        # Custom JSON mode and its content survive going to review and back
        at.toggle("disco_custom_json_mode").set_value(True).run(timeout=TIMEOUT)
        custom_json = at.text_area("disco_custom_json").value
        click_nav_button(at)
        click_nav_button(at, key="back_button_top")
        assert at.toggle("disco_custom_json_mode").value is True
        assert at.text_area("disco_custom_json").value == custom_json
        asserts.assert_no_error_on_page(at, "settings tab")

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_empty_ligand_warning_only_after_interaction(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        click_nav_button(at)

        # On first load the CCD field is empty but untouched — no warning should be shown yet
        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.ligand is None
        assert not at.warning, f"Unexpected warning before interaction: {[w.value for w in at.warning]}"

        # After the user interacts with the CCD field and leaves it empty, the warning appears
        at.text_input("disco_ccd_code").set_value("ATP").run(timeout=TIMEOUT)
        at.text_input("disco_ccd_code").set_value("").run(timeout=TIMEOUT)
        assert workflow.disco_params.ligand is None
        assert at.warning, "Expected a warning after interacting with an empty CCD field"
        assert any("unconditional" in w.value.lower() for w in at.warning)

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_empty_ligand_warning_on_review(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Intro -> settings -> review without specifying a ligand
        click_nav_button(at)
        click_nav_button(at)

        # Reaching the review step is an explicit attempt to proceed, so the warning should appear
        assert at.warning, "Expected a warning on the review step when no ligand was specified"
        assert any("unconditional" in w.value.lower() for w in at.warning)

    @pytest.mark.parametrize("test_wrapper", [DISCO_DESIGN_FILE], indirect=True)
    def test_custom_json_mode(self, test_wrapper) -> None:
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        click_nav_button(at)

        workflow = at.session_state.workflows[page_key]
        # In structured mode, custom_input_json is not set
        assert workflow.disco_params.custom_input_json is None

        # Enable custom JSON mode — the structured ligand fields become disabled and an editor appears
        at.toggle("disco_custom_json_mode").set_value(True).run(timeout=TIMEOUT)
        assert at.text_input("disco_ccd_code").disabled, "Ligand field should be disabled in custom JSON mode"

        custom = '[{"sequences": [{"proteinChain": {"sequence": "------", "count": 2}}], "name": "my_job"}]'
        at.text_area("disco_custom_json").set_value(custom).run(timeout=TIMEOUT)
        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.custom_input_json == custom
        asserts.assert_no_error_on_page(at, "settings tab")

        # Disabling custom JSON mode clears the custom JSON again
        at.toggle("disco_custom_json_mode").set_value(False).run(timeout=TIMEOUT)
        workflow = at.session_state.workflows[page_key]
        assert workflow.disco_params.custom_input_json is None
