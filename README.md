# BianQue (扁鹊) · Cross-Platform Hardware Inspection

> 望闻问切 — a full checkup for your hardware.

**BianQue** is a pure-Python hardware inspection & burn-in workflow. Run a new
machine end-to-end — screen, camera, microphone, speaker, keyboard, mouse,
thermal, battery, disk, memory, network — and export an archivable report.

Named after Bian Que, the legendary physician of the Warring States period, whose
four diagnostic methods (望闻问切 — observe, listen, inquire, palpate) map neatly
onto hardware inspection: observe (screen, camera), listen (speaker, microphone),
inquire (hardware info), palpate (thermal stress).

## Features

| Check | Detail |
|-------|--------|
| Overview | CPU / memory / disk / GPU / board auto-discovery |
| Screen | resolution · refresh · DPI + full-screen 6-colour dead-pixel test (drifting hint) |
| Camera | live preview + snapshot capture |
| Microphone | live level meter + record/playback |
| Speaker | independent L/R channel + frequency sweep |
| Keyboard | full-key test incl. Tab (virtual keyboard lights up) |
| Mouse | left/middle/right, wheel, movement |
| Thermal | CPU stress + frequency / temperature / throttling watch |
| Battery | charge, cycle count, health |
| Disk | SSD/HDD detection + SMART health + sequential benchmark |
| Memory | per-module timing/channel/bandwidth + write/read self-test |
| Network | interfaces + ICMP latency / packet loss |
| Report | export HTML / Markdown / JSON |

### Deep hardware collection

- **CPU**: physical/logical cores, per-core usage, L1/L2/L3 cache, Apple Silicon P/E core split
- **Memory**: per-module manufacturer/type/capacity/speed(timing)/part number, channel count, theoretical bandwidth
- **GPU**: chip model, vendor, VRAM, core count, supported graphics APIs (e.g. Metal 4)
- **Disk**: SSD/HDD detection, protocol (NVMe/SATA/USB), SMART health status

### i18n

Full UI translation in **10 languages**, switched live from the menu bar:

简体中文 · English · 日本語 · Français · Русский · Deutsch · Português · Español · 한국어 · Italiano

## Install

```bash
pip install -e .
```

Requires Python ≥ 3.10. Dependencies: PySide6, psutil, numpy, sounddevice.

## Usage

```bash
bianque          # launch the GUI
bianque-gui      # same (GUI script)
```

Work through the left navigation; every page has explicit start/confirm
buttons and results aggregate into the status bar. Export from the "Report"
page.

## Platform Support

| Capability | macOS | Windows | Linux |
|------------|-------|---------|-------|
| Screen / camera / keyboard / mouse | ✅ | ✅ | ✅ |
| CPU / memory / disk info | ✅ | ✅ | ✅ |
| Disk / memory benchmark | ✅ | ✅ | ✅ |
| Battery cycles / health | ✅ (`system_profiler`) | ✅ (`wmic`) | ✅ (`upower`) |
| CPU temperature / fan speed | ⚠️ needs SMC | ✅ (WMI) | ✅ (`psutil`) |

On macOS, temperature/fan reads are restricted by the OS; BianQue degrades
gracefully and judges thermals from frequency/usage during the stress test.

## Development

```bash
pip install -e ".[dev]"
pytest                # all tests
ruff check .          # lint
mypy bianque             # type check
```

## License

[GPL-3.0-or-later](LICENSE)
