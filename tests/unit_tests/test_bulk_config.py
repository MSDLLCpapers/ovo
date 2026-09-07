import io
import os
import zipfile

import pytest
import yaml

from ovo import config, storage
from ovo.core.database.models import UnknownWorkflow, WorkflowTypes
from ovo.core.database.models_rfdiffusion import (
    RFdiffusionScaffoldDesignWorkflow,
    RFdiffusionParams,
    ProteinMPNNParams,
)
from ovo.core.logic.bulk_submission_logic import (
    BulkSubmission,
    export_bulk_config,
    export_bulk_config_zip,
    get_unresolved_input_paths,
    get_bulk_config_template,
    import_bulk_config,
    resolve_input_paths,
)
from ovo.core.logic.import_export_logic import can_export_bulk_config
from ovo.core.utils.bulk_submission_utils import (
    count_grid_combos,
    dump_bulk_config_yaml,
    expand_grid_configs,
    match_uploaded_file,
    parse_bulk_config_yaml,
    replace_storage_paths,
)


def test_bulk_config_round_trip(example_pdb_path):
    # 1. Build a workflow with the local file path (not yet in storage)
    workflow = RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(
            input_pdb_paths=[str(example_pdb_path)],
            contigs=["A111-114/10/A117-119"],
            num_designs=1,
            timesteps=1,
        ),
        protein_mpnn_params=ProteinMPNNParams(
            num_sequences=1,
            sampling_temp=0.01,
        ),
    )

    # 2. Export to YAML string — local path is preserved verbatim
    yaml_str = dump_bulk_config_yaml(export_bulk_config([BulkSubmission(workflow=workflow, pool_name="Test pool")]))
    parsed = yaml.safe_load(yaml_str)
    assert parsed["submissions"][0]["pool_name"] == "Test pool"
    assert parsed["submissions"][0]["workflow"]["rfdiffusion_params"]["input_pdb_paths"] == [str(example_pdb_path)]

    # 3. Round-trip: import back from the parsed dict
    submissions = import_bulk_config(parsed)
    assert len(submissions) == 1
    assert submissions[0].get_pool_name() == "Test pool"
    workflows = [s.workflow for s in submissions]
    assert workflows[0].rfdiffusion_params.input_pdb_paths == [str(example_pdb_path)]

    # 4. Store the file and replace the local path with the storage path
    storage_path = storage.store_input(project_id="test_project", file_path=str(example_pdb_path))
    replace_storage_paths(workflows, {str(example_pdb_path): storage_path})
    assert workflows[0].rfdiffusion_params.input_pdb_paths == [storage_path]

    # 5. Export to ZIP (export_files=True) — files stored under inputs/<basename>,
    #    workflows mutated in-place to reference the new zip paths
    basename = os.path.basename(storage_path)
    expected_zip_path = f"inputs/{basename}"

    zip_bytes, unreadable_paths = export_bulk_config_zip(submissions)
    assert isinstance(zip_bytes, bytes) and len(zip_bytes) > 0
    assert unreadable_paths == []

    # export_bulk_config_zip rewrites paths in workflows in-place
    assert workflows[0].rfdiffusion_params.input_pdb_paths == [expected_zip_path]

    # 6. Inspect the ZIP contents
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = zf.namelist()

        assert "bulk_config.yaml" in names, f"bulk_config.yaml not found in zip, got: {names}"
        assert expected_zip_path in names, f"Expected '{expected_zip_path}' in zip, got: {names}"

        top_level = {n.split("/")[0] for n in names}
        assert top_level == {"bulk_config.yaml", "inputs"}, f"Unexpected top-level entries: {top_level}"

        # YAML inside the ZIP references the inputs/ path
        parsed_from_zip = yaml.safe_load(zf.read("bulk_config.yaml").decode("utf-8"))
        submissions2 = import_bulk_config(parsed_from_zip)
        assert submissions2[0].workflow.rfdiffusion_params.input_pdb_paths == [expected_zip_path]

        # Stored file bytes match the original PDB
        assert zf.read(expected_zip_path) == storage.read_file_bytes(storage_path)


