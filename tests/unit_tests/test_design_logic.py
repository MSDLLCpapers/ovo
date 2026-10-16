import zipfile

import pandas as pd
import pytest

from ovo import storage
from ovo.core.logic import design_logic
from ovo.core.logic.design_logic_rfdiffusion import prepare_custom_backbones
from ovo.core.utils.pdb import get_standardized_remarks_from_pdb_str


class TestTabularFileUpload:
    """Test creating designs from tabular files."""

    def test_create_designs_from_dataframe(self):
        """Test creating designs from a DataFrame."""
        df = pd.DataFrame(
            {
                "design_id": ["design_001", "design_002"],
                "seq_A": [
                    "MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLLKRMKV",
                    "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDG",
                ],
                "seq_B": ["MGSSHHHHHH", "MGSSHHHHHHSSGLVPR"],
                "description": ["Test design 1", "Test design 2"],
            }
        )

        designs = design_logic.create_designs_from_dataframe(
            df=df,
            id_column="design_id",
            column_chains={"seq_A": "A", "seq_B": "B"},
            pool_id="testpool123",
        )

        assert len(designs) == 2

        # Check first design
        design1 = designs[0]
        assert design1.id == "ovo_testpool123_design_001"
        assert len(design1.spec.chains) == 2
        assert design1.spec.chains[0].chain_ids == ["A"]
        assert design1.spec.chains[0].sequence == "MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLLKRMKV"
        assert design1.spec.chains[0].type == "protein"
        assert design1.spec.chains[1].chain_ids == ["B"]
        assert design1.spec.chains[1].sequence == "MGSSHHHHHH"
        assert design1.structure_path is None  # No structure file for sequence-only designs

        # Check second design
        design2 = designs[1]
        assert design2.id == "ovo_testpool123_design_002"
        assert len(design2.spec.chains) == 2


def test_prepare_custom_binder_backbones(tmp_path, example_pdb_path):
    """Custom binder backbones should be zipped with the REMARK header of their contig."""
    storage_paths = [
        storage.store_input(
            project_id="test_project", file_path=str(example_pdb_path), filename=f"backbone_{index}.pdb"
        )
        for index in range(2)
    ]

    prepared_path = prepare_custom_backbones(
        custom_backbones=storage_paths,
        workdir=str(tmp_path),
        design_type="binder",
        contigs=["5-5/A6-10/0 B20-130", "10-10/0 B20-130"],
    )

    assert prepared_path.endswith("custom_backbones.zip")
    with zipfile.ZipFile(prepared_path) as zip_file:
        assert sorted(zip_file.namelist()) == ["backbone_0.pdb", "backbone_1.pdb"]
        partial_selection_pdb = zip_file.read("backbone_0.pdb").decode()
        whole_binder_pdb = zip_file.read("backbone_1.pdb").decode()
    assert get_standardized_remarks_from_pdb_str(partial_selection_pdb) == {
        "Standardized contig": "5-5/A6-10/0 B20-130",
        "Chains": "A B",
    }

    # The binder residues kept fixed are labelled for ProteinMPNN-FastRelax, which reads the labels
    # rather than the contig - here only the first five residues of the binder are redesigned
    assert [line for line in partial_selection_pdb.splitlines() if "PDBinfo-LABEL" in line] == [
        f"REMARK PDBinfo-LABEL:{residue: >5} FIXED" for residue in range(6, 11)
    ]
    # Nothing is fixed when the whole binder is redesigned
    assert "PDBinfo-LABEL" not in whole_binder_pdb

    # Each backbone is redesigned according to its own contig, so there must be one for each of them
    with pytest.raises(ValueError, match="one contig for each custom backbone"):
        prepare_custom_backbones(
            custom_backbones=storage_paths,
            workdir=str(tmp_path),
            design_type="binder",
            contigs=["5-5/A6-10/0 B20-130"],
        )
