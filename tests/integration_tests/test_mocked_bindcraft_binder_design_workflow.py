from ovo import db, design_logic, storage
from ovo.core.database import models_bindcraft
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY


def test_mocked_bindcraft_miniprotein(project_data):
    project, project_round, custom_pool = project_data

    workflow = models_bindcraft.BindCraftBinderDesignWorkflow(
        bindcraft_params=models_bindcraft.BindCraftParams(
            # Note that this is just mocked input, real outputs are based on mocked-output.zip
            input_pdb_path=storage.store_input(project.id, RESOURCES_DIR / "examples/inputs/5ELI_A.pdb"),
            # Using trimmed structure
            target_chains="E",
            binder_length="50,100",
            hotspots="E64,E88,E96",
            number_of_final_designs=20,
            time_limit_hours=6,
            filter_type="Default",
            design_protocol="Default",
            interface_protocol="AlphaFold2",
            template_protocol="Default",
            prediction_protocol="Default",
            # Use this to run multiple parallel copies of BindCraft
            num_replicas=1,
            # dictionary with advanced settings that override default values
            # for example {"omit_AAs": ""}
            custom_advanced_settings={},
            # dictionary with filter settings that override default values
            # for example {"1_pLDDT": {"threshold": 0.8, "higher": true}}
            custom_filter_settings={},
        )
    )
    workflow.validate()
    workflow.get_table_row()

    design_job, pool = design_logic.submit_design_workflow(
        # Your initialized workflow settings
        workflow=workflow,
        # Name your pool of designs
        pool_name="4ZXB mocked bindcraft miniproteins",
        pool_description="5 example structures from pool nvl",
        # see schedulers for available scheduler keys
        scheduler_key=TEST_SCHEDULER_KEY,
        # Project and Round where the Pool will be created
        round_id=project_round.id,
        # Run a mocked (stub) test
        submission_args=dict(stub=True),
    )

    jobs = design_logic.get_design_jobs_table(id=pool.id)
    print(jobs)
    assert len(jobs) == 1

    # wait for job to complete and process results
    pool = design_logic.process_results(design_job)

    num_designs = db.Design.count(pool_id=pool.id)
    assert num_designs == 4

    designs = db.Design.select(pool_id=pool.id)
    design_ids = sorted([d.id for d in designs])
    for i, suffix in enumerate(
        [
            "_Clashing_traj_l51_s338503",
            "_LowConfidence_traj_l55_s760578",
            # "_Relaxed_traj_l50_s65548", # we do not store Relaxed designs - see processing logic
            "_rank01_bindcraft",
            "_rejected01_bindcraft",
        ]
    ):
        assert design_ids[i].endswith(suffix)

    design = designs[0]
    assert len(design.spec.chains) == 1
    assert design.spec.chains[0].chain_ids == ["B"]

    length = db.select_descriptor_values("bindcraft|sequence|Length", design_ids)
    assert len(length.dropna()) == 4

    variant = db.select_descriptor_values("bindcraft|designs|DesignVariant", design_ids)
    assert len(variant.dropna()) == 4

    plddt = db.select_descriptor_values("bindcraft|af2|Average_pLDDT", design_ids)
    assert len(plddt.dropna()) == 2

    ipae = db.select_descriptor_values("bindcraft|af2|Average_i_pAE", design_ids)
    assert len(ipae.dropna()) == 2

    dg = db.select_descriptor_values("bindcraft|interface|Average_dG", design_ids)
    assert len(dg.dropna()) == 2
