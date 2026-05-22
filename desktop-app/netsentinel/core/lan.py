"""LAN discovery + lightweight device fingerprinting.

Uses Scapy ARP sweep when available, falls back to system `arp -a`.
Fingerprinting is *passive*: vendor lookup (OUI), TTL-based OS guess via a
single ping, and reverse-DNS hostname. No exploitation, no port scanning of
services that require auth.
"""
from __future__ import annotations
import ipaddress
import platform
import re
import socket
import subprocess
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import psutil

try:
    from scapy.all import ARP, Ether, srp        # type: ignore
    _HAS_SCAPY = True
except Exception:
    _HAS_SCAPY = False

try:
    from mac_vendor_lookup import MacLookup
    _MAC = MacLookup()
except Exception:
    _MAC = None


@dataclass
class Device:
    ip: str
    mac: str
    vendor: str
    hostname: str
    os_guess: str
    online: bool
    def dict(self): return asdict(self)


def _local_cidr() -> str | None:
    for _, addrs in psutil.net_if_addrs().items():
        for a in addrs:
            if a.family == socket.AF_INET and not a.address.startswith("127."):
                try:
                    net = ipaddress.IPv4Network(f"{a.address}/{a.netmask}", strict=False)
                    if net.prefixlen >= 16:
                        return str(net)
                except Exception:
                    continue
    return None


def _ping(ip: str, timeout_ms: int = 600) -> tuple[bool, int | None]:
    """Returns (alive, ttl)."""
    sysname = platform.system()
    cmd = (["ping", "-n", "1", "-w", str(timeout_ms), ip] if sysname == "Windows"
           else ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), ip])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        alive = out.returncode == 0
        ttl = None
        m = re.search(r"ttl[=|:](\d+)", out.stdout, re.I)
        if m:
            ttl = int(m.group(1))
        return alive, ttl
    except Exception:
        return False, None


def _os_from_ttl(ttl: int | None) -> str:
    if ttl is None: return "—"
    if ttl >= 200:  return "Network device"
    if ttl >= 100:  return "Windows"
    if ttl >= 60:   return "Linux/macOS/iOS"
    return "Unknown"


def _vendor(mac: str) -> str:
    if not _MAC: return "—"
    try:
        return _MAC.lookup(mac)
    except Exception:
        return "—"


def _hostname(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "—"


def _arp_table() -> dict[str, str]:
    """Fallback: parse `arp -a`."""
    try:
        out = subprocess.check_output(["arp", "-a"], text=True, errors="ignore", timeout=5)
    except Exception:
        return {}
    table = {}
    for ln in out.splitlines():
        m = re.search(r"(\d+\.\d+\.\d+\.\d+).+?([0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2})", ln, re.I)
        if m:
            table[m.group(1)] = m.group(2).replace("-", ":").lower()
    return table


def discover(timeout: float = 2.0) -> list[Device]:
    cidr = _local_cidr()
    if not cidr:
        return []

    pairs: dict[str, str] = {}
    if _HAS_SCAPY:
        try:
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=cidr),
                         timeout=timeout, verbose=False)
            for _, r in ans:
                pairs[r.psrc] = r.hwsrc.lower()
        except Exception:
            pairs = {}

    if not pairs:
        # warm ARP cache then read it
        for ip in ipaddress.IPv4Network(cidr).hosts():
            _ping(str(ip), 200)
        pairs = _arp_table()

    devices: list[Device] = []
    with ThreadPoolExecutor(max_workers=32) as ex:
        futs = {ex.submit(_ping, ip): (ip, mac) for ip, mac in pairs.items()}
        for fut in futs:
            ip, mac = futs[fut]
            alive, ttl = fut.result()
            devices.append(Device(
                ip=ip, mac=mac, vendor=_vendor(mac),
                hostname=_hostname(ip), os_guess=_os_from_ttl(ttl),
                online=alive,
            ))
    devices.sort(key=lambda d: tuple(int(p) for p in d.ip.split(".")))
    return devices
