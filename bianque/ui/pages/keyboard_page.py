"""Keyboard inspection: full-key test via an on-screen virtual keyboard."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from bianque.i18n import tr
from bianque.ui.pages.base import BasePage

_HIT_STYLE = "background: #16a34a; color: #fff; border: 1px solid #16a34a;"
_IDLE_STYLE = ""

_ROWS: list[list[tuple[str, str | int]]] = [
    [
        ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"),
        ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("0", "0"), ("-", "-"),
        ("=", "="), ("⌫", Qt.Key.Key_Backspace),
    ],
    [
        ("Tab", Qt.Key.Key_Tab), ("Q", "q"), ("W", "w"), ("E", "e"), ("R", "r"),
        ("T", "t"), ("Y", "y"), ("U", "u"), ("I", "i"), ("O", "o"), ("P", "p"),
        ("[", "["), ("]", "]"), ("\\", "\\"),
    ],
    [
        ("Caps", Qt.Key.Key_CapsLock), ("A", "a"), ("S", "s"), ("D", "d"), ("F", "f"),
        ("G", "g"), ("H", "h"), ("J", "j"), ("K", "k"), ("L", "l"), (";", ";"),
        ("'", "'"), ("⏎", Qt.Key.Key_Return),
    ],
    [
        ("⇧", Qt.Key.Key_Shift), ("Z", "z"), ("X", "x"), ("C", "c"), ("V", "v"),
        ("B", "b"), ("N", "n"), ("M", "m"), (",", ","), (".", "."), ("/", "/"),
        ("⇧", Qt.Key.Key_Shift),
    ],
    [
        ("Ctrl", Qt.Key.Key_Control), ("Opt", Qt.Key.Key_Alt), ("⌘", Qt.Key.Key_Meta),
        ("Space", Qt.Key.Key_Space), ("⌘", Qt.Key.Key_Meta), ("Alt", Qt.Key.Key_Alt),
        ("←", Qt.Key.Key_Left), ("↑", Qt.Key.Key_Up), ("↓", Qt.Key.Key_Down), ("→", Qt.Key.Key_Right),
    ],
]

_FN_ROW = [(f"F{i}", getattr(Qt.Key, f"Key_F{i}")) for i in range(1, 13)]


class KeyButton(QPushButton):
    def __init__(self, label: str, matcher: str | int) -> None:
        super().__init__(label)
        self.matcher = matcher
        self.is_hit = False
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(46, 40)
        self.setStyleSheet(_IDLE_STYLE)

    def matches(self, key: int, text: str) -> bool:
        if isinstance(self.matcher, str):
            return text == self.matcher
        return key == int(self.matcher)

    def mark_hit(self) -> None:
        self.is_hit = True
        self.setStyleSheet(_HIT_STYLE)


class KeyboardPage(BasePage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Keyboard", "Press every key; pressed keys turn green", parent)
        self._buttons: list[KeyButton] = []
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        grid = QGridLayout()
        grid.setSpacing(4)

        for col, (label, matcher) in enumerate(_FN_ROW):
            btn = self._add_button(label, matcher)
            grid.addWidget(btn, 0, col)

        for row, keys in enumerate(_ROWS, start=1):
            for col, (label, matcher) in enumerate(keys):
                btn = self._add_button(label, matcher)
                grid.addWidget(btn, row, col)

        self.content.addLayout(grid)

        self.progress_lbl = QLabel()
        self.content.addWidget(self.progress_lbl)

        self.unhit_lbl = QLabel("")
        self.unhit_lbl.setWordWrap(True)
        self.unhit_lbl.setStyleSheet("color: #9aa3ad;")
        self.content.addWidget(self.unhit_lbl)

        btn_row = QHBoxLayout()
        self.reset_btn = QPushButton(tr("Reset"))
        self.ok_btn = QPushButton(tr("All OK ✓"))
        self.bad_btn = QPushButton(tr("Faulty key ✗"))
        self.reset_btn.clicked.connect(self._reset)
        self.ok_btn.clicked.connect(self._confirm_ok)
        self.bad_btn.clicked.connect(self._confirm_bad)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.bad_btn)
        btn_row.addStretch(1)
        self.content.addLayout(btn_row)

        self._update_progress()

    def _add_button(self, label: str, matcher: str | int) -> KeyButton:
        btn = KeyButton(label, matcher)
        self._buttons.append(btn)
        return btn

    def _update_progress(self) -> None:
        hit = sum(1 for b in self._buttons if b.is_hit)
        total = len(self._buttons)
        self.progress_lbl.setText(tr("Tested {0} / {1} keys", hit, total))
        unhit = [b.text() for b in self._buttons if not b.is_hit]
        if unhit:
            self.unhit_lbl.setText(f"{tr('Untested')}: " + "  ".join(unhit))
        else:
            self.unhit_lbl.setText(tr("All keys pressed ✓"))

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        text = event.text().lower()
        key = event.key()
        if key == Qt.Key.Key_Backtab:
            key = Qt.Key.Key_Tab
        for btn in self._buttons:
            if not btn.is_hit and btn.matches(key, text):
                btn.mark_hit()
        self._update_progress()
        event.accept()

    def focusNextPrevChild(self, next_child: bool) -> bool:  # noqa: N802
        # Tab / Shift+Tab must be treated as keys under test, not focus navigation.
        return False

    def _reset(self) -> None:
        for btn in self._buttons:
            btn.is_hit = False
            btn.setStyleSheet(_IDLE_STYLE)
        self._update_progress()

    def _confirm_ok(self) -> None:
        hit = sum(1 for b in self._buttons if b.is_hit)
        total = len(self._buttons)
        self.mark_pass("keyboard.keys", "Keyboard Keys", tr("Confirmed {0}/{1} keys OK", hit, total), {"tested": hit, "total": total})

    def _confirm_bad(self) -> None:
        unhit = [b.text() for b in self._buttons if not b.is_hit]
        self.mark_fail("keyboard.keys", "Keyboard Keys", tr("Keys likely faulty: {0}", " ".join(unhit)), {"unhit": unhit})

    def showEvent(self, event) -> None:  # noqa: N802
        self.setFocus()
        super().showEvent(event)
