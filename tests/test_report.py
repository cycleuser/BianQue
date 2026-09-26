import json
import os

from juzi.core import report
from juzi.core.models import Status


def test_format_bytes():
    assert report.format_bytes(0) == "0.0 B"
    assert report.format_bytes(1024) == "1.0 KB"
    assert report.format_bytes(1024 * 1024) == "1.0 MB"
    assert report.format_bytes(None) == "N/A"


def test_format_duration():
    assert report.format_duration(59) == "59s"
    assert report.format_duration(65) == "1m05s"
    assert report.format_duration(3661) == "1h01m01s"


def test_render_markdown(sample_report):
    md = report.render_markdown(sample_report)
    assert "验机报告" in md
    assert "检查A" in md
    assert "通过" in md


def test_render_html(sample_report):
    html = report.render_html(sample_report)
    assert "JuZi" in html
    assert "检查A" in html


def test_render_json(sample_report):
    data = json.loads(report.render_json(sample_report))
    assert data["host"] == "test-host"
    assert len(data["results"]) == 2


def test_save_report_markdown(tmp_path, sample_report):
    path = str(tmp_path / "report.md")
    report.save_report(sample_report, path)
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        assert "验机报告" in fh.read()


def test_save_report_html(tmp_path, sample_report):
    path = str(tmp_path / "report.html")
    report.save_report(sample_report, path)
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
        assert "<html" in content


def test_save_report_json(tmp_path, sample_report):
    path = str(tmp_path / "report.json")
    report.save_report(sample_report, path)
    with open(path, encoding="utf-8") as fh:
        assert json.loads(fh.read())["platform"] == "test-platform"


def test_report_count_includes_all_statuses(sample_report):
    counts = sample_report.count_by_status()
    assert counts[Status.PASS] == 1
    assert counts[Status.FAIL] == 1
