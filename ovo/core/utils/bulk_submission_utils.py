import copy
import itertools
import math
import os
import re
from collections import defaultdict
from collections.abc import Hashable, Iterator

import yaml


class StrictYamlLoader(yaml.SafeLoader):
    """YAML loader that rejects duplicate keys, which YAML itself resolves to the last value.

    Silently dropping the earlier value is never what the user meant — most often they repeated a
    'workflow' key where they meant to add another entry to the 'submissions' list.
    """

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, Hashable):
                continue  # Let PyYAML report the unhashable key itself
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    "while parsing a mapping",
                    node.start_mark,
                    f"found duplicate key '{key}' - the value defined here replaces the earlier one.\n"
                    f"To submit more than one workflow, add another '- pool_name:' entry to 'submissions'.",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


class DoubleQuotedYamlDumper(yaml.SafeDumper):
    """YAML dumper that quotes with double quotes, where PyYAML would use single quotes."""

    def choose_scalar_style(self):
        style = super().choose_scalar_style()
        return '"' if style == "'" else style


def parse_bulk_config_yaml(config_text: str) -> dict:
    """Parse the YAML/JSON text of a bulk submission config into a config dict.

    :raises yaml.YAMLError: if the text is not valid YAML/JSON, or repeats a key in a mapping
        (see :class:`StrictYamlLoader`)
    """
    assert isinstance(config_text, str), f"Expected the config text, got {type(config_text).__name__}"
    return yaml.load(config_text, Loader=StrictYamlLoader)


def dump_bulk_config_yaml(config_dict: dict) -> str:
    """Serialize a bulk submission config dict to YAML, in the layout used for import and export."""
    assert isinstance(config_dict, dict), f"Expected a config dict, got {type(config_dict).__name__}"
    return yaml.dump(
        config_dict,
        Dumper=DoubleQuotedYamlDumper,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
    )


SUBMISSION_KEYS = ("pool_name", "pool_description", "workflow")


def get_workflow_configs(config_dict: dict) -> list[dict]:
    """Return the workflow config dicts of a bulk submission config, validating its overall structure.

    :raises ValueError: if the config is not a dict with a non-empty 'submissions' list of dicts,
        each holding a 'workflow' dict and nothing but the keys of :data:`SUBMISSION_KEYS`
    """
    if not isinstance(config_dict, dict):
        raise ValueError("Config must be a dict with a top-level 'submissions' key")
    submissions = config_dict.get("submissions")
    if not isinstance(submissions, list) or not submissions:
        raise ValueError("Config must contain a non-empty 'submissions' list")

    workflow_configs = []
    for submission in submissions:
        if not isinstance(submission, dict):
            raise ValueError(f"Each entry of 'submissions' must be a dict, got: {submission!r}")
        if unknown := [key for key in submission if key not in SUBMISSION_KEYS]:
            raise ValueError(
                f"Unknown key(s) in a 'submissions' entry: {', '.join(sorted(unknown))} "
                f"(expected only: {', '.join(SUBMISSION_KEYS)})"
            )
        wf_config = submission.get("workflow")
        if not isinstance(wf_config, dict):
            raise ValueError(f"Each entry of 'submissions' needs a 'workflow' dict, got: {wf_config!r}")
        workflow_configs.append(wf_config)
    return workflow_configs


