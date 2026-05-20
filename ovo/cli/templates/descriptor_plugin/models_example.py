from dataclasses import dataclass, field
from typing import Callable, TypedDict
from ovo.core.database import DescriptorWorkflow, WorkflowTypes, Design, Base
from __MODULE_NAME__ import descriptors___MODULE_SUFFIX__


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
        from ovo import db, descriptor_logic

        designs = db.select(Design, id__in=self.design_ids)

        return {
            # NOTE: see prepare_design_sequences if your workflow supports sequence input
            "input_pdb": descriptor_logic.prepare_design_structures(designs, workdir=workdir),
            "chains": ",".join(self.chains),
            **self.params,
        }

    def process_results(self, job: "DescriptorJob", callback: Callable = None) -> list[Base]:
        """Process results of a successful workflow - download files from workdir, save DesignJob, Pool and Designs"""
        from ovo.core.logic.descriptor_logic import read_descriptor_file_values, read_per_design_files

        descriptor_values = read_descriptor_file_values(
            descriptor_job=job,
            # descriptor key prefix (pipeline|tool_key) -> filename to parse from pipeline output folder (.csv or .jsonl)
            filenames={
                "__PIPELINE_NAME__|__MODULE_SUFFIX__": "__MODULE_SUFFIX__.csv",
            },
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
        )
        # TODO adapt this to your output files or remove this if you don't produce per-design files
        descriptor_values += read_per_design_files(
            descriptor_job=job,
            # mapping from design.id to ID column in produced file
            design_id_mapping={design_id: design_id for design_id in self.design_ids},
            # individual files per design
            design_files={
                # filename produced by pipeline -> subdir in storage, file suffix in storage, descriptor key
                "__MODULE_SUFFIX__/{}.csv": (
                    "descriptors",
                    "___MODULE_SUFFIX__.csv",
                    descriptors___MODULE_SUFFIX__.EXAMPLE_FILE.key,
                ),
            },
            callback=callback,
        )
        return descriptor_values + [job]
