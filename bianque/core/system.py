"""Cross-platform system/hardware information collection.

Uses ``psutil`` for portable metrics and platform-specific read-only
commands (``system_profiler`` / ``wmic`` / ``lspci`` / ``sysfs``) for the
rest. Every probe degrades gracefully to ``None`` when unavailable.
"""

from __future__ import annotations

import json
import platform
import re
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
        "per_core_freq_mhz": None,
        "per_core_usage": None,
        "cache": {},
        "perf_levels": None,
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
    try:
        info["per_core_freq_mhz"] = [f.current for f in psutil.cpu_freq(percpu=True)]
    except (NotImplementedError, FileNotFoundError, OSError):
        pass
    try:
        info["per_core_usage"] = psutil.cpu_percent(percpu=True, interval=0.1)
    except (NotImplementedError, OSError):
        pass
    info["cache"] = _get_cache_info()

    if IS_MAC:
        mac_freq = _mac_cpu_freq()
        if mac_freq[0] is not None:
            info["freq_current_mhz"], info["freq_max_mhz"], info["freq_min_mhz"] = mac_freq
        else:
            # Apple Silicon: psutil reports bogus tiny freq values; clear them.
            info["freq_current_mhz"] = None
            info["freq_max_mhz"] = None
            info["freq_min_mhz"] = None
            info["per_core_freq_mhz"] = None
        info["perf_levels"] = _mac_perf_levels()

    if IS_MAC:
        brand = _apple_silicon_brand() or platform.processor() or None
        info["brand"] = brand
    elif IS_WIN:
        info["brand"] = _wmic("cpu", "name")
    else:
        info["brand"] = _linux_cpu_model() or platform.processor() or None

    info["brand"] = info["brand"] or platform.processor() or "Unknown CPU"
    return info


def _get_cache_info() -> dict[str, Any]:
    """L1/L2/L3 cache sizes in bytes (best-effort, per platform)."""
    cache: dict[str, Any] = {}
    if IS_MAC:
        out, _, code = _run(
            [
                "sysctl", "-n",
                "hw.l1icachesize", "hw.l1dcachesize", "hw.l2cachesize", "hw.l3cachesize",
            ],
            timeout=10.0,
        )
        if code == 0:
            vals = out.split()
            names = ("l1i", "l1d", "l2", "l3")
            for name, val in zip(names, vals, strict=False):
                if val.strip().isdigit():
                    cache[name] = int(val.strip())
    elif IS_WIN:
        l2 = _wmic("cpu", "l2cachesize")
        l3 = _wmic("cpu", "l3cachesize")
        if l2 and l2.isdigit():
            cache["l2"] = int(l2) * 1024
        if l3 and l3.isdigit():
            cache["l3"] = int(l3) * 1024
    else:
        for name, path in (
            ("l1d", "/sys/devices/system/cpu/cpu0/cache/index0/size"),
            ("l1i", "/sys/devices/system/cpu/cpu0/cache/index1/size"),
            ("l2", "/sys/devices/system/cpu/cpu0/cache/index2/size"),
            ("l3", "/sys/devices/system/cpu/cpu0/cache/index3/size"),
        ):
            raw = _read_file(path)
            if raw:
                cache[name] = _parse_size(raw)
    return cache


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
        "disk_drives": get_disk_drives(),
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


def _mac_cpu_freq() -> tuple[float | None, float | None, float | None]:
    """CPU frequency in MHz via ``sysctl hw.cpufrequency`` (Intel Macs only).

    Returns ``(current, max, min)``; Apple Silicon reports no such keys so all
    are ``None``.
    """
    out, _, code = _run(["sysctl", "-n", "hw.cpufrequency", "hw.cpufrequency_max"], timeout=10.0)
    if code != 0:
        return None, None, None
    vals = out.split()
    if len(vals) < 2:
        return None, None, None
    try:
        cur = float(vals[0]) / 1e6
        mx = float(vals[1]) / 1e6
    except ValueError:
        return None, None, None
    if cur <= 0 or mx <= 0:
        return None, None, None
    return round(cur), round(mx), None


