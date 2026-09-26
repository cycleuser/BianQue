"""Report page: summary table + export to Markdown/HTML/JSON."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from bianque.core.models import Report
from bianque.core.report import save_report
from bianque.i18n import tr
from bianque.ui.pages.base import BasePage
from bianque.ui.widgets.common import status_label


class ReportPage(BasePage):
    def __init__(self, get_report: Callable[[], Report], parent: QWidget | None = None) -> None:
        super().__init__("Report", "Aggregate all results and export a report", parent)
        self._get_report = get_report

        self.summary_lbl = QLabel("")
        self.content.addWidget(self.summary_lbl)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([tr("Check Item"), tr("Status"), tr("Result")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.content.addWidget(self.table, stretch=1)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton(tr("Refresh"))
        self.export_btn = QPushButton(tr("Export Report…"))
        self.export_btn.setObjectName("primary")
        self.refresh_btn.clicked.connect(self.refresh)
        self.export_btn.clicked.connect(self._export)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.export_btn)
        btn_row.addStretch(1)
        self.content.addLayout(btn_row)

        self.refresh()

    def refresh(self) -> None:
        report = self._get_report()
        counts = report.count_by_status()
        self.summary_lbl.setText(
            tr("{0} items · Pass {1} · Fail {2} · Unknown {3} · Skipped {4}",
               len(report.results), counts["pass"], counts["fail"], counts["unknown"], counts["skipped"])
        )
        self.table.setRowCount(0)
        for r in report.results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(tr(r.name)))
            self.table.setCellWidget(row, 1, status_label(r.status))
            self.table.setItem(row, 2, QTableWidgetItem(r.message))

    def _export(self) -> None:
        path, _filter = QFileDialog.getSaveFileName(
            self,
            tr("Export Report"),
            "bianque_report.html",
            "HTML (*.html);;Markdown (*.md);;JSON (*.json)",
        )
        if not path:
            return
        try:
            save_report(self._get_report(), path)
        except OSError as exc:
            QMessageBox.warning(self, tr("Export failed"), str(exc))
            return
        QMessageBox.information(self, tr("Export succeeded"), f"{tr('Report saved to')}:\n{path}")

    def showEvent(self, event) -> None:  # noqa: N802
        self.refresh()
        super().showEvent(event)
