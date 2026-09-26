"""Cross-platform system/hardware information collection.

Uses ``psutil`` for portable metrics and platform-specific read-only
commands (``system_profiler`` / ``wmic`` / ``lspci`` / ``sysfs``) for the
rest. Every probe degrades gracefully to ``None`` when unavailable.
"""

from __future__ import annotations

import json
import platform
import socket
import subprocess
import sys
from collections.abc import Callable
from functools import lru_cache
from typing import Any

import psutil

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


def _run(cmd: list[str], timeout: float = 15.0) -> tuple[str, str, int]:
    """Run a read-only command, returning (stdout, stderr, returncode)."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            errors="replace",
        )
        return proc.stdout, proc.stderr, proc.returncode
    except (subprocess.SubprocessError, OSError):
        return "", "", -1


@lru_cache(maxsize=1)
def _system_profiler_json(datatype: str) -> dict[str, Any]:
    """macOS ``system_profiler <datatype> -json`` parsed (cached)."""
    if not IS_MAC:
        return {}
    out, _, code = _run(["system_profiler", datatype, "-json"], timeout=30.0)
    if code != 0 or not out.strip():
        return {}
    try:
        return dict(json.loads(out))
    except json.JSONDecodeError:
        return {}


def get_os_info() -> dict[str, Any]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "hostname": socket.gethostname(),
    }


def get_cpu_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "brand": None,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "freq_current_mhz": None,
        "freq_max_mhz": None,
        "freq_min_mhz": None,
        "usage_percent": None,
        "load_avg": None,
    }
    try:
        freq = psutil.cpu_freq()
        if freq is not None:
            info["freq_current_mhz"] = freq.current
            info["freq_max_mhz"] = freq.max
            info["freq_min_mhz"] = freq.min
    except (NotImplementedError, FileNotFoundError, OSError):
        pass
    try:
        info["usage_percent"] = psutil.cpu_percent(interval=0.1)
    except (NotImplementedError, OSError):
        pass
    try:
        info["load_avg"] = list(psutil.getloadavg())
    except (OSError, AttributeError):
        pass

    if IS_MAC:
        brand = _apple_silicon_brand() or platform.processor() or None
        info["brand"] = brand
    elif IS_WIN:
        info["brand"] = _wmic("cpu", "name")
    else:
        info["brand"] = _linux_cpu_model() or platform.processor() or None

    info["brand"] = info["brand"] or platform.processor() or "Unknown CPU"
    return info


def get_memory_info() -> dict[str, Any]:
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "total_bytes": vm.total,
        "available_bytes": vm.available,
        "used_bytes": vm.used,
        "percent": vm.percent,
        "swap_total_bytes": sw.total,
        "swap_used_bytes": sw.used,
        "swap_percent": sw.percent,
    }


def get_disk_partitions() -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    for p in psutil.disk_partitions(all=False):
        entry: dict[str, Any] = {
            "device": p.device,
            "mountpoint": p.mountpoint,
            "fstype": p.fstype,
            "total_bytes": None,
            "used_bytes": None,
            "percent": None,
        }
        try:
            usage = psutil.disk_usage(p.mountpoint)
            entry["total_bytes"] = usage.total
            entry["used_bytes"] = usage.used
            entry["percent"] = usage.percent
        except (OSError, PermissionError):
            pass
        parts.append(entry)
    return parts


def get_gpu_info() -> list[dict[str, Any]]:
    if IS_MAC:
        return _mac_gpu()
    if IS_WIN:
        return _win_gpu()
    return _linux_gpu()


def get_board_info() -> dict[str, Any]:
    if IS_MAC:
        hw = _system_profiler_json("SPHardwareDataType")
        items = hw.get("SPHardwareDataType") or []
        if items:
            i0 = items[0]
            return {
                "model": i0.get("model_name") or i0.get("machine_name"),
                "identifier": i0.get("machine_model"),
                "serial": i0.get("serial_number"),
                "chip": i0.get("chip_type"),
                "memory": i0.get("physical_memory"),
                "cpu_count": i0.get("number_processors"),
            }
        return {}
    if IS_WIN:
        return {
            "model": _wmic("csproduct", "name"),
            "manufacturer": _wmic("csproduct", "vendor"),
            "serial": _wmic("bios", "serialnumber"),
        }
    return {
        "model": _read_file("/sys/class/dmi/id/product_name"),
        "manufacturer": _read_file("/sys/class/dmi/id/sys_vendor"),
    }


def get_system_snapshot() -> dict[str, Any]:
    """Aggregate all system info into one dict for the overview page."""
    return {
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_partitions(),
        "gpu": get_gpu_info(),
        "board": get_board_info(),
        "boot_time": psutil.boot_time(),
    }


# --------------------------------------------------------------------------- #
# Platform helpers
# --------------------------------------------------------------------------- #

def _wmic(klass: str, prop: str) -> str | None:
    """Query a single WMIC property (Windows, read-only)."""
    if not IS_WIN:
        return None
    out, _, code = _run(
        ["wmic", klass, "get", prop, "/value"], timeout=20.0
    )
    if code != 0:
        return None
    for line in out.splitlines():
        line = line.strip()
        if "=" in line:
            key, _, val = line.partition("=")
            if key.strip().lower() == prop.lower() and val.strip():
                return val.strip()
    return None


def _apple_silicon_brand() -> str | None:
    """Brand string for Apple Silicon via sysctl (no system_profiler needed)."""
    out, _, code = _run(["sysctl", "-n", "machdep.cpu.brand_string"], timeout=10.0)
    if code == 0 and out.strip():
        return out.strip()
    return None


def _linux_cpu_model() -> str | None:
    return _read_file("/proc/cpuinfo", _extract_cpu_model) or None


def _extract_cpu_model(text: str) -> str | None:
    for line in text.splitlines():
        if line.lower().startswith("model name"):
            _, _, val = line.partition(":")
            return val.strip()
    return None


def _mac_gpu() -> list[dict[str, Any]]:
    disp = _system_profiler_json("SPDisplaysDataType")
    out: list[dict[str, Any]] = []
    for item in disp.get("SPDisplaysDataType") or []:
        out.append(
            {
                "name": item.get("sppci_model") or item.get("_name"),
                "vendor": item.get("spdisplays_vendor"),
                "vram": item.get("spdisplays_vram") or item.get("spdisplays_vram_shared"),
                "displays": item.get("spdisplays_ndrvs") or [],
            }
        )
    return out


def _win_gpu() -> list[dict[str, Any]]:
    name = _wmic("path", "name")
    out: list[dict[str, Any]] = []
    if name:
        out.append({"name": name, "vendor": None, "vram": None})
    return out


def _linux_gpu() -> list[dict[str, Any]]:
    out, _, code = _run(["lspci"], timeout=10.0)
    gpus = []
    if code == 0:
        for line in out.splitlines():
            low = line.lower()
            if "vga" in low or "3d" in low or "display" in low:
                gpus.append({"name": line.strip(), "vendor": None, "vram": None})
    return gpus


def _read_file(path: str, transform: Callable[[str], str | None] | None = None) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read().strip()
    except OSError:
        return None
    if not text:
        return None
    if transform is not None:
        return transform(text)
    return text
