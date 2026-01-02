"""OOTP-style QTableView wrapper.

This is the foundation for large/high-row-count \"table-ish\" surfaces:
- consistent row heights
- QSS-driven header styling
- sorting via QSortFilterProxyModel
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QTimer, Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView


@dataclass(frozen=True)
class TablePersistenceKey:
    page_id: str
    table_id: str
    version: str = "v1"


class OOTPTableView(QTableView):
    def __init__(
        self,
        *,
        row_height: int = 24,
        allow_horizontal_scroll: bool = True,
        scroll_variant: str | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("OOTPTableView")
        if scroll_variant is not None:
            self.setProperty("scrollVariant", scroll_variant)

        self.setAlternatingRowColors(False)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)

        vh = self.verticalHeader()
        vh.setVisible(False)
        vh.setDefaultSectionSize(int(row_height))

        hh = self.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QHeaderView.Interactive)
        hh.setHighlightSections(False)
        hh.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        if allow_horizontal_scroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._proxy: QSortFilterProxyModel | None = None
        self._persistence: TablePersistenceKey | None = None
        self._settings = None
        self._restore_scheduled = False
        self._in_restore = False
        self._restored_once = False
        self._persistence_ready = False

    def set_source_model(self, model) -> None:
        """Wrap the given model in a sorting proxy and set it on the view."""
        proxy = QSortFilterProxyModel(self)
        proxy.setDynamicSortFilter(True)
        proxy.setSortCaseSensitivity(Qt.CaseInsensitive)
        proxy.setSourceModel(model)
        self._proxy = proxy
        self.setModel(proxy)
        self.sortByColumn(0, Qt.AscendingOrder)
        self._apply_default_column_widths_if_available()
        self._schedule_restore()

    @property
    def proxy(self) -> QSortFilterProxyModel | None:
        return self._proxy

    @property
    def restored_once(self) -> bool:
        return bool(self._restored_once)

    def enable_persistence(self, *, settings, key: TablePersistenceKey) -> None:
        """Enable persistence for column widths and sort state.

        `settings` should be a QSettings instance (or compatible).
        """
        self._settings = settings
        self._persistence = key
        # If there's existing state, avoid overwriting it with initial layout signals
        # before we've had a chance to restore.
        prefix = self._settings_prefix()
        has_existing = False
        if prefix is not None:
            try:
                has_existing = bool(settings.value(f"{prefix}/columns/widths")) or bool(
                    settings.value(f"{prefix}/sort/column")
                )
            except Exception:
                has_existing = False
        self._persistence_ready = not has_existing

        hh = self.horizontalHeader()
        hh.sectionResized.connect(lambda *_args: self._save_column_widths())
        hh.sortIndicatorChanged.connect(lambda idx, order: self._save_sort(idx, order))

        # Apply immediately if model already present.
        self._schedule_restore()

    def _apply_default_column_widths_if_available(self) -> None:
        model = self.model()
        if model is None:
            return
        # Default widths should be applied by the caller for now.
        return

    def _settings_prefix(self) -> str | None:
        if self._settings is None or self._persistence is None:
            return None
        key = self._persistence
        return f"ui/pages/{key.page_id}/tables/{key.table_id}/{key.version}"

    def _schedule_restore(self, *, force: bool = False) -> None:
        if self._restore_scheduled and not force:
            return
        self._restore_scheduled = True
        QTimer.singleShot(0, self._restore_persistence)

    def _restore_persistence(self) -> None:
        self._restore_scheduled = False
        # The view can be destroyed before our QTimer fires (pytest-qt teardown).
        try:
            _ = self.objectName()
        except RuntimeError:
            return
        prefix = self._settings_prefix()
        if prefix is None:
            return
        try:
            model = self.model()
        except RuntimeError:
            return
        if model is None:
            return
        settings = self._settings

        def _to_int(v) -> int | None:
            try:
                # QVariant-like objects may stringify cleanly.
                return int(v)  # type: ignore[arg-type]
            except Exception:
                try:
                    return int(str(v).strip())
                except Exception:
                    return None

        # Column widths are stored as a comma-separated string for backend consistency.
        raw_widths = settings.value(f"{prefix}/columns/widths", defaultValue=None)
        widths_list: list[object] = []
        if raw_widths:
            widths_list = [w.strip() for w in str(raw_widths).split(",") if w.strip()]

        self._in_restore = True
        try:
            col_count = int(model.columnCount())
            persist_count = max(0, col_count - 1) if self.horizontalHeader().stretchLastSection() else col_count
            for i, w in enumerate(widths_list[:persist_count]):
                try:
                    maybe = _to_int(w)
                    if maybe is None:
                        continue
                    hh = self.horizontalHeader()
                    # Ensure the section is actually resizable before applying persisted width.
                    hh.setSectionResizeMode(i, QHeaderView.Interactive)
                    hh.resizeSection(i, maybe)
                    if i == 0:
                        self.setProperty("restoredWidth0", maybe)
                except Exception:
                    continue
        finally:
            self._in_restore = False
            self._restored_once = True
            # After the first restore pass, allow future user-driven changes to persist.
            self._persistence_ready = True

        # Sort state
        sort_col = settings.value(f"{prefix}/sort/column")
        sort_order = settings.value(f"{prefix}/sort/order")
        try:
            if sort_col is not None and sort_order is not None:
                self.sortByColumn(int(sort_col), Qt.SortOrder(int(sort_order)))
        except Exception:
            return

    def _save_column_widths(self, *, force: bool = False) -> None:
        prefix = self._settings_prefix()
        if prefix is None:
            return
        if self._in_restore:
            return
        if (not force) and (not self._persistence_ready):
            return
        model = self.model()
        if model is None:
            return
        settings = self._settings
        widths: list[int] = []
        col_count = int(model.columnCount())
        persist_count = max(0, col_count - 1) if self.horizontalHeader().stretchLastSection() else col_count
        for i in range(persist_count):
            widths.append(int(self.columnWidth(i)))
        settings.setValue(f"{prefix}/columns/widths", ",".join(str(w) for w in widths))
        try:
            settings.sync()
        except Exception:
            pass

    def _save_sort(self, logicalIndex: int, order: Qt.SortOrder) -> None:  # noqa: N802 - Qt signal
        prefix = self._settings_prefix()
        if prefix is None:
            return
        if self._in_restore or not self._persistence_ready:
            return
        settings = self._settings
        settings.setValue(f"{prefix}/sort/column", int(logicalIndex))
        # PySide's enum types aren't always directly int()-castable.
        try:
            order_int = int(order.value)  # type: ignore[union-attr]
        except Exception:
            order_int = 0 if order == Qt.AscendingOrder else 1
        settings.setValue(f"{prefix}/sort/order", order_int)
        try:
            settings.sync()
        except Exception:
            pass

    def setColumnWidth(self, column: int, width: int) -> None:  # noqa: N802 - Qt API
        # Route via the header to avoid layout resets in some Qt styles.
        self.horizontalHeader().resizeSection(int(column), int(width))
        # Programmatic width changes don't always emit sectionResized; persist explicitly.
        self._save_column_widths(force=True)

    def showEvent(self, event) -> None:  # type: ignore[override]  # pragma: no cover
        super().showEvent(event)
        # Ensure persistence is applied after the view is actually shown/layouted.
        self._schedule_restore(force=True)

    def resizeEvent(self, event) -> None:  # type: ignore[override]  # pragma: no cover
        super().resizeEvent(event)
        # First real resize after show is a reliable point to apply column widths.
        if self._persistence is not None and self._settings is not None and not self._restored_once:
            self._schedule_restore(force=True)


__all__ = ["OOTPTableView", "TablePersistenceKey"]

