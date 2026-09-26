import pytest

from juzi.core import network


def test_get_network_info():
    info = network.get_network_info()
    assert "interfaces" in info
    assert isinstance(info["interfaces"], list)


@pytest.mark.integration
def test_ping_localhost():
    result = network.ping(host="127.0.0.1", count=2)
    assert result.host == "127.0.0.1"
    if result.error is None:
        assert result.received >= 1
        assert result.avg_ms is not None
        assert result.avg_ms >= 0
    else:
        assert result.error


MAC_STYLE_OUTPUT = (
    "PING 223.5.5.5 (223.5.5.5): 56 data bytes\n"
    "--- 223.5.5.5 ping statistics ---\n"
    "3 packets transmitted, 3 packets received, 0.0% packet loss\n"
    "round-trip min/avg/max/stddev = 26.533/49.848/85.896/25.853 ms\n"
)

LINUX_STYLE_OUTPUT = (
    "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n"
    "64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.12 ms\n"
    "64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.11 ms\n"
    "--- 127.0.0.1 ping statistics ---\n"
    "2 packets transmitted, 2 received, 0% packet loss\n"
)


def test_ping_parses_macos_roundtrip(mocker):
    mocker.patch.object(network, "_run", return_value=(MAC_STYLE_OUTPUT, "", 0))
    r = network.ping(host="223.5.5.5", count=3)
    assert r.transmitted == 3
    assert r.received == 3
    assert r.loss_percent == 0.0
    assert r.avg_ms == 49.85
    assert r.min_ms == 26.53
    assert r.max_ms == 85.9


def test_ping_parses_linux_times(mocker):
    mocker.patch.object(network, "_run", return_value=(LINUX_STYLE_OUTPUT, "", 0))
    r = network.ping(host="127.0.0.1", count=2)
    assert r.received == 2
    assert r.avg_ms == pytest.approx(0.115, abs=0.01)
    assert r.min_ms == 0.11
    assert r.max_ms == 0.12


def test_ping_failure(mocker):
    mocker.patch.object(network, "_run", return_value=("", "timeout", 1))
    r = network.ping(host="10.255.255.1", count=2)
    assert r.error
    assert r.received == 0

