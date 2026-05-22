"""Cross-platform WiFi scanner. Uses OS-native tools — no injection / no attacks."""
from __future__ import annotations
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, asdict


@dataclass
class WifiNetwork:
    ssid: str
    bssid: str
    signal: int        # dBm or percent depending on OS
    security: str
    channel: str
    frequency: str

    def dict(self): return asdict(self)


def scan() -> list[WifiNetwork]:
    sysname = platform.system()
    try:
        if sysname == "Windows":
            return _scan_windows()
        if sysname == "Darwin":
            return _scan_macos()
        return _scan_linux()
    except Exception:
        return []


# ---------- Windows (netsh) ----------
def _scan_windows() -> list[WifiNetwork]:
    out = subprocess.check_output(
        ["netsh", "wlan", "show", "networks", "mode=bssid"],
        text=True, errors="ignore", timeout=15,
    )
    nets, cur, bssid = [], {}, {}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("SSID ") and "BSSID" not in s:
            if cur and bssid:
                nets.append(_mk(cur, bssid))
            cur = {"ssid": s.split(":", 1)[1].strip() or "<hidden>"}
            bssid = {}
        elif s.startswith("Authentication"):
            cur["security"] = s.split(":", 1)[1].strip()
        elif s.startswith("BSSID"):
            bssid["bssid"] = s.split(":", 1)[1].strip()
        elif s.startswith("Signal"):
            bssid["signal"] = int(re.sub(r"[^\d]", "", s.split(":", 1)[1]) or 0)
        elif s.startswith("Channel"):
            bssid["channel"] = s.split(":", 1)[1].strip()
        elif s.startswith("Radio type") or s.startswith("Band"):
            bssid.setdefault("frequency", s.split(":", 1)[1].strip())
    if cur and bssid:
        nets.append(_mk(cur, bssid))
    return nets


def _mk(cur, bssid):
    return WifiNetwork(
        ssid=cur.get("ssid", ""),
        bssid=bssid.get("bssid", ""),
        signal=bssid.get("signal", 0),
        security=cur.get("security", "Unknown"),
        channel=bssid.get("channel", ""),
        frequency=bssid.get("frequency", ""),
    )


# ---------- Linux (nmcli) ----------
def _scan_linux() -> list[WifiNetwork]:
    if not shutil.which("nmcli"):
        return []
    out = subprocess.check_output(
        ["nmcli", "-t", "-f",
         "SSID,BSSID,SIGNAL,SECURITY,CHAN,FREQ", "device", "wifi", "list"],
        text=True, errors="ignore", timeout=15,
    )
    nets = []
    for line in out.splitlines():
        # nmcli -t uses ':' as separator; BSSID also contains ':' so split carefully
        parts = re.split(r'(?<!\\):', line)
        parts = [p.replace("\\:", ":") for p in parts]
        if len(parts) < 6:
            continue
        ssid, bssid, signal, sec, ch, freq = parts[:6]
        nets.append(WifiNetwork(
            ssid=ssid or "<hidden>", bssid=bssid,
            signal=int(signal or 0), security=sec or "Open",
            channel=ch, frequency=freq,
        ))
    return nets


# ---------- macOS (airport) ----------
def _scan_macos() -> list[WifiNetwork]:
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    if not shutil.which(airport) and not subprocess.os.path.exists(airport):
        return []
    out = subprocess.check_output([airport, "-s"], text=True, timeout=15)
    lines = out.splitlines()[1:]
    nets = []
    for ln in lines:
        m = re.match(r"\s*(.+?)\s+([0-9a-f:]{17})\s+(-?\d+)\s+(\S+)\s+\S+\s+(\S+)", ln)
        if m:
            ssid, bssid, sig, ch, sec = m.groups()
            nets.append(WifiNetwork(
                ssid=ssid, bssid=bssid, signal=int(sig),
                security=sec, channel=ch, frequency=""))
    return nets
