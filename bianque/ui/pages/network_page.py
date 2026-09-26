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
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import info_grid
from bianque.ui.worker import Task


class NetworkPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Network", "View interfaces and test network latency", parent)
        self._task: Task | None = None

        info = network.get_network_info()
        items = []
        for iface in info["interfaces"]:
            ip = ", ".join(iface["ips"]) or tr("No IP")
            speed = f"{iface['speed_mbps']} Mbps" if iface["speed_mbps"] else "N/A"
            state = tr("Connected") if iface["up"] else tr("Not connected")
            items.append((iface["name"], f"{ip} · {speed} · {state}"))
        self.content.addWidget(info_grid(items or [(tr("Network"), tr("None"))]))

        row = QHBoxLayout()
        row.addWidget(QLabel(tr("Target address") + ":"))
        self.host = QLineEdit("223.5.5.5")
        row.addWidget(self.host)
        self.ping_btn = QPushButton(tr("Ping Test"))
        self.ping_btn.setObjectName("primary")
        self.ping_btn.clicked.connect(self._ping)
        row.addWidget(self.ping_btn)
        row.addStretch(1)
        self.content.addLayout(row)

        self.result_lbl = QLabel("")
        self.result_lbl.setWordWrap(True)
        self.content.addWidget(self.result_lbl)
        self.content.addStretch(1)

        self.mark_pass("network.interfaces", "Network Interfaces", tr("{0} interfaces", len(info["interfaces"])))

    def _ping(self) -> None:
        host = self.host.text().strip() or "223.5.5.5"
        self.ping_btn.setEnabled(False)
        self.result_lbl.setText(tr("Pinging {0}…", host))
        self._task = Task(lambda progress, stop_event: network.ping(host=host, count=4))
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_error(self, message: str) -> None:
        self.ping_btn.setEnabled(True)
        self.result_lbl.setText(f"{tr('Ping failed')}: {message}")
        self.mark_unknown("network.ping", "Network Latency", message)

    def _on_done(self, result: Any) -> None:
        self.ping_btn.setEnabled(True)
        r = result
        if r.error:
            self.result_lbl.setText(f"{tr('Ping failed')}: {r.error}")
            self.mark_fail("network.ping", "Network Latency", tr("Cannot reach {0}", r.host), r.to_dict())
            return
        self.result_lbl.setText(
            f"{r.host}: {tr('sent')} {r.transmitted}, {tr('received')} {r.received}, "
            f"{tr('loss')} {r.loss_percent}%\n"
            f"{tr('min')} {r.min_ms} ms / {tr('avg')} {r.avg_ms} ms / {tr('max')} {r.max_ms} ms"
        )
        if r.loss_percent > 0:
            self.mark_fail("network.ping", "Network Latency", tr("Loss {0}%", r.loss_percent), r.to_dict())
        else:
            self.mark_pass("network.ping", "Network Latency", tr("Avg {0} ms, no loss", r.avg_ms), r.to_dict())
