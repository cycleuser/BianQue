import os
import wave

import numpy as np

from juzi.core import audio


def test_generate_tone_shape_and_range():
    tone = audio.generate_tone(frequency=440, duration=0.1, channels=2)
    assert tone.shape[1] == 2
    assert tone.shape[0] == int(0.1 * audio.SAMPLE_RATE)
    assert float(np.max(np.abs(tone))) <= 1.0
    assert tone.dtype == np.float32


def test_generate_sweep_shape():
    sweep = audio.generate_sweep(duration=0.1, channels=1)
    assert sweep.shape[1] == 1
    assert sweep.shape[0] == int(0.1 * audio.SAMPLE_RATE)


def test_write_wav(tmp_path):
    path = str(tmp_path / "tone.wav")
    tone = audio.generate_tone(frequency=440, duration=0.05, channels=2)
    audio.write_wav(path, tone)
    assert os.path.exists(path)
    with wave.open(path, "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == audio.SAMPLE_RATE


def test_list_audio_devices_structure():
    info = audio.list_audio_devices()
    assert "inputs" in info
    assert "outputs" in info
    assert "available" in info
