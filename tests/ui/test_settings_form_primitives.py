import pytest

from gridironlabs.ui.pages.settings_page import SettingsPage


@pytest.mark.qt
def test_settings_page_contains_settings_panel(qtbot, monkeypatch, tmp_path):
    root = tmp_path / "app"
    root.mkdir()
    monkeypatch.setenv("GRIDIRONLABS_ROOT", str(root))

    from gridironlabs.core.config import AppPaths, load_config

    paths = AppPaths.from_env()
    config = load_config(paths, env_file=None)

    page = SettingsPage(config=config, paths=paths)
    qtbot.addWidget(page)
    page.resize(1100, 800)
    page.show()
    qtbot.waitExposed(page)

    from gridironlabs.ui.panels import PanelChrome

    assert page.findChild(PanelChrome, "PanelChrome") is not None
