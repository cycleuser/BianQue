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

from bianque.core import memory as memory_core
from bianque.core import system
from bianque.core.report import format_bytes
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_box
from bianque.ui.worker import Task


class OverviewPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Overview", "Auto-detect hardware info (CPU / memory / disk / GPU / board)", parent)
        self._task: Task | None = None

        self.refresh_btn = QPushButton(tr("Rescan"))
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
        self._lay.addWidget(QLabel(tr("Scanning hardware…")))
        self.refresh_btn.setEnabled(False)
        self._task = Task(self._collect)
        self._task.signals.finished.connect(self._on_snapshot)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _collect(self, progress, stop_event) -> tuple[dict, dict]:
        return system.get_system_snapshot(), memory_core.get_memory_details()

    def _clear_boxes(self) -> None:
        while self._lay.count():
            item = self._lay.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

    def _on_error(self, message: str) -> None:
        self._clear_boxes()
        self._lay.addWidget(QLabel(f"{tr('Scan failed')}: {message}"))
        self.refresh_btn.setEnabled(True)
        self.mark_unknown("overview.system", "Overview", message)

    def _on_snapshot(self, result: tuple[dict, dict]) -> None:
        snap, mem_detail = result
        self._clear_boxes()
        os_info = snap["os"]
        cpu = snap["cpu"]
        mem = snap["memory"]
        board = snap.get("board", {})

        self._lay.addWidget(
            info_box(
                tr("System"),
                [
                    (tr("System"), f"{os_info['system']} {os_info['release']}"),
                    (tr("Architecture"), os_info["machine"]),
                    (tr("Hostname"), os_info["hostname"]),
                    (tr("Python"), os_info["python"]),
                ],
            )
        )
        if board:
            self._lay.addWidget(
                info_box(
                    tr("Board"),
                    [
                        (tr("Model"), board.get("model")),
                        (tr("Chip"), board.get("chip")),
                        (tr("Serial Number"), board.get("serial")),
                    ],
                )
            )

        cpu_items = [
            (tr("Model"), cpu["brand"]),
            (tr("Physical Cores"), cpu["physical_cores"]),
            (tr("Logical Cores"), cpu["logical_cores"]),
            (tr("Current Frequency"), f"{cpu['freq_current_mhz']:.0f} MHz" if cpu["freq_current_mhz"] else "N/A"),
            (tr("Max Frequency"), f"{cpu['freq_max_mhz']:.0f} MHz" if cpu["freq_max_mhz"] else "N/A"),
        ]
        for level in cpu.get("perf_levels") or []:
            label = tr(level.get("name") or "Core")
            cpu_items.append((label, level.get("cores")))
        cache = cpu.get("cache") or {}
        if cache:
            parts = []
            for k in ("l1i", "l1d", "l2", "l3"):
                if cache.get(k):
                    parts.append(f"{k.upper()}: {format_bytes(cache[k])}")
            cpu_items.append((tr("Cache"), "  ".join(parts)))
        if cpu.get("per_core_usage"):
            usage = "  ".join(f"{u:.0f}%" for u in cpu["per_core_usage"])
            cpu_items.append((tr("Per-core Usage"), usage))
        self._lay.addWidget(info_box(tr("CPU"), cpu_items))

        mem_items = [
            (tr("Total"), format_bytes(mem["total_bytes"])),
            (tr("Available"), format_bytes(mem["available_bytes"])),
            (tr("Usage"), f"{mem['percent']}%"),
            (tr("Swap"), format_bytes(mem["swap_total_bytes"])),
        ]
        if mem_detail.get("channels"):
            mem_items.append((tr("Channels"), mem_detail["channels"]))
        if mem_detail.get("bandwidth_gbps"):
            mem_items.append((tr("Bandwidth"), f"{mem_detail['bandwidth_gbps']} GB/s"))
        self._lay.addWidget(info_box(tr("Memory"), mem_items))

        for mod in mem_detail.get("modules") or []:
            mod_items = [
                (tr("Slot"), mod.get("slot")),
                (tr("Manufacturer"), mod.get("manufacturer")),
                (tr("Type"), mod.get("type")),
                (tr("Capacity"), mod.get("capacity")),
                (tr("Speed"), f"{mod['speed_mhz']} MHz" if mod.get("speed_mhz") else "N/A"),
                (tr("Timing"), mod.get("timing") or "N/A"),
                (tr("Part Number"), mod.get("part_number") or "N/A"),
            ]
            self._lay.addWidget(info_box(f"{tr('Modules')} · {mod.get('slot')}", mod_items))

        for i, gpu in enumerate(snap.get("gpu", []), start=1):
            gpu_items = [
                (tr("Model"), gpu.get("name")),
                (tr("Chip"), gpu.get("chip")),
                (tr("Vendor"), gpu.get("vendor")),
                (tr("VRAM"), gpu.get("vram") or "N/A"),
                (tr("GPU Cores"), gpu.get("cores") or "N/A"),
            ]
            if gpu.get("apis"):
                gpu_items.append((tr("API Support"), ", ".join(gpu["apis"])))
            self._lay.addWidget(info_box(f"{tr('GPU')} {i}", gpu_items))

        disk_items = []
        for p in snap.get("disks", []):
            total = format_bytes(p["total_bytes"]) if p["total_bytes"] else "N/A"
            percent = f"{p['percent']}%" if p["percent"] is not None else "N/A"
            disk_items.append((p["mountpoint"], f"{total} · {tr('Used')} {percent}"))
        self._lay.addWidget(info_box(tr("Partitions"), disk_items or [(tr("None"), "N/A")]))

        for d in snap.get("disk_drives", []):
            type_label = tr("SSD") if d.get("type") == "ssd" else (tr("HDD") if d.get("type") == "hdd" else d.get("type"))
            health = tr("Good") if d.get("health") == "good" else (tr("Bad") if d.get("health") == "bad" else "N/A")
            drive_items = [
                (tr("Model"), d.get("model")),
                (tr("Type"), type_label),
                (tr("Protocol"), d.get("protocol") or "N/A"),
                (tr("SMART Status"), d.get("smart_status") or "N/A"),
                (tr("Health"), health),
                (tr("Location"), tr("Internal") if d.get("is_internal") else tr("External")),
            ]
            if d.get("size_bytes"):
                drive_items.append((tr("Capacity"), format_bytes(d["size_bytes"])))
            self._lay.addWidget(info_box(f"{tr('Disk Drives')} · {d.get('model')}", drive_items))

        self._lay.addStretch(1)
        self.refresh_btn.setEnabled(True)

        self.mark_pass("overview.cpu", "CPU", cpu["brand"], {"logical_cores": cpu["logical_cores"]})
        self.mark_pass("overview.memory", "Memory", f"{format_bytes(mem['total_bytes'])}", {"total_bytes": mem["total_bytes"]})
        self.mark_pass("overview.disks", "Disk Drives", f"{len(snap.get('disk_drives', []))}", {"drives": len(snap.get('disk_drives', []))})
        self.mark_pass("overview.gpu", "GPU", f"{len(snap.get('gpu', []))}", {"gpus": len(snap.get('gpu', []))})
