"""Report rendering (Markdown / HTML / JSON) and formatting helpers."""

from __future__ import annotations

import datetime
import html
import json

from bianque.core.models import Report, Status
from bianque.i18n import tr

_STATUS_KEY = {
    Status.PASS: "Pass",
    Status.FAIL: "Fail",
    Status.UNKNOWN: "Unknown",
    Status.SKIPPED: "Skipped",
}

_STATUS_COLOR = {
    Status.PASS: "#16a34a",
    Status.FAIL: "#dc2626",
    Status.UNKNOWN: "#d97706",
    Status.SKIPPED: "#9ca3af",
}


def _status_label(status: str) -> str:
    return tr(_STATUS_KEY.get(status, status))


def format_bytes(num: float | None) -> str:
    if num is None:
        return "N/A"
    value = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(value) < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} EB"


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def format_timestamp(epoch: float) -> str:
    return datetime.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def render_json(report: Report) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"# BianQue(扁鹊) {tr('Inspection Report')}")
    lines.append("")
    lines.append(f"- {tr('Generated at')}: {format_timestamp(report.generated_at)}")
    lines.append(f"- {tr('Host')}: {report.host}")
    lines.append(f"- {tr('Platform')}: {report.platform}")
    lines.append("")
    counts = report.count_by_status()
    lines.append(f"## {tr('Summary')}")
    lines.append("")
    lines.append(f"- {tr('Pass')}: {counts[Status.PASS]}")
    lines.append(f"- {tr('Fail')}: {counts[Status.FAIL]}")
    lines.append(f"- {tr('Unknown')}: {counts[Status.UNKNOWN]}")
    lines.append(f"- {tr('Skipped')}: {counts[Status.SKIPPED]}")
    lines.append("")
    lines.append(f"## {tr('Details')}")
    lines.append("")
    for r in report.results:
        lines.append(f"### {tr(r.name)} — {_status_label(r.status)}")
        lines.append("")
        if r.message:
            lines.append(r.message)
            lines.append("")
        if r.data:
            lines.append("```json")
            lines.append(json.dumps(r.data, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def render_html(report: Report) -> str:
    counts = report.count_by_status()
    rows = []
    for r in report.results:
        color = _STATUS_COLOR.get(r.status, "#9ca3af")
        label = _status_label(r.status)
        data_str = html.escape(json.dumps(r.data, ensure_ascii=False)) if r.data else ""
        rows.append(
            f"""
            <tr>
              <td>{html.escape(tr(r.name))}</td>
              <td><span class="badge" style="background:{color}">{label}</span></td>
              <td>{html.escape(r.message)}</td>
              <td><pre>{data_str}</pre></td>
            </tr>
            """
        )
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>BianQue {tr('Inspection Report')}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
          max-width: 1000px; margin: 2rem auto; padding: 0 1rem; color: #1f2937; }}
  h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: .5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ border: 1px solid #e5e7eb; padding: .5rem .75rem; text-align: left;
            vertical-align: top; }}
  th {{ background: #f9fafb; }}
  .badge {{ color: #fff; padding: .15rem .6rem; border-radius: 999px; font-size: .8rem; }}
  pre {{ margin: 0; font-size: .8rem; white-space: pre-wrap; word-break: break-all; }}
  .meta {{ color: #6b7280; font-size: .9rem; }}
  .summary {{ display: flex; gap: 1.5rem; margin: 1rem 0; }}
</style>
</head>
<body>
<h1>BianQue(扁鹊) {tr('Inspection Report')}</h1>
<p class="meta">
  {tr('Generated at')}: {html.escape(format_timestamp(report.generated_at))} ·
  {tr('Host')}: {html.escape(report.host)} ·
  {tr('Platform')}: {html.escape(report.platform)}
</p>
<div class="summary">
  <div>{tr('Pass')} <b style="color:#16a34a">{counts[Status.PASS]}</b></div>
  <div>{tr('Fail')} <b style="color:#dc2626">{counts[Status.FAIL]}</b></div>
  <div>{tr('Unknown')} <b style="color:#d97706">{counts[Status.UNKNOWN]}</b></div>
  <div>{tr('Skipped')} <b style="color:#9ca3af">{counts[Status.SKIPPED]}</b></div>
</div>
<table>
  <thead><tr><th>{tr('Check Item')}</th><th>{tr('Status')}</th><th>{tr('Result')}</th><th>{tr('Data')}</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</body>
</html>
"""


def save_report(report: Report, path: str) -> None:
    """Write a report file, format inferred from the extension."""
    lower = path.lower()
    if lower.endswith(".html") or lower.endswith(".htm"):
        content = render_html(report)
    elif lower.endswith(".json"):
        content = render_json(report)
    else:
        content = render_markdown(report)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
