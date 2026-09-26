"""Mouse / touchpad inspection: buttons, wheel and movement."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

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
        super().__init__("鼠标/触控板检测", "在下方区域点击左右键、滚动滚轮并移动光标", parent)

        self.area = MouseTestArea()
        self.area.set_callback(self._refresh)
        self.content.addWidget(self.area, stretch=1)

        self.info_lbl = QLabel()
        self.content.addWidget(self.info_lbl)

        self.ok_btn = QPushButton("确认全部正常 ✓")
        self.bad_btn = QPushButton("确认异常 ✗")
        self.ok_btn.clicked.connect(self._confirm_ok)
        self.bad_btn.clicked.connect(self._confirm_bad)
        self.content.addWidget(self.ok_btn)
        self.content.addWidget(self.bad_btn)

        self._refresh()

    def _refresh(self) -> None:
        a = self.area
        left = "✓" if a.left else "未按"
        middle = "✓" if a.middle else "未按"
        right = "✓" if a.right else "未按"
        moved = "✓" if a.moved else "未移动"
        wheel = f"上{a.wheel_up} / 下{a.wheel_down}"
        self.info_lbl.setText(
            f"左键：{left}    中键：{middle}    右键：{right}\n"
            f"滚轮：{wheel}    移动：{moved}    坐标：({a._pos[0]}, {a._pos[1]})"
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
        self.mark_pass("mouse.buttons", "鼠标按键", "鼠标按键/滚轮/移动均正常", data)

    def _confirm_bad(self) -> None:
        self.mark_fail("mouse.buttons", "鼠标按键", "已标记鼠标异常")
