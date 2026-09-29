from ovo import Design, DesignSpec, DesignChain, DesignWorkflow
from ovo.app.components.workflow_visualization_components import (
    get_selected_alignments,
    get_shared_alignment_options,
)
from ovo.core.database.models import AlignmentOption
from ovo.core.database.models_rfdiffusion import RFdiffusionScaffoldDesignWorkflow


def make_design(designed_chain_ids: list[list[str]], design_id: str = "ovo_tap_1", contigs=None) -> Design:
    return Design(
        id=design_id,
        pool_id="tap",
        spec=DesignSpec(
            chains=[
                DesignChain(
                    type="protein",
                    chain_ids=chain_ids,
                    sequence="ACDEFGHIK",
                    contig=contigs[i] if contigs else None,
                )
                for i, chain_ids in enumerate(designed_chain_ids)
            ]
        ),
    )


def test_alignment_options_split_design_and_target_chains():
    design = make_design([["A"]])

    options = DesignWorkflow.get_alignment_options(design, chain_ids=["A", "B", "C"])

    assert options == {
        "On target": AlignmentOption([("B", None), ("C", None)]),
        "On design": AlignmentOption([("A", None)]),
    }


def test_alignment_options_without_target_chain():
    design = make_design([["A"]])

    options = DesignWorkflow.get_alignment_options(design, chain_ids=["A"])

    assert options == {"On design": AlignmentOption([("A", None)])}, (
        "Structures with no target chain should not offer aligning on target"
    )


def test_alignment_options_ignore_chains_missing_from_structure():
    # a chain can be in the design spec but absent from the structure we are visualizing
    design = make_design([["A", "D"]])

    options = DesignWorkflow.get_alignment_options(design, chain_ids=["A", "B"])

    assert options == {"On target": AlignmentOption([("B", None)]), "On design": AlignmentOption([("A", None)])}


def test_scaffold_alignment_options_include_the_motif():
    # 10 generated residues, then 5 residues scaffolded from residues 20-24 of input chain A, then 10 generated
    design = make_design([["A"]], contigs=["10-10/A20-24/10-10"])

    options = RFdiffusionScaffoldDesignWorkflow.get_alignment_options(design, chain_ids=["A"])

    assert options["On motif"] == AlignmentOption(
        [("A", [11, 12, 13, 14, 15])], representation="cartoon+ball-and-stick", all_atom=True
    ), "The motif is the part of the design taken from the input structure, aligned on all of its atoms"
    assert "On design" in options, "The options of the base workflow should still be offered"


def test_scaffold_alignment_options_without_contig():
    design = make_design([["A"]])

    options = RFdiffusionScaffoldDesignWorkflow.get_alignment_options(design, chain_ids=["A"])

    assert "On motif" not in options, "Designs without a contig have no known motif"


def test_shared_alignment_options_across_workflows():
    # an RFdiffusion binder is chain A and its target chain B, a BindCraft binder is the other way around
    rfdiffusion_design = make_design([["A"]], design_id="ovo_tap_1")
    bindcraft_design = make_design([["B"]], design_id="ovo_tap_2")
    options_by_design = {
        design.id: DesignWorkflow.get_alignment_options(design, chain_ids=["A", "B"])
        for design in [rfdiffusion_design, bindcraft_design]
    }

    assert get_shared_alignment_options(options_by_design) == ["On target", "On design"], (
        "Designs of different workflows share the option labels, each aligned on its own chains"
    )
    assert options_by_design["ovo_tap_1"]["On target"].chain_residue_mapping == [("B", None)]
    assert options_by_design["ovo_tap_2"]["On target"].chain_residue_mapping == [("A", None)]


def test_shared_alignment_options_only_offers_options_of_all_designs():
    binder_design = make_design([["A"]], design_id="ovo_tap_1")
    # a prediction of the binder alone has no target chain, so it cannot be aligned on target
    binder_only_design = make_design([["A"]], design_id="ovo_tap_2")
    options_by_design = {
        "ovo_tap_1": DesignWorkflow.get_alignment_options(binder_design, chain_ids=["A", "B"]),
        "ovo_tap_2": DesignWorkflow.get_alignment_options(binder_only_design, chain_ids=["A"]),
    }

    assert get_shared_alignment_options(options_by_design) == ["On design"]


def test_shared_alignment_options_without_designs():
    assert get_shared_alignment_options({}) == []


def test_selected_alignments_use_the_chains_of_each_design():
    # the same "On target" label means chain B for the first design and chain A for the second one
    options_by_design = {
        "ovo_tap_1": DesignWorkflow.get_alignment_options(
            make_design([["A"]], design_id="ovo_tap_1"), chain_ids=["A", "B"]
        ),
        "ovo_tap_2": DesignWorkflow.get_alignment_options(
            make_design([["B"]], design_id="ovo_tap_2"), chain_ids=["A", "B"]
        ),
    }
    # two structures of the first design and one of the second one
    structure_design_ids = ["ovo_tap_1", "ovo_tap_1", "ovo_tap_2"]

    alignments = get_selected_alignments(structure_design_ids, options_by_design, "On target")

    assert [option.chain_residue_mapping for option in alignments] == [
        [("B", None)],
        [("B", None)],
        [("A", None)],
    ], "Every structure should be aligned using the chains of its own design"
