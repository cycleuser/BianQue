"""Audio helpers: test-tone synthesis and device enumeration."""

from __future__ import annotations

import wave
from typing import Any

import numpy as np

SAMPLE_RATE = 44100


def generate_tone(
    frequency: float = 440.0,
    duration: float = 1.0,
    sample_rate: int = SAMPLE_RATE,
    channels: int = 2,
    amplitude: float = 0.5,
    fade: float = 0.02,
) -> np.ndarray:
    """Synthesize a stereo sine tone with short fade in/out to avoid clicks.

    Returns a float32 array of shape ``(n_samples, channels)`` in [-1, 1].
    """
    n = int(sample_rate * duration)
    t = np.arange(n) / sample_rate
    wave_mono = amplitude * np.sin(2 * np.pi * frequency * t)
    if fade > 0:
        fade_n = int(sample_rate * fade)
        if fade_n > 0 and fade_n * 2 < n:
            env = np.ones(n, dtype=np.float64)
            env[:fade_n] = np.linspace(0.0, 1.0, fade_n)
            env[-fade_n:] = np.linspace(1.0, 0.0, fade_n)
            wave_mono = wave_mono * env
    stereo = np.stack([wave_mono] * channels, axis=1)
    return stereo.astype(np.float32)  # type: ignore[no-any-return]


def generate_sweep(
    duration: float = 2.0,
    sample_rate: int = SAMPLE_RATE,
    channels: int = 2,
    amplitude: float = 0.4,
    f0: float = 100.0,
    f1: float = 8000.0,
) -> np.ndarray:
    """Generate a log frequency sweep from ``f0`` to ``f1`` Hz."""
    n = int(sample_rate * duration)
    t = np.arange(n) / sample_rate
    phase = 2 * np.pi * f0 * duration * (np.exp(t / duration * np.log(f1 / f0)) - 1) / np.log(f1 / f0)
    mono = amplitude * np.sin(phase)
    return np.stack([mono] * channels, axis=1).astype(np.float32)  # type: ignore[no-any-return]


def _float_to_pcm16(samples: np.ndarray) -> bytes:
    pcm = np.clip(samples, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype(np.int16)
    return pcm.tobytes()


def write_wav(path: str, samples: np.ndarray, sample_rate: int = SAMPLE_RATE) -> None:
    """Write a float32 stereo sample array to a 16-bit PCM WAV file."""
    pcm = _float_to_pcm16(samples)
    channels = samples.shape[1] if samples.ndim > 1 else 1
    with wave.open(path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)


def list_audio_devices() -> dict[str, Any]:
    """Enumerate input/output devices via sounddevice (best-effort)."""
    result: dict[str, Any] = {"inputs": [], "outputs": [], "available": False}
    try:
        import sounddevice as sd  # type: ignore

        devices = sd.query_devices()
        result["available"] = True
        for idx, dev in enumerate(devices):
            entry = {
                "index": idx,
                "name": dev.get("name"),
                "channels": max(dev.get("max_input_channels", 0), dev.get("max_output_channels", 0)),
                "default_samplerate": dev.get("default_samplerate"),
            }
            if dev.get("max_input_channels", 0) > 0:
                result["inputs"].append(entry)
            if dev.get("max_output_channels", 0) > 0:
                result["outputs"].append(entry)
    except (ImportError, OSError):
        pass
    return result
