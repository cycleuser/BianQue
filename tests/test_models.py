from juzi.core.models import CheckResult, Report, Status


def test_status_all():
    assert set(Status.all()) == {Status.PASS, Status.FAIL, Status.UNKNOWN, Status.SKIPPED}


def test_check_result_roundtrip():
    r = CheckResult(key="screen.dead_pixel", name="坏点", status=Status.PASS, message="ok", data={"n": 0})
    raw = r.to_dict()
    back = CheckResult.from_dict(raw)
    assert back.key == r.key
    assert back.name == r.name
    assert back.status == r.status
    assert back.message == r.message
    assert back.data == r.data


def test_check_result_defaults():
    r = CheckResult(key="k", name="n")
    assert r.status == Status.UNKNOWN
    assert r.data == {}


def test_report_count_by_status():
    report = Report()
    report.add(CheckResult(key="1", name="a", status=Status.PASS))
    report.add(CheckResult(key="2", name="b", status=Status.PASS))
    report.add(CheckResult(key="3", name="c", status=Status.FAIL))
    counts = report.count_by_status()
    assert counts[Status.PASS] == 2
    assert counts[Status.FAIL] == 1
    assert counts[Status.UNKNOWN] == 0
    assert counts[Status.SKIPPED] == 0


def test_report_to_dict():
    report = Report(host="h", platform="p")
    report.add(CheckResult(key="1", name="a", status=Status.PASS))
    d = report.to_dict()
    assert d["host"] == "h"
    assert len(d["results"]) == 1
