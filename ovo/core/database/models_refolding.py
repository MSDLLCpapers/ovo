from abc import ABC
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Optional

from ovo.core.database import DescriptorJob
from ovo.core.database.descriptors_refolding import REFOLDING_TESTS_BY_TYPE
from ovo.core.database.models import (
    DescriptorWorkflow,
    WorkflowTypes,
    Base,
    DescriptorValue,
)
from dataclasses import dataclass, field


class RefoldingSupportedDesignWorkflow(ABC):
    """Abstract class that defines an interface for workflows supported by the RefoldingWorkflow workflow"""

    def get_refolding_native_pdb_path(self, contig_index: int) -> Optional[str]:
        raise NotImplementedError()

    def get_refolding_design_paths(self, design_ids: list[str]) -> dict[str, str]:
        raise NotImplementedError()

    def get_refolding_design_type(self) -> str:
        raise NotImplementedError()

    def get_refolding_designed_chains(self) -> list[str]:
        raise NotImplementedError()


@WorkflowTypes.register("Refolding workflow")
@dataclass
class RefoldingWorkflow(DescriptorWorkflow):
    # list of designed chains
    chains: List[str] = field(default_factory=list)
    tests: List[str] = None
    design_type: str = None
    native_pdb_path: str = None

    def get_pipeline_name(self) -> str:
        return "ovo.refolding"

    def prepare_params(self, workdir: str) -> dict:
        from ovo.core.logic.descriptor_logic import prepare_refolding_params

        return prepare_refolding_params(self, workdir=workdir)

    def process_results(self, job: DescriptorJob, callback: Callable | None = None) -> list[Base]:
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse
            filenames={f"refolding|{test}": test for test in self.tests},
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )

        structure_descriptor_values = self.store_outputs(job, callback)

        descriptor_values += structure_descriptor_values
        return descriptor_values + [job]

    def store_outputs(self, job: DescriptorJob, callback: Optional[Callable] = None) -> list[DescriptorValue]:
        """Store structure files for all designs and tests, using the batch/contig discovery logic."""
        from ovo import get_scheduler, storage, config

        # pool = db.get(Pool, design_job_id=job.id)
        scheduler = get_scheduler(job.scheduler_key)
        source_output_path = scheduler.get_output_dir(job.job_id)
        # destination_dir = os.path.join("project", job.project_id, "pools", pool.id, "designs")

        structure_descriptor_values = []
        items_to_save = []
        contig_number = 1
        while True:
            any_files_in_contig = False
            batch_number = 1

            while True:
                batch_name = f"contig{contig_number}_batch{batch_number}"
                batch_output_path = f"{source_output_path}/{batch_name}"
                any_files_in_batch = False

                for design_id in self.design_ids:
                    pool_id = design_id.split("_")[1]
                    for test in self.tests:
                        source_structure_path = f"{batch_output_path}/{test}/{design_id}_{test}.pdb"
                        if storage.file_exists(source_structure_path):
                            items_to_save.append(
                                (
                                    design_id,
                                    batch_output_path,
                                    test,
                                    pool_id,
                                )
                            )
                            any_files_in_batch = True
                            any_files_in_contig = True

                if not any_files_in_batch:
                    break
                batch_number += 1

            if not any_files_in_contig:
                break
            contig_number += 1

        if not items_to_save:
            return structure_descriptor_values

        with storage.archive_context(delete_if_exists=True):
            with ThreadPoolExecutor(config.storage.num_copy_threads) as executor:
                futures = [
                    executor.submit(
                        self.store_output,
                        design_id,
                        test,
                        batch_output_path,
                        os.path.join("project", job.project_id, "pools", pool_id, "designs"),
                        job.id,
                        self.chains,
                    )
                    for design_id, batch_output_path, test, pool_id in items_to_save
                ]

                for i, future in enumerate(futures):
                    values = future.result()
                    structure_descriptor_values.extend(values)

                    if callback:
                        callback(
                            value=(i + 1) / len(futures),
                            text=f"Storing structure files ({i + 1}/{len(futures)})",
                        )

        return structure_descriptor_values

    @classmethod
    def store_output(
        cls,
        design_id: str,
        test: str,
        batch_output_path: str | None,
        destination_dir: str,
        descriptor_job_id: str,
        chains: str | list[str],
        source_structure_path: Optional[str] = None,
        primary: bool = False,
    ) -> list[DescriptorValue]:
        """Store structure files and create descriptor values for all refolding test types."""
        from ovo import storage

        assert batch_output_path or source_structure_path, (
            "Either batch_output_path or source_structure_path must be provided"
        )

        if source_structure_path is None:
            source_structure_path = os.path.join(batch_output_path, test, f"{design_id}_{test}.pdb")

        stored_path = storage.store_file_path(
            source_abs_path=source_structure_path,
            storage_rel_path=os.path.join(destination_dir, test, f"{design_id}_{test}.pdb"),
            overwrite=False,
        )

        if test.startswith("boltz"):
            structure_descriptor_key_final = "boltz_predicted_structure_path"
        elif test.startswith("af2"):
            structure_descriptor_key_final = "af2_structure_path"
        elif test.startswith("esmfold"):
            structure_descriptor_key_final = "esmfold_predicted_structure_path"
        else:
            raise ValueError(f"Unknown test type: {test}")

        return [
            DescriptorValue(
                descriptor_key=f"{cls.get_descriptor_key_prefix(test, primary=primary)}|{structure_descriptor_key_final}",
                value=stored_path,
                design_id=design_id,
                descriptor_job_id=descriptor_job_id,
                chains=",".join(chains) if chains else "A",
            )
        ]

    @classmethod
    def get_descriptor_key_prefix(cls, test: str, primary: bool = False) -> str:
        if not primary:
            return f"refolding|{test}"

        if test.startswith("af2_"):
            # Historical reasons - store AF2 metrics under "af2_primary" prefix to simplify downstream analysis
            return "refolding|af2_primary"
        else:
            return f"refolding|{test}"

    def validate(self):
        super().validate()
        if not self.design_type:
            raise ValueError("Design type not specified")
        if not self.tests:
            raise ValueError("No tests specified")
        for test in self.tests:
            # TODO validate test name
            assert test in REFOLDING_TESTS_BY_TYPE[self.design_type], (
                f"Invalid test for design type {self.design_type}: {test}"
            )
