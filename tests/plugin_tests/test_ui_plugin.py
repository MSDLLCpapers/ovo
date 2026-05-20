"""Test UI plugin creation and registration"""

from tests.plugin_tests.utils import install_plugin, run_ovo_init_plugin, verify_plugin_registration


def test_ui_plugin_creation_and_registration(ovo_venv, tmp_path):
    """Test that a UI plugin created via CLI is correctly registered"""
    venv_dir, python_path = ovo_venv

    # Create UI plugin via CLI
    plugin_dir = run_ovo_init_plugin(
        tmp_path,
        [
            "ovo_test_ui",
            "ui",
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

plugin = [p for p in plugins if p.module_name == "ovo_test_ui"][0]
assert "ovo.design_view" in plugin.extension_points, "Missing ovo.design_view extension point"
assert len(plugin.extension_points["ovo.design_view"]) == 1, "Expected 1 design view"

design_views = get_extension_points("ovo.design_view", DesignView)
view = [v for v in design_views if v.title == "🔥 My design view"][0]
assert view.path == "ovo_test_ui.design_view_test_ui:ovo_test_ui_fragment", "Incorrect design view path"
assert view.labels == [], "Expected empty labels list"
""",
    )
