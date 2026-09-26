"""UI smoke tests: pages instantiate and the main window assembles."""

import pytest

from juzi.ui.main_window import MainWindow
from juzi.ui.pages.base import BasePage


@pytest.fixture
def window(qtbot):
    win = MainWindow()
    qtbot.addWidget(win)
    return win


def test_main_window_assembles(window):
    assert window.nav.count() == 13
    assert window.stack.count() == 13
    assert window.windowTitle().startswith("JuZi")


def test_navigation_switches_pages(window, qtbot):
    for i in range(window.nav.count()):
        window.nav.setCurrentRow(i)
        qtbot.wait(10)
        assert window.stack.currentIndex() == i


def test_pages_are_base_pages(window):
    for i in range(window.stack.count()):
        page = window.stack.widget(i)
        assert isinstance(page, BasePage)


def test_report_dedup_by_key(window):
    from juzi.core.models import CheckResult, Status

    window._on_result(CheckResult(key="k", name="a", status=Status.UNKNOWN))
    window._on_result(CheckResult(key="k", name="a", status=Status.PASS))
    assert len(window.report.results) == 1
    assert window.report.results[0].status == Status.PASS


def test_report_page_refresh(window):
    from juzi.core.models import CheckResult, Status

    window.report.results = [
        CheckResult(key="x", name="测试", status=Status.PASS, message="好"),
    ]
    report_page = window.stack.widget(12)
    report_page.refresh()
    assert report_page.table.rowCount() == 1