def _mac_perf_levels() -> list[dict[str, Any]] | None:
    """Performance/efficiency core counts (Apple Silicon) via ``sysctl -a``."""
    out, _, code = _run(["sysctl", "-a"], timeout=10.0)
    if code != 0:
        return None
    levels: dict[int, dict[str, Any]] = {}
    for line in out.splitlines():
        m = re.match(r"hw\.perflevel(\d+)\.(\w+):\s*(.+)", line.strip())
        if not m:
            continue
        idx, field, value = int(m.group(1)), m.group(2), m.group(3).strip()
        levels.setdefault(idx, {"index": idx})
        if field == "name":
            levels[idx]["name"] = value
        elif field == "physicalcpu":
            levels[idx]["cores"] = int(value)
    if not levels:
        return None
    return [levels[i] for i in sorted(levels)]


def _linux_cpu_model() -> str | None:
    return _read_file("/proc/cpuinfo", _extract_cpu_model) or None


def _extract_cpu_model(text: str) -> str | None:
    for line in text.splitlines():
        if line.lower().startswith("model name"):
            _, _, val = line.partition(":")
            return val.strip()
    return None


def get_disk_drives() -> list[dict[str, Any]]:
    """Physical disk drives with type (SSD/HDD), protocol and SMART health."""
    if IS_MAC:
        return _mac_disks()
    if IS_WIN:
        return _win_disks()
    return _linux_disks()


def _mac_gpu() -> list[dict[str, Any]]:
    disp = _system_profiler_json("SPDisplaysDataType")
    out: list[dict[str, Any]] = []
    for item in disp.get("SPDisplaysDataType") or []:
        metal = _metal_name(item.get("spdisplays_mtlgpufamilysupport"))
        apis = [metal] if metal else []
        out.append(
            {
                "name": item.get("sppci_model") or item.get("_name"),
                "vendor": _vendor_name(item.get("spdisplays_vendor")),
                "chip": item.get("sppci_model") or item.get("_name"),
                "vram": item.get("spdisplays_vram") or item.get("spdisplays_vram_shared"),
                "cores": item.get("sppci_cores"),
                "apis": apis,
                "driver": None,
                "displays": item.get("spdisplays_ndrvs") or [],
            }
        )
    return out


def _win_gpu() -> list[dict[str, Any]]:
    rows = _wmic_multi(
        "path", "win32_VideoController",
        ["name", "adapterram", "driverversion", "videoprocessor"],
    )
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "name": r.get("name"),
                "vendor": None,
                "chip": r.get("videoprocessor") or r.get("name"),
                "vram": _format_bytes_raw(r.get("adapterram")),
                "cores": None,
                "apis": [],
                "driver": r.get("driverversion"),
                "displays": [],
            }
        )
    return out


def _linux_gpu() -> list[dict[str, Any]]:
    out, _, code = _run(["lspci", "-v"], timeout=10.0)
    gpus: list[dict[str, Any]] = []
    if code == 0:
        for line in out.splitlines():
            low = line.lower()
            if "vga" in low or "3d" in low or "display" in low:
                gpus.append(
                    {
                        "name": line.strip(),
                        "vendor": None,
                        "chip": line.strip(),
                        "vram": None,
                        "cores": None,
                        "apis": [],
                        "driver": None,
                        "displays": [],
                    }
                )
    return gpus


def _mac_disks() -> list[dict[str, Any]]:
    storage = _system_profiler_json("SPStorageDataType")
    drives: dict[str, dict[str, Any]] = {}
    for item in storage.get("SPStorageDataType") or []:
        pd = item.get("physical_drive") or {}
        if not pd:
            continue
        key = str(pd.get("media_name") or pd.get("device_name") or "unknown")
        vol_size = item.get("size_in_bytes")
        if key not in drives:
            medium = (pd.get("medium_type") or "").lower()
            drives[key] = {
                "model": pd.get("device_name") or key,
                "type": "ssd" if "ssd" in medium else ("hdd" if "hdd" in medium or "rotational" in medium else "unknown"),
                "protocol": pd.get("protocol"),
                "smart_status": pd.get("smart_status"),
                "health": _normalize_health(pd.get("smart_status")),
                "is_internal": pd.get("is_internal_disk") == "yes",
                "size_bytes": vol_size,
            }
        elif vol_size:
            existing = drives[key].get("size_bytes")
            if existing is None or vol_size > existing:
                drives[key]["size_bytes"] = vol_size
    return list(drives.values())


