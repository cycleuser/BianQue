"""Disk inspection page: partitions + sequential read/write benchmark."""

from __future__ import annotations

import tempfile
from typing import Any

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.core import disk
from bianque.core.report import format_bytes
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_grid
from bianque.ui.worker import Task


class DiskPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Disk", "View partitions and measure read/write speed", parent)
        self._task: Task | None = None

        parts = disk.get_disk_info()
        items = [
            (
                p["mountpoint"],
                f"{format_bytes(p['total_bytes']) if p['total_bytes'] else 'N/A'} · "
                f"{tr('Used')} {p['percent']}%" if p["percent"] is not None else "N/A",
            )
            for p in parts
        ]
        self.content.addWidget(info_grid(items or [(tr("Disk"), "N/A")]))

        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Test size (MB)") + ":"))
        self.size_box = QDoubleSpinBox()
        self.size_box.setRange(16.0, 4096.0)
        self.size_box.setValue(256.0)
        row.addWidget(self.size_box)
        self.bench_btn = QPushButton(tr("Start Benchmark"))
        self.bench_btn.setObjectName("primary")
        self.bench_btn.clicked.connect(self._bench)
        row.addWidget(self.bench_btn)
        row.addStretch(1)
        self.content.addLayout(row)

        self.result_lbl = QLabel("")
        self.result_lbl.setWordWrap(True)
        self.content.addWidget(self.result_lbl)
        self.content.addStretch(1)

        self.mark_pass("disk.info", "Partitions", tr("{0} partitions", len(parts)), {"count": len(parts)})

    def _bench(self) -> None:
        self.bench_btn.setEnabled(False)
        self.result_lbl.setText(tr("Benchmarking…"))
        size = self.size_box.value()
        self._task = Task(
            lambda progress, stop_event: disk.run_disk_benchmark(
                path=tempfile.gettempdir(), size_mb=size
            )
        )
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.bench_btn.setEnabled(True)
        self.result_lbl.setText(f"{tr('Benchmark failed')}: {message}")
        self.mark_unknown("disk.benchmark", "Disk Benchmark", message)

    def _on_done(self, result: Any) -> None:
        self.bench_btn.setEnabled(True)
        r = result
        if r.error:
            self.result_lbl.setText(f"{tr('Benchmark failed')}: {r.error}")
            self.mark_unknown("disk.benchmark", "Disk Benchmark", r.error)
            return
        self.result_lbl.setText(
            f"{tr('Write')} {r.write_speed_mbps:.1f} MB/s\n{tr('Read')} {r.read_speed_mbps:.1f} MB/s"
        )
        self.mark_pass(
            "disk.benchmark",
            "Disk Benchmark",
            tr("Write {0} MB/s, read {1} MB/s", r.write_speed_mbps, r.read_speed_mbps),
            r.to_dict(),
        )
