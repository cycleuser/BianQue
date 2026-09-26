"""Screen inspection: resolution/refresh info + full-screen dead-pixel test."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from juzi.ui.pages.base import BasePage
from juzi.ui.widgets.common import info_grid

COLORS: list[tuple[str, str]] = [
    ("#d9483b", "红"),
    ("#16a34a", "绿"),
    ("#3b82f6", "蓝"),
    ("#f5f5f5", "白"),
    ("#000000", "黑"),
    ("#7d8590", "灰"),
]


class FullScreenColor(QWidget):
    """Frameless full-screen solid color; click / arrow keys cycle colors."""

    def __init__(self, screen, colors: list[tuple[str, str]]) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self._colors = colors
        self._idx = 0
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CursorShape.BlankCursor)
        self._hint = QLabel(self)
        self._hint.setStyleSheet("font-size: 20px; padding: 12px; border-radius: 6px;")
        self._hint.move(40, 40)
        self._hint.adjustSize()
        self._apply()

    def _apply(self) -> None:
        rgb, name = self._colors[self._idx]
        self.setStyleSheet(f"background-color: {rgb};")
        bg = QColor(rgb)
        contrast = "#000000" if bg.lightness() > 128 else "#ffffff"
        self._hint.setStyleSheet(
            f"font-size: 20px; padding: 12px; border-radius: 6px; "
            f"background: {contrast}; color: {rgb};"
        )
        self._hint.setText(f" {name}  {self._idx + 1}/{len(self._colors)}   点击/方向键切换 · ESC 退出 ")
        self._hint.adjustSize()

    def _next(self) -> None:
        self._idx = (self._idx + 1) % len(self._colors)
        self._apply()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self._next()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Escape,):
            self.close()
        elif event.key() in (
            Qt.Key.Key_Space,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
        ):
            self._next()


class ScreenPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("屏幕检测", "检查分辨率/刷新率，并用全屏纯色找出坏点", parent)
        self._fullscreen: FullScreenColor | None = None

        screens = QGuiApplication.screens()
        items = []
        for i, s in enumerate(screens, start=1):
            geo = s.geometry()
            items.append(
                (
                    f"屏幕 {i}",
                    f"{s.name()}  {geo.width()}×{geo.height()}  @ {s.refreshRate():.0f}Hz  DPI {s.logicalDotsPerInch():.0f}",
                )
            )
        self.content.addWidget(info_grid(items or [("屏幕", "未检测到")]))

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("开始坏点检测（全屏纯色）")
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self._start_dead_pixel)
        btn_row.addWidget(self.start_btn)
        self.content.addLayout(btn_row)

        self.result_row = QHBoxLayout()
        self.result_label = QLabel("坏点检测结果：")
        self.pass_btn = QPushButton("无坏点")
        self.fail_btn = QPushButton("发现坏点")
        self.pass_btn.clicked.connect(lambda: self._finish(True))
        self.fail_btn.clicked.connect(lambda: self._finish(False))
        self.pass_btn.setEnabled(False)
        self.fail_btn.setEnabled(False)
        self.result_row.addWidget(self.result_label)
        self.result_row.addWidget(self.pass_btn)
        self.result_row.addWidget(self.fail_btn)
        self.result_row.addStretch(1)
        self.content.addLayout(self.result_row)

        self.content.addStretch(1)

        self.mark_pass(
            "screen.info",
            "屏幕参数",
            f"{len(screens)} 个显示器",
            {"screens": items},
        )

    def _start_dead_pixel(self) -> None:
        screens = QGuiApplication.screens()
        self._fullscreen = FullScreenColor(screens[0], COLORS)
        self._fullscreen.showFullScreen()
        self.pass_btn.setEnabled(True)
        self.fail_btn.setEnabled(True)
        self.start_btn.setEnabled(False)

    def _finish(self, ok: bool) -> None:
        if self._fullscreen is not None:
            self._fullscreen.close()
            self._fullscreen = None
        if ok:
            self.result_label.setText("坏点检测结果：未发现坏点 ✓")
            self.mark_pass("screen.dead_pixel", "坏点检测", "六色纯色观察未发现坏点")
        else:
            self.result_label.setText("坏点检测结果：发现坏点 ✗")
            self.mark_fail("screen.dead_pixel", "坏点检测", "发现坏点，建议更换屏幕或联系售后")
        self.start_btn.setEnabled(True)
        self.pass_btn.setEnabled(False)
        self.fail_btn.setEnabled(False)
