"""Cluster designs whose designed chains are labelled differently (e.g. RFdiffusion "A" vs BindCraft "B").

Clustering has to be submitted as a single job, since cluster IDs are only meaningful within the whole
set of designs, so such designs cannot simply be submitted separately. Instead, the DESIGNED_CHAINS
placeholder is used and each design's structure is filtered and relabelled to a canonical chain ID
before it is passed to the pipeline.
"""

from ovo import db, storage
from ovo.core.database import descriptors_clustering
from ovo.core.database.models import DESIGNED_CHAINS, Design, DescriptorValue, Pool
from ovo.core.database.models_clustering import FoldseekClusteringWorkflow, FoldseekParams
from ovo.core.logic import descriptor_logic
from ovo.core.utils.pdb import trim_pdb_str
from ovo.core.utils.resources import RESOURCES_DIR
from ovo.core.utils.tests import TEST_SCHEDULER_KEY

# Residue ranges of chain A of the example structure, used to create structurally distinct designs
DESIGN_RESIDUE_RANGES = [(20, 131), (20, 100), (60, 131)]


def _relabel_chain(pdb_str: str, chain_id: str, new_chain_id: str) -> str:
    """Relabel a chain in a PDB string (column 21), without using the utility that is under test here"""
    return "\n".join(
        line[:21] + new_chain_id + line[22:]
        if line[:6].strip() in ("ATOM", "HETATM", "TER") and len(line) > 21 and line[21] == chain_id
        else line
        for line in pdb_str.splitlines()
    )


def _create_pool(project_id: str, round_id: str, pool_name: str, chain_id: str) -> list[Design]:
    """Create a pool of designs whose designed chain is labelled with the given chain ID"""
    pool = Pool(id=Pool.generate_id(), round_id=round_id, name=pool_name, author="test")
    db.save(pool)

    pdb_str = _relabel_chain((RESOURCES_DIR / "examples/inputs/5ELI_A.pdb").read_text(), "A", chain_id)

    designs = []
    for start_res, end_res in DESIGN_RESIDUE_RANGES:
        design = Design.from_pdb_file(
            storage=storage,
            filename=f"design_{start_res}_{end_res}.pdb",
            pdb_str=trim_pdb_str(pdb_str, chain_id, start_res, end_res),
            chains=[chain_id],
            project_id=project_id,
            pool_id=pool.id,
        )
        db.save(design)
        assert design.spec.get_designed_chain_ids() == [chain_id]
        designs.append(design)
    return designs


def test_mixed_designed_chains_clustering(project_data):
    project, project_round, custom_pool = project_data

    # Two pools of structurally identical designs, differing only in the label of their designed chain
    designs_a = _create_pool(project.id, project_round.id, "Designed chain A", chain_id="A")
    designs_b = _create_pool(project.id, project_round.id, "Designed chain B", chain_id="B")
    design_ids = [design.id for design in designs_a + designs_b]

    clustering = FoldseekClusteringWorkflow(
        chains=[DESIGNED_CHAINS],
        design_ids=design_ids,
        params=FoldseekParams(
            exhaustive_search=True,
            e=100,
        ),
    )
    clustering.validate()
    descriptor_job = descriptor_logic.submit_descriptor_workflow(
        workflow=clustering, scheduler_key=TEST_SCHEDULER_KEY, project_id=project.id
    )
    descriptor_logic.process_results(descriptor_job)

    # All designs should be clustered, even though their designed chains are labelled differently
    cluster_ids = db.select_descriptor_values(
        descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key, design_ids, descriptor_job_id=descriptor_job.id
    )
    assert len(cluster_ids.dropna()) == len(design_ids)

    # Designs with identical structures should be clustered together, no matter how their chain is labelled
    for design_a, design_b in zip(designs_a, designs_b):
        assert cluster_ids[design_a.id] == cluster_ids[design_b.id], (
            f"Expected {design_a.id} (chain A) and {design_b.id} (chain B) to be in the same cluster"
        )

    # The resolved chain IDs are stored for each design, not the DESIGNED_CHAINS placeholder
    stored_chains = db.select_dict(
        DescriptorValue,
        "design_id",
        "chains",
        descriptor_job_id=descriptor_job.id,
        descriptor_key=descriptors_clustering.FOLDSEEK_REPR_CLUSTER_ID.key,
    )
    assert stored_chains == {
        **{design.id: "A" for design in designs_a},
        **{design.id: "B" for design in designs_b},
    }

    # The workflow itself keeps the placeholder, to make it clear that the designed chains were used
    assert db.DescriptorJob.get(id=descriptor_job.id).workflow.chains == [DESIGNED_CHAINS]