def test_export_bulk_config_reports_unreadable_inputs():
    """An input that cannot be read is reported and keeps its original path in the exported config."""
    missing_path = "projects/test_project/inputs/deleted/does_not_exist.pdb"
    workflow = _workflow_with_input(missing_path)

    zip_bytes, unreadable_paths = export_bulk_config_zip([BulkSubmission(workflow=workflow)])

    assert unreadable_paths == [missing_path]
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        assert zf.namelist() == ["bulk_config.yaml"]
        parsed = yaml.safe_load(zf.read("bulk_config.yaml").decode("utf-8"))
    # Not rewritten to an inputs/ path that is not in the ZIP
    assert parsed["submissions"][0]["workflow"]["rfdiffusion_params"]["input_pdb_paths"] == [missing_path]


def test_export_bulk_config_of_unknown_workflow():
    """A workflow whose plugin is gone is exported from the raw dict it was stored with."""
    stored = {
        "name": "Plugin that was uninstalled",
        "plugin_params": {"num_designs": 7, "input_pdb_paths": ["projects/p1/inputs/target.pdb"]},
    }
    workflow = UnknownWorkflow(data=stored, error="Unknown workflow type")
    assert can_export_bulk_config(workflow), "An UnknownWorkflow still holds its parameters"

    config_dict = export_bulk_config([BulkSubmission(workflow=workflow, pool_name="uninstalled plugin pool")])
    exported = config_dict["submissions"][0]
    assert exported["pool_name"] == "uninstalled plugin pool"
    assert exported["workflow"] == stored, "The stored params should be exported as they are"

    # It can only be submitted back once the plugin is installed again, and says so
    with pytest.raises(ValueError, match="is not registered"):
        import_bulk_config(config_dict)


def test_workflow_templates_round_trip():
    """Every generated template must parse back into a workflow of that same type."""
    workflow_names = WorkflowTypes.get_design_workflow_types()
    assert workflow_names, "No submittable design workflow types are registered"

    for name in workflow_names:
        template_yaml = get_bulk_config_template(name)
        submissions = import_bulk_config(yaml.safe_load(template_yaml))
        assert len(submissions) == 1, f"Template for {name} expanded to {len(submissions)} workflows"
        assert submissions[0].workflow.name == name
        assert submissions[0].pool_name is None, f"Template for {name} should not name a pool"
        assert submissions[0].combo == {}, f"Template for {name} should not contain grid values"

    with pytest.raises(ValueError):
        get_bulk_config_template("Not a workflow type")


def test_expand_grid_configs_cartesian_product():
    """Multiple grid fields expand into their Cartesian product, other values are carried over."""
    config_dict = {"name": "Test", "params": {"a": {"grid": [1, 2]}, "b": {"grid": ["x", "y", "z"]}, "c": 5}}

    assert count_grid_combos(config_dict) == 6
    expanded, combos = expand_grid_configs(config_dict)

    assert [(cfg["params"]["a"], cfg["params"]["b"]) for cfg in expanded] == [
        (1, "x"),
        (1, "y"),
        (1, "z"),
        (2, "x"),
        (2, "y"),
        (2, "z"),
    ]
    assert combos[0] == {"params.a": 1, "params.b": "x"}
    assert combos[-1] == {"params.a": 2, "params.b": "z"}
    assert all(cfg["params"]["c"] == 5 for cfg in expanded)
    # The input config is deep-copied, not substituted in place
    assert config_dict["params"]["a"] == {"grid": [1, 2]}


def test_expand_grid_configs_inside_list():
    """A grid nested in a list is addressed by index and substituted at that position only."""
    config_dict = {"params": {"paths": ["fixed.pdb", {"grid": ["a.pdb", "b.pdb"]}]}}

    assert count_grid_combos(config_dict) == 2
    expanded, combos = expand_grid_configs(config_dict)

    assert [cfg["params"]["paths"] for cfg in expanded] == [["fixed.pdb", "a.pdb"], ["fixed.pdb", "b.pdb"]]
    assert combos == [{"params.paths[1]": "a.pdb"}, {"params.paths[1]": "b.pdb"}]


def test_import_bulk_config_rejects_invalid_workflows():
    """A config that would produce an UnknownWorkflow is rejected instead of being submitted."""
    workflow_name = next(iter(WorkflowTypes.get_design_workflow_types()))

    with pytest.raises(ValueError, match="non-empty 'submissions' list"):
        import_bulk_config({})
    with pytest.raises(ValueError, match="must be a dict"):
        import_bulk_config({"submissions": ["RFdiffusion scaffold design"]})
    with pytest.raises(ValueError, match="needs a 'workflow' dict"):
        import_bulk_config({"submissions": [{"pool_name": "test"}]})
    with pytest.raises(ValueError, match="Unknown key"):
        import_bulk_config({"submissions": [{"pool": "test", "workflow": {"name": workflow_name}}]})
    with pytest.raises(ValueError, match="needs a 'name'"):
        import_bulk_config({"submissions": [{"workflow": {"rfdiffusion_params": {}}}]})
    with pytest.raises(ValueError, match="is not registered"):
        import_bulk_config({"submissions": [{"workflow": {"name": "Not a workflow type"}}]})

    with pytest.raises(ValueError, match="Invalid config for workflow"):
        import_bulk_config({"submissions": [{"workflow": {"name": workflow_name, "not_a_param_field": {"x": 1}}}]})


