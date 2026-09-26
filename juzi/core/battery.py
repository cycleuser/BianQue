"""Battery health probing (percent, cycle count, condition)."""

from __future__ import annotations

import sys
from typing import Any

import psutil

from juzi.core.system import _run, _system_profiler_json

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


def get_battery_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "present": False,
        "percent": None,
        "power_plugged": None,
        "secsleft": None,
        "cycle_count": None,
        "condition": None,
        "design_capacity": None,
        "full_capacity": None,
    }
    try:
        batt = psutil.sensors_battery()
        if batt is not None:
            info["present"] = True
            info["percent"] = batt.percent
            info["power_plugged"] = batt.power_plugged
            info["secsleft"] = batt.secsleft
    except (NotImplementedError, OSError):
        pass

    extra: dict[str, Any] = {}
    if IS_MAC:
        extra = _mac_battery()
    elif IS_WIN:
        extra = _win_battery()
    elif IS_LINUX:
        extra = _linux_battery()
    info.update(extra)
    return info


def _mac_battery() -> dict[str, Any]:
    power = _system_profiler_json("SPPowerDataType")
    items = power.get("SPPowerDataType") or []
    if not items:
        return {}
    batt = items[0]
    return {
        "cycle_count": batt.get("sppower_battery_cycle_count") or batt.get("cycle_count"),
        "condition": batt.get("sppower_battery_condition") or batt.get("condition"),
        "max_capacity_percent": batt.get("sppower_battery_max_capacity")
        or batt.get("maximum_capacity"),
    }


def _win_battery() -> dict[str, Any]:
    out, _, code = _run(
        ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining,DesignCapacity,FullChargeCapacity", "/value"],
        timeout=20.0,
    )
    if code != 0:
        return {}
    result: dict[str, Any] = {}
    for line in out.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip().lower(), val.strip()
        if not val or val == "0":
            continue
        if key == "estimatedchargeremaining":
            result["percent"] = int(val)
        elif key == "designcapacity":
            result["design_capacity"] = int(val)
        elif key == "fullchargecapacity":
            result["full_capacity"] = int(val)
    return result


def _linux_battery() -> dict[str, Any]:
    out, _, code = _run(["upower", "-d"], timeout=15.0)
    if code != 0:
        return {}
    result: dict[str, Any] = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("energy-full-design"):
            result["design_capacity"] = line.split(":", 1)[1].strip()
        elif line.startswith("energy-full"):
            result["full_capacity"] = line.split(":", 1)[1].strip()
        elif line.startswith("capacity"):
            result["percent"] = line.split(":", 1)[1].strip()
    return result
