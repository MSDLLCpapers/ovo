from dataclasses import dataclass, field
from typing import Callable, TypedDict
from ovo.core.database import DescriptorWorkflow, WorkflowTypes, Design, Base


class __WORKFLOW_CLASS_NAME__ParamsType(TypedDict):
    """Typed dictionary workflow parameters

    Used only for type hinting purposes - actual params are stored as a dict
    """

    # foo: str
    # add parameters as needed


default_params = {
    # Set default parameter values here
    # "foo": "bar",
}


@WorkflowTypes.register()
@dataclass
class __WORKFLOW_CLASS_NAME__(DescriptorWorkflow):
    params: __WORKFLOW_CLASS_NAME__ParamsType = field(
        default_factory=lambda: {**default_params},
    )

    def get_pipeline_name(self) -> str:
        return "__MODULE_NAME__.__PIPELINE_NAME__"

    def prepare_params(self, workdir: str) -> dict:
        from ovo import db, storage

        # Collect pdb paths and ids in the same order (db.select does not guarantee same order)
        storage_paths = []
        design_ids = []
        for design in db.select(Design, id__in=self.design_ids):
            if not design.structure_path:
                continue
            storage_paths.append(design.structure_path)
            design_ids.append(design.id)
        # Prepare a txt file with workflow input paths, each file renamed to design_id.pdb
        input_path = storage.prepare_workflow_inputs(storage_paths, workdir, names=design_ids)
        # Submit job
        return {"input_pdb": input_path, "chains": ",".join(self.chains), **self.params}

    def process_results(self, job: "DescriptorJob", callback: Callable = None) -> list[Base]:
        """Process results of a successful workflow - download files from workdir, save DesignJob, Pool and Designs"""
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse from pipeline output folder (.csv or .jsonl)
            filenames={
                "__PIPELINE_NAME__|__MODULE_SUFFIX__": "__MODULE_SUFFIX__.csv",
            },
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )
        return descriptor_values + [job]