def test_import_bulk_config_names_pools_per_submission():
    """Each submission names its own pools, and its grid combos are numbered from 1 within it."""
    workflow_name, WorkflowType = next(iter(WorkflowTypes.get_design_workflow_types().items()))
    param_field, params = next(iter(WorkflowType().get_param_fields().items()))
    param_key = next(iter(params.to_dict()))

    def submission_config(pool_name: str, grid: list, pool_description: str = "") -> dict:
        return {
            "pool_name": pool_name,
            "pool_description": pool_description,
            "workflow": {"name": workflow_name, param_field: {param_key: {"grid": grid}}},
        }

    submissions = import_bulk_config(
        {"submissions": [submission_config("first", [1, 2, 3]), submission_config("second", [4])]}
    )

    # The second submission starts counting its combos from 1 again, and gets no suffix with one combo
    assert BulkSubmission.get_pool_names(submissions) == [
        "first Combo 1",
        "first Combo 2",
        "first Combo 3",
        "second",
    ]
    assert [(s.combo_index, s.num_combos) for s in submissions] == [(0, 3), (1, 3), (2, 3), (0, 1)]
    assert submissions[0].get_pool_description() == f"[{param_key}=1]"
    # A prefix given by the front-end is prepended to the name from the config, not replacing it
    assert BulkSubmission.get_pool_names(submissions, "TREM2")[0] == "TREM2 first Combo 1"

    # The description behaves the same way: the prefix is prepended, the combo values appended
    described = import_bulk_config({"submissions": [submission_config("first", [1, 2], "from the config")]})
    assert described[0].get_pool_description() == f"from the config [{param_key}=1]"
    assert (
        described[0].get_pool_description("typed by the user") == f"typed by the user from the config [{param_key}=1]"
    )

    # A submission without a pool name in the config is named by the prefix alone
    submissions = import_bulk_config({"submissions": [submission_config("", [1, 2])]})
    assert all(s.pool_name is None for s in submissions)
    assert BulkSubmission.get_pool_names(submissions, "from the UI") == ["from the UI Combo 1", "from the UI Combo 2"]
    assert submissions[0].get_pool_description("typed by the user") == f"typed by the user [{param_key}=1]"

    # Without a name from either side there is nothing to create the pool under
    with pytest.raises(ValueError, match="Missing pool name for submission"):
        BulkSubmission.get_pool_names(submissions)


def test_parse_bulk_config_rejects_duplicate_keys():
    """A repeated key is reported instead of silently keeping the last value, as YAML would."""
    config_text = (
        "submissions:\n"
        "- pool_name: fff\n"
        "  workflow:\n"
        "    name: A\n"
        "  workflow:\n"  # meant to be another submission, YAML would drop the first workflow
        "    name: B\n"
    )

    with pytest.raises(yaml.YAMLError, match="found duplicate key 'workflow'"):
        parse_bulk_config_yaml(config_text)

    # What the user meant, two submissions, parses fine
    assert parse_bulk_config_yaml(config_text.replace("  workflow:\n    name: B", "- workflow:\n    name: B")) == {
        "submissions": [{"pool_name": "fff", "workflow": {"name": "A"}}, {"workflow": {"name": "B"}}]
    }


def test_bulk_config_yaml_uses_double_quotes():
    """Quoted scalars are exported with double quotes, where PyYAML would use single quotes."""
    pool_name = "TREM2: M1W"  # the colon forces the name to be quoted
    yaml_str = dump_bulk_config_yaml(
        export_bulk_config([BulkSubmission(workflow=_workflow_with_input("x.pdb"), pool_name=pool_name)])
    )

    assert f'pool_name: "{pool_name}"' in yaml_str
    assert "'" not in yaml_str, f"Single quotes in exported config:\n{yaml_str}"
    # And it is still valid YAML, parsing back to the same name
    assert parse_bulk_config_yaml(yaml_str)["submissions"][0]["pool_name"] == pool_name


