"""Deterministic UI snapshot CLI for agent workflows.

Outputs:
- ui_artifacts/<name>.window.png
- ui_artifacts/<name>.target.png
- ui_artifacts/<name>.json

Supports:
- full-page snapshot: --page page-home [--panel panel-...]
- discovery: --list-pages, --list-panels --page page-home
- panel-only snapshot: --panel-only panel-objectName
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def _ensure_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deterministic UI snapshot utility (PNG + JSON).")
    # Note: discovery flags must be allowed to combine with --page (e.g. --list-panels --page page-home),
    # so we avoid strict mutually-exclusive groups and validate manually in main().
    p.add_argument("--page", type=str, default=None, help="Target page objectName (e.g. page-home).")
    p.add_argument("--list-pages", action="store_true", help="List pages (objectName/class/geometry).")
    p.add_argument("--list-panels", action="store_true", help="List panels on a page (requires --page).")
    p.add_argument("--panel-only", type=str, metavar="PANEL", default=None, help="Instantiate only a panel by objectName.")

    p.add_argument("--panel", type=str, default=None, help="Target panel objectName within the page.")
    p.add_argument("--out", type=str, default="ui_artifacts", help="Output directory (default ui_artifacts/).")
    p.add_argument("--name", type=str, default=None, help="Stable label for output filenames.")

    p.add_argument("--resolution", choices=["1440p", "1080p"], default="1440p", help="Canonical window resolution.")
    p.add_argument("--size", type=str, default=None, help="Override window size as WxH (e.g. 2560x1440).")
    p.add_argument("--full-content", action="store_true", help="Also render full content images for QScrollArea targets (v1).")
    return p.parse_args()


def main() -> int:
    _ensure_src_on_path()
    args = parse_args()

    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import QApplication

    from gridironlabs.core.config import AppPaths, load_config
    from gridironlabs.core.logging import configure_logging
    from gridironlabs.ui.main_window import GridironLabsMainWindow
    from gridironlabs.ui.dev.snapshot import (
        RES_1080P,
        RES_1440P,
        app_font_info,
        compute_target_rects,
        crop_pixmap_dpi_correct,
        env_scaling_info,
        find_widget_by_object_name,
        force_window_geometry,
        grab_window_pixmap,
        list_candidate_panels,
        render_full_content_for_scroll_area,
        save_pixmap,
        screen_info_for,
        scroll_diagnostics,
        wait_for_stable_geometry,
        widget_tree,
        write_json,
    )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = AppPaths.from_env()
    config = load_config(paths)
    logger = configure_logging(paths, config)

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Gridiron Labs")
    app.setOrganizationName("Gridiron Labs")
    # Keep font consistent with the real app.
    app.setFont(QFont("Roboto Condensed"))

    # Load the same stylesheet as the real app would.
    from gridironlabs import resources as package_resources

    try:
        stylesheet = package_resources.read_text("theme.qss", encoding="utf-8")
    except Exception:
        stylesheet = ""
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = GridironLabsMainWindow(config=config, paths=paths, logger=logger)
    window.show()
    app.processEvents()

    # Canonical sizing.
    if args.size:
        try:
            w_str, h_str = str(args.size).lower().replace(" ", "").split("x", 1)
            res_w, res_h = int(w_str), int(h_str)
        except Exception:
            raise SystemExit("--size must be formatted as WxH, e.g. 2560x1440")
    else:
        res = RES_1440P if args.resolution == "1440p" else RES_1080P
        res_w, res_h = res.width, res.height

    force_window_geometry(window, width=res_w, height=res_h, x=0, y=0)
    app.processEvents()

    # Discovery modes.
    if args.list_pages:
        pages: dict[str, Any] = window.pages  # type: ignore[attr-defined]
        for key, page in pages.items():
            print(
                f"{key}\t{page.objectName()}\t{type(page).__name__}\t"
                f"{page.geometry().x()},{page.geometry().y()},{page.geometry().width()},{page.geometry().height()}\t"
                f"visible={page.isVisible()}"
            )
        return 0

    if args.list_panels:
        if not args.page:
            raise SystemExit("--list-panels requires --page <page_objectName>")
        window.navigate_to(args.page)  # type: ignore[attr-defined]
        app.processEvents()
        page = find_widget_by_object_name(window, args.page)
        if page is None:
            raise SystemExit(f"Page not found: {args.page}")
        for p in list_candidate_panels(page):
            geom = p["geometry"]
            print(
                f"{p['objectName']}\t{p['class']}\t{geom['x']},{geom['y']},{geom['w']},{geom['h']}\tvisible={p['visible']}"
            )
        return 0

    if args.panel_only:
        from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

        from gridironlabs.ui.pages.base_page import BasePage
        from gridironlabs.ui.style.tokens import GRID
        from gridironlabs.ui.dev.panels import panel_registry

        reg = panel_registry()
        if args.panel_only not in reg:
            known = ", ".join(sorted(reg.keys())) or "(none registered)"
            raise SystemExit(f"Unknown panel-only target: {args.panel_only}. Known: {known}")

        # Minimal host window.
        host = QMainWindow()
        host.setObjectName("SnapshotPanelOnlyWindow")
        host.show()
        app.processEvents()
        force_window_geometry(host, width=res_w, height=res_h, x=0, y=0)
        app.processEvents()

        # Mimic Home grid pitch (BasePage uses GridCanvas with 36 cols).
        page = BasePage(cols=GRID.cols, rows=12)
        page.setObjectName("page-snapshot-panel-only")

        panel = reg[args.panel_only]()
        if not panel.objectName():
            panel.setObjectName(args.panel_only)
        # Full width by default; match Home spans once schedule integration lands.
        page.add_panel(panel, col=0, row=0, col_span=GRID.cols, row_span=12)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(page)
        host.setCentralWidget(container)

        settle = wait_for_stable_geometry(panel)
        host_pm = grab_window_pixmap(host)
        rects = compute_target_rects(host, panel, pixmap=host_pm)
        crop_pm = crop_pixmap_dpi_correct(host_pm, rect_px=_rect_from_dict(rects["rect_px"]))

        name = args.name or args.panel_only
        base = out_dir / f"{name}.panel-only"
        save_pixmap(Path(f"{base}.window.png"), host_pm)
        save_pixmap(Path(f"{base}.target.png"), crop_pm)

        payload: dict[str, Any] = {
            "name": name,
            "mode": "panel-only",
            "panel_objectName": args.panel_only,
            "requested": {"size": [res_w, res_h], "pos": [0, 0], "resolution": args.resolution, "size_arg": args.size},
            "actual": {
                "geometry": _rect_dict(host.geometry()),
                "frame_geometry": _rect_dict(host.frameGeometry()),
            },
            "screen": screen_info_for(host),
            "env": {"qt_scaling": env_scaling_info()},
            "font": app_font_info(),
            "settle": settle,
            "capture": {
                "window_pixmap_dpr": float(host_pm.devicePixelRatio() or 1.0),
                "target_rects": rects,
            },
            "tree": widget_tree(panel),
            "scrollAreas": scroll_diagnostics(panel),
        }

        if args.full_content:
            fulls: list[dict[str, Any]] = []
            from PySide6.QtWidgets import QAbstractScrollArea

            for area in panel.findChildren(QAbstractScrollArea):
                pm, meta = render_full_content_for_scroll_area(area)
                entry = {"objectName": area.objectName(), "class": type(area).__name__, "meta": meta}
                if pm is not None and meta.get("supported"):
                    safe_on = area.objectName() or type(area).__name__
                    out_path = Path(f"{base}.fullcontent.{safe_on}.png")
                    save_pixmap(out_path, pm)
                    entry["path"] = str(out_path)
                fulls.append(entry)
            payload["full_content"] = fulls

        write_json(Path(f"{base}.json"), payload)
        return 0

    # Snapshot mode (page / optional panel).
    if not args.page:
        raise SystemExit("Snapshot mode requires --page <page_objectName> (or use --list-pages / --list-panels / --panel-only).")
    page_name: str = args.page
    window.navigate_to(page_name)  # type: ignore[attr-defined]
    app.processEvents()

    page = find_widget_by_object_name(window, page_name)
    if page is None:
        raise SystemExit(f"Page not found: {page_name}")
    target: Any = page
    if args.panel:
        target_widget = find_widget_by_object_name(page, args.panel)
        if target_widget is None:
            raise SystemExit(f"Panel not found on page {page_name}: {args.panel}")
        target = target_widget

    settle = wait_for_stable_geometry(target)
    window_pm = grab_window_pixmap(window)
    rects = compute_target_rects(window, target, pixmap=window_pm)
    crop_pm = crop_pixmap_dpi_correct(window_pm, rect_px=_rect_from_dict(rects["rect_px"]))

    name = args.name or (args.panel or page_name)
    base = out_dir / name
    save_pixmap(Path(f"{base}.window.png"), window_pm)
    save_pixmap(Path(f"{base}.target.png"), crop_pm)

    payload: dict[str, Any] = {
        "name": name,
        "mode": "page" if args.panel is None else "panel",
        "requested": {"size": [res_w, res_h], "pos": [0, 0], "resolution": args.resolution, "size_arg": args.size},
        "actual": {
            "geometry": _rect_dict(window.geometry()),
            "frame_geometry": _rect_dict(window.frameGeometry()),
        },
        "screen": screen_info_for(window),
        "env": {"qt_scaling": env_scaling_info()},
        "font": app_font_info(),
        "settle": settle,
        "capture": {
            "window_pixmap_dpr": float(window_pm.devicePixelRatio() or 1.0),
            "target_rects": rects,
        },
        "tree": widget_tree(target),
        "scrollAreas": scroll_diagnostics(target),
    }

    # Optional full-content capture (v1: QScrollArea only).
    if args.full_content:
        fulls: list[dict[str, Any]] = []
        from PySide6.QtWidgets import QAbstractScrollArea

        for area in target.findChildren(QAbstractScrollArea):
            pm, meta = render_full_content_for_scroll_area(area)
            entry = {"objectName": area.objectName(), "class": type(area).__name__, "meta": meta}
            if pm is not None and meta.get("supported"):
                safe_on = area.objectName() or type(area).__name__
                out_path = Path(f"{base}.fullcontent.{safe_on}.png")
                save_pixmap(out_path, pm)
                entry["path"] = str(out_path)
            fulls.append(entry)
        payload["full_content"] = fulls

    write_json(Path(f"{base}.json"), payload)
    return 0


def _rect_dict(rect) -> dict[str, int]:
    return {"x": int(rect.x()), "y": int(rect.y()), "w": int(rect.width()), "h": int(rect.height())}


def _rect_from_dict(d: dict[str, int]):
    from PySide6.QtCore import QRect

    return QRect(int(d["x"]), int(d["y"]), int(d["w"]), int(d["h"]))


if __name__ == "__main__":
    raise SystemExit(main())

