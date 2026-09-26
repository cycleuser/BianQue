"""Memory inspection page: info + write/read self-test."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.core import memory
from bianque.core.report import format_bytes
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_box, info_grid
from bianque.ui.worker import Task


class MemoryPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Memory", "View memory info and run a self-test", parent)
        self._task: Task | None = None

        info = memory.get_memory_details()
        items = [
            (tr("Total"), format_bytes(info["total_bytes"])),
            (tr("Available"), format_bytes(info["available_bytes"])),
            (tr("Usage"), f"{info['percent']}%"),
        ]
        if info.get("channels"):
            items.append((tr("Channels"), info["channels"]))
        if info.get("bandwidth_gbps"):
            items.append((tr("Bandwidth"), f"{info['bandwidth_gbps']} GB/s"))
        self.content.addWidget(info_grid(items))

        for mod in info.get("modules") or []:
            self.content.addWidget(
                info_box(
                    f"{tr('Modules')} · {mod.get('slot')}",
                    [
                        (tr("Manufacturer"), mod.get("manufacturer") or "N/A"),
                        (tr("Type"), mod.get("type") or "N/A"),
                        (tr("Capacity"), mod.get("capacity") or "N/A"),
                        (tr("Speed"), f"{mod['speed_mhz']} MHz" if mod.get("speed_mhz") else "N/A"),
                        (tr("Timing"), mod.get("timing") or "N/A"),
                        (tr("Part Number"), mod.get("part_number") or "N/A"),
                    ],
                )
            )

        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Self-test size (MB)") + ":"))
        self.size_box = QDoubleSpinBox()
        self.size_box.setRange(64.0, 2048.0)
        self.size_box.setValue(256.0)
        row.addWidget(self.size_box)
        self.test_btn = QPushButton(tr("Run Self-Test"))
        self.test_btn.setObjectName("primary")
        self.test_btn.clicked.connect(self._test)
        row.addWidget(self.test_btn)
        row.addStretch(1)
        self.content.addLayout(row)

        self.result_lbl = QLabel("")
        self.result_lbl.setWordWrap(True)
        self.content.addWidget(self.result_lbl)
        self.content.addStretch(1)

        self.mark_pass(
            "memory.info",
            "Memory Info",
            tr("Total {0}", format_bytes(info["total_bytes"])),
            {"total_bytes": info["total_bytes"]},
        )

    def _test(self) -> None:
        self.test_btn.setEnabled(False)
        self.result_lbl.setText(tr("Running memory self-test…"))
        size = self.size_box.value()
        self._task = Task(
            lambda progress, stop_event: memory.run_memory_self_test(size_mb=size)
        )
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.test_btn.setEnabled(True)
        self.result_lbl.setText(f"{tr('Scan failed')}: {message}")
        self.mark_unknown("memory.self_test", "Memory Self-Test", message)

    def _on_done(self, result: Any) -> None:
        self.test_btn.setEnabled(True)
        r = result
        if not r.ok:
            self.result_lbl.setText(tr("Memory verify failed"))
            self.mark_fail("memory.self_test", "Memory Self-Test", tr("Memory verify failed"), r.to_dict())
            return
        self.result_lbl.setText(tr("Passed: write {0} MB/s, read {1} MB/s", r.write_speed_mbps, r.read_speed_mbps))
        self.mark_pass(
            "memory.self_test",
            "Memory Self-Test",
            tr("Passed: write {0} MB/s, read {1} MB/s", r.write_speed_mbps, r.read_speed_mbps),
            r.to_dict(),
        )
