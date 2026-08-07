from ovo.core.database import Threshold, DesignJob


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


def get_saved_thresholds_by_pool_id(jobs_by_pool_id: dict[str, DesignJob]) -> dict[str, dict[str, Threshold]]:
    """Extract acceptance thresholds from design jobs, indexed by pool ID.

    Returns empty dict for pools without acceptance thresholds configured.
    """
    thresholds_by_pool = {}
    for pool_id, job in jobs_by_pool_id.items():
        if hasattr(job.workflow, "acceptance_thresholds") and job.workflow.acceptance_thresholds:
            thresholds_by_pool[pool_id] = job.workflow.acceptance_thresholds
        else:
            thresholds_by_pool[pool_id] = {}
    return thresholds_by_pool


def get_inconsistent_threshold_descriptor_keys(thresholds_by_pool_id: dict[str, dict[str, Threshold]]) -> set[str]:
    """Identify descriptors with different threshold values across pools.

    Includes differences in enabled/disabled state.
    """
    inconsistent_keys = set()
    threshold_values_by_descriptor = {}
    for pool_thresholds in thresholds_by_pool_id.values():
        for descriptor_key, threshold in pool_thresholds.items():
            if descriptor_key not in threshold_values_by_descriptor:
                threshold_values_by_descriptor[descriptor_key] = set()
            if not threshold.enabled:
                threshold_values_by_descriptor[descriptor_key].add("disabled")
            else:
                threshold_values_by_descriptor[descriptor_key].add(threshold.format())

    for descriptor_key, values in threshold_values_by_descriptor.items():
        if len(values) > 1:
            inconsistent_keys.add(descriptor_key)

    return inconsistent_keys
