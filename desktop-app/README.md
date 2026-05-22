# NetSentinel — WiFi & Network Security Analyzer

A modern, Kali-inspired cybersecurity dashboard for **authorized** network
auditing, personal WiFi monitoring, and educational labs.

> ⚠️ **Legal notice**
> This tool is for **defensive** auditing only. It does **not** crack
> passwords, send deauth frames, perform DDoS, or attempt unauthorized
> access. Use only on networks you own or have written permission to test.

---

## Features

| Module | What it does |
|---|---|
| **WiFi Scanner** | Lists nearby SSIDs with signal, security, channel, BSSID |
| **Network Analyzer** | ARP-sweeps your LAN and fingerprints devices (IP / MAC / vendor / hostname / OS guess) |
| **Security Audit** | Flags open / WEP / WPA networks and gives hardening tips |
| **Password Strength** | Local entropy + dictionary check, crack-time estimate |
| **Internet Testing** | Speedtest, ping, DNS, latency, packet-loss |
| **Realtime Monitor** | Live bandwidth + live packet stats (animated) |
| **Reports** | PDF export, SQLite scan history, device whitelist, alerts |

UI: dark Kali-style dashboard, neon-blue accents, glassmorphism cards,
animated pyqtgraph charts, sidebar navigation.

---

## Quick start

```bash
cd desktop-app
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m netsentinel
```

> On Windows, run the terminal **as Administrator** for full WiFi scan and
> ARP results. On Linux, you may need `sudo` (or grant `cap_net_raw` to
> Python) for Scapy ARP sweeps.

---

## Build a Windows .exe

```bash
pip install pyinstaller
python build_exe.py
```

Output: `dist/NetSentinel.exe` (one-file, no console window).

### Size & startup optimizations applied

The `build_exe.py` script:

- uses `--onefile --windowed --noupx-friendly` flags
- excludes heavy unused modules (`tkinter`, `unittest`, `pydoc`, `test`,
  `email.test`, `distutils`, `setuptools`, `pip`, `wheel`)
- strips debug symbols
- enables UPX compression if `upx` is on PATH
- pre-imports only what the UI needs to keep cold-start fast
- splash screen via PyInstaller `--splash` so users get instant feedback

Typical result: ~45–55 MB single-file exe, ~1.5 s cold start on Win11.

---

## Project layout

```
desktop-app/
├── netsentinel/
│   ├── __main__.py            # entrypoint
│   ├── app.py                 # QApplication + MainWindow
│   ├── theme.py               # Kali-style QSS dark theme
│   ├── db.py                  # SQLite persistence
│   ├── widgets/
│   │   ├── sidebar.py
│   │   ├── glass_card.py
│   │   ├── toast.py
│   │   ├── status_dot.py
│   │   └── animated_chart.py
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── wifi_scanner.py
│   │   ├── network_analyzer.py
│   │   ├── security_audit.py
│   │   ├── password_checker.py
│   │   ├── internet_test.py
│   │   ├── realtime_monitor.py
│   │   └── reports.py
│   └── core/
│       ├── wifi.py            # WiFi scanning (Win/Linux/macOS)
│       ├── lan.py             # ARP sweep + fingerprinting
│       ├── audit.py           # security scoring + recommendations
│       ├── password.py        # entropy + dictionary check
│       ├── speed.py           # speedtest / ping / DNS
│       ├── monitor.py         # psutil bandwidth + scapy packet stats
│       ├── pdf_report.py      # ReportLab PDF export
│       └── common_passwords.txt
├── requirements.txt
├── build_exe.py
└── README.md
```
