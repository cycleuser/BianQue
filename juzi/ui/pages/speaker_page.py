"""Speaker inspection: left/right channel and sweep tone playback."""

from __future__ import annotations

import tempfile

import numpy as np
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from juzi.core import audio as audio_core
from juzi.ui.pages.base import BasePage


class SpeakerPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("扬声器检测", "分别播放左右声道与扫频信号，确认扬声器正常", parent)
        self._effect: QSoundEffect | None = None

        self.content.addWidget(QLabel("点击播放测试音，注意区分左右声道："))

        row1 = QHBoxLayout()
        for label, pan in (("左声道", "left"), ("右声道", "right"), ("双声道", "both")):
            btn = QPushButton(f"▶ {label}")
            btn.clicked.connect(lambda _=False, p=pan: self._play_tone(440.0, p))
            row1.addWidget(btn)
        sweep_btn = QPushButton("▶ 扫频（低频→高频）")
        sweep_btn.clicked.connect(self._play_sweep)
        row1.addWidget(sweep_btn)
        row1.addStretch(1)
        self.content.addLayout(row1)

        self.content.addWidget(QLabel("声道确认："))
        row2 = QHBoxLayout()
        self.left_ok = QPushButton("左声道正常 ✓")
        self.left_bad = QPushButton("左声道无声 ✗")
        self.right_ok = QPushButton("右声道正常 ✓")
        self.right_bad = QPushButton("右声道无声 ✗")
        self.left_ok.clicked.connect(lambda: self._confirm("speaker.left", "左声道", True))
        self.left_bad.clicked.connect(lambda: self._confirm("speaker.left", "左声道", False))
        self.right_ok.clicked.connect(lambda: self._confirm("speaker.right", "右声道", True))
        self.right_bad.clicked.connect(lambda: self._confirm("speaker.right", "右声道", False))
        row2.addWidget(self.left_ok)
        row2.addWidget(self.left_bad)
        row2.addWidget(self.right_ok)
        row2.addWidget(self.right_bad)
        row2.addStretch(1)
        self.content.addLayout(row2)

        self.status_lbl = QLabel("")
        self.content.addWidget(self.status_lbl)
        self.content.addStretch(1)

    def _stereo(self, freq: float, pan: str) -> np.ndarray:
        mono = audio_core.generate_tone(freq, duration=1.2, channels=1)
        zero = np.zeros_like(mono)
        if pan == "left":
            return np.concatenate([mono, zero], axis=1)
        if pan == "right":
            return np.concatenate([zero, mono], axis=1)
        return np.concatenate([mono, mono], axis=1)

    def _play(self, samples: np.ndarray, label: str) -> None:
        path = tempfile.mktemp(prefix="juzi_spk_", suffix=".wav")
        audio_core.write_wav(path, samples)
        self._effect = QSoundEffect(self)
        self._effect.setSource(QUrl.fromLocalFile(path))
        self._effect.setVolume(1.0)
        self._effect.play()
        self.status_lbl.setText(f"正在播放：{label}")

    def _play_tone(self, freq: float, pan: str) -> None:
        self._play(self._stereo(freq, pan), f"{pan} {freq:.0f}Hz")

    def _play_sweep(self) -> None:
        self._play(audio_core.generate_sweep(duration=2.0), "扫频信号")

    def _confirm(self, key: str, name: str, ok: bool) -> None:
        if ok:
            self.mark_pass(key, name, f"{name}正常")
            self.status_lbl.setText(f"{name}已确认正常 ✓")
        else:
            self.mark_fail(key, name, f"{name}无声")
            self.status_lbl.setText(f"{name}已标记异常 ✗")
