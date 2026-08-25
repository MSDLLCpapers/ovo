import pandas as pd

from ovo import db, schedulers, storage
from ovo.core.database.models_refolding import RefoldingWorkflow
from ovo.core.logic import descriptor_logic, design_logic
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_sequence_only_refolding(project_data):
    project, project_round, _ = project_data

    sequence_pool = db.Pool(
        id=db.Pool.generate_id(),
        round_id=project_round.id,
        name="Sequence Pool for Refolding",
        author="test",
    )
    db.save(sequence_pool)
    designs = design_logic.create_designs_from_dataframe(
        df=pd.read_csv(RESOURCES_DIR / "examples/inputs/sample_designs.csv"),
        id_column="design_id",
        column_chains={"A": "A", "B": "B"},
        pool_id=sequence_pool.id,
    )
    db.save_all(designs)
    design_ids = [d.id for d in designs]

    test = "af2_model_1_ptm_seq_3rec"
    refolding: RefoldingWorkflow = RefoldingWorkflow(
        # the sequence refolding script predicts a single chain at a time
        chains=["A"],
        design_ids=design_ids,
        tests=[test],
        design_type="sequence",
    )
    refolding.validate()

    params = refolding.prepare_params(workdir=schedulers[TEST_SCHEDULER_KEY].workdir)
    assert params["input_designs"].endswith(".csv"), "Should prepare a csv file for sequence-only refolding"
    prepared_df = pd.read_csv(params["input_designs"], index_col=0)
    assert prepared_df.index.tolist() == design_ids, "Prepared CSV should have design IDs as index"
    assert prepared_df["A"].tolist() == [d.spec.get_chain("A").sequence for d in designs], (
        "Prepared CSV should contain the correct sequences"
    )

    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=refolding, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    af2_plddt = db.select_descriptor_values(f"refolding|{test}|plddt", design_ids)
    assert len(af2_plddt.dropna()) == 3
    assert (af2_plddt > 10).all()

    af2_ptm = db.select_descriptor_values(f"refolding|{test}|ptm", design_ids)
    assert len(af2_ptm.dropna()) == 3
    assert ((af2_ptm >= 0) & (af2_ptm <= 1)).all()

    af2_pdb_paths = db.select_descriptor_values(f"refolding|{test}|af2_structure_path", design_ids)
    assert len(af2_pdb_paths.dropna()) == 3
    assert af2_pdb_paths.iloc[0].endswith(".pdb")
    assert "ATOM " in storage.read_file_str(af2_pdb_paths.iloc[0])