def _collect_grid_paths(obj, path=""):
    """Recursively find all {grid: [...]} nodes, returning list of (dotted_path, values)."""
    results = []
    if isinstance(obj, dict):
        if list(obj.keys()) == ["grid"] and isinstance(obj["grid"], list):
            results.append((path, obj["grid"]))
        else:
            for k, v in obj.items():
                child_path = f"{path}.{k}" if path else k
                results.extend(_collect_grid_paths(v, child_path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(_collect_grid_paths(v, f"{path}[{i}]"))
    return results


def _set_nested(obj, path, value):
    """Set a value at a dotted/indexed path in a nested dict/list structure."""
    # 'a.b[0].c' -> ['a', 'b', 0, 'c']. Only a bracketed segment becomes a list index,
    # so an all-digit dict key still resolves as a key.
    parts = [int(part[:-1]) if part.endswith("]") else part for part in re.findall(r"[^.\[]+\]?", path)]
    node = obj
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value


def count_grid_combos(config: dict) -> int:
    """Return how many workflows a config will expand into, without expanding it.

    Used to enforce the workflows limit before :func:`expand_grid_configs` materializes the whole
    Cartesian product, which deep-copies the config once per combo.
    """
    grid_paths = _collect_grid_paths(config)
    return math.prod(len(values) for _, values in grid_paths) if grid_paths else 1


def expand_grid_configs(config: dict) -> tuple[list[dict], list[dict]]:
    """Expand {grid: [...]} nodes in a workflow config dict via Cartesian product.

    Returns (expanded_configs, combos) where combos[i] maps dotted param path to
    the substituted value for expanded_configs[i]. Returns ([config], [{}]) when
    no grid keys are present.
    """
    grid_paths = _collect_grid_paths(config)
    if not grid_paths:
        return [config], [{}]

    paths = [p for p, _ in grid_paths]
    value_lists = [v for _, v in grid_paths]
    empty_paths = [path for path, values in grid_paths if not values]
    if empty_paths:
        raise ValueError(f"Grid values cannot be empty: {', '.join(empty_paths)}")

    expanded = []
    combos = []
    for combo_values in itertools.product(*value_lists):
        cfg = copy.deepcopy(config)
        combo = {}
        for path, value in zip(paths, combo_values):
            _set_nested(cfg, path, value)
            combo[path] = value
        expanded.append(cfg)
        combos.append(combo)

    return expanded, combos


def format_combo_string(combo: dict) -> str:
    """Return ' [key=val, ...]' from a combo dict (last path segment as key), or '' if empty."""
    if not combo:
        return ""
    parts = []
    for path, value in combo.items():
        key = path.split(".")[-1].rstrip("]").split("[")[0]
        parts.append(f"{key}={value}")
    return " [" + ", ".join(parts) + "]"


def _set_storage_path_value(wf, dotted: str, old_value: str, new_value: str) -> None:
    """Replace old_value with new_value in the storage_path field at dotted path."""
    parts = dotted.split(".")
    obj = wf
    for part in parts[:-1]:
        obj = getattr(obj, part)
    attr = getattr(obj, parts[-1])
    if isinstance(attr, list):
        setattr(obj, parts[-1], [new_value if v == old_value else v for v in attr])
    elif attr == old_value:
        setattr(obj, parts[-1], new_value)


def iter_storage_path_values(workflows: list) -> Iterator[tuple[object, str, str]]:
    """Yield (workflow, dotted field path, value) for every non-empty storage_path value of the workflows.

    The single traversal the other storage path helpers are built on, in workflow, field and list
    order — so an export naming files after their paths stays deterministic.
    """
    from ovo.core.logic.import_export_logic import find_storage_path_fields

    for wf in workflows:
        for dotted in find_storage_path_fields(type(wf)):
            obj = wf
            for part in dotted.split("."):
                obj = getattr(obj, part, None)
                if obj is None:
                    break
            if obj is None:
                continue
            for value in obj if isinstance(obj, list) else [obj]:
                if value:
                    yield wf, dotted, value


def replace_storage_paths(workflows: list, path_mapping: dict[str, str]) -> None:
    """Replace storage path values in-place across all workflows.

    path_mapping: {old_path: new_path}. Modifies workflows in place.
    """
    for wf, dotted, value in list(iter_storage_path_values(workflows)):
        if value in path_mapping and path_mapping[value] != value:
            _set_storage_path_value(wf, dotted, value, path_mapping[value])


def replace_config_values(config_dict, path_mapping: dict[str, str]):
    """Return a copy of a bulk submission config with every string value found in path_mapping replaced.

    The config counterpart of :func:`replace_storage_paths`, for a config that is not expanded yet -
    it walks the plain data, so paths inside a grid or a list are replaced too.
    """
    if isinstance(config_dict, dict):
        return {k: replace_config_values(v, path_mapping) for k, v in config_dict.items()}
    if isinstance(config_dict, list):
        return [replace_config_values(v, path_mapping) for v in config_dict]
    if isinstance(config_dict, str):
        return path_mapping.get(config_dict, config_dict)
    return config_dict


def match_uploaded_file(path: str, uploaded_files: dict[str, bytes] = None) -> str | None:
    """Return the uploaded_files key holding the file for path, or None if there is no match.

    A directory or ZIP upload keeps the directory prefix in its key (e.g. "inputs/target.pdb"), so a
    config referencing just "target.pdb" is matched by basename as long as that basename is unique.
    """
    if not uploaded_files:
        return None
    if path in uploaded_files:
        return path
    basename = os.path.basename(path)
    matches = [key for key in uploaded_files if os.path.basename(key) == basename]
    return matches[0] if len(matches) == 1 else None


def get_storage_path_values(workflows: list) -> dict[str, set[str]]:
    """Return all non-empty storage_path field values across all expanded workflow instances.

    Returns a dict mapping dotted field paths to sets of path values found across all workflows.
    """
    paths = defaultdict(set)
    for _, dotted, value in iter_storage_path_values(workflows):
        paths[dotted].add(value)
    return paths


def get_unique_storage_path_values(workflows: list) -> list[str]:
    """Return the non-empty storage_path values of the workflows, deduplicated, in traversal order."""
    return list(dict.fromkeys(value for _, _, value in iter_storage_path_values(workflows)))
