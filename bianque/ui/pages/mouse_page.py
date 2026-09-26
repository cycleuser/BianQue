"""Mouse / touchpad inspection: capture mode with dead-spot mapping.

The page shows a full-size, touchpad-proportioned map. Entering capture mode
grabs the mouse (like a virtual machine) so every movement is mapped onto the
pad; the cells the cursor passes over light up green. Press the release key
(Command+G / Win+G / Super+G) to release. Cells that never lit up are the
dead spots where the touchpad/mouse does not respond.
"""

from __future__ import annotations

import platform
from collections.abc import Callable

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QCursor, QKeyEvent, QMouseEvent, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QWidget

from bianque.i18n import tr
from bianque.ui.pages.base import BasePage

GRID_COLS = 12
GRID_ROWS = 8
RELATIVE_SCALE = 2.0


def _release_key_name() -> str:
    system = platform.system()
    if system == "Darwin":
        return "Command"
    if system == "Windows":
        return "Win"
    return "Super"


def _is_release_key(event: QKeyEvent) -> bool:
    if event.key() != Qt.Key.Key_G:
        return False
    mods = event.modifiers()
    return bool(mods & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier))


class MouseMapView(QWidget):
    """Full-size touchpad map with mouse capture and dead-spot coverage."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._captured = False
        self._pos = (0.5, 0.5)
        self._trail: list[tuple[float, float]] = []
        self._covered: set[tuple[int, int]] = set()
        self._lock_center = QPoint()
        self.left = False
        self.middle = False
        self.right = False
        self.wheel_up = 0
        self.wheel_down = 0
        self.moved = False
        self._callback: Callable[[], None] | None = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(300)

    # ---- capture ----
    def start_capture(self) -> None:
        self._captured = True
        self._trail.clear()
        self.setCursor(Qt.CursorShape.BlankCursor)
        QApplication.setOverrideCursor(Qt.CursorShape.BlankCursor)
        self.grabMouse()
        self.setFocus()
        # Lock the physical pointer inside the map so it can't wander outside.
        self._lock_center = self.mapToGlobal(self.rect().center())
        QCursor.setPos(self._lock_center)
        self._notify()

    def stop_capture(self) -> None:
        if not self._captured:
            return
        self._captured = False
        self.unsetCursor()
        QApplication.restoreOverrideCursor()
        self.releaseMouse()
        self._notify()

    def _lock_pointer(self) -> None:
        QCursor.setPos(self._lock_center)

    def set_callback(self, cb: Callable[[], None]) -> None:
        self._callback = cb

    def _notify(self) -> None:
        if self._callback is not None:
            self._callback()

    # ---- coverage ----
    def total_cells(self) -> int:
        return GRID_COLS * GRID_ROWS

    def covered_cells(self) -> int:
        return len(self._covered)

    def dead_cells(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if (r, c) not in self._covered]

    def _mark_cell(self) -> None:
        nx, ny = self._pos
        col = min(int(nx * GRID_COLS), GRID_COLS - 1)
        row = min(int(ny * GRID_ROWS), GRID_ROWS - 1)
        self._covered.add((row, col))

    # ---- events ----
    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if self._captured and _is_release_key(event):
            self.stop_capture()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not self._captured:
            return
        self.moved = True
        # Relative mapping: the physical pointer is locked to the map centre,
        # only its delta moves the mapped dot (like a VM capturing the mouse).
        global_pos = event.globalPosition().toPoint()
        dx = global_pos.x() - self._lock_center.x()
        dy = global_pos.y() - self._lock_center.y()
        nx = max(0.0, min(1.0, self._pos[0] + dx / max(self.width(), 1) * RELATIVE_SCALE))
        ny = max(0.0, min(1.0, self._pos[1] + dy / max(self.height(), 1) * RELATIVE_SCALE))
        self._pos = (nx, ny)
        self._trail.append((nx, ny))
        if len(self._trail) > 300:
            self._trail = self._trail[-300:]
        self._mark_cell()
        QCursor.setPos(self._lock_center)
        self.update()
        self._notify()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not self._captured:
            return
        btn = event.button()
        self.left |= btn == Qt.MouseButton.LeftButton
        self.middle |= btn == Qt.MouseButton.MiddleButton
        self.right |= btn == Qt.MouseButton.RightButton
        self._notify()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if not self._captured:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self.wheel_up += 1
        elif delta < 0:
            self.wheel_down += 1
        self._notify()

    # ---- painting ----
    def _pad_rect(self) -> QRectF:
        m = 10.0
        return QRectF(m, m, max(self.width() - 2 * m, 1), max(self.height() - 2 * m, 1))

    def _cell_rect(self, row: int, col: int, rect: QRectF) -> QRectF:
        cw = rect.width() / GRID_COLS
        ch = rect.height() / GRID_ROWS
        return QRectF(rect.left() + col * cw, rect.top() + row * ch, cw, ch)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._pad_rect()

        # background
        painter.setPen(QPen(QColor("#343a45"), 1.5))
        painter.setBrush(QColor("#14161a"))
        painter.drawRoundedRect(rect, 10, 10)

        # covered cells (green)
        painter.setPen(QPen(QColor("#1f3b28"), 1))
        painter.setBrush(QColor(22, 163, 74, 90))
        for row, col in self._covered:
            painter.drawRect(self._cell_rect(row, col, rect))

        # grid lines
        painter.setPen(QPen(QColor("#2a313b"), 1))
        cw = rect.width() / GRID_COLS
        ch = rect.height() / GRID_ROWS
        for c in range(1, GRID_COLS):
            x = rect.left() + c * cw
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
        for r in range(1, GRID_ROWS):
            y = rect.top() + r * ch
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))

        # trail
        if self._captured and len(self._trail) > 1:
            pts = [
                QPointF(rect.left() + nx * rect.width(), rect.top() + ny * rect.height())
                for nx, ny in self._trail
            ]
            painter.setPen(QPen(QColor(59, 130, 246, 120), 2))
            for i in range(len(pts) - 1):
                painter.drawLine(pts[i], pts[i + 1])

        # current position dot
        if self._captured:
            nx, ny = self._pos
            p = QPointF(rect.left() + nx * rect.width(), rect.top() + ny * rect.height())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(59, 130, 246, 50))
            painter.drawEllipse(p, 12, 12)
            painter.setBrush(QColor("#3b82f6"))
            painter.drawEllipse(p, 5, 5)

        # center hint text
        painter.setPen(QColor("#e6e8eb"))
        if self._captured:
            hint = tr("Press {0}+G to release", _release_key_name())
        else:
            hint = tr("Click Start Capture to begin")
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, hint)
        painter.end()


class MousePage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Mouse / Touchpad", "Capture the pointer and sweep the pad to find dead spots", parent)

        self.map = MouseMapView()
        self.map.set_callback(self._refresh)
        self.content.addWidget(self.map, stretch=1)

        btn_row = QHBoxLayout()
        self.capture_btn = QPushButton(tr("Start Capture"))
        self.capture_btn.setObjectName("primary")
        self.capture_btn.clicked.connect(self._toggle_capture)
        btn_row.addWidget(self.capture_btn)
        btn_row.addStretch(1)
        self.content.addLayout(btn_row)

        self.info_lbl = QLabel()
        self.content.addWidget(self.info_lbl)

        row2 = QHBoxLayout()
        self.ok_btn = QPushButton(tr("Confirm OK ✓"))
        self.bad_btn = QPushButton(tr("Confirm faulty ✗"))
        self.ok_btn.clicked.connect(self._confirm_ok)
        self.bad_btn.clicked.connect(self._confirm_bad)
        row2.addWidget(self.ok_btn)
        row2.addWidget(self.bad_btn)
        row2.addStretch(1)
        self.content.addLayout(row2)

        self._refresh()

    def _toggle_capture(self) -> None:
        if self.map._captured:
            self.map.stop_capture()
        else:
            self.map.start_capture()

    def _refresh(self) -> None:
        m = self.map
        if m._captured:
            self.capture_btn.setText(tr("Stop Capture"))
        else:
            self.capture_btn.setText(tr("Start Capture"))

        total = m.total_cells()
        covered = m.covered_cells()
        dead = m.dead_cells()
        left = "✓" if m.left else tr("Not pressed")
        middle = "✓" if m.middle else tr("Not pressed")
        right = "✓" if m.right else tr("Not pressed")
        self.info_lbl.setText(
            tr("Coverage {0}/{1} cells · dead {2}", covered, total, len(dead))
            + "\n"
            + f"{tr('Left')}: {left}    {tr('Middle')}: {middle}    {tr('Right')}: {right}"
            + f"    {tr('Wheel')}: {tr('up {0} / down {1}', m.wheel_up, m.wheel_down)}"
        )

    def _confirm_ok(self) -> None:
        m = self.map
        covered = m.covered_cells()
        total = m.total_cells()
        data = {
            "covered": covered,
            "total": total,
            "left": m.left,
            "middle": m.middle,
            "right": m.right,
            "wheel_up": m.wheel_up,
            "wheel_down": m.wheel_down,
        }
        if covered == total:
            self.mark_pass("mouse.buttons", "Mouse Buttons", tr("All cells covered ✓"), data)
        else:
            self.mark_pass(
                "mouse.buttons",
                "Mouse Buttons",
                tr("Coverage {0}/{1} cells", covered, total),
                data,
            )

    def _confirm_bad(self) -> None:
        m = self.map
        dead = m.dead_cells()
        self.mark_fail(
            "mouse.buttons",
            "Mouse Buttons",
            tr("Dead spots: {0} cells", len(dead)),
            {"dead_cells": dead},
        )
