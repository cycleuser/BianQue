from juzi.core import stress


def test_run_cpu_stress_completes():
    result = stress.run_cpu_stress(duration=1.0, threads=2)
    assert result.threads == 2
    assert result.completed is True
    assert result.duration >= 0.9
    assert 0.0 <= result.avg_usage <= 100.0
    assert 0.0 <= result.peak_usage <= 100.0


def test_run_cpu_stress_threads_clamped():
    result = stress.run_cpu_stress(duration=0.5, threads=-3)
    assert result.threads >= 1
