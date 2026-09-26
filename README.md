# JuZi (巨子) · Cross-Platform Hardware Inspection

> 鲁班造器，巨子验器 — "Lu Ban builds tools; JuZi inspects them."

**JuZi** is a pure-Python hardware inspection & burn-in workflow. Run a new
machine end-to-end — screen, camera, microphone, speaker, keyboard, mouse,
thermal, battery, disk, memory, network — and export an archivable report.

Named after the Mohist "JuZi" (chief of the Mohists): if Lu Ban was the master
craftsman, the JuZi was the master *inspector*.

## Features

| Check | Detail |
|-------|--------|
| Overview | CPU / memory / disk / GPU / board auto-discovery |
| Screen | resolution · refresh · DPI + full-screen 6-colour dead-pixel test |
| Camera | live preview + snapshot capture |
| Microphone | live level meter + record/playback |
| Speaker | independent L/R channel + frequency sweep |
| Keyboard | full-key test (virtual keyboard lights up) |
| Mouse | left/middle/right, wheel, movement |
| Thermal | CPU stress + frequency / temperature / throttling watch |
| Battery | charge, cycle count, health |
| Disk | partitions + sequential read/write benchmark |
| Memory | capacity/speed info + write/read self-test |
| Network | interfaces + ICMP latency / packet loss |
| Report | export HTML / Markdown / JSON |

## Install

```bash
pip install -e .
```

Requires Python ≥ 3.10. Dependencies: PySide6, psutil, numpy, sounddevice.

## Usage

```bash
juzi          # launch the GUI
juzi-gui      # same (GUI script)
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

On macOS, temperature/fan reads are restricted by the OS; JuZi degrades
gracefully and judges thermals from frequency/usage during the stress test.

## Development

```bash
pip install -e ".[dev]"
pytest                # all tests
ruff check .          # lint
mypy juzi             # type check
```

## License

[GPL-3.0-or-later](LICENSE)
