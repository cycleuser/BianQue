"""Network inspection page: interfaces + ICMP latency."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from bianque.core import network
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_grid
from bianque.ui.worker import Task


class NetworkPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("网络检测", "查看网卡信息并测试网络延迟", parent)
        self._task: Task | None = None

        info = network.get_network_info()
        items = []
        for iface in info["interfaces"]:
            ip = ", ".join(iface["ips"]) or "无 IP"
            speed = f"{iface['speed_mbps']} Mbps" if iface["speed_mbps"] else "N/A"
            items.append((iface["name"], f"{ip} · {speed} · {'已连接' if iface['up'] else '未连接'}"))
        self.content.addWidget(info_grid(items or [("网卡", "无")]))

        row = QHBoxLayout()
        row.addWidget(QLabel("目标地址："))
        self.host = QLineEdit("223.5.5.5")
        row.addWidget(self.host)
        self.ping_btn = QPushButton("Ping 测试")
        self.ping_btn.setObjectName("primary")
        self.ping_btn.clicked.connect(self._ping)
        row.addWidget(self.ping_btn)
        row.addStretch(1)
        self.content.addLayout(row)

        self.result_lbl = QLabel("")
        self.result_lbl.setWordWrap(True)
        self.content.addWidget(self.result_lbl)
        self.content.addStretch(1)

        self.mark_pass("network.interfaces", "网络接口", f"{len(info['interfaces'])} 个接口")

    def _ping(self) -> None:
        host = self.host.text().strip() or "223.5.5.5"
        self.ping_btn.setEnabled(False)
        self.result_lbl.setText(f"正在 ping {host} …")
        self._task = Task(lambda progress, stop_event: network.ping(host=host, count=4))
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.ping_btn.setEnabled(True)
        self.result_lbl.setText(f"Ping 失败：{message}")
        self.mark_unknown("network.ping", "网络延迟", message)

    def _on_done(self, result: Any) -> None:
        self.ping_btn.setEnabled(True)
        r = result
        if r.error:
            self.result_lbl.setText(f"Ping 失败：{r.error}")
            self.mark_fail("network.ping", "网络延迟", f"无法连接 {r.host}", r.to_dict())
            return
        self.result_lbl.setText(
            f"{r.host}：发送 {r.transmitted}，接收 {r.received}，丢包 {r.loss_percent}%\n"
            f"最小 {r.min_ms} ms / 平均 {r.avg_ms} ms / 最大 {r.max_ms} ms"
        )
        if r.loss_percent > 0:
            self.mark_fail("network.ping", "网络延迟", f"丢包 {r.loss_percent}%", r.to_dict())
        else:
            self.mark_pass(
                "network.ping",
                "网络延迟",
                f"平均 {r.avg_ms} ms，无丢包",
                r.to_dict(),
            )
