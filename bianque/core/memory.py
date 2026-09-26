"""Memory information and a write/read self-test."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Any

import psutil

from bianque.core.system import _run, _system_profiler_json

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"


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
    """Virtual memory plus physical DIMM details where available."""
    vm = psutil.virtual_memory()
    info: dict[str, Any] = {
        "total_bytes": vm.total,
        "available_bytes": vm.available,
        "percent": vm.percent,
        "dimm_count": None,
        "dimm_speed": None,
        "dimm_type": None,
    }
    if IS_MAC:
        info.update(_mac_dimm())
    elif IS_WIN:
        info["dimm_speed"] = _win_dimm_speed()
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


def _mac_dimm() -> dict[str, Any]:
    mem = _system_profiler_json("SPMemoryDataType")
    items = mem.get("SPMemoryDataType") or []
    if not items:
        return {}
    i0 = items[0]
    return {
        "dimm_count": i0.get("dimm_number") or i0.get("dimm_manufacturer"),
        "dimm_speed": i0.get("dimm_speed"),
        "dimm_type": i0.get("dimm_type"),
    }


def _win_dimm_speed() -> Any:
    out, _, code = _run(
        ["wmic", "memorychip", "get", "Speed,Capacity,Manufacturer", "/value"],
        timeout=20.0,
    )
    if code != 0:
        return None
    speeds = []
    for line in out.splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            if key.strip().lower() == "speed" and val.strip().isdigit():
                speeds.append(val.strip())
    return speeds[0] if speeds else None
