"""Thermal / stress inspection: CPU burn-in with temperature & frequency watch."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QWidget,
)

from bianque.core import stress, thermal
from bianque.core.report import format_duration
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.worker import Task


class ThermalPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Thermal", "Stress the CPU and watch usage, frequency and temperature", parent)
        self._task: Task | None = None
        self._temps_before: list[dict] = []

        self.content.addWidget(QLabel(tr("Stress duration (s)") + ":"))
        row = QHBoxLayout()
        self.duration = QDoubleSpinBox()
        self.duration.setRange(5.0, 300.0)
        self.duration.setValue(15.0)
        self.duration.setSuffix(" s")
        row.addWidget(self.duration)

        self.start_btn = QPushButton(tr("Start Stress Test"))
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self._start)
        row.addWidget(self.start_btn)
        row.addStretch(1)
        self.content.addLayout(row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.content.addWidget(self.progress)

        self.live_lbl = QLabel("")
        self.content.addWidget(self.live_lbl)

        self.result_lbl = QLabel("")
        self.result_lbl.setWordWrap(True)
        self.content.addWidget(self.result_lbl)

        self.sensor_lbl = QLabel("")
        self.sensor_lbl.setWordWrap(True)
        self.sensor_lbl.setStyleSheet("color: #9aa3ad;")
        self.content.addWidget(self.sensor_lbl)
        self.content.addStretch(1)

        self._refresh_sensors()

    def _refresh_sensors(self) -> None:
        temps = thermal.get_temperatures()
        fans = thermal.get_fan_speeds()
        if not thermal.thermal_supported():
            self.sensor_lbl.setText(tr("No temperature access on this platform"))
        else:
            t_str = "  ".join(f"{t['label']}:{t['current']}°C" for t in temps)
            f_str = "  ".join(f"{f['label']}:{f['current']}RPM" for f in fans)
            self.sensor_lbl.setText(f"{tr('Temperature')}: {t_str or tr('None')}    {tr('Fans')}: {f_str or tr('None')}")
        self.report(
            "thermal.sensors",
            "Temperature Sensors",
            "pass" if temps else "unknown",
            tr("Detected {0} temperature sensors", len(temps)) if temps else tr("Cannot read temperature sensors"),
            {"temperatures": temps, "fans": fans},
        )

    def _start(self) -> None:
        self._temps_before = thermal.get_temperatures()
        self.start_btn.setEnabled(False)
        self.progress.setValue(0)
        self.result_lbl.setText(tr("Stress running…"))
        duration = self.duration.value()
        self._task = Task(
            lambda progress, stop_event: stress.run_cpu_stress(
                duration=duration,
                on_progress=progress,
                stop_event=stop_event,
            )
        )
        self._task.signals.progress.connect(self._on_progress)
        self._task.signals.finished.connect(self._on_done)
        self._task.signals.error.connect(self._on_error)
        self._task.start()

    def _on_progress(self, fraction: float, cpu_percent: float) -> None:
        self.progress.setValue(int(fraction * 100))
        self.live_lbl.setText(tr("CPU usage: {0}%", f"{cpu_percent:.0f}"))

    def _on_error(self, message: str) -> None:
        self.start_btn.setEnabled(True)
        self.result_lbl.setText(f"{tr('Stress failed')}: {message}")
        self.mark_unknown("thermal.stress", "Stress Test", message)

    def _on_done(self, result: Any) -> None:
        self.start_btn.setEnabled(True)
        self.progress.setValue(100)
        r = result
        self._refresh_sensors()

        freq_drop = None
        if r.freq_max_mhz is not None and r.freq_min_mhz is not None:
            freq_drop = r.freq_max_mhz - r.freq_min_mhz

        lines = [
            tr("Duration {0}, {1} threads", format_duration(r.duration), r.threads),
            tr("Avg usage {0}%, peak {1}%", f"{r.avg_usage:.0f}", f"{r.peak_usage:.0f}"),
            tr("Frequency {0} → {1} MHz", r.freq_before_mhz, r.freq_after_mhz),
        ]
        if freq_drop is not None:
            lines.append(tr("Frequency variation {0} MHz", f"{freq_drop:.0f}"))
        self.result_lbl.setText("\n".join(lines))

        data = {
            "avg_usage": round(r.avg_usage, 1),
            "peak_usage": round(r.peak_usage, 1),
            "freq_before_mhz": r.freq_before_mhz,
            "freq_after_mhz": r.freq_after_mhz,
            "freq_drop_mhz": round(freq_drop, 1) if freq_drop is not None else None,
        }

        if not r.completed:
            self.mark_unknown("thermal.stress", "Stress Test", tr("Stress interrupted"), data)
        elif freq_drop is not None and freq_drop > 500:
            self.mark_fail(
                "thermal.stress",
                "Stress Test",
                tr("Frequency dropped {0} MHz under load, possible throttling", f"{freq_drop:.0f}"),
                data,
            )
        else:
            self.mark_pass(
                "thermal.stress",
                "Stress Test",
                tr("Stable under full load, peak {0}%, no throttling", f"{r.peak_usage:.0f}"),
                data,
            )
