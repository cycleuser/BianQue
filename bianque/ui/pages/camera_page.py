"""Camera inspection: live preview + snapshot capture."""

from __future__ import annotations

import tempfile

from PySide6.QtMultimedia import QCamera, QImageCapture, QMediaCaptureSession, QMediaDevices
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.i18n import tr
from bianque.ui.pages.base import BasePage


class CameraPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Camera", "Preview the camera and take a snapshot", parent)
        self._camera: QCamera | None = None
        self._session: QMediaCaptureSession | None = None
        self._capture: QImageCapture | None = None
        self._snap_path: str | None = None

        devices = QMediaDevices.videoInputs()
        self.combo = QComboBox()
        for dev in devices:
            self.combo.addItem(dev.description())
        self.content.addWidget(self.combo)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(320)
        self.content.addWidget(self.video_widget, stretch=1)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton(tr("Start Preview"))
        self.stop_btn = QPushButton(tr("Stop Preview"))
        self.snap_btn = QPushButton(tr("Snapshot"))
        self.ok_btn = QPushButton(tr("Picture OK ✓"))
        self.start_btn.clicked.connect(self._start)
        self.stop_btn.clicked.connect(self._stop)
        self.snap_btn.clicked.connect(self._snap)
        self.ok_btn.clicked.connect(self._confirm_ok)
        self.stop_btn.setEnabled(False)
        self.snap_btn.setEnabled(False)
        self.ok_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.snap_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.ok_btn)
        self.content.addLayout(btn_row)

        self.status_lbl = QLabel("")
        self.content.addWidget(self.status_lbl)

        if not devices:
            self.start_btn.setEnabled(False)
            self.mark_unknown("camera.device", "Camera", "No camera detected")
            self.status_lbl.setText(tr("No camera detected"))

    def _start(self) -> None:
        try:
            devices = QMediaDevices.videoInputs()
            device = devices[self.combo.currentIndex()]
            self._camera = QCamera(device)
            self._capture = QImageCapture()
            self._session = QMediaCaptureSession()
            self._session.setCamera(self._camera)
            self._session.setVideoOutput(self.video_widget)
            self._session.setImageCapture(self._capture)
            self._capture.imageSaved.connect(self._on_image_saved)
            self._camera.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.snap_btn.setEnabled(True)
            self.status_lbl.setText(tr("Previewing…"))
            self.mark_pass("camera.device", "Camera", f"{tr('Opened')} {device.description()}")
        except Exception as exc:  # noqa: BLE001
            self.status_lbl.setText(f"{tr('Failed to open')}: {exc}")
            self.mark_fail("camera.device", "Camera", f"{tr('Failed to open')}: {exc}")

    def _stop(self) -> None:
        if self._camera is not None:
            self._camera.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.snap_btn.setEnabled(False)
        self.status_lbl.setText(tr("Stopped"))

    def _snap(self) -> None:
        if self._capture is None:
            return
        path = tempfile.mktemp(prefix="bianque_snap_", suffix=".jpg")
        self._capture.captureToFile(path)

    def _on_image_saved(self, _id: int, path: str) -> None:
        self._snap_path = path
        self.status_lbl.setText(f"{tr('Snapshot saved')}: {path}")
        self.ok_btn.setEnabled(True)

    def _confirm_ok(self) -> None:
        self.mark_pass("camera.image", "Camera Image", "Image OK", {"snap_path": self._snap_path})
        self.status_lbl.setText(tr("Confirmed OK ✓"))

    def hideEvent(self, event) -> None:  # noqa: N802
        self._stop()
        super().hideEvent(event)
