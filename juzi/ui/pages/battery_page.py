"""Battery inspection page."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from juzi.core import battery
from juzi.ui.pages.base import BasePage
from juzi.ui.widgets.common import info_grid
from juzi.ui.worker import Task


class BatteryPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("电池检测", "检查电池电量、健康度与循环次数", parent)
        self._task: Task | None = None

        self.refresh_btn = QPushButton("读取电池信息")
        self.refresh_btn.clicked.connect(self.refresh)
        self.content.addWidget(self.refresh_btn, stretch=0)

        self._label = QLabel("尚未读取")
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
        self._label.setText("正在读取电池信息…")
        self._task = Task(lambda progress, stop_event: battery.get_battery_info())
        self._task.signals.finished.connect(self._on_info)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.refresh_btn.setEnabled(True)
        self._label.setText(f"读取失败：{message}")
        self.mark_unknown("battery.info", "电池", message)

    def _on_info(self, info: dict) -> None:
        self.refresh_btn.setEnabled(True)
        self._label.setText("")
        if not info.get("present"):
            self._label.setText("未检测到电池（可能是台式机或电池被移除）")
            self.mark_unknown("battery.info", "电池", "未检测到电池")
            return

        items = [
            ("电量", f"{info['percent']}%"),
            ("充电状态", "充电中" if info["power_plugged"] else "使用电池"),
            ("循环次数", info.get("cycle_count") or "N/A"),
            ("健康状态", info.get("condition") or "N/A"),
        ]
        if info.get("max_capacity_percent"):
            items.append(("最大容量", f"{info['max_capacity_percent']}%"))
        if info.get("design_capacity"):
            items.append(("设计容量", str(info["design_capacity"])))
        if info.get("full_capacity"):
            items.append(("满充容量", str(info["full_capacity"])))

        self._box_lay.addWidget(info_grid(items))

        self.mark_pass(
            "battery.info",
            "电池",
            f"电量 {info['percent']}%，循环 {info.get('cycle_count') or 'N/A'} 次",
            info,
        )
