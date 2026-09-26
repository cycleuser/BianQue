"""CPU stress / burn-in workload for thermal inspection.

The workload is CPU-bound and multi-threaded; NumPy matrix products release
the GIL so all cores can be saturated. Progress and frequency are sampled with
``psutil`` so we can detect throttling under load.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import psutil


@dataclass
class StressResult:
    duration: float
    threads: int
    avg_usage: float
    peak_usage: float
    freq_before_mhz: float | None
    freq_after_mhz: float | None
    freq_min_mhz: float | None
    freq_max_mhz: float | None
    completed: bool
    usage_samples: list[float] = field(default_factory=list)
    freq_samples: list[float] = field(default_factory=list)


def _cpu_worker(stop_event: threading.Event) -> None:
    """One CPU-saturating worker thread."""
    try:
        import numpy as np

        size = 384
        a = np.random.rand(size, size)
        b = np.random.rand(size, size)
        while not stop_event.is_set():
            c = a @ b
            a = (c + 0.0001) % 1.0
    except ImportError:
        # Fallback: pure-Python float churn (single-core under the GIL).
        x = 0.0
        while not stop_event.is_set():
            x = (x * 1.0000001 + 1.0) % 1e9


def _current_freq() -> float | None:
    try:
        freq = psutil.cpu_freq()
        return freq.current if freq is not None else None
    except (NotImplementedError, FileNotFoundError, OSError):
        return None


def run_cpu_stress(
    duration: float = 10.0,
    threads: int | None = None,
    on_progress: Callable[[float, float], None] | None = None,
    stop_event: threading.Event | None = None,
) -> StressResult:
    """Run a CPU stress workload for ``duration`` seconds.

    Args:
        duration: Target runtime in seconds.
        threads: Worker thread count; defaults to logical core count.
        on_progress: Optional callback ``(fraction, cpu_percent)``.
        stop_event: Optional external cancellation event.

    Returns:
        :class:`StressResult` with usage/frequency statistics.
    """
    threads = threads or psutil.cpu_count(logical=True) or 4
    threads = max(1, int(threads))

    freq_before = _current_freq()
    worker_stop = threading.Event()
    workers = [
        threading.Thread(target=_cpu_worker, args=(worker_stop,), daemon=True)
        for _ in range(threads)
    ]
    for w in workers:
        w.start()

    usages: list[float] = []
    freqs: list[float] = []
    start = time.time()
    elapsed = 0.0
    while elapsed < duration:
        if stop_event is not None and stop_event.is_set():
            break
        usage = psutil.cpu_percent(interval=None)
        freq = _current_freq()
        usages.append(usage)
        if freq is not None:
            freqs.append(freq)
        if on_progress is not None:
            on_progress(min(elapsed / duration, 1.0), usage)
        time.sleep(1.0)
        elapsed = time.time() - start

    worker_stop.set()
    for w in workers:
        w.join(timeout=2.0)

    completed = elapsed >= duration
    avg_usage = sum(usages) / len(usages) if usages else 0.0
    peak_usage = max(usages) if usages else 0.0
    freq_after = _current_freq()
    freq_min = min(freqs) if freqs else None
    freq_max = max(freqs) if freqs else None

    return StressResult(
        duration=elapsed,
        threads=threads,
        avg_usage=avg_usage,
        peak_usage=peak_usage,
        freq_before_mhz=freq_before,
        freq_after_mhz=freq_after,
        freq_min_mhz=freq_min,
        freq_max_mhz=freq_max,
        completed=completed,
        usage_samples=usages,
        freq_samples=freqs,
    )
