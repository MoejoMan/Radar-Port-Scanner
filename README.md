![alt text](assets/RadarPS_LOGO.png)

# Radar Port Scanner

A **fast, modern, multi-threaded port scanner** with a sleek PyQt5 GUI. Built for security professionals, network engineers, and developers.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![License: MIT](https://img.shields.io/badge/license-MIT-purple)

> **Status:** Beta — Core scanner fully functional, GUI in active development

A fast, multi-threaded port scanner with GUI, profile management, and scheduling. Detects open, closed, and filtered ports with banner grabbing and detailed reporting.

**Note:** This tool is for educational purposes only. Do not scan networks or devices without explicit permission. Unauthorized scanning may be illegal.

## 🚀 Quick Start

### Windows Users
**Just double-click `START.bat`** - It handles everything!
- Checks for Python
- Installs dependencies
- Launches the app

### Linux/Mac Users
```bash
python launcher.py
```

Or manually:
```bash
pip install -r requirements.txt
python main.py
```

## Features

- **Multi-threaded scanning** - 200 concurrent threads for speed
- **Port detection** - Identifies open, closed, and filtered ports
- **Banner grabbing** - Service identification on open ports
- **Pre-set categories:**
  - Web (HTTP, HTTPS, HTTP-alt)
  - Database (MySQL, PostgreSQL, MSSQL)
  - Email (SMTP, POP3, IMAP)
  - Admin (SSH, RDP, VNC)
- **Custom port ranges** - Scan any range you specify
- **PyQt5 GUI** - User-friendly interface (in development)
- **Save profiles** - Store and reuse scan configurations
- **Scheduled scans** - Run scans at specific intervals (planned)
- **JSON results** - Export detailed scan data

## Requirements

- Python 3.8+

### First Time Setup (If Python isn't installed)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important:** Check "Add Python to PATH" during installation
3. Run `START.bat` (Windows) or `python launcher.py` (Linux/Mac)

### Manual Install

```bash
pip install -r requirements.txt
python main.py
```

## Project Structure

```
Port-Scanner/
├── START.bat            # Windows quick start (double-click!)
├── launcher.py          # Cross-platform launcher
├── run.bat              # Alternative Windows launcher
├── main.py              # PyQt5 GUI application
├── portscan.py          # Core scanner engine
├── profiles.py          # Profile & database management
├── Port_Scanner.ui      # GUI layout (Qt Designer)
├── requirements.txt     # Python dependencies
├── data.db              # Profile storage (auto-created)
├── assets/              # Logo and images
└── README.md            # This file
```

## Usage (Current - CLI)

```python
from portscan import PortScanner

# Create scanner
scanner = PortScanner(timeout=0.6, threads=200)

# Set progress callback (optional)
scanner.set_progress_callback(lambda scanned, total: print(f"{scanned}/{total}"))

# Run scan
results = scanner.scan(target="192.168.1.1", ports=[80, 443, 22, 3306])

# Check results
if results["success"]:
    summary = results["results"]["summary"]
    print(f"Open ports: {summary['total_open']}")
else:
    print(f"Error: {results['error']}")
```

## Planned Features

- [ ] PyQt5 GUI interface
- [ ] Save/load scan profiles
- [ ] Scheduled scans with APScheduler
- [ ] Visual dashboard with charts
- [ ] Scan history and comparisons

## DISCLAIMER

This tool is for educational purposes only. Do not scan networks or devices without explicit permission. Unauthorized scanning may be illegal. The author assumes no liability for misuse.
