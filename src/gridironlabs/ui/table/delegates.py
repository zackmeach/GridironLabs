"""Item delegates for OOTPTableView cells (icons, badges, rating colors, multi-line)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QModelIndex, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


def _rating_color(value: int) -> QColor:
    # Mirror the broad tiers used in theme.qss; keep logic stable.
    if value >= 70:
        return QColor("#0284c7")  # blue
    if value >= 55:
        return QColor("#10b981")  # green
    if value >= 40:
        return QColor("#f59e0b")  # amber
    return QColor("#ef4444")  # red


class RatingColorDelegate(QStyledItemDelegate):
    """Paint numeric values with a tier color (OOTP-style ratings columns)."""

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:  # noqa: N802
        super().initStyleOption(option, index)
        # Ensure right-aligned numeric display if model didn't set it.
        option.displayAlignment = option.displayAlignment or (Qt.AlignRight | Qt.AlignVCenter)

    def paint(  # noqa: N802 - Qt API
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> None:
        value = index.data(Qt.DisplayRole)
        try:
            rating = int(str(value).strip())
        except Exception:
            rating = -1

        opt = QStyleOptionViewItem(option)
        if rating >= 0:
            opt.palette.setColor(QPalette.ColorRole.Text, _rating_color(rating))
        super().paint(painter, opt, index)


__all__ = ["RatingColorDelegate"]

