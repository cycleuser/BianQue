"""Microphone inspection: live level meter + record/playback."""

from __future__ import annotations

import queue
import tempfile
from typing import Any

import numpy as np
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.core import audio as audio_core
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import LevelMeter
from bianque.ui.worker import Task

SAMPLE_RATE = 44100


class MicrophonePage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("麦克风检测", "对麦克风说话，观察电平变化；可录音回放确认", parent)
        self._stream: Any = None
        self._q: queue.Queue[float] = queue.Queue()
        self._peak = 0.0
        self._task: Task | None = None
        self._effect: QSoundEffect | None = None

        devices = audio_core.list_audio_devices()
        self.combo = QComboBox()
        for dev in devices["inputs"]:
            self.combo.addItem(dev["name"])
        self.content.addWidget(self.combo)

        self.meter = LevelMeter()
        self.content.addWidget(self.meter)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("开始监听")
        self.stop_btn = QPushButton("停止监听")
        self.rec_btn = QPushButton("录音 3 秒并回放")
        self.ok_btn = QPushButton("确认正常 ✓")
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)
        self.rec_btn.clicked.connect(self._record)
        self.ok_btn.clicked.connect(self._confirm)
        self.stop_btn.setEnabled(False)
        self.rec_btn.setEnabled(False)
        self.ok_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.rec_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.ok_btn)
        self.content.addLayout(btn_row)

        self.status_lbl = QLabel("")
        self.content.addWidget(self.status_lbl)
        self.content.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._poll)

        if not devices["available"] or not devices["inputs"]:
            self.start_btn.setEnabled(False)
            self.mark_unknown("microphone.device", "麦克风", "未检测到麦克风输入设备")
            self.status_lbl.setText("未检测到麦克风输入设备")

    def _start(self) -> None:
        try:
            import sounddevice as sd  # type: ignore

            def callback(indata, frames, time_info, status):  # noqa: ARG001
                rms = float(np.sqrt(np.mean(np.square(indata))))
                self._q.put(min(1.0, rms * 6.0))

            self._stream = sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE)
            self._stream.start()
            self._timer.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.rec_btn.setEnabled(True)
            self.ok_btn.setEnabled(True)
            self.status_lbl.setText("监听中… 请对麦克风说话")
            self.mark_pass("microphone.device", "麦克风", "已打开输入设备")
        except Exception as exc:  # noqa: BLE001
            self.status_lbl.setText(f"打开失败：{exc}")
            self.mark_fail("microphone.device", "麦克风", f"打开失败：{exc}")

    def _poll(self) -> None:
        level = 0.0
        try:
            while True:
                level = max(level, self._q.get_nowait())
        except queue.Empty:
            pass
        if level > 0:
            self._peak = max(self._peak, level)
            self.meter.set_level(level)

    def _stop(self) -> None:
        self._timer.stop()
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:  # noqa: BLE001
                pass
        self._stream = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.meter.reset()
        self.status_lbl.setText("已停止监听")

    def _record(self) -> None:
        if self._task is not None and self._task.is_running():
            return
        self.rec_btn.setEnabled(False)
        self.status_lbl.setText("正在录音 3 秒…")
        self._task = Task(self._record_fn)
        self._task.signals.finished.connect(self._on_recorded)
        self._task.signals.error.connect(lambda e: self.status_lbl.setText(f"录音失败：{e}"))
        self._task.start()

    def _record_fn(self, progress, stop_event) -> str:
        import sounddevice as sd  # type: ignore

        duration = 3
        data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=2, dtype="float32")
        sd.wait()
        path = tempfile.mktemp(prefix="bianque_mic_", suffix=".wav")
        audio_core.write_wav(path, data, SAMPLE_RATE)
        return path

    def _on_recorded(self, path: str) -> None:
        self.rec_btn.setEnabled(True)
        self.status_lbl.setText(f"录音完成，正在回放：{path}")
        self._effect = QSoundEffect(self)
        self._effect.setSource(QUrl.fromLocalFile(path))
        self._effect.setVolume(1.0)
        self._effect.play()

    def _confirm(self) -> None:
        heard = self._peak > 0.05
        self.mark_pass(
            "microphone.audio",
            "麦克风收音",
            f"采集到语音信号（峰值 {self._peak:.2f}）" if heard else "已确认麦克风正常",
            {"peak_level": round(self._peak, 3)},
        )
        self.status_lbl.setText("已确认麦克风正常 ✓")

    def hideEvent(self, event) -> None:  # noqa: N802
        self._stop()
        super().hideEvent(event)
