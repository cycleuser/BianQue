"""Network interface information and ICMP latency probing."""

from __future__ import annotations

import re
import socket
import sys
from dataclasses import dataclass, field
from typing import Any

import psutil

from bianque.core.system import _run

IS_WIN = sys.platform == "win32"

_TIME_RE = re.compile(r"time[=<]\s*([0-9.]+)\s*ms", re.IGNORECASE)
_TRANSMITTED_RE = re.compile(r"(\d+)\s+packets?\s+transmitted", re.IGNORECASE)
_RECEIVED_RE = re.compile(r"(\d+)\s+packets?\s+received", re.IGNORECASE)
_LOSS_RE = re.compile(r"([0-9.]+)%\s+packet\s+loss", re.IGNORECASE)
_ROUNDTRIP_RE = re.compile(
    r"round-trip[^=]*=\s*([0-9.]+)/([0-9.]+)/([0-9.]+)", re.IGNORECASE
)


@dataclass
class PingResult:
    host: str
    transmitted: int = 0
    received: int = 0
    loss_percent: float = 0.0
    min_ms: float | None = None
    avg_ms: float | None = None
    max_ms: float | None = None
    error: str | None = None
    times_ms: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "transmitted": self.transmitted,
            "received": self.received,
            "loss_percent": self.loss_percent,
            "min_ms": self.min_ms,
            "avg_ms": self.avg_ms,
            "max_ms": self.max_ms,
            "error": self.error,
        }


def get_network_info() -> dict[str, Any]:
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    counters = psutil.net_io_counters(pernic=True)

    interfaces = []
    for name, addr_list in addrs.items():
        ips = [a.address for a in addr_list if a.family == socket.AF_INET]
        macs = [
            a.address
            for a in addr_list
            if a.family not in (socket.AF_INET, socket.AF_INET6)
        ]
        stat = stats.get(name)
        counter = counters.get(name)
        interfaces.append(
            {
                "name": name,
                "ips": ips,
                "mac": macs[0] if macs else None,
                "up": stat.isup if stat else None,
                "speed_mbps": stat.speed if stat else None,
                "bytes_sent": counter.bytes_sent if counter else None,
                "bytes_recv": counter.bytes_recv if counter else None,
            }
        )
    return {"interfaces": interfaces}


def ping(host: str = "8.8.8.8", count: int = 4, timeout: float = 10.0) -> PingResult:
    """Ping ``host`` ``count`` times and parse round-trip latency."""
    if IS_WIN:
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout * 1000)), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout)), host]
    out, err, code = _run(cmd, timeout=timeout + 5.0)
    result = PingResult(host=host)

    if code != 0:
        result.error = (err or out).strip()[:200] or "ping failed"
        return result

    times = [float(m) for m in _TIME_RE.findall(out)]
    result.times_ms = times

    transmitted = _extract_int(_TRANSMITTED_RE, out, count)
    received = _extract_int(_RECEIVED_RE, out, len(times))
    loss = _extract_float(_LOSS_RE, out, None)
    result.transmitted = transmitted
    result.received = received
    if loss is not None:
        result.loss_percent = loss
    elif transmitted > 0:
        result.loss_percent = round((transmitted - received) / transmitted * 100, 1)

    if times:
        result.min_ms = round(min(times), 2)
        result.avg_ms = round(sum(times) / len(times), 2)
        result.max_ms = round(max(times), 2)
    else:
        m = _ROUNDTRIP_RE.search(out)
        if m:
            result.min_ms = round(float(m.group(1)), 2)
            result.avg_ms = round(float(m.group(2)), 2)
            result.max_ms = round(float(m.group(3)), 2)
    return result


def _extract_int(pattern: re.Pattern[str], text: str, default: int) -> int:
    m = pattern.search(text)
    return int(m.group(1)) if m else default


def _extract_float(pattern: re.Pattern[str], text: str, default: float | None) -> float | None:
    m = pattern.search(text)
    return float(m.group(1)) if m else default
