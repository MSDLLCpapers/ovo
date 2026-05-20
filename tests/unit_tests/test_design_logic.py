import pandas as pd

from ovo.core.logic import design_logic


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
