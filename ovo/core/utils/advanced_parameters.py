import json
import collections.abc


def load_json_from_file(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        raise
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


def get_dict_diff(default: dict, custom: dict):
    diff = {}
    for key, custom_value in custom.items():
        if key not in default:
            diff[key] = custom_value
            continue

        default_value = default[key]
        if isinstance(custom_value, dict) and isinstance(default_value, dict):
            nested_diff = get_dict_diff(default_value, custom_value)
            if nested_diff:
                diff[key] = nested_diff
        elif custom_value != default_value:
            diff[key] = custom_value
    return diff


def merge_dictionaries(default: dict, diff: dict):
    if diff is None:
        return default.copy()

    merged = default.copy()
    for key, diff_value in diff.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(diff_value, collections.abc.Mapping):
            merged[key] = merge_dictionaries(merged[key], diff_value)
        else:
            merged[key] = diff_value
    return merged
