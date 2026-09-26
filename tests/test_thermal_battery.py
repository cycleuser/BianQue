from juzi.core import battery, thermal


def test_get_battery_info_structure():
    info = battery.get_battery_info()
    assert "present" in info
    assert "percent" in info
    assert "cycle_count" in info


def test_thermal_supported_returns_bool():
    assert isinstance(thermal.thermal_supported(), bool)


def test_get_temperatures_returns_list():
    assert isinstance(thermal.get_temperatures(), list)


def test_get_fan_speeds_returns_list():
    assert isinstance(thermal.get_fan_speeds(), list)
