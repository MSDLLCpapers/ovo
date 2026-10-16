import os

import pytest
from streamlit.testing.v1 import AppTest

from ovo import storage
from ovo.core.database.models_rfdiffusion import RFdiffusionBinderDesignWorkflow
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.constants import OVO_PAGES, TIMEOUT
from tests.unit_tests.utils.rfdiffusion_utils import click_nav_button

DIVERSIFICATION_FILE = os.path.join(OVO_PAGES, "rfdiffusion", "binder_diversification.py")

# Sections of the page, see the sections of show_prev_next_sections
SELECTION_SECTION = 2
SEQUENCE_DESIGN_SECTION = 3


@pytest.mark.parametrize("test_wrapper", [DIVERSIFICATION_FILE], indirect=True)
def test_sequence_redesign_protocol(test_wrapper, ovo_resources_path):
    """The sequence redesign protocol submits the input structures as custom backbones."""
    at = test_wrapper
    workflow = set_input_structure(at, ovo_resources_path, section=SELECTION_SECTION)
    at.run(timeout=TIMEOUT)
    asserts.assert_no_error_on_page(at, "selection section")

    # Partial diffusion is the default protocol, which designs backbones with RFdiffusion
    assert not workflow.rfdiffusion_params.custom_backbones

    # The protocol is picked in the sequence design section
    click_nav_button(at)
    # A segmented control is only reachable as a button_group in older Streamlit versions
    protocol_control = next(control for control in at.get("button_group") if control.key == "diversification_protocol")
    protocol_control.set_value("Sequence redesign").run(timeout=TIMEOUT)
    asserts.assert_no_error_on_page(at, "sequence design section of sequence redesign")
    assert workflow.rfdiffusion_params.custom_backbones == workflow.rfdiffusion_params.input_pdb_paths

    # Nothing is previewed without backbone design, so the settings follow the sequence design
    click_nav_button(at)
    asserts.assert_no_error_on_page(at, "settings section of sequence redesign")
    assert [subheader.value for subheader in at.subheader] == ["Settings"]
    # The parameters of RFdiffusion are hidden, including the advanced ones
    assert "Model weights" not in [radio.label for radio in at.radio]
    assert not [
        number_input for number_input in at.number_input if number_input.label.startswith("Number of structure designs")
    ]
    assert not [number_input for number_input in at.number_input if "timesteps" in number_input.label]


@pytest.mark.parametrize("test_wrapper", [DIVERSIFICATION_FILE], indirect=True)
def test_selection_action_of_equally_many_residues(test_wrapper, ovo_resources_path):
    """Selecting as many residues as are already selected is still a change that can be applied."""
    at = test_wrapper
    workflow = set_input_structure(at, ovo_resources_path, section=SELECTION_SECTION)
    # Four residues are selected, none of them one of the four in contact with the target
    workflow.set_selected_segments(["A1-4"], contig_index=0, partial_diffusion=True)
    at.run(timeout=TIMEOUT)
    asserts.assert_no_error_on_page(at, "selection section")

    select_menu(at).set_value("Residues in contact with target").run(timeout=TIMEOUT)
    apply_button = next(button for button in at.button if button.label == "Select")
    assert not apply_button.disabled, "Selecting other residues is a change even when there are as many"

    # The dialog is a fragment, which AppTest cannot rerun on its own - the menu that opened it is
    # set again, so that the dialog is shown in the same run the apply button is clicked in
    select_menu(at).set_value("Residues in contact with target")
    apply_button.click()
    at.run(timeout=TIMEOUT)
    asserts.assert_no_error_on_page(at, "selection section after applying the action")
    assert workflow.get_selected_segments(contig_index=0, partial_diffusion=True) == ["A8-8", "A11-12", "A15-15"]


@pytest.mark.parametrize("test_wrapper", [DIVERSIFICATION_FILE], indirect=True)
def test_invalid_stored_amino_acid_bias(test_wrapper, ovo_resources_path):
    """An amino acid bias that cannot be parsed stays editable, see show_mpnn_sequence_design_inputs."""
    at = test_wrapper
    workflow = set_input_structure(at, ovo_resources_path, section=SEQUENCE_DESIGN_SECTION)
    workflow.protein_mpnn_params.bias_aa = "F:"
    at.run(timeout=TIMEOUT)

    assert not at.exception, [exception.value for exception in at.exception]
    assert [error.value for error in at.error] == [
        "Invalid bias, expected amino acids and their bias as for example F:1,K:-1"
    ]
    assert at.text_input("mpnn_bias_custom").value == "F:"

    # The value can be corrected in the input it is kept in
    at.text_input("mpnn_bias_custom").set_value("F:1").run(timeout=TIMEOUT)
    asserts.assert_no_error_on_page(at, "sequence design section")
    assert workflow.protein_mpnn_params.bias_aa == "F:1"


def select_menu(at: AppTest):
    """Get the menu button of the Select operation of the selection section."""
    return next(button for button in at.get("menu_button") if button.key == "selection_operation_Select")


def set_input_structure(at: AppTest, ovo_resources_path: str, section: int) -> RFdiffusionBinderDesignWorkflow:
    """Set up the page at the given section with one input structure, as the input step would.

    The input step takes design IDs or an uploaded file, neither of which AppTest can provide, so the
    workflow it would leave behind is written to the session state instead.

    :return: the workflow of the page, which the page keeps updating
    """
    from ovo.app.pages.rfdiffusion.binder_diversification import get_contigs_for_input_structures

    input_pdb_path = storage.store_input(
        project_id="test_project",
        file_path=os.path.join(ovo_resources_path, "examples/inputs/ovo_buv_0789_cycle02_trimmed.pdb"),
    )
    workflow = RFdiffusionBinderDesignWorkflow(input_name="test")
    workflow.rfdiffusion_params.input_pdb_paths = [input_pdb_path]
    workflow.rfdiffusion_params.partial_diffusion = True
    workflow.rfdiffusion_params.contigs = get_contigs_for_input_structures([input_pdb_path])
    at.session_state["workflows"] = {DIVERSIFICATION_FILE: workflow}
    at.session_state["current_section_" + DIVERSIFICATION_FILE] = section
    return workflow
