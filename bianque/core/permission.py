"""macOS camera / microphone permission (TCC) helpers.

On macOS, camera and microphone access requires user consent. A command-line
Python process has no app bundle with the usual ``NSCameraUsageDescription``,
so ``QCamera`` simply fails until the permission is granted. These helpers
query the AVFoundation authorization status and request it via the system
prompt. On non-macOS platforms they report "authorized" and are no-ops.
"""

from __future__ import annotations

import subprocess
import sys

IS_MAC = sys.platform == "darwin"

STATUS_NOT_DETERMINED = 0
STATUS_RESTRICTED = 1
STATUS_DENIED = 2
STATUS_AUTHORIZED = 3

_STATUS_LABEL = {
    STATUS_NOT_DETERMINED: "not_determined",
    STATUS_RESTRICTED: "restricted",
    STATUS_DENIED: "denied",
    STATUS_AUTHORIZED: "authorized",
}


def check_permission(kind: str) -> int:
    """Return the AVFoundation authorization status for ``kind``.

    ``kind`` is ``"video"`` (camera) or ``"audio"`` (microphone). Returns
    :data:`STATUS_AUTHORIZED` on non-macOS or when AVFoundation is missing.
    """
    if not IS_MAC:
        return STATUS_AUTHORIZED
    try:
        import AVFoundation
    except ImportError:
        return STATUS_AUTHORIZED
    try:
        media = getattr(AVFoundation, f"AVMediaType{kind.capitalize()}")
        return int(AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(media))
    except Exception:  # noqa: BLE001
        return STATUS_AUTHORIZED


def check_camera_permission() -> int:
    return check_permission("video")


def check_microphone_permission() -> int:
    return check_permission("audio")


def request_permission(kind: str, timeout: float = 30.0) -> bool:
    """Request camera/microphone access, blocking until answered or timeout.

    Uses a nested Qt event loop so the AVFoundation completion handler (which
    is delivered on the run loop) can be awaited from the UI thread.
    """
    if not IS_MAC:
        return True
    try:
        import AVFoundation
    except ImportError:
        return True

    from PySide6.QtCore import QEventLoop, QTimer

    media = getattr(AVFoundation, f"AVMediaType{kind.capitalize()}")
    result: dict[str, bool] = {"granted": False}
    loop = QEventLoop()

    def _handler(granted: bool) -> None:
        result["granted"] = bool(granted)
        loop.quit()

    AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_(media, _handler)
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(int(timeout * 1000))
    loop.exec()
    return result["granted"]


def request_camera_permission(timeout: float = 30.0) -> bool:
    return request_permission("video", timeout)


def request_microphone_permission(timeout: float = 30.0) -> bool:
    return request_permission("audio", timeout)


def open_privacy_settings(kind: str) -> None:
    """Open the macOS System Settings pane for camera or microphone privacy."""
    if not IS_MAC:
        return
    target = "Privacy_Camera" if kind == "video" else "Privacy_Microphone"
    subprocess.Popen(
        ["open", f"x-apple.systempreferences:com.apple.preference.security?{target}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def permission_status_label(status: int) -> str:
    return _STATUS_LABEL.get(status, "unknown")
