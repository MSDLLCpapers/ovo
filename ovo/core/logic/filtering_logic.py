from ovo.core.database import Threshold


def filter_designs_by_thresholds(
    all_design_ids: list[str],
    thresholds: dict[str, Threshold],
    # descriptor_key -> design_id -> value
    values: dict[str, dict[str, float | None]],
) -> tuple[list[str], dict[str, int]]:
    """Filter designs by thresholds (inclusive - <=, >=)

    :param all_design_ids: list of design ids
    :param thresholds: dictionary descriptor_key -> Threshold object
    :param values: dictionary descriptor_key -> descriptor values (index = design_id, value = descriptor value)

    :return: tuple:
        - list of design ids that pass the thresholds, in original order
        - dictionary descriptor_key -> number of designs that pass the threshold
    """
    filtered_design_ids = []
    num_accepted_by_descriptor = {}
    num_missing_by_descriptor = {}
    for design_id in all_design_ids:
        passes_all = True
        for descriptor_key, threshold in thresholds.items():
            if not threshold.enabled:
                continue
            if descriptor_key not in values:
                print("Available descriptor values:", values)
                raise ValueError(
                    f"Cannot filter by descriptor '{descriptor_key}', value is missing for all {len(all_design_ids):,} designs"
                )
            if design_id not in values[descriptor_key]:
                num_missing_by_descriptor[descriptor_key] = num_missing_by_descriptor.get(descriptor_key, 0) + 1
                passes_all = False
                continue
            passes = threshold.passes(values[descriptor_key][design_id])
            passes_all &= passes
            if descriptor_key not in num_accepted_by_descriptor:
                num_accepted_by_descriptor[descriptor_key] = 0
            if passes:
                num_accepted_by_descriptor[descriptor_key] += 1
        if passes_all:
            filtered_design_ids.append(design_id)
    if num_missing_by_descriptor:
        print("Descriptors with missing descriptor values marked as NOT ACCEPTED:")
        for descriptor_key, num in num_missing_by_descriptor.items():
            print(descriptor_key, num)
    return filtered_design_ids, num_accepted_by_descriptor
