"""Background task runner: run blocking core work off the UI thread.

Uses a daemon :class:`threading.Thread` (not ``QThread``) so a task can never
crash the process if it is still running when the app tears down. Results flow
back to the UI thread through Qt signals, which are thread-safe.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Signal


class TaskSignals(QObject):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(float, float)


class Task(QObject):
    """Run ``fn(progress, stop_event)`` in a daemon worker thread.

    The ``progress`` callable emits :class:`TaskSignals.progress`; ``stop_event``
    is a :class:`threading.Event` for cooperative cancellation.
    """

    def __init__(self, fn: Callable[..., Any], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._fn = fn
        self._stop = threading.Event()
        self.signals = TaskSignals()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            result = self._fn(progress=self.signals.progress.emit, stop_event=self._stop)
            self.signals.finished.emit(result)
        except Exception as exc:  # noqa: BLE001 - surface any failure to UI
            self.signals.error.emit(str(exc))

    def cancel(self) -> None:
        self._stop.set()

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
