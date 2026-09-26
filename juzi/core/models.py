"""Shared data models for JuZi checks and reports."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class Status:
    """Unified check result status."""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    SKIPPED = "skipped"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.PASS, cls.FAIL, cls.UNKNOWN, cls.SKIPPED]


@dataclass
class CheckResult:
    """A single check item result.

    Attributes:
        key: Stable identifier such as ``screen.dead_pixel``.
        name: Human-readable display name.
        status: One of :class:`Status`.
        message: Human-readable outcome summary.
        data: Structured payload (metrics, raw numbers).
        timestamp: Epoch seconds when the check was produced.
    """

    key: str
    name: str
    status: str = Status.UNKNOWN
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> CheckResult:
        return cls(
            key=str(raw.get("key", "")),
            name=str(raw.get("name", "")),
            status=str(raw.get("status", Status.UNKNOWN)),
            message=str(raw.get("message", "")),
            data=dict(raw.get("data", {})),
            timestamp=float(raw.get("timestamp", time.time())),
        )


@dataclass
class Report:
    """Aggregated inspection report."""

    results: list[CheckResult] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)
    host: str = ""
    platform: str = ""

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    def count_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = dict.fromkeys(Status.all(), 0)
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "host": self.host,
            "platform": self.platform,
            "results": [r.to_dict() for r in self.results],
        }
