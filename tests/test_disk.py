import os

from bianque.core import disk


def test_run_disk_benchmark():
    result = disk.run_disk_benchmark(size_mb=2.0)
    assert result.error is None
    assert result.write_speed_mbps > 0
    assert result.read_speed_mbps > 0


def test_run_disk_benchmark_cleans_up():
    import tempfile

    tmpdir = tempfile.mkdtemp()
    result = disk.run_disk_benchmark(path=tmpdir, size_mb=1.0)
    assert result.error is None
    leftovers = [f for f in os.listdir(tmpdir) if f.startswith("bianque_bench_")]
    assert leftovers == []


def test_get_disk_info():
    info = disk.get_disk_info()
    assert isinstance(info, list)
