"""Cross-platform thermal (temperature / fan) probing.

Readings come from ``psutil`` on Linux, WMI on Windows, and are unsupported on
macOS without SMC access (``powermetrics`` needs root). Every probe degrades
gracefully to an empty list + a ``supported`` flag.
"""

from __future__ import annotations

import sys
from typing import Any

import psutil

from juzi.core.system import _run

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


def thermal_supported() -> bool:
    if IS_LINUX:
        return bool(psutil.sensors_temperatures())
    if IS_WIN:
        return _win_wmi_available()
    return False


def get_temperatures() -> list[dict[str, Any]]:
    """Return temperature sensors as dicts: label, current, high, critical."""
    if IS_LINUX:
        return _linux_temperatures()
    if IS_WIN:
        return _win_temperatures()
    return []


def get_fan_speeds() -> list[dict[str, Any]]:
    """Return fan sensors as dicts: label, current (RPM)."""
    if IS_LINUX:
        return _linux_fans()
    if IS_WIN:
        return _win_fans()
    return []


# --------------------------------------------------------------------------- #
# Linux
# --------------------------------------------------------------------------- #

def _linux_temperatures() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    try:
        for name, entries in psutil.sensors_temperatures().items():
            for e in entries:
                result.append(
                    {
                        "label": e.label or name,
                        "current": e.current,
                        "high": e.high,
                        "critical": e.critical,
                    }
                )
    except (NotImplementedError, OSError):
        pass
    return result


def _linux_fans() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    try:
        for name, entries in psutil.sensors_fans().items():
            for e in entries:
                result.append({"label": e.label or name, "current": e.current})
    except (NotImplementedError, OSError):
        pass
    return result


# --------------------------------------------------------------------------- #
# Windows (WMI via PowerShell, read-only)
# --------------------------------------------------------------------------- #

def _win_wmi_available() -> bool:
    out, _, code = _run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance -Namespace root/wmi -ClassName "
            "MSAcpi_ThermalZoneTemperature",
        ],
        timeout=20.0,
    )
    return code == 0 and bool(out.strip())


def _win_temperatures() -> list[dict[str, Any]]:
    out, _, code = _run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "(Get-CimInstance -Namespace root/wmi -ClassName "
            "MSAcpi_ThermalZoneTemperature | Measure-Object -Property "
            "CurrentTemperature -Average).Average",
        ],
        timeout=20.0,
    )
    if code != 0 or not out.strip():
        return []
    try:
        # WMI reports tenths of Kelvin.
        tenths_k = float(out.strip())
        celsius = tenths_k / 10.0 - 273.15
    except ValueError:
        return []
    return [{"label": "ThermalZone", "current": round(celsius, 1), "high": None, "critical": None}]


def _win_fans() -> list[dict[str, Any]]:
    out, _, code = _run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Fan | Select-Object -ExpandProperty DesiredSpeed",
        ],
        timeout=20.0,
    )
    fans: list[dict[str, Any]] = []
    if code == 0:
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit():
                fans.append({"label": "Fan", "current": int(line)})
    return fans
