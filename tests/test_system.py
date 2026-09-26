from bianque.core import system


def test_os_info():
    info = system.get_os_info()
    assert info["system"]
    assert info["hostname"]


def test_cpu_info():
    info = system.get_cpu_info()
    assert info["brand"]
    assert isinstance(info["logical_cores"], int)
    assert info["logical_cores"] >= 1


def test_memory_info():
    info = system.get_memory_info()
    assert info["total_bytes"] > 0
    assert 0 <= info["percent"] <= 100


def test_disk_partitions():
    parts = system.get_disk_partitions()
    assert isinstance(parts, list)
    assert len(parts) >= 1


def test_gpu_info_returns_list():
    assert isinstance(system.get_gpu_info(), list)


def test_board_info_returns_dict():
    assert isinstance(system.get_board_info(), dict)


def test_system_snapshot_keys():
    snap = system.get_system_snapshot()
    for key in ("os", "cpu", "memory", "disks", "gpu", "board", "boot_time"):
        assert key in snap
    assert "disk_drives" in snap


def test_cpu_info_extended_fields():
    info = system.get_cpu_info()
    assert "per_core_usage" in info
    assert "perf_levels" in info
    assert "cache" in info
    assert isinstance(info["cache"], dict)


def test_disk_drives_returns_list():
    drives = system.get_disk_drives()
    assert isinstance(drives, list)
    for d in drives:
        assert "type" in d
        assert "health" in d
        assert "smart_status" in d


def test_gpu_info_extended_fields():
    for gpu in system.get_gpu_info():
        assert "chip" in gpu
        assert "apis" in gpu
        assert "cores" in gpu

