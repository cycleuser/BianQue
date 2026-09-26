"""Main window: left navigation + stacked inspection pages + language menu."""

from __future__ import annotations

import platform
import socket

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from bianque.core.models import CheckResult, Report, Status
from bianque.i18n import (
    available_languages,
    get_language,
    language_changed_signal,
    set_language,
    tr,
)
from bianque.ui.pages.base import BasePage
from bianque.ui.pages.battery_page import BatteryPage
from bianque.ui.pages.camera_page import CameraPage
from bianque.ui.pages.disk_page import DiskPage
from bianque.ui.pages.keyboard_page import KeyboardPage
from bianque.ui.pages.memory_page import MemoryPage
from bianque.ui.pages.microphone_page import MicrophonePage
from bianque.ui.pages.mouse_page import MousePage
from bianque.ui.pages.network_page import NetworkPage
from bianque.ui.pages.overview_page import OverviewPage
from bianque.ui.pages.report_page import ReportPage
from bianque.ui.pages.screen_page import ScreenPage
from bianque.ui.pages.speaker_page import SpeakerPage
from bianque.ui.pages.thermal_page import ThermalPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BianQue 扁鹊 · 验机工具")
        self.resize(1100, 760)

        self.report = Report(
            host=socket.gethostname(),
            platform=f"{platform.system()} {platform.release()}",
        )
        self._results_by_key: dict[str, CheckResult] = {}

        self.nav = QListWidget()
        self.nav.setFixedWidth(200)
        self.stack = QStackedWidget()
        self._lang_actions: dict[str, QAction] = {}

        self._build_language_menu()
        self._populate_pages()

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self._update_status_bar()

    def _build_language_menu(self) -> None:
        menu = self.menuBar().addMenu(tr("Language"))
        group = QActionGroup(self)
        group.setExclusive(True)
        for code, name in available_languages():
            action = QAction(name, self, checkable=True)
            action.setChecked(code == get_language())
            action.triggered.connect(lambda _checked=False, c=code: self._switch_language(c))
            group.addAction(action)
            menu.addAction(action)
            self._lang_actions[code] = action
        language_changed_signal().connect(self._on_language_changed)

    def _switch_language(self, code: str) -> None:
        set_language(code)

    def _on_language_changed(self, code: str) -> None:
        for lang, action in self._lang_actions.items():
            action.setChecked(lang == code)
        self._populate_pages()
        self._update_status_bar()

    def _populate_pages(self) -> None:
        self.nav.clear()
        while self.stack.count():
            widget = self.stack.widget(0)
            if widget is not None:
                self.stack.removeWidget(widget)
                widget.deleteLater()
        for page in self._build_pages():
            self._add_page(page)
        self.nav.setCurrentRow(0)

    def _build_pages(self) -> list[BasePage]:
        return [
            OverviewPage(),
            ScreenPage(),
            CameraPage(),
            MicrophonePage(),
            SpeakerPage(),
            KeyboardPage(),
            MousePage(),
            ThermalPage(),
            BatteryPage(),
            DiskPage(),
            MemoryPage(),
            NetworkPage(),
            ReportPage(get_report=lambda: self.report),
        ]

    def _add_page(self, page: BasePage) -> None:
        page.set_result_callback(self._on_result)
        item = QListWidgetItem(page.page_title)
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.nav.addItem(item)
        self.stack.addWidget(page)

    def _on_result(self, result: CheckResult) -> None:
        self._results_by_key[result.key] = result
        self.report.results = list(self._results_by_key.values())
        self._update_status_bar()

    def _update_status_bar(self) -> None:
        counts = self.report.count_by_status()
        self.statusBar().showMessage(
            f"{tr('Pass')} {counts[Status.PASS]}  ·  "
            f"{tr('Fail')} {counts[Status.FAIL]}  ·  "
            f"{tr('Unknown')} {counts[Status.UNKNOWN]}  ·  "
            f"{tr('Skipped')} {counts[Status.SKIPPED]}"
        )
