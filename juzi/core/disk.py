"""Disk information and sequential read/write benchmark."""

from __future__ import annotations

import os
import tempfile
import time
from dataclasses import dataclass

from juzi.core import system

BLOCK_SIZE = 1024 * 1024  # 1 MiB


@dataclass
class DiskResult:
    path: str
    size_mb: float
    write_speed_mbps: float
    read_speed_mbps: float
    error: str | None = None

    def to_dict(self) -> dict[str, float | str | None]:
        return {
            "path": self.path,
            "size_mb": self.size_mb,
            "write_speed_mbps": self.write_speed_mbps,
            "read_speed_mbps": self.read_speed_mbps,
            "error": self.error,
        }


def get_disk_info() -> list[dict]:
    return system.get_disk_partitions()


def run_disk_benchmark(
    path: str | None = None,
    size_mb: float = 128.0,
    block_size: int = BLOCK_SIZE,
) -> DiskResult:
    """Measure sequential write/read throughput on a temporary file.

    The file is created under ``path`` (or the system temp dir), written once,
    fsync'd, read back, then removed. Returns :class:`DiskResult`.
    """
    if path is None:
        path = tempfile.gettempdir()
    path = os.path.abspath(path)

    try:
        os.makedirs(path, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix="juzi_bench_", dir=path)
        os.close(fd)

        total_bytes = int(size_mb * 1024 * 1024)
        block = os.urandom(block_size)

        # --- write ---
        start = time.perf_counter()
        with open(tmp, "wb") as fh:
            remaining = total_bytes
            while remaining > 0:
                chunk = block if remaining >= block_size else block[:remaining]
                fh.write(chunk)
                remaining -= len(chunk)
            fh.flush()
            os.fsync(fh.fileno())
        write_elapsed = time.perf_counter() - start

        # --- read ---
        start = time.perf_counter()
        with open(tmp, "rb") as fh:
            while fh.read(block_size):
                pass
        read_elapsed = time.perf_counter() - start

        write_mbps = (total_bytes / 1024 / 1024) / write_elapsed if write_elapsed else 0.0
        read_mbps = (total_bytes / 1024 / 1024) / read_elapsed if read_elapsed else 0.0

        return DiskResult(
            path=path,
            size_mb=size_mb,
            write_speed_mbps=round(write_mbps, 2),
            read_speed_mbps=round(read_mbps, 2),
        )
    except OSError as exc:
        return DiskResult(path=path, size_mb=size_mb, write_speed_mbps=0.0, read_speed_mbps=0.0, error=str(exc))
    finally:
        try:
            if "tmp" in locals():
                os.remove(tmp)
        except OSError:
            pass
