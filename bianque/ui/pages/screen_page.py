"""Screen inspection: resolution/refresh info + full-screen dead-pixel test."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_grid

COLORS: list[tuple[str, str]] = [
    ("#d9483b", "Red"),
    ("#16a34a", "Green"),
    ("#3b82f6", "Blue"),
    ("#f5f5f5", "White"),
    ("#000000", "Black"),
    ("#7d8590", "Gray"),
]


class FullScreenColor(QWidget):
    """Frameless full-screen solid color; click / arrow keys cycle colors.

    The hint label drifts along the screen edges so it never permanently
    occludes a dead pixel.
    """

    def __init__(self, screen, colors: list[tuple[str, str]]) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self._colors = colors
        self._idx = 0
        self._t = 0.0
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CursorShape.BlankCursor)
        self._hint = QLabel(self)
        self._hint.setStyleSheet("font-size: 20px; padding: 12px; border-radius: 6px;")
        self._hint.adjustSize()

        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._drift)
        self._timer.start()

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
        self._hint.setText(
            f" {tr(name)}  {self._idx + 1}/{len(self._colors)}   {tr('click/arrows to switch · ESC to quit')} "
        )
        self._hint.adjustSize()

    def _drift(self) -> None:
        """Move the hint along the screen perimeter (clockwise)."""
        w = max(self.width() - self._hint.width(), 0)
        h = max(self.height() - self._hint.height(), 0)
        self._t += 3.0
        perimeter = 2 * (w + h) if (w + h) > 0 else 1
        d = self._t % perimeter
        if d < w:
            x, y = d, 0.0
        elif d < w + h:
            x, y = float(w), d - w
        elif d < 2 * w + h:
            x, y = w - (d - w - h), float(h)
        else:
            x, y = 0.0, h - (d - 2 * w - h)
        self._hint.move(int(x), int(y))

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

    def closeEvent(self, event) -> None:  # noqa: N802
        self._timer.stop()
        super().closeEvent(event)


class ScreenPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Screen", "Check resolution / refresh rate and find dead pixels", parent)
        self._fullscreen: FullScreenColor | None = None

        screens = QGuiApplication.screens()
        items = []
        for i, s in enumerate(screens, start=1):
            geo = s.geometry()
            items.append(
                (
                    f"{tr('Screen')} {i}",
                    f"{s.name()}  {geo.width()}×{geo.height()}  @ {s.refreshRate():.0f}Hz  DPI {s.logicalDotsPerInch():.0f}",
                )
            )
        self.content.addWidget(info_grid(items or [(tr("Screen"), tr("None"))]))

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton(tr("Start Dead Pixel Test (full-screen)"))
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self._start_dead_pixel)
        btn_row.addWidget(self.start_btn)
        self.content.addLayout(btn_row)

        self.result_row = QHBoxLayout()
        self.result_label = QLabel(f"{tr('Dead pixel result')}:")
        self.pass_btn = QPushButton(tr("No dead pixel"))
        self.fail_btn = QPushButton(tr("Dead pixel found"))
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
            "Screen",
            f"{len(screens)} {tr('Displays')}",
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
            self.result_label.setText(f"{tr('Dead pixel result')}: {tr('No dead pixel')} ✓")
            self.mark_pass("screen.dead_pixel", "Dead Pixel", "No dead pixel found")
        else:
            self.result_label.setText(f"{tr('Dead pixel result')}: {tr('Dead pixel found')} ✗")
            self.mark_fail("screen.dead_pixel", "Dead Pixel", "Dead pixel found, recommend replacement")
        self.start_btn.setEnabled(True)
        self.pass_btn.setEnabled(False)
        self.fail_btn.setEnabled(False)
