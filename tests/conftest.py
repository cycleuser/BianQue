import os
import sys
from pathlib import Path

import pytest

# Headless Qt for CI/tests (must be set before any PySide6 import).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_report():
    from bianque.core.models import CheckResult, Report, Status

    report = Report(host="test-host", platform="test-platform")
    report.add(CheckResult(key="a", name="检查A", status=Status.PASS, message="ok"))
    report.add(CheckResult(key="b", name="检查B", status=Status.FAIL, message="bad"))
    return report
