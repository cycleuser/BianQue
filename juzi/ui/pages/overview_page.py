"""Hardware overview page: aggregate system info."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from juzi.core import system
from juzi.core.report import format_bytes
from juzi.ui.pages.base import BasePage
from juzi.ui.widgets.common import info_box
from juzi.ui.worker import Task


class OverviewPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("硬件总览", "自动采集本机硬件信息（CPU / 内存 / 磁盘 / GPU / 主板）", parent)
        self._task: Task | None = None

        self.refresh_btn = QPushButton("重新采集")
        self.refresh_btn.clicked.connect(self.refresh)
        self.content.addWidget(self.refresh_btn, stretch=0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._container = QWidget()
        self._lay = QVBoxLayout(self._container)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(10)
        self._scroll.setWidget(self._container)
        self.content.addWidget(self._scroll, stretch=1)

        QTimer.singleShot(0, self.refresh)

    def refresh(self) -> None:
        self._clear_boxes()
        self._lay.addWidget(QLabel("正在采集硬件信息…"))
        self.refresh_btn.setEnabled(False)
        self._task = Task(lambda progress, stop_event: system.get_system_snapshot())
        self._task.signals.finished.connect(self._on_snapshot)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _clear_boxes(self) -> None:
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

    def _on_error(self, message: str) -> None:
        self._clear_boxes()
        self._lay.addWidget(QLabel(f"采集失败：{message}"))
        self.refresh_btn.setEnabled(True)
        self.mark_unknown("overview.system", "硬件总览", message)

    def _on_snapshot(self, snap: dict) -> None:
        self._clear_boxes()
        os_info = snap["os"]
        cpu = snap["cpu"]
        mem = snap["memory"]
        board = snap.get("board", {})

        self._lay.addWidget(
            info_box(
                "系统",
                [
                    ("系统", f"{os_info['system']} {os_info['release']}"),
                    ("架构", os_info["machine"]),
                    ("主机名", os_info["hostname"]),
                    ("Python", os_info["python"]),
                ],
            )
        )
        if board:
            board_items = [
                ("型号", board.get("model")),
                ("芯片", board.get("chip")),
                ("序列号", board.get("serial")),
            ]
            self._lay.addWidget(info_box("主板", board_items))

        self._lay.addWidget(
            info_box(
                "CPU",
                [
                    ("型号", cpu["brand"]),
                    ("物理核心", cpu["physical_cores"]),
                    ("逻辑核心", cpu["logical_cores"]),
                    ("当前频率", f"{cpu['freq_current_mhz']} MHz" if cpu["freq_current_mhz"] else "N/A"),
                    ("最大频率", f"{cpu['freq_max_mhz']} MHz" if cpu["freq_max_mhz"] else "N/A"),
                ],
            )
        )
        self._lay.addWidget(
            info_box(
                "内存",
                [
                    ("总容量", format_bytes(mem["total_bytes"])),
                    ("可用", format_bytes(mem["available_bytes"])),
                    ("使用率", f"{mem['percent']}%"),
                    ("Swap", format_bytes(mem["swap_total_bytes"])),
                ],
            )
        )

        for i, gpu in enumerate(snap.get("gpu", []), start=1):
            self._lay.addWidget(
                info_box(
                    f"GPU {i}",
                    [
                        ("型号", gpu.get("name")),
                        ("厂商", gpu.get("vendor")),
                        ("显存", gpu.get("vram")),
                    ],
                )
            )

        disk_items = []
        for p in snap.get("disks", []):
            total = format_bytes(p["total_bytes"]) if p["total_bytes"] else "N/A"
            percent = f"{p['percent']}%" if p["percent"] is not None else "N/A"
            disk_items.append((p["mountpoint"], f"{total} · 已用 {percent}"))
        self._lay.addWidget(info_box("磁盘分区", disk_items or [("无", "N/A")]))

        self._lay.addStretch(1)
        self.refresh_btn.setEnabled(True)

        self.mark_pass(
            "overview.cpu",
            "CPU 信息",
            cpu["brand"],
            {"logical_cores": cpu["logical_cores"], "freq_max_mhz": cpu["freq_max_mhz"]},
        )
        self.mark_pass(
            "overview.memory",
            "内存信息",
            f"总量 {format_bytes(mem['total_bytes'])}",
            {"total_bytes": mem["total_bytes"]},
        )
        self.mark_pass(
            "overview.disks",
            "磁盘信息",
            f"{len(snap.get('disks', []))} 个分区",
            {"count": len(snap.get("disks", []))},
        )
