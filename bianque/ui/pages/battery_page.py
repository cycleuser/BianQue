"""Battery inspection page."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bianque.core import battery
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_grid
from bianque.ui.worker import Task


class BatteryPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Battery", "Check charge level, cycle count and health", parent)
        self._task: Task | None = None

        self.refresh_btn = QPushButton(tr("Read Battery Info"))
        self.refresh_btn.clicked.connect(self.refresh)
        self.content.addWidget(self.refresh_btn, stretch=0)

        self._label = QLabel(tr("Not read yet"))
        self._label.setWordWrap(True)
        self.content.addWidget(self._label)

        self._box = QWidget()
        self._box_lay = QVBoxLayout(self._box)
        self._box_lay.setContentsMargins(0, 0, 0, 0)
        self.content.addWidget(self._box)
        self.content.addStretch(1)

        QTimer.singleShot(0, self.refresh)

    def _clear_box(self) -> None:
        while self._box_lay.count():
            item = self._box_lay.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

    def refresh(self) -> None:
        self.refresh_btn.setEnabled(False)
        self._clear_box()
        self._label.setText(tr("Reading battery info…"))
        self._task = Task(lambda progress, stop_event: battery.get_battery_info())
        self._task.signals.finished.connect(self._on_info)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.refresh_btn.setEnabled(True)
        self._label.setText(f"{tr('Scan failed')}: {message}")
        self.mark_unknown("battery.info", "Battery", message)

    def _on_info(self, info: dict) -> None:
        self.refresh_btn.setEnabled(True)
        self._label.setText("")
        if not info.get("present"):
            self._label.setText(tr("No battery detected (desktop or removed)"))
            self.mark_unknown("battery.info", "Battery", "No battery detected")
            return

        items = [
            (tr("Charge"), f"{info['percent']}%"),
            (tr("Power"), tr("Charging") if info["power_plugged"] else tr("On Battery")),
            (tr("Cycle Count"), info.get("cycle_count") or "N/A"),
            (tr("Health Status"), info.get("condition") or "N/A"),
        ]
        if info.get("max_capacity_percent"):
            items.append((tr("Max Capacity"), f"{info['max_capacity_percent']}%"))
        if info.get("design_capacity"):
            items.append((tr("Design Capacity"), str(info["design_capacity"])))
        if info.get("full_capacity"):
            items.append((tr("Full Capacity"), str(info["full_capacity"])))

        self._box_lay.addWidget(info_grid(items))

        self.mark_pass(
            "battery.info",
            "Battery",
            tr("Charge {0}%, cycles {1}", info["percent"], info.get("cycle_count") or "N/A"),
            info,
        )