def _win_disks() -> list[dict[str, Any]]:
    rows = _wmic_multi("path", "win32_diskdrive", ["model", "mediatype", "size", "status"])
    out: list[dict[str, Any]] = []
    for r in rows:
        media = (r.get("mediatype") or "").lower()
        out.append(
            {
                "model": r.get("model"),
                "type": "ssd" if "ssd" in media else ("hdd" if "hdd" in media else "unknown"),
                "protocol": r.get("interfacetype"),
                "smart_status": r.get("status"),
                "health": _normalize_health(r.get("status")),
                "is_internal": None,
                "size_bytes": r.get("size"),
            }
        )
    return out


def _linux_disks() -> list[dict[str, Any]]:
    out, _, code = _run(["lsblk", "-d", "-o", "name,rota,size,model,tran"], timeout=10.0)
    if code != 0:
        return []
    drives: list[dict[str, Any]] = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 4)
        if len(parts) < 2:
            continue
        name = parts[0]
        rota = parts[1]
        drives.append(
            {
                "model": parts[3].strip() if len(parts) > 3 else name,
                "type": "hdd" if rota == "1" else "ssd",
                "protocol": parts[4].strip() if len(parts) > 4 else None,
                "smart_status": None,
                "health": "unknown",
                "is_internal": None,
                "size_bytes": parts[2] if len(parts) > 2 else None,
            }
        )
    return drives


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _wmic_multi(scope: str, klass: str, props: list[str]) -> list[dict[str, Any]]:
    """Query multiple WMIC properties, returning a list of row dicts."""
    if not IS_WIN:
        return []
    out, _, code = _run(
        ["wmic", scope, klass, "get", ",".join(props), "/value"], timeout=20.0
    )
    if code != 0:
        return []
    rows: list[dict[str, Any]] = []
    cur: dict[str, Any] = {}
    for line in out.splitlines():
        line = line.strip()
        if not line:
            if cur:
                rows.append(cur)
                cur = {}
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            cur[key.strip().lower()] = val.strip()
    if cur:
        rows.append(cur)
    return rows


def _vendor_name(raw: Any) -> str | None:
    if not raw:
        return None
    text = str(raw)
    for token in text.replace("sppci_vendor_", "").replace("spdisplays_vendor_", "").split("_"):
        if token:
            return token.capitalize()
    return text


def _metal_name(raw: Any) -> str | None:
    if not raw:
        return None
    text = str(raw)
    m = re.search(r"metal(\d+)", text, re.IGNORECASE)
    if m:
        return f"Metal {m.group(1)}"
    for token in text.split("_"):
        if token.lower().startswith("metal"):
            return token.capitalize()
    return None


def _normalize_health(raw: Any) -> str:
    if raw is None:
        return "unknown"
    text = str(raw).lower()
    if any(word in text for word in ("verified", "passed", "ok", "healthy")):
        return "good"
    if any(word in text for word in ("fail", "failing", "warning", "pred fail")):
        return "bad"
    return "unknown"


def _parse_size(raw: str) -> int | None:
    """Parse a human size like '32K' / '4M' / '1G' into bytes."""
    raw = raw.strip()
    m = re.match(r"(\d+(?:\.\d+)?)\s*([kKmMgG]?)", raw)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2).lower()
    factor = {"": 1, "k": 1024, "m": 1024**2, "g": 1024**3}[unit]
    return int(num * factor)


def _format_bytes_raw(raw: Any) -> str | None:
    if raw is None:
        return None
    try:
        num = int(str(raw).strip())
    except (ValueError, TypeError):
        return None
    if num <= 0:
        return None
    return f"{num / (1024 ** 3):.1f} GB"


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
