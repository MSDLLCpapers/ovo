import importlib
import importlib.metadata
import sys
from dataclasses import dataclass, field
from typing import Any, Type, TypeVar

from pydantic import BaseModel, Field


@dataclass
class WorkflowPage:
    """Represents a workflow page in the plugin system"""

    module_name: str
    title: str
    path: str
    category: str
    labels: list[str] = field(default_factory=list)
    short_description: str | None = None
    thumbnail: str | None = None


@dataclass
class DesignView:
    """Represents a design view in the plugin system"""

    title: str
    path: str
    labels: list[str] = field(default_factory=list)


class OVOPlugin(BaseModel):
    """Plugin configuration validated with Pydantic"""

    # Name of the plugin module, such as ovo_plugin_name
    module_name: str
    # list of submodule names to import (used to register workflows and other classes defined in the plugin)
    submodule_names: list[str] = Field(default_factory=list)
    # Generic extension points for various plugin types
    extension_points: dict[str, list[Any]] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, plugin_dict: dict, module_name: str) -> "OVOPlugin":
        """Create OVOPlugin from legacy dict format with original validation logic"""

        if "extension_points" not in plugin_dict:
            # backwards compatibility: if "extension_points" are not present,
            # try to create them from legacy keys like "pages" and "design_views"
            plugin_dict["extension_points"] = _get_extension_points_from_legacy_plugin_dict(
                plugin_dict=plugin_dict,
                module_name=module_name,
            )
            if "modules" in plugin_dict:
                assert isinstance(plugin_dict["modules"], list), (
                    "Expected 'modules' to be a list of submodule names, got {}".format(plugin_dict["modules"])
                )
                plugin_dict["submodule_names"] = plugin_dict.pop("modules")
        elif plugin_dict.get("pages") or plugin_dict.get("design_views") or plugin_dict.get("modules"):
            # avoid supporting both legacy and new formats at the same time to prevent confusion
            raise ValueError(
                f"Plugin {module_name} has both legacy keys like 'pages', 'design_views' or 'modules', as well as new 'extension_points'. "
                f"Please consolidate to only use 'extension_points'."
            )

        return cls(
            module_name=module_name,
            **plugin_dict,
        )


def _get_extension_points_from_legacy_plugin_dict(plugin_dict: dict, module_name: str) -> dict[str, list[Any]]:
    """Create "extension_points" entries from legacy plugin dict keys like "pages" and "design_views" with validation"""
    extension_points = {}
    pages = plugin_dict.get("pages", {})
    assert isinstance(pages, dict), "Plugin 'pages' should be a dict, got {} in {}".format(type(pages), module_name)

    workflow_pages = []
    for category, pages_in_category in pages.items():
        assert isinstance(pages_in_category, list), (
            "Plugin 'pages' should be a dict of lists, got dict of {} in {}".format(
                type(pages_in_category), module_name
            )
        )
        # Convert each page dict to WorkflowPage with group_label as a label
        for page_dict in pages_in_category:
            workflow_page = dict(
                module_name=module_name,
                title=page_dict["title"],
                path=page_dict["page"],
                category=category,
                labels=page_dict.get("labels", [category]),
                short_description=page_dict.get("short_description"),
                thumbnail=page_dict.get("thumbnail"),
            )
            workflow_pages.append(workflow_page)

    extension_points["ovo.workflow_page"] = extension_points.get("ovo.workflow_page", []) + workflow_pages

    design_views_dict = plugin_dict.get("design_views", {})
    design_views = []
    for view_title, view_path in design_views_dict.items():
        assert isinstance(view_path, str), (
            "Expected view path to be a string (my_module.submodule:method_name), got {}".format(type(view_path))
        )
        design_view = dict(title=view_title, path=view_path, labels=[])
        design_views.append(design_view)

    extension_points["ovo.design_view"] = extension_points.get("ovo.design_view", []) + design_views

    descriptors = plugin_dict.get("descriptors")
    if descriptors is not None:
        assert isinstance(descriptors, str), (
            "Expected descriptors path to be a string (my_module.submodule), got {}".format(type(descriptors))
        )
        extension_points["ovo.descriptors"] = extension_points.get("ovo.descriptors", []) + [descriptors]
    return extension_points


def load_plugins() -> list[OVOPlugin]:
    """Load all registered plugins and return list of validated OVOPlugin instances"""
    plugins = []

    for entry_point in importlib.metadata.entry_points(group="ovo.plugins"):
        module_name = entry_point.value.split(":")[0]
        if entry_point.name == "plugin":
            print("Registering plugin {}".format(module_name), file=sys.stderr)
            plugin_dict = entry_point.load()
            # If already an OVOPlugin instance, use it directly
            if isinstance(plugin_dict, OVOPlugin):
                plugin = plugin_dict
            else:
                # Validate it's a dict before processing
                assert isinstance(plugin_dict, dict), (
                    "Plugin should be a dict or OVOPlugin instance, got {} in {}".format(type(plugin_dict), module_name)
                )
                # Parse dict to OVOPlugin with validation
                plugin = OVOPlugin.from_dict(plugin_dict, module_name)
            plugins.append(plugin)

    return plugins


def load_variable(path):
    module_path, var_name = path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# Get list of validated plugins
plugins: list[OVOPlugin] = load_plugins()

T = TypeVar("T")


def get_extension_points(extension_point_key: str, result_type: Type[T]) -> list[T]:
    """Get all extension points of a given type from all plugins

    Args:
        extension_point_key: The extension point identifier (e.g., "ovo.workflow_page", "ovo.design_view")
        result_type: The expected type of the extension point results (e.g., WorkflowPage, DesignView, str)

    Returns:
        List of all items registered for the given extension point across all plugins
    """
    results = []
    for plugin in plugins:
        if extension_point_key not in plugin.extension_points:
            continue
        for raw_result in plugin.extension_points[extension_point_key]:
            if isinstance(raw_result, dict):
                # If the result is a dict, try to parse it into the expected type
                try:
                    if hasattr(result_type, "from_dict"):
                        result = result_type.from_dict(raw_result)
                    else:
                        result = result_type(**raw_result)
                except Exception as e:
                    raise ValueError(
                        f"Error parsing extension point {extension_point_key} from plugin {plugin.module_name}: {e}"
                    ) from e
            elif result_type is str:
                assert isinstance(raw_result, str), (
                    f"Expected string result for extension point {extension_point_key} from plugin {plugin.module_name}, got {type(raw_result)}: {raw_result}"
                )
                result = raw_result
            else:
                result = result_type(raw_result)
            results.append(result)
    return results