def test_get_pool_names_rejects_duplicates():
    """Two submissions naming the same pool are refused up front, not halfway through submitting."""
    workflow_name = next(iter(WorkflowTypes.get_design_workflow_types()))
    submission_config = {"pool_name": "same name", "workflow": {"name": workflow_name}}
    submissions = import_bulk_config({"submissions": [submission_config, dict(submission_config)]})

    with pytest.raises(ValueError, match="Duplicate pool name\\(s\\): same name"):
        BulkSubmission.get_pool_names(submissions)


def test_import_bulk_config_checks_limit_before_expanding():
    """A grid over the limit is refused up front, without deep-copying a config per combo."""
    limit = config.props.bulk_submission_workflows_limit
    workflow_name = next(iter(WorkflowTypes.get_design_workflow_types()))
    workflow_config = {"name": workflow_name, "not_a_param_field": {"grid": list(range(limit + 1))}}

    # The limit is reported, not the invalid field that expansion would have failed on
    with pytest.raises(ValueError, match=f"Cannot submit {limit + 1} workflows"):
        import_bulk_config({"submissions": [{"workflow": workflow_config}]})


def _workflow_with_input(path: str) -> RFdiffusionScaffoldDesignWorkflow:
    return RFdiffusionScaffoldDesignWorkflow(
        rfdiffusion_params=RFdiffusionParams(input_pdb_paths=[path], contigs=["A111-114/10/A117-119"]),
    )


def test_resolve_input_paths_from_local_dir(example_pdb_path):
    """A path relative to base_dir is uploaded to storage and rewritten on the workflow."""
    workflow = _workflow_with_input(os.path.basename(example_pdb_path))
    resolve_input_paths([workflow], project_id="test_project", base_dir=os.path.dirname(example_pdb_path))

    (storage_path,) = workflow.rfdiffusion_params.input_pdb_paths
    assert storage_path != os.path.basename(example_pdb_path), "The path should be rewritten in place"
    assert storage.file_exists(storage_path)


def test_resolve_input_paths_already_in_storage(example_pdb_path):
    """A path that is already in storage is left untouched, with or without a base_dir."""
    storage_path = storage.store_input(project_id="test_project", file_path=str(example_pdb_path))
    workflow = _workflow_with_input(storage_path)

    resolve_input_paths([workflow], project_id="test_project")
    assert workflow.rfdiffusion_params.input_pdb_paths == [storage_path]


def test_match_uploaded_file():
    """Uploads keeping a directory prefix are matched by basename, unless the basename is ambiguous."""
    uploaded_files = {"inputs/target.pdb": b"x"}

    assert match_uploaded_file("inputs/target.pdb", uploaded_files) == "inputs/target.pdb"
    assert match_uploaded_file("target.pdb", uploaded_files) == "inputs/target.pdb"
    assert match_uploaded_file("other.pdb", uploaded_files) is None
    assert match_uploaded_file("target.pdb", None) is None
    assert match_uploaded_file("target.pdb", {"a/target.pdb": b"x", "b/target.pdb": b"y"}) is None


def test_resolve_input_paths_from_directory_upload(example_pdb_path):
    """Bytes handed in by the caller (the web app's uploader) are stored, matched by basename."""
    file_bytes = open(example_pdb_path, "rb").read()
    uploaded_files = {"inputs/target.pdb": file_bytes}

    assert get_unresolved_input_paths([_workflow_with_input("target.pdb")], uploaded_files=uploaded_files) == {}

    workflow = _workflow_with_input("target.pdb")
    resolve_input_paths([workflow], project_id="test_project", uploaded_files=uploaded_files)

    (storage_path,) = workflow.rfdiffusion_params.input_pdb_paths
    assert os.path.basename(storage_path).endswith("target.pdb")
    assert storage.read_file_bytes(storage_path) == file_bytes


def test_resolve_input_paths_missing_file():
    """An input that is neither uploaded, in storage nor on disk is reported, not silently dropped."""
    workflow = _workflow_with_input("does_not_exist.pdb")

    unresolved = get_unresolved_input_paths([workflow])
    assert unresolved == {"rfdiffusion_params.input_pdb_paths": ["does_not_exist.pdb"]}

    with pytest.raises(FileNotFoundError):
        resolve_input_paths([workflow], project_id="test_project")
    with pytest.raises(FileNotFoundError):
        resolve_input_paths([workflow], project_id="test_project", base_dir=os.path.dirname(__file__))
