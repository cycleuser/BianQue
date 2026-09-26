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

from juzi.core import stress, thermal
from juzi.core.report import format_duration
from juzi.ui.pages.base import BasePage
from juzi.ui.worker import Task


class ThermalPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("散热/压力检测", "对 CPU 加压并观察占用率、频率与温度，判断散热是否正常", parent)
        self._task: Task | None = None
        self._temps_before: list[dict] = []

        self.content.addWidget(QLabel("压力测试时长（秒）："))
        row = QHBoxLayout()
        self.duration = QDoubleSpinBox()
        self.duration.setRange(5.0, 300.0)
        self.duration.setValue(15.0)
        self.duration.setSuffix(" 秒")
        row.addWidget(self.duration)

        self.start_btn = QPushButton("开始压力测试")
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
            self.sensor_lbl.setText(
                "当前平台不支持直接读取 CPU 温度/风扇转速（macOS 需要 SMC 权限）。"
                "将依据压力测试中的频率与占用率判断散热。"
            )
        else:
            t_str = "  ".join(f"{t['label']}:{t['current']}°C" for t in temps)
            f_str = "  ".join(f"{f['label']}:{f['current']}RPM" for f in fans)
            self.sensor_lbl.setText(f"温度：{t_str or '无'}    风扇：{f_str or '无'}")
        self.report(
            "thermal.sensors",
            "温度传感器",
            "pass" if temps else "unknown",
            f"检测到 {len(temps)} 个温度传感器" if temps else "无法读取温度传感器",
            {"temperatures": temps, "fans": fans},
        )

    def _start(self) -> None:
        self._temps_before = thermal.get_temperatures()
        self.start_btn.setEnabled(False)
        self.progress.setValue(0)
        self.result_lbl.setText("正在加压…")
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
        self.live_lbl.setText(f"CPU 占用：{cpu_percent:.0f}%")

    def _on_error(self, message: str) -> None:
        self.start_btn.setEnabled(True)
        self.result_lbl.setText(f"压力测试出错：{message}")
        self.mark_unknown("thermal.stress", "压力测试", message)

    def _on_done(self, result: Any) -> None:
        self.start_btn.setEnabled(True)
        self.progress.setValue(100)
        r = result
        self._refresh_sensors()

        freq_drop = None
        if r.freq_max_mhz is not None and r.freq_min_mhz is not None:
            freq_drop = r.freq_max_mhz - r.freq_min_mhz

        lines = [
            f"持续 {format_duration(r.duration)}，{r.threads} 线程",
            f"平均占用 {r.avg_usage:.0f}%，峰值 {r.peak_usage:.0f}%",
            f"频率：起始 {r.freq_before_mhz} MHz → 结束 {r.freq_after_mhz} MHz",
        ]
        if freq_drop is not None:
            lines.append(f"频率波动 {freq_drop:.0f} MHz")
        self.result_lbl.setText("\n".join(lines))

        data = {
            "avg_usage": round(r.avg_usage, 1),
            "peak_usage": round(r.peak_usage, 1),
            "freq_before_mhz": r.freq_before_mhz,
            "freq_after_mhz": r.freq_after_mhz,
            "freq_drop_mhz": round(freq_drop, 1) if freq_drop is not None else None,
        }

        if not r.completed:
            self.mark_unknown("thermal.stress", "压力测试", "压力测试被中断", data)
        elif freq_drop is not None and freq_drop > 500:
            self.mark_fail(
                "thermal.stress",
                "压力测试",
                f"压力测试期间频率下降 {freq_drop:.0f} MHz，可能出现过热降频",
                data,
            )
        else:
            self.mark_pass(
                "thermal.stress",
                "压力测试",
                f"满载稳定，峰值占用 {r.peak_usage:.0f}%，无异常降频",
                data,
            )
