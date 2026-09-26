"""Page base class shared by all inspection pages."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from bianque.core.models import CheckResult, Status
from bianque.i18n import tr


class BasePage(QWidget):
    """A single inspection page with a header and a content area."""

    def __init__(self, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.page_title = tr(title)
        self._result_cb: Callable[[CheckResult], None] | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 12)
        title_lbl = QLabel(tr(title))
        title_lbl.setObjectName("title")
        self.subtitle_lbl = QLabel(tr(subtitle))
        self.subtitle_lbl.setObjectName("subtitle")
        self.subtitle_lbl.setWordWrap(True)
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(self.subtitle_lbl)
        root.addWidget(header)

        self.content = QVBoxLayout()
        self.content.setSpacing(10)
        root.addLayout(self.content, 1)

    def set_result_callback(self, cb: Callable[[CheckResult], None]) -> None:
        self._result_cb = cb

    def report(self, key: str, name: str, status: str, message: str = "", data: dict | None = None) -> CheckResult:
        result = CheckResult(key=key, name=name, status=status, message=message, data=data or {})
        if self._result_cb is not None:
            self._result_cb(result)
        return result

    def mark_pass(self, key: str, name: str, message: str = "", data: dict | None = None) -> CheckResult:
        return self.report(key, name, Status.PASS, message, data)

    def mark_fail(self, key: str, name: str, message: str = "", data: dict | None = None) -> CheckResult:
        return self.report(key, name, Status.FAIL, message, data)

    def mark_unknown(self, key: str, name: str, message: str = "", data: dict | None = None) -> CheckResult:
        return self.report(key, name, Status.UNKNOWN, message, data)
