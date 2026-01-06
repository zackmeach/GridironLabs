"""Deterministic UI snapshot utilities (PNG + JSON).

This module is used by the `scripts/ui_snapshot.py` CLI to:
- force deterministic window geometry
- wait for stable layout
- capture screenshots with DPI-correct crops
- dump widget tree + key geometry/metadata for agent inspection
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QFontInfo, QGuiApplication, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QAbstractScrollArea, QWidget


@dataclass(frozen=True)
class SnapshotResolution:
    width: int
    height: int


RES_1440P = SnapshotResolution(2560, 1440)
RES_1080P = SnapshotResolution(1920, 1080)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def save_pixmap(path: Path, pixmap: QPixmap) -> None:
    ensure_dir(path.parent)
    pixmap.save(str(path))


def env_scaling_info() -> dict[str, str | None]:
    keys = [
        "QT_SCALE_FACTOR",
        "QT_SCREEN_SCALE_FACTORS",
        "QT_AUTO_SCREEN_SCALE_FACTOR",
        "QT_FONT_DPI",
    ]
    return {k: os.environ.get(k) for k in keys}


def app_font_info() -> dict[str, Any]:
    app = QApplication.instance()
    if app is None:
        return {}
    font = app.font()
    try:
        resolved = QFontInfo(font).family()
    except Exception:
        resolved = font.family()
    # PySide enum wrappers can vary; keep JSON stable across platforms.
    style_hint = font.styleHint()
    style_hint_value = getattr(style_hint, "value", None)
    return {
        "requested_family": font.family(),
        "resolved_family": resolved,
        "point_size": font.pointSize(),
        "pixel_size": font.pixelSize(),
        "style_hint": int(style_hint_value) if style_hint_value is not None else str(style_hint),
    }


def screen_info_for(widget: QWidget) -> dict[str, Any]:
    # Prefer the screen hosting the widget; fall back to primary.
    screen = None
    try:
        screen = widget.screen()
    except Exception:
        screen = None
    if screen is None:
        screen = QGuiApplication.primaryScreen()
    if screen is None:
        return {}
    return {
        "name": getattr(screen, "name", lambda: None)(),
        "geometry": _rect_dict(screen.geometry()),
        "available_geometry": _rect_dict(screen.availableGeometry()),
        "device_pixel_ratio": float(screen.devicePixelRatio()),
        "logical_dpi_x": float(screen.logicalDotsPerInchX()),
        "logical_dpi_y": float(screen.logicalDotsPerInchY()),
        "physical_dpi_x": float(screen.physicalDotsPerInchX()),
        "physical_dpi_y": float(screen.physicalDotsPerInchY()),
    }


def force_window_geometry(window: QWidget, *, width: int, height: int, x: int = 0, y: int = 0) -> None:
    # Use a deterministic top-left position to simplify crop math.
    window.setGeometry(int(x), int(y), int(width), int(height))
    QApplication.processEvents()


def wait_for_stable_geometry(
    target: QWidget,
    *,
    max_wait_ms: int = 1500,
    interval_ms: int = 50,
    stable_samples: int = 3,
) -> dict[str, Any]:
    """Wait until target geometry is stable for N consecutive samples."""

    start = time.monotonic()
    samples: list[dict[str, Any]] = []

    def snapshot() -> dict[str, Any]:
        try:
            global_pos = target.mapToGlobal(QPoint(0, 0))
            size = target.size()
            visible = target.isVisible()
        except Exception:
            global_pos = QPoint(-1, -1)
            size = None
            visible = False
        return {
            "t_ms": int((time.monotonic() - start) * 1000),
            "global_pos": [int(global_pos.x()), int(global_pos.y())],
            "size": [int(size.width()), int(size.height())] if size is not None else None,
            "visible": bool(visible),
        }

    consecutive = 0
    last = None
    while True:
        QApplication.processEvents()
        cur = snapshot()
        samples.append(cur)
        if last is not None and _stable_key(cur) == _stable_key(last):
            consecutive += 1
        else:
            consecutive = 1
        last = cur

        if consecutive >= stable_samples:
            break
        if (time.monotonic() - start) * 1000 >= max_wait_ms:
            break
        time.sleep(max(0.0, interval_ms / 1000.0))

    stable_after_ms = samples[-1]["t_ms"] if samples else None
    return {
        "stable_after_ms": stable_after_ms,
        "stable_samples": int(stable_samples),
        "samples": samples,
    }


def grab_window_pixmap(window: QWidget) -> QPixmap:
    screen = window.screen() or QGuiApplication.primaryScreen()
    if screen is None:
        raise RuntimeError("No QScreen available for screenshot capture")
    return screen.grabWindow(int(window.winId()))


def compute_target_rects(window: QWidget, target: QWidget, *, pixmap: QPixmap) -> dict[str, Any]:
    """Compute logical and pixel rectangles for cropping target from a window screenshot."""

    window_top_left = window.mapToGlobal(QPoint(0, 0))
    target_top_left = target.mapToGlobal(QPoint(0, 0))
    size = target.size()
    rect_logical = QRect(target_top_left - window_top_left, size)

    dpr = float(pixmap.devicePixelRatio() or 1.0)
    rect_px = QRect(
        int(round(rect_logical.x() * dpr)),
        int(round(rect_logical.y() * dpr)),
        int(round(rect_logical.width() * dpr)),
        int(round(rect_logical.height() * dpr)),
    )
    return {
        "device_pixel_ratio": dpr,
        "rect_logical": _rect_dict(rect_logical),
        "rect_px": _rect_dict(rect_px),
    }


def crop_pixmap_dpi_correct(pixmap: QPixmap, *, rect_px: QRect) -> QPixmap:
    """Crop a pixmap using pixel-space coordinates (DPI-correct)."""

    img: QImage = pixmap.toImage()
    cropped_img = img.copy(rect_px)
    out = QPixmap.fromImage(cropped_img)
    # Preserve DPR so downstream consumers interpret the crop correctly.
    out.setDevicePixelRatio(pixmap.devicePixelRatio() or 1.0)
    return out


def widget_tree(root: QWidget, *, include_children: bool = True) -> dict[str, Any]:
    """Capture a widget subtree with geometry and key dynamic properties."""

    def _node(w: QWidget) -> dict[str, Any]:
        props = _key_properties(w)
        try:
            global_pos = w.mapToGlobal(QPoint(0, 0))
        except Exception:
            global_pos = QPoint(-1, -1)

        data: dict[str, Any] = {
            "class": type(w).__name__,
            "objectName": w.objectName(),
            "visible": bool(w.isVisible()),
            "enabled": bool(w.isEnabled()),
            "geometry": _rect_dict(w.geometry()),
            "global_pos": [int(global_pos.x()), int(global_pos.y())],
            "properties": props,
        }
        if include_children:
            children = [c for c in w.findChildren(QWidget, options=Qt.FindDirectChildrenOnly)]
            data["children"] = [_node(c) for c in children]
        return data

    return _node(root)


def find_widget_by_object_name(root: QWidget, name: str) -> QWidget | None:
    if root.objectName() == name:
        return root
    for child in root.findChildren(QWidget):
        if child.objectName() == name:
            return child
    return None


def list_candidate_panels(root: QWidget) -> list[dict[str, Any]]:
    """List candidate panels within a page (PanelChrome + panel-* objectNames)."""
    out: list[dict[str, Any]] = []
    for w in root.findChildren(QWidget):
        on = w.objectName()
        if not on:
            continue
        if on.startswith("panel-") or type(w).__name__ == "PanelChrome":
            out.append(
                {
                    "objectName": on,
                    "class": type(w).__name__,
                    "geometry": _rect_dict(w.geometry()),
                    "visible": bool(w.isVisible()),
                }
            )
    # Prefer stable output ordering.
    out.sort(key=lambda r: (r["objectName"], r["class"]))
    return out


def scroll_diagnostics(root: QWidget) -> list[dict[str, Any]]:
    """Collect scroll/viewport metrics for any QAbstractScrollArea in subtree."""
    out: list[dict[str, Any]] = []
    for area in root.findChildren(QAbstractScrollArea):
        try:
            vbar = area.verticalScrollBar()
            hbar = area.horizontalScrollBar()
        except Exception:
            continue

        vpol = area.verticalScrollBarPolicy()
        hpol = area.horizontalScrollBarPolicy()
        vpol_val = getattr(vpol, "value", None)
        hpol_val = getattr(hpol, "value", None)

        entry: dict[str, Any] = {
            "class": type(area).__name__,
            "objectName": area.objectName(),
            "geometry": _rect_dict(area.geometry()),
            "viewport_size": [int(area.viewport().width()), int(area.viewport().height())],
            "vbar": {
                "policy": int(vpol_val) if vpol_val is not None else str(vpol),
                "visible": bool(vbar.isVisible()),
                "maximum": int(vbar.maximum()),
                "page_step": int(vbar.pageStep()),
                "value": int(vbar.value()),
            },
            "hbar": {
                "policy": int(hpol_val) if hpol_val is not None else str(hpol),
                "visible": bool(hbar.isVisible()),
                "maximum": int(hbar.maximum()),
                "page_step": int(hbar.pageStep()),
                "value": int(hbar.value()),
            },
        }

        # QTableView last-row visibility check (most reliable for table surfaces).
        try:
            from PySide6.QtWidgets import QTableView

            if isinstance(area, QTableView):
                model = area.model()
                if model is not None and model.rowCount() > 0:
                    last_row = int(model.rowCount() - 1)
                    idx0 = model.index(last_row, 0)
                    rect = area.visualRect(idx0)
                    entry["last_row"] = {
                        "row": last_row,
                        "visual_rect_in_viewport": _rect_dict(rect),
                        "fully_visible_in_viewport": area.viewport().rect().contains(rect),
                    }
        except Exception:
            pass

        # QScrollArea content metrics (best-effort).
        try:
            content = area.widget()  # type: ignore[attr-defined]
        except Exception:
            content = None
        if content is not None:
            try:
                entry["content_size"] = [int(content.width()), int(content.height())]
                hint = content.sizeHint()
                entry["content_size_hint"] = [int(hint.width()), int(hint.height())]
            except Exception:
                pass

            # Heuristic \"last content child\" bounding rect mapped into viewport.
            try:
                last = _find_last_visible_descendant(content)
                if last is not None:
                    last_rect = QRect(QPoint(0, 0), last.size())
                    top_left_in_view = last.mapTo(area.viewport(), QPoint(0, 0))
                    last_rect_in_view = QRect(top_left_in_view, last.size())
                    entry["last_content_descendant"] = {
                        "objectName": last.objectName(),
                        "class": type(last).__name__,
                        "rect_in_viewport": _rect_dict(last_rect_in_view),
                        "fully_visible_in_viewport": area.viewport().rect().contains(last_rect_in_view),
                    }
            except Exception:
                pass

        # \"clipped\" signal.
        entry["is_clipped_vertical"] = int(vbar.maximum()) > 0
        out.append(entry)

    out.sort(key=lambda r: (r.get("objectName") or "", r.get("class") or ""))
    return out


def render_full_content_for_scroll_area(area: QAbstractScrollArea) -> tuple[QPixmap | None, dict[str, Any]]:
    """Render full content for QScrollArea-like surfaces (v1: QScrollArea only)."""
    meta: dict[str, Any] = {"supported": False}
    try:
        from PySide6.QtWidgets import QScrollArea

        if not isinstance(area, QScrollArea):
            meta["reason"] = "Only QScrollArea full-content render is supported in v1"
            return None, meta
        content = area.widget()
        if content is None:
            meta["reason"] = "No content widget set"
            return None, meta
        dpr = float((area.window().windowHandle().devicePixelRatio() if area.window().windowHandle() else 1.0))
        size = content.size()
        img = QImage(int(round(size.width() * dpr)), int(round(size.height() * dpr)), QImage.Format_ARGB32)
        img.setDevicePixelRatio(dpr)
        img.fill(Qt.GlobalColor.transparent)
        # Render at 0,0 in its own coordinate space.
        from PySide6.QtGui import QPainter

        painter = QPainter(img)
        content.render(painter)
        painter.end()
        pm = QPixmap.fromImage(img)
        pm.setDevicePixelRatio(dpr)
        meta["supported"] = True
        meta["device_pixel_ratio"] = dpr
        meta["content_size"] = [int(size.width()), int(size.height())]
        return pm, meta
    except Exception as exc:
        meta["reason"] = f"Exception: {exc}"
        return None, meta


def _stable_key(sample: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(sample.get(k) for k in ("global_pos", "size", "visible"))


def _rect_dict(rect: QRect) -> dict[str, int]:
    return {"x": int(rect.x()), "y": int(rect.y()), "w": int(rect.width()), "h": int(rect.height())}


def _key_properties(w: QWidget) -> dict[str, Any]:
    # Keep this small and stable; include the properties that drive QSS/contract behavior.
    keys = [
        "panelVariant",
        "barRole",
        "scrollVariant",
        "leadersVariant",
        "stripe",
        "severity",
        "intent",
    ]
    props: dict[str, Any] = {}
    for k in keys:
        try:
            v = w.property(k)
        except Exception:
            v = None
        if v is not None:
            props[k] = v
    return props


def _find_last_visible_descendant(root: QWidget) -> QWidget | None:
    """Heuristic: choose the visible descendant with the largest y+height in root coords."""
    best: tuple[int, QWidget] | None = None
    for w in root.findChildren(QWidget):
        try:
            if not w.isVisible():
                continue
            pos = w.mapTo(root, QPoint(0, 0))
            bottom = int(pos.y() + w.height())
        except Exception:
            continue
        if best is None or bottom > best[0]:
            best = (bottom, w)
    return best[1] if best else None


__all__ = [
    "RES_1440P",
    "RES_1080P",
    "SnapshotResolution",
    "app_font_info",
    "compute_target_rects",
    "crop_pixmap_dpi_correct",
    "env_scaling_info",
    "find_widget_by_object_name",
    "force_window_geometry",
    "grab_window_pixmap",
    "list_candidate_panels",
    "render_full_content_for_scroll_area",
    "save_pixmap",
    "screen_info_for",
    "scroll_diagnostics",
    "wait_for_stable_geometry",
    "widget_tree",
    "write_json",
]

