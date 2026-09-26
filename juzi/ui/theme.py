"""Qt theme: colour palette and global stylesheet."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

# Brand colours (墨家 · 玄黑 + 朱红 accent)
BG = "#14161a"
BG_ALT = "#1c1f24"
PANEL = "#23272f"
BORDER = "#343a45"
TEXT = "#e6e8eb"
TEXT_DIM = "#9aa3ad"
ACCENT = "#d9483b"
GREEN = "#16a34a"
RED = "#dc2626"
AMBER = "#d97706"
BLUE = "#3b82f6"

QSS = f"""
* {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}}
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
}}
QListWidget {{
    background: {BG_ALT};
    border: none;
    outline: none;
}}
QListWidget::item {{
    padding: 10px 16px;
    color: {TEXT_DIM};
    border-left: 3px solid transparent;
}}
QListWidget::item:hover {{
    background: {PANEL};
    color: {TEXT};
}}
QListWidget::item:selected {{
    background: {PANEL};
    color: {TEXT};
    border-left: 3px solid {ACCENT};
}}
QFrame#header {{
    background: {BG_ALT};
    border-bottom: 1px solid {BORDER};
}}
QLabel#title {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#subtitle {{
    color: {TEXT_DIM};
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px;
    background: {PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {TEXT};
}}
QPushButton {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 6px 16px;
    color: {TEXT};
}}
QPushButton:hover {{ background: #2b313a; }}
QPushButton:pressed {{ background: #313845; }}
QPushButton:disabled {{ color: #5b636c; }}
QPushButton#primary {{
    background: {ACCENT};
    border: none;
    color: #ffffff;
    font-weight: 600;
}}
QPushButton#primary:hover {{ background: #e05547; }}
QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    background: {BG_ALT};
    color: {TEXT};
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 3px;
}}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
    color: {TEXT};
}}
QTextEdit, QPlainTextEdit {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px;
    color: {TEXT};
}}
QTableWidget {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    gridline-color: {BORDER};
}}
QHeaderView::section {{
    background: {PANEL};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 5px;
}}
QScrollBar:vertical {{
    background: {BG_ALT}; width: 10px; margin: 0;
}}
QScrollBar::handle:vertical {{ background: #3a414c; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QStatusBar {{ background: {BG_ALT}; color: {TEXT_DIM}; }}
QLabel#status-pass {{ color: {GREEN}; font-weight: 600; }}
QLabel#status-fail {{ color: {RED}; font-weight: 600; }}
QLabel#status-unknown {{ color: {AMBER}; font-weight: 600; }}
QLabel#status-skipped {{ color: {TEXT_DIM}; font-weight: 600; }}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_ALT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    app.setPalette(palette)
    app.setStyleSheet(QSS)
