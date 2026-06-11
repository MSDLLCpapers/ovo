import logging

import pytest
from pytest_mock import MockerFixture

from ovo.core.database.models_rfdiffusion import ProteinMPNNParams
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.constants import TIMEOUT, SCAFFOLD_DESIGN_FILE
from tests.unit_tests.utils.mocking import mock_molstar
from tests.unit_tests.utils.rfdiffusion_utils import click_nav_button, settings_tab, review_and_submit_tab

logger = logging.getLogger(__name__)

page_key = SCAFFOLD_DESIGN_FILE


class TestScaffoldDesign:
    """Scaffold design page tests."""

    @pytest.mark.parametrize(
        "test_wrapper",
        [SCAFFOLD_DESIGN_FILE],
        indirect=True,
    )
    def test_default_values(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """
        Test scaffold design workflow with PDB code input.
        """
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Intro tab — skip
        click_nav_button(at)

        # Input tab
        at.text_input("input_pdb_code").set_value("1myj").run(timeout=TIMEOUT)
        workflow = at.session_state.workflows[page_key]
        assert workflow.rfdiffusion_params.input_pdb.endswith("1myj.pdb"), "Verify that PDB code was registered."
        asserts.assert_no_error_on_page(at, "input tab")

        # Selection tab
        click_nav_button(at)
        with mock_molstar(
            {
                "sequenceSelections": [{"chainId": "A", "residues": list(range(3, 17 + 1)) + list(range(59, 77 + 1))}],
            }
        )(mocker):
            logger.info("Testing selection tab...")
            at.run()
            asserts.assert_no_error_on_page(at, "selection tab")
            workflow = at.session_state.workflows[page_key]
            assert workflow.selected_segments == ["A3-17", "A59-77"]

        # Preview tab
        click_nav_button(at)
        workflow = at.session_state.workflows[page_key]
        contig = workflow.rfdiffusion_params.contig
        assert contig == "A3-17/A59-77"
        asserts.assert_equal(
            contig,
            at.text_input("input_contig").value,
            "Verify that displayed contig is equal to contig in workflow parameters.",
        )

        # Inpainting tab
        click_nav_button(at)
        at.run()
        with mock_molstar(
            {
                "sequenceSelections": [{"chainId": "A", "residues": list(range(5, 7 + 1)) + list(range(61, 65 + 1))}],
            }
        )(mocker):
            logger.info("Testing inpainting tab...")
            at.run()
            asserts.assert_no_error_on_page(at, "inpainting tab")
            workflow = at.session_state.workflows[page_key]
            assert workflow.rfdiffusion_params.inpaint_seq == "A5-7/A61-65"

        # Settings tab
        click_nav_button(at)
        pool_name = "test scaffold design default values"
        settings_tab(at, page_key, pool_name, contig=contig)

        num_sequences = at.number_input("num_sequences")
        assert num_sequences.value == ProteinMPNNParams().num_sequences  # as per ProteinMPNNParams default

        # Confirmation tab
        click_nav_button(at)
        review_and_submit_tab(at, mock_scheduler, pool_name)
