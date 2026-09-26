"""Mouse / touchpad inspection: buttons, wheel and movement."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from bianque.i18n import tr
from bianque.ui.pages.base import BasePage


class MouseTestArea(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.left = False
        self.middle = False
        self.right = False
        self.wheel_up = 0
        self.wheel_down = 0
        self.moved = False
        self._pos = (0.0, 0.0)
        self._callback: Callable[[], None] | None = None
        self.setMinimumHeight(220)
        self.setMouseTracking(True)
        self.setStyleSheet("border: 1px dashed #343a45; border-radius: 6px;")

    def set_callback(self, cb: Callable[[], None]) -> None:
        self._callback = cb

    def _notify(self) -> None:
        if self._callback is not None:
            self._callback()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        btn = event.button()
        self.left |= btn == Qt.MouseButton.LeftButton
        self.middle |= btn == Qt.MouseButton.MiddleButton
        self.right |= btn == Qt.MouseButton.RightButton
        self._notify()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self.moved = True
        self._pos = (event.position().x(), event.position().y())
        self._notify()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        delta = event.angleDelta().y()
        if delta > 0:
            self.wheel_up += 1
        elif delta < 0:
            self.wheel_down += 1
        self._notify()


class MousePage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Mouse / Touchpad", "Click, scroll and move the pointer in the area below", parent)

        self.area = MouseTestArea()
        self.area.set_callback(self._refresh)
        self.content.addWidget(self.area, stretch=1)

        self.info_lbl = QLabel()
        self.content.addWidget(self.info_lbl)

        self.ok_btn = QPushButton(tr("Confirm OK ✓"))
        self.bad_btn = QPushButton(tr("Confirm faulty ✗"))
        self.ok_btn.clicked.connect(self._confirm_ok)
        self.bad_btn.clicked.connect(self._confirm_bad)
        self.content.addWidget(self.ok_btn)
        self.content.addWidget(self.bad_btn)

        self._refresh()

    def _refresh(self) -> None:
        a = self.area
        left = "✓" if a.left else tr("Not pressed")
        middle = "✓" if a.middle else tr("Not pressed")
        right = "✓" if a.right else tr("Not pressed")
        moved = "✓" if a.moved else tr("Not pressed")
        wheel = tr("up {0} / down {1}", a.wheel_up, a.wheel_down)
        self.info_lbl.setText(
            f"{tr('Left')}: {left}    {tr('Middle')}: {middle}    {tr('Right')}: {right}\n"
            f"{tr('Wheel')}: {wheel}    {tr('Moved')}: {moved}    ({a._pos[0]:.0f}, {a._pos[1]:.0f})"
        )

    def _confirm_ok(self) -> None:
        a = self.area
        data = {
            "left": a.left,
            "middle": a.middle,
            "right": a.right,
            "moved": a.moved,
            "wheel_up": a.wheel_up,
            "wheel_down": a.wheel_down,
        }
        self.mark_pass("mouse.buttons", "Mouse Buttons", tr("Mouse buttons/wheel/movement OK"), data)

    def _confirm_bad(self) -> None:
        self.mark_fail("mouse.buttons", "Mouse Buttons", tr("Mouse marked faulty"))
