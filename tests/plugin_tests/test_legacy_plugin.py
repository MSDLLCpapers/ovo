"""Test legacy plugin format support"""

from pathlib import Path

from tests.plugin_tests.utils import install_plugin, verify_plugin_registration


def test_legacy_plugin_format(ovo_venv, tmp_path):
    """Test that legacy plugin format is still supported and converted correctly"""
    venv_dir, python_path = ovo_venv
    plugin_dir = tmp_path / "test_plugin"

    # Create legacy plugin manually
    create_legacy_plugin(plugin_dir, "ovo_test_legacy")

    # Install plugin and verify conversion
    install_plugin(plugin_dir, venv_dir)
    verify_plugin_registration(
        python_path,
        """
from ovo.core.plugins import plugins, get_extension_points, WorkflowPage, DesignView

plugin = [p for p in plugins if p.module_name == "ovo_test_legacy"][0]

# Verify legacy format was converted to extension_points
assert "ovo.workflow_page" in plugin.extension_points, "Missing ovo.workflow_page (pages not converted)"
assert "ovo.design_view" in plugin.extension_points, "Missing ovo.design_view (design_views not converted)"
assert "ovo.descriptors" in plugin.extension_points, "Missing ovo.descriptors extension point"
assert plugin.submodule_names == ["ovo_test_legacy.models_test_legacy"], "Incorrect submodule_names (modules not converted)"

# Test workflow pages (converted from "pages")
workflow_pages = get_extension_points("ovo.workflow_page", WorkflowPage)
page = [p for p in workflow_pages if p.module_name == "ovo_test_legacy"][0]
assert page.title == "Legacy Page", "Incorrect workflow page title"
assert page.category == "Legacy Tool", "Incorrect workflow page category"
assert page.labels == ["legacy"], "Incorrect workflow page labels"
assert page.short_description == "Legacy page description", "Incorrect workflow page description"

# Test design views (converted from "design_views")
design_views = get_extension_points("ovo.design_view", DesignView)
view = [v for v in design_views if v.title == "Legacy Design View"][0]
assert view.path == "ovo_test_legacy.design_view_test_legacy:legacy_fragment", "Incorrect design view path"

# Test descriptors
descriptors = get_extension_points("ovo.descriptors", str)
assert any("test_legacy" in d for d in descriptors), "Legacy descriptor not found"
""",
    )


def create_legacy_plugin(plugin_dir: Path, module_name: str):
    """Create plugin with legacy format for backward compatibility testing"""
    module_suffix = module_name.removeprefix("ovo_")
    module_dir = plugin_dir / module_name
    module_dir.mkdir(parents=True)

    # pyproject.toml
    (plugin_dir / "pyproject.toml").write_text(
        f"""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{module_name.replace("_", "-")}"
version = "0.1.0"
dependencies = []

[project.entry-points."ovo.plugins"]
plugin = "{module_name}:plugin"
"""
    )

    # __init__.py with legacy format
    (module_dir / "__init__.py").write_text(
        f"""plugin = dict(
    pages = {{
        "Legacy Tool": [
            dict(
                page="{module_name}.legacy_page",
                title="Legacy Page",
                labels=["legacy"],
                short_description="Legacy page description",
            )
        ],
    }},
    design_views = {{
        "Legacy Design View": "{module_name}.design_view_{module_suffix}:legacy_fragment",
    }},
    descriptors = "{module_name}.descriptors_{module_suffix}",
    modules = [
        "{module_name}.models_{module_suffix}",
    ]
)
"""
    )

    # Minimal supporting files
    (module_dir / f"design_view_{module_suffix}.py").write_text("def legacy_fragment(): return 'Legacy'")
    (module_dir / f"descriptors_{module_suffix}.py").write_text(
        """from ovo.core.database.models import NumericGlobalDescriptor, Descriptor

LEGACY_DESCRIPTOR = NumericGlobalDescriptor(
    key="legacy_pipeline|legacy_tool|legacy_value",
    name="Legacy Value",
    description="Legacy descriptor",
    tool="LegacyTool",
)

DESCRIPTORS = [v for v in globals().values() if isinstance(v, Descriptor)]
"""
    )
    (module_dir / f"models_{module_suffix}.py").write_text("# models")
