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

from bianque.core import audio as audio_core
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage


class SpeakerPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Speaker", "Play left/right channels and a sweep tone", parent)
        self._effect: QSoundEffect | None = None

        self.content.addWidget(QLabel(tr("Click to play test tones; note left/right:")))

        row1 = QHBoxLayout()
        for label, pan in (("Left Channel", "left"), ("Right Channel", "right"), ("Both Channels", "both")):
            btn = QPushButton(f"▶ {tr(label)}")
            btn.clicked.connect(lambda _=False, p=pan: self._play_tone(440.0, p))
            row1.addWidget(btn)
        sweep_btn = QPushButton(f"▶ {tr('Sweep (low→high)')}")
        sweep_btn.clicked.connect(self._play_sweep)
        row1.addWidget(sweep_btn)
        row1.addStretch(1)
        self.content.addLayout(row1)

        self.content.addWidget(QLabel(tr("Channel confirmation:")))
        row2 = QHBoxLayout()
        self.left_ok = QPushButton(tr("Left OK ✓"))
        self.left_bad = QPushButton(tr("Left silent ✗"))
        self.right_ok = QPushButton(tr("Right OK ✓"))
        self.right_bad = QPushButton(tr("Right silent ✗"))
        self.left_ok.clicked.connect(lambda: self._confirm("speaker.left", "Left Channel", True))
        self.left_bad.clicked.connect(lambda: self._confirm("speaker.left", "Left Channel", False))
        self.right_ok.clicked.connect(lambda: self._confirm("speaker.right", "Right Channel", True))
        self.right_bad.clicked.connect(lambda: self._confirm("speaker.right", "Right Channel", False))
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
        path = tempfile.mktemp(prefix="bianque_spk_", suffix=".wav")
        audio_core.write_wav(path, samples)
        self._effect = QSoundEffect(self)
        self._effect.setSource(QUrl.fromLocalFile(path))
        self._effect.setVolume(1.0)
        self._effect.play()
        self.status_lbl.setText(f"{tr('Playing')}: {label}")

    def _play_tone(self, freq: float, pan: str) -> None:
        label = {"left": "Left Channel", "right": "Right Channel", "both": "Both Channels"}[pan]
        self._play(self._stereo(freq, pan), f"{tr(label)} {freq:.0f}Hz")

    def _play_sweep(self) -> None:
        self._play(audio_core.generate_sweep(duration=2.0), tr("Sweep (low→high)"))

    def _confirm(self, key: str, name: str, ok: bool) -> None:
        if ok:
            self.mark_pass(key, name, f"{tr(name)} {tr('OK')}")
            self.status_lbl.setText(f"{tr(name)} {tr('Confirmed OK ✓')}")
        else:
            self.mark_fail(key, name, f"{tr(name)} {tr('silent')}")
            self.status_lbl.setText(f"{tr(name)} {tr('marked faulty ✗')}")
