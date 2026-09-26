"""Memory information: capacity, modules, speed/timing, channels, bandwidth."""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass
from typing import Any

import psutil

from bianque.core.system import _run, _system_profiler_json

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

_DDR_TYPE_MAP = {
    20: "DDR", 21: "DDR2", 24: "DDR3", 26: "DDR4", 34: "DDR5",
}


@dataclass
class MemoryTestResult:
    size_mb: float
    ok: bool
    write_speed_mbps: float
    read_speed_mbps: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "size_mb": self.size_mb,
            "ok": self.ok,
            "write_speed_mbps": self.write_speed_mbps,
            "read_speed_mbps": self.read_speed_mbps,
            "error": self.error,
        }


def get_memory_details() -> dict[str, Any]:
    """Virtual memory plus per-module DIMM details where available."""
    vm = psutil.virtual_memory()
    info: dict[str, Any] = {
        "total_bytes": vm.total,
        "available_bytes": vm.available,
        "percent": vm.percent,
        "modules": [],
        "channels": None,
        "bandwidth_gbps": None,
    }

    if IS_MAC:
        info.update(_mac_memory())
    elif IS_WIN:
        info.update(_win_memory())
    else:
        info.update(_linux_memory())

    modules = info.get("modules") or []
    channels = info.get("channels")
    if channels and modules:
        speed = modules[0].get("speed_mhz")
        if speed:
            # DDR 64-bit per channel -> bytes/s = channels * MT/s * 8
            info["bandwidth_gbps"] = round(channels * speed * 8 / 1000, 1)
    return info


def run_memory_self_test(size_mb: float = 256.0) -> MemoryTestResult:
    """Allocate ``size_mb``, write a pattern, then read-verify it."""
    size = int(size_mb * 1024 * 1024)
    pattern = bytes((0x5A, 0xA5, 0x3C, 0xC3)) * (1024 * 1024 // 4)
    try:
        buf = bytearray(size)
    except (MemoryError, OverflowError) as exc:
        return MemoryTestResult(size_mb=size_mb, ok=False, write_speed_mbps=0.0, read_speed_mbps=0.0, error=str(exc))

    start = time.perf_counter()
    for i in range(0, size, len(pattern)):
        buf[i : i + len(pattern)] = pattern
    write_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    ok = True
    for i in range(0, size, len(pattern)):
        if buf[i : i + len(pattern)] != pattern:
            ok = False
            break
    read_elapsed = time.perf_counter() - start

    write_mbps = (size / 1024 / 1024) / write_elapsed if write_elapsed else 0.0
    read_mbps = (size / 1024 / 1024) / read_elapsed if read_elapsed else 0.0
    return MemoryTestResult(
        size_mb=size_mb,
        ok=ok,
        write_speed_mbps=round(write_mbps, 2),
        read_speed_mbps=round(read_mbps, 2),
    )


# --------------------------------------------------------------------------- #
# Platform helpers
# --------------------------------------------------------------------------- #

def _mac_memory() -> dict[str, Any]:
    """macOS: manufacturer/type/capacity from system_profiler.

    Apple Silicon exposes no per-module speed/timing/channel, so those stay
    ``None`` (the OS does not report them).
    """
    mem = _system_profiler_json("SPMemoryDataType")
    items = mem.get("SPMemoryDataType") or []
    modules: list[dict[str, Any]] = []
    for i, item in enumerate(items, start=1):
        capacity = item.get("SPMemoryDataType") or item.get("dimm_size")
        modules.append(
            {
                "slot": f"DIMM {i}",
                "manufacturer": item.get("dimm_manufacturer"),
                "type": item.get("dimm_type"),
                "capacity": capacity,
                "speed_mhz": None,
                "timing": None,
                "part_number": item.get("dimm_part_number"),
                "serial": item.get("dimm_serial_number"),
            }
        )
    return {"modules": modules, "channels": None}


def _win_memory() -> dict[str, Any]:
    """Windows: full DIMM details from ``wmic memorychip``."""
    out, _, code = _run(
        [
            "wmic", "memorychip", "get",
            "BankLabel,DeviceLocator,Manufacturer,Capacity,Speed,PartNumber,"
            "SerialNumber,SMBIOSMemoryType,ConfiguredClockSpeed", "/value",
        ],
        timeout=20.0,
    )
    if code != 0:
        return {"modules": [], "channels": None}

    raw: dict[str, list[str]] = {}
    for line in out.splitlines():
        line = line.strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        raw.setdefault(key.strip().lower(), []).append(val.strip())

    def col(name: str, idx: int) -> Any:
        vals = raw.get(name.lower(), [])
        return vals[idx] if idx < len(vals) else None

    count = len(raw.get("banklabel", [])) or len(raw.get("capacity", []))
    modules: list[dict[str, Any]] = []
    for i in range(count):
        speed = _to_int(col("speed", i))
        type_code = _to_int(col("smbiosmemorytype", i))
        modules.append(
            {
                "slot": f"{col('banklabel', i)} {col('devicelocator', i)}".strip() or f"DIMM {i + 1}",
                "manufacturer": col("manufacturer", i),
                "type": _DDR_TYPE_MAP.get(type_code) if type_code else None,
                "capacity": _bytes_to_gb(col("capacity", i)),
                "speed_mhz": speed,
                "timing": None,
                "part_number": col("partnumber", i),
                "serial": col("serialnumber", i),
            }
        )
    channels = count if count else None
    return {"modules": modules, "channels": channels}


def _linux_memory() -> dict[str, Any]:
    """Linux: DIMM details from ``dmidecode -t memory`` (best-effort, may need root)."""
    out, _, code = _run(["dmidecode", "-t", "memory"], timeout=15.0)
    if code != 0 or not out.strip():
        return {"modules": [], "channels": None}

    modules: list[dict[str, Any]] = []
    cur: dict[str, Any] = {}
    for line in out.splitlines():
        stripped = line.strip()
        if not stripped:
            if cur:
                modules.append(cur)
                cur = {}
            continue
        key, _, val = stripped.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "size" and val and val not in ("no module installed", "unknown"):
            if not cur.get("slot"):
                cur["slot"] = "DIMM"
            cur["capacity"] = val
        elif key == "type" and val and val not in ("unknown",):
            cur["type"] = val
        elif key == "speed" and val and "unknown" not in val:
            cur["speed_mhz"] = _first_int(val)
        elif key == "manufacturer" and val not in ("unknown", "not specified"):
            cur["manufacturer"] = val
        elif key == "part number" and val not in ("unknown", "not specified", "[empty]"):
            cur["part_number"] = val
        elif key == "serial number" and val not in ("unknown", "not specified", "[empty]"):
            cur["serial"] = val
        elif key == "locator" and val not in ("unknown",):
            cur["slot"] = val
    if cur:
        modules.append(cur)

    channels = len([m for m in modules if m.get("capacity")]) or None
    return {"modules": modules, "channels": channels}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def _first_int(text: str) -> int | None:
    m = re.search(r"\d+", text)
    return int(m.group(0)) if m else None


def _bytes_to_gb(value: Any) -> str | None:
    num = _to_int(value)
    if num is None:
        return None
    return f"{num / (1024 ** 3):.0f} GB"
