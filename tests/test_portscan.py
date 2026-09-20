import errno
import socket
import threading

import pytest

from portscan import PortScanner


@pytest.fixture
def banner_server():
    """A local TCP server that sends a banner to every connection."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    srv.listen(5)
    srv.settimeout(0.2)
    stop = threading.Event()

    def loop():
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                conn.sendall(b"SSH-2.0-Radar-Test\r\n")
            finally:
                conn.close()

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    yield srv.getsockname()[1]
    stop.set()
    thread.join(timeout=2)
    srv.close()


# Windows can take about two seconds to report a refused connection, so tests that
# need a port to read as "closed" use a timeout comfortably above that.
CLOSED_TIMEOUT = 3.5


def free_closed_port():
    """A port on localhost with nothing listening on it."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


# ---------- port parsing ----------

def test_parse_ports_preset():
    assert PortScanner().parse_ports("Web") == [80, 443, 8080]


def test_parse_ports_list_and_range():
    assert PortScanner().parse_ports("22, 80-82, 443") == [22, 80, 81, 82, 443]


def test_parse_ports_ignores_garbage():
    assert PortScanner().parse_ports("abc, 80, 9-x") == [80]


def test_compress_port_ranges():
    ports = [{"port": 80}, {"port": 81}, {"port": 82}, {"port": 90}]
    assert PortScanner.compress_port_ranges(ports) == ["80-82", "90"]
    assert PortScanner.compress_port_ranges([]) == []


def test_get_service_name():
    scanner = PortScanner()
    assert scanner.get_service_name(22) == "SSH"
    assert scanner.get_service_name(9999) == ""


# ---------- classification ----------

@pytest.mark.parametrize(
    "code, expected",
    [
        (0, "open"),
        (errno.ECONNREFUSED, "closed"),
        (10061, "closed"),
        (errno.ETIMEDOUT, "filtered"),
        (errno.EHOSTUNREACH, "filtered"),
        (10060, "filtered"),
        (10035, "filtered"),
    ],
)
def test_classify_connect_result(code, expected):
    assert PortScanner.classify_connect_result(code) == expected


# ---------- scanning against localhost ----------

def test_scan_detects_open_port_and_banner(banner_server):
    result = PortScanner(timeout=1.0, threads=4).scan("127.0.0.1", [banner_server])
    assert result["success"] is True
    data = result["results"]
    assert data["summary"]["total_open"] == 1
    assert data["open_ports"][0]["port"] == banner_server
    assert data["open_ports"][0]["banner"] == "SSH-2.0-Radar-Test"


def test_scan_reports_closed_port():
    result = PortScanner(timeout=CLOSED_TIMEOUT, threads=4).scan("127.0.0.1", [free_closed_port()])
    summary = result["results"]["summary"]
    assert summary["total_closed"] == 1
    assert summary["total_open"] == 0


def test_scan_sorts_results_and_mixes_states(banner_server):
    closed = free_closed_port()
    result = PortScanner(timeout=CLOSED_TIMEOUT, threads=4).scan("127.0.0.1", [banner_server, closed])
    data = result["results"]
    assert [p["port"] for p in data["open_ports"]] == [banner_server]
    assert [p["port"] for p in data["closed_ports"]] == [closed]


def test_progress_callback_reports_every_port():
    seen = []
    scanner = PortScanner(timeout=CLOSED_TIMEOUT, threads=4)
    scanner.set_progress_callback(lambda scanned, total: seen.append((scanned, total)))
    ports = [free_closed_port() for _ in range(3)]
    scanner.scan("127.0.0.1", ports)
    assert len(seen) == 3
    assert seen[-1] == (3, 3)


def test_scan_unresolvable_host(monkeypatch):
    def boom(_host):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(socket, "gethostbyname", boom)
    result = PortScanner().scan("does-not-exist.invalid", [80])
    assert result["success"] is False
    assert result["results"] is None
    assert "Could not resolve" in result["error"]
