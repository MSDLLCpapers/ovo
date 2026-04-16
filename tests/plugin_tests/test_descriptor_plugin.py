"""Test descriptor plugin creation and registration"""

from tests.plugin_tests.utils import install_plugin, run_ovo_init_plugin, verify_plugin_registration


def test_descriptor_plugin_creation_and_registration(ovo_venv, tmp_path):
    """Test that a descriptor plugin created via CLI is correctly registered"""
    venv_dir, python_path = ovo_venv

    # Create descriptor plugin via CLI
    plugin_dir = run_ovo_init_plugin(
        tmp_path,
        [
            "ovo_test_descriptor",
            "descriptor",
            "TestToolWorkflow",
            "test-tool",
            "n",  # don't run git init
            "n",  # don't add MIT license
        ],
    )

    # Install plugin and verify
    install_plugin(plugin_dir, venv_dir)
    verify_plugin_registration(
        python_path,
        """
from ovo.core.plugins import plugins, get_extension_points, DesignView

plugin = [p for p in plugins if p.module_name == "ovo_test_descriptor"][0]
assert "ovo.design_view" in plugin.extension_points, "Missing ovo.design_view extension point"
assert "ovo.descriptors" in plugin.extension_points, "Missing ovo.descriptors extension point"
assert plugin.submodule_names == ["ovo_test_descriptor.models_test_descriptor"], "Incorrect submodule_names"

design_views = get_extension_points("ovo.design_view", DesignView)
view = [v for v in design_views if v.title == "💥 My Method"][0]
assert view.path == "ovo_test_descriptor.design_view_test_descriptor:ovo_test_descriptor_fragment", "Incorrect design view path"

descriptors = get_extension_points("ovo.descriptors", str)
assert any("test_descriptor" in d for d in descriptors), "Descriptor not found in extension points"
""",
    )
