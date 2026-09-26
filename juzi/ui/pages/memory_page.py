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

from juzi.core import memory
from juzi.core.report import format_bytes
from juzi.ui.pages.base import BasePage
from juzi.ui.widgets.common import info_grid
from juzi.ui.worker import Task


class MemoryPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("内存检测", "查看内存信息并做读写自检", parent)
        self._task: Task | None = None

        info = memory.get_memory_details()
        items = [
            ("总容量", format_bytes(info["total_bytes"])),
            ("可用", format_bytes(info["available_bytes"])),
            ("使用率", f"{info['percent']}%"),
            ("内存条数", info.get("dimm_count") or "N/A"),
            ("内存频率", info.get("dimm_speed") or "N/A"),
            ("类型", info.get("dimm_type") or "N/A"),
        ]
        self.content.addWidget(info_grid(items))

        row = QHBoxLayout()
        row.addWidget(QLabel("自检大小 (MB)："))
        self.size_box = QDoubleSpinBox()
        self.size_box.setRange(64.0, 2048.0)
        self.size_box.setValue(256.0)
        row.addWidget(self.size_box)
        self.test_btn = QPushButton("开始读写自检")
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
            "内存信息",
            f"总量 {format_bytes(info['total_bytes'])}",
            {"total_bytes": info["total_bytes"]},
        )

    def _test(self) -> None:
        self.test_btn.setEnabled(False)
        self.result_lbl.setText("正在做内存读写自检…")
        size = self.size_box.value()
        self._task = Task(
            lambda progress, stop_event: memory.run_memory_self_test(size_mb=size)
        )
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.test_btn.setEnabled(True)
        self.result_lbl.setText(f"自检失败：{message}")
        self.mark_unknown("memory.self_test", "内存自检", message)

    def _on_done(self, result: Any) -> None:
        self.test_btn.setEnabled(True)
        r = result
        if not r.ok:
            self.result_lbl.setText("内存读写校验失败，可能存在问题！")
            self.mark_fail("memory.self_test", "内存自检", "读写校验不一致", r.to_dict())
            return
        self.result_lbl.setText(
            f"校验通过：写 {r.write_speed_mbps:.1f} MB/s，读 {r.read_speed_mbps:.1f} MB/s"
        )
        self.mark_pass(
            "memory.self_test",
            "内存自检",
            f"读写校验通过，写 {r.write_speed_mbps:.1f} MB/s",
            r.to_dict(),
        )
