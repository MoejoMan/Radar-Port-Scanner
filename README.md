![Radar Port Scanner](assets/RadarPS_LOGO.png)

# Radar Port Scanner

[![Tests](https://github.com/MoejoMan/Radar-Port-Scanner/actions/workflows/tests.yml/badge.svg)](https://github.com/MoejoMan/Radar-Port-Scanner/actions/workflows/tests.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![License: MIT](https://img.shields.io/badge/license-MIT-purple)

A multi threaded TCP port scanner in Python with a PyQt5 GUI. It separates open, closed, and filtered ports, grabs service banners from open ports, and can save scan configurations as profiles.

> **Status:** Beta. The scanner engine is tested. The GUI is still in active development.

**Use it only on systems you own or have written permission to test.** Unauthorised scanning may be illegal.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

On Windows you can also double click `START.bat`.

## What works today

- **Multi threaded scanning.** A thread pool, 200 workers by default, with a progress callback.
- **Open, closed, and filtered detection.** A completed handshake is open, an active refusal is closed, and no usable reply (timeout, unreachable) is filtered. The same rules apply on Linux, macOS, and Windows. Windows can take about two seconds to report a refused connection, so from Windows use a timeout of 3 seconds or more if you need closed and filtered told apart.
- **Banner grabbing** on open ports, with UTF 8 and Latin 1 decoding.
- **Port input.** Presets (web, database, email, admin) or custom lists and ranges such as `22, 80-90, 443`.
- **Profiles.** A SQLite backed profile manager to save, load, list, and delete scan configurations.
- **PyQt5 GUI** with start, cancel, live progress, and a results view.
- **Structured results.** `scan()` returns a plain dictionary that is easy to serialise, for example with `json.dumps`.

## Use the engine from Python

```python
from portscan import PortScanner

scanner = PortScanner(timeout=0.6, threads=200)
scanner.set_progress_callback(lambda scanned, total: print(f"{scanned}/{total}"))

ports = scanner.parse_ports("22, 80, 443, 3306")
result = scanner.scan("192.168.1.1", ports)

if result["success"]:
    summary = result["results"]["summary"]
    print(f"Open: {summary['total_open']}  Closed: {summary['total_closed']}  Filtered: {summary['total_filtered']}")
else:
    print(f"Error: {result['error']}")
```

## Testing

```bash
pip install pytest
python -m pytest -q
```

The tests cover port parsing, range compression, the open, closed, and filtered classification, banner grabbing, progress reporting, and error handling. Scan tests run against sockets opened on `127.0.0.1`, so they never touch the network. GitHub Actions runs them on Ubuntu and Windows for every push to `main` and every pull request.

## Project structure

```
Radar-Port-Scanner/
  main.py             PyQt5 GUI application
  portscan.py         Scanner engine
  profiles.py         Profile storage (SQLite)
  Port_Scanner.ui     GUI layout (Qt Designer)
  START.bat           Windows launcher
  requirements.txt    Python dependencies
  tests/              Test suite
  assets/             Logo and images
```

## Not built yet

- Scheduled scans
- JSON export from the GUI
- Charts and a visual dashboard
- Scan history and comparisons

## Disclaimer

This tool is for educational purposes only. The author accepts no liability for misuse.

## License

MIT, see [LICENSE](LICENSE).
