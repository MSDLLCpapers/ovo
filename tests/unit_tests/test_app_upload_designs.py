import os
import time

import pytest
from pytest_mock import MockerFixture

from ovo import db
from ovo.app.utils.testing import show_test_dialog
from ovo.core.database import Pool, Design
from tests.unit_tests.utils import asserts
from tests.unit_tests.utils.constants import TIMEOUT, DESIGNS_FILE


class TestUploadCSV:
    """Test uploading designs from CSV files through the Streamlit UI."""

    @pytest.mark.parametrize(
        "test_wrapper",
        [DESIGNS_FILE],
        indirect=True,
    )
    def test_upload_csv_file(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """Test uploading designs from a CSV file through the UI."""
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Show the dialog in test mode (bypasses button click requirement)
        show_test_dialog(at, "create_new_pool")
        at.run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After opening upload dialog")

        # Load the sample CSV file
        csv_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "ovo",
            "resources",
            "examples",
            "inputs",
            "sample_designs.csv",
        )

        with open(csv_path, "rb") as f:
            csv_content = f.read()

        # Upload the CSV file - Streamlit testing expects (filename, content, mime_type)
        file_uploader = at.file_uploader("uploader")
        file_uploader.set_value([("sample_designs.csv", csv_content, "text/csv")]).run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After CSV upload")

        # Verify the file was uploaded
        assert file_uploader.value is not None, "File should be uploaded"
        assert len(file_uploader.value) == 1, "Should have one file uploaded"
        assert file_uploader.value[0].name == "sample_designs.csv", "File name should match"

        # Now the dialog should show column configuration UI
        # Select ID column (should default to "design_id")
        id_col_selector = at.selectbox("id_column")
        assert id_col_selector.value == "design_id", "Default ID column should be design_id"

        # Select sequence columns A and B
        seq_col_multiselect = at.multiselect("sequence_columns")
        seq_col_multiselect.set_value(["A", "B"]).run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After selecting sequence columns")

        # Verify chain ID inputs are shown with correct defaults
        chain_id_A = at.text_input("chain_id_A")
        chain_id_B = at.text_input("chain_id_B")
        assert chain_id_A.value == "A", "Chain ID for column A should be prefilled with 'A'"
        assert chain_id_B.value == "B", "Chain ID for column B should be prefilled with 'B'"

        # Enter pool name (use timestamp to ensure uniqueness)
        pool_name = f"test_csv_upload_pool_{int(time.time())}"
        pool_name_input = at.text_input("pool_name")
        pool_name_input.set_value(pool_name).run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After entering pool name")

        # Verify the pool name is set correctly
        assert pool_name_input.value == pool_name, (
            f"Pool name should be set to '{pool_name}', got '{pool_name_input.value}'"
        )

        # Click submit button
        submit_btn = at.button("submit")
        assert not submit_btn.disabled, "Submit button should be enabled"

        # Click submit - this will execute the submission logic and rerun the page
        submit_btn.click().run(timeout=TIMEOUT)

        # The submission handler will save to DB and call st.rerun()
        # The dialog may reopen on rerun (because is_test_dialog_shown is still true)
        # but the data should already be saved to the database

        pools = db.select(Pool, name=pool_name)
        assert len(pools) == 1, f"Should have exactly 1 pool named '{pool_name}'"
        pool = pools[0]

        # Verify designs were created
        designs = db.select(Design, pool_id=pool.id)
        assert len(designs) == 3, f"Should have created 3 designs, found {len(designs)}"

        # Verify design IDs
        design_ids = sorted([d.id for d in designs])
        assert any("design_001" in d_id for d_id in design_ids), "design_001 should be in database"
        assert any("design_002" in d_id for d_id in design_ids), "design_002 should be in database"
        assert any("design_003" in d_id for d_id in design_ids), "design_003 should be in database"

        # Verify design structure
        for design in designs:
            assert len(design.spec.chains) == 2, f"Each design should have 2 chains, got {len(design.spec.chains)}"
            assert design.spec.chains[0].chain_ids == ["A"], (
                f"First chain should be ['A'], got {design.spec.chains[0].chain_ids}"
            )
            assert design.spec.chains[1].chain_ids == ["B"], (
                f"Second chain should be ['B'], got {design.spec.chains[1].chain_ids}"
            )
            assert design.spec.chains[0].type == "protein", "First chain type should be protein"
            assert design.spec.chains[1].type == "protein", "Second chain type should be protein"
            assert design.spec.chains[0].sequence is not None, "First chain should have a sequence"
            assert design.spec.chains[1].sequence is not None, "Second chain should have a sequence"
            assert design.structure_path is None, "Sequence-only designs should have no structure file"

    @pytest.mark.parametrize(
        "test_wrapper",
        [DESIGNS_FILE],
        indirect=True,
    )
    def test_upload_pdb_file(self, mocker: MockerFixture, test_wrapper, mock_scheduler) -> None:
        """Test uploading designs from a PDB structure file through the UI."""
        at = test_wrapper
        at.run(timeout=TIMEOUT)

        # Show the dialog in test mode
        show_test_dialog(at, "create_new_pool")
        at.run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After opening upload dialog")

        # Load the PDB file
        pdb_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "ovo",
            "resources",
            "examples",
            "inputs",
            "5ELI_A.pdb",
        )

        with open(pdb_path, "rb") as f:
            pdb_content = f.read()

        # Upload the PDB file
        file_uploader = at.file_uploader("uploader")
        file_uploader.set_value([("5ELI_A.pdb", pdb_content, "chemical/x-pdb")]).run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After PDB upload")

        # Verify the file was uploaded
        assert file_uploader.value is not None, "File should be uploaded"
        assert len(file_uploader.value) == 1, "Should have one file uploaded"
        assert file_uploader.value[0].name == "5ELI_A.pdb", "File name should match"

        # For PDB files, we need to specify chain IDs to analyze
        chains_input = at.text_input("chains_to_analyze")
        chains_input.set_value("A").run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After entering chains")

        # Enter pool name
        pool_name = f"test_pdb_upload_pool_{int(time.time())}"
        pool_name_input = at.text_input("pool_name")
        pool_name_input.set_value(pool_name).run(timeout=TIMEOUT)

        asserts.assert_no_error_on_page(at, "After entering pool name")

        # Click submit
        submit_btn = at.button("submit")
        assert not submit_btn.disabled, "Submit button should be enabled"

        submit_btn.click().run(timeout=TIMEOUT)

        pools = db.select(Pool, name=pool_name)
        assert len(pools) == 1, f"Should have exactly 1 pool named '{pool_name}'"
        pool = pools[0]

        # Verify design was created
        designs = db.select(Design, pool_id=pool.id)
        assert len(designs) == 1, f"Should have created 1 design from PDB file"

        # Verify design structure
        design = designs[0]
        assert design.id == f"ovo_{pool.id}_5ELI_A", "Design ID should match PDB filename"
        assert len(design.spec.chains) >= 1, "Design should have at least 1 chain"
        assert design.spec.chains[0].chain_ids == ["A"], "Chain should be A"
        assert design.spec.chains[0].type == "protein", "Chain type should be protein"
        assert design.spec.chains[0].sequence is not None, "Chain should have a sequence"
        assert design.structure_path is not None, "Structure file should be stored"
        assert design.structure_path.endswith(".pdb"), "Structure file should be PDB"
