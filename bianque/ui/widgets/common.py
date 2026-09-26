"""Reusable UI widgets: status badge, level meter, info grid."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from bianque.core.models import Status

_STATUS_STYLE = {
    Status.PASS: ("status-pass", "通过"),
    Status.FAIL: ("status-fail", "失败"),
    Status.UNKNOWN: ("status-unknown", "未知"),
    Status.SKIPPED: ("status-skipped", "跳过"),
}


def status_label(status: str) -> QLabel:
    objname, text = _STATUS_STYLE.get(status, ("status-unknown", status))
    label = QLabel(text)
    label.setObjectName(objname)
    return label


class LevelMeter(QWidget):
    """Horizontal audio level meter with peak hold."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._level = 0.0
        self._peak = 0.0
        self.setMinimumHeight(40)
        self.setMinimumWidth(200)

    def set_level(self, value: float) -> None:
        self._level = max(0.0, min(1.0, value))
        if self._level > self._peak:
            self._peak = self._level
        self.update()

    def reset(self) -> None:
        self._level = 0.0
        self._peak = 0.0
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1c1f24"))
        painter.drawRoundedRect(0, 0, w, h, 4, 4)

        if self._level <= 0.0:
            return

        bar_w = int(w * self._level)
        if bar_w > 0:
            color = QColor("#16a34a")
            if self._level > 0.8:
                color = QColor("#dc2626")
            elif self._level > 0.5:
                color = QColor("#d97706")
            painter.setBrush(color)
            painter.drawRoundedRect(0, 0, bar_w, h, 4, 4)

        peak_x = int(w * self._peak) - 2
        if peak_x > 0:
            painter.setBrush(QColor("#e6e8eb"))
            painter.drawRoundedRect(peak_x, 0, 2, h, 1, 1)


def info_grid(items: list[tuple[str, Any]], parent: QWidget | None = None) -> QWidget:
    """Render a key/value list as a two-column grid inside a frame."""
    frame = QFrame(parent)
    layout = QGridLayout(frame)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setHorizontalSpacing(16)
    layout.setVerticalSpacing(6)
    for row, (key, value) in enumerate(items):
        key_lbl = QLabel(str(key))
        key_lbl.setStyleSheet("color: #9aa3ad;")
        val_lbl = QLabel(str(value))
        val_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        val_lbl.setWordWrap(True)
        layout.addWidget(key_lbl, row, 0, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(val_lbl, row, 1)
    layout.setColumnStretch(0, 0)
    layout.setColumnStretch(1, 1)
    return frame


def info_box(title: str, items: list[tuple[str, Any]], parent: QWidget | None = None) -> QGroupBox:
    """A framed group with a title and an info grid."""
    box = QGroupBox(title, parent)
    lay = QVBoxLayout(box)
    lay.addWidget(info_grid(items, box))
    return box
