"""Settings page scaffold.



Panel implementations were removed so you can iterate on the panel concept from a

clean slate.

"""



from __future__ import annotations



from gridironlabs.core.config import AppConfig, AppPaths

from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig

from gridironlabs.ui.pages.base_page import BasePage

from gridironlabs.ui.style.tokens import GRID





class SettingsPage(BasePage):

    """Settings page scaffold that owns a grid canvas."""



    def __init__(

        self,

        *,

        config: AppConfig,

        paths: AppPaths,

        overlay_config: GridOverlayConfig | None = None,

    ) -> None:

        self.config = config

        self.paths = paths

        self.overlay_config = overlay_config or GridOverlayConfig()



        super().__init__(cols=GRID.cols, rows=12, overlay_config=self.overlay_config)

        self.setObjectName("page-settings")

