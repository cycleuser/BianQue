from bianque.core import memory


def test_get_memory_details_structure():
    info = memory.get_memory_details()
    assert "total_bytes" in info
    assert "modules" in info
    assert "channels" in info
    assert "bandwidth_gbps" in info
    assert isinstance(info["modules"], list)


def test_get_memory_details_modules_fields():
    info = memory.get_memory_details()
    for mod in info["modules"]:
        for field in ("slot", "manufacturer", "type", "capacity", "speed_mhz", "timing"):
            assert field in mod


def test_run_memory_self_test_small():
    result = memory.run_memory_self_test(size_mb=32.0)
    assert result.ok is True
    assert result.error is None
    assert result.write_speed_mbps > 0
    assert result.read_speed_mbps > 0
