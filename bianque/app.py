"""Application entry point."""

from __future__ import annotations

import sys


def main() -> int:
    """Create the Qt application and show the main window."""
    from PySide6.QtWidgets import QApplication

    from bianque import __version__
    from bianque.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("BianQue")
    app.setApplicationDisplayName("BianQue 扁鹊 · 验机工具")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("cycleuser")

    from bianque.ui.theme import apply_theme

    apply_theme(app)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
