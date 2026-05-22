"""Internet diagnostics: speed test, ping, DNS, packet-loss."""
from __future__ import annotations
import platform
import re
import socket
import statistics
import subprocess
import time


def ping(host: str = "8.8.8.8", count: int = 10) -> dict:
    sysname = platform.system()
    cmd = (["ping", "-n", str(count), host] if sysname == "Windows"
           else ["ping", "-c", str(count), host])
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=count + 5)
        times = [float(t) for t in re.findall(r"time[=<]([\d.]+)\s*ms", out.stdout)]
        sent  = count
        recv  = len(times) or _windows_received(out.stdout) or 0
        loss  = round(100 * (sent - recv) / sent, 1) if sent else 0.0
        return {
            "host": host,
            "sent": sent, "received": recv, "loss_pct": loss,
            "min_ms":  round(min(times), 2) if times else None,
            "avg_ms":  round(statistics.mean(times), 2) if times else None,
            "max_ms":  round(max(times), 2) if times else None,
            "jitter":  round(statistics.pstdev(times), 2) if len(times) > 1 else 0.0,
        }
    except Exception as e:
        return {"host": host, "error": str(e)}


def _windows_received(text: str) -> int | None:
    m = re.search(r"Received\s*=\s*(\d+)", text)
    return int(m.group(1)) if m else None


def dns_lookup(host: str = "cloudflare.com") -> dict:
    t0 = time.perf_counter()
    try:
        ip = socket.gethostbyname(host)
        return {"host": host, "ip": ip, "ms": round((time.perf_counter() - t0) * 1000, 2)}
    except Exception as e:
        return {"host": host, "error": str(e)}


def speedtest() -> dict:
    """Wraps speedtest-cli — runs in a worker thread on the UI side."""
    try:
        import speedtest as st
        s = st.Speedtest(secure=True)
        s.get_best_server()
        down = s.download() / 1_000_000
        up   = s.upload(pre_allocate=False) / 1_000_000
        res  = s.results.dict()
        return {
            "download_mbps": round(down, 2),
            "upload_mbps":   round(up, 2),
            "ping_ms":       round(res.get("ping", 0), 2),
            "server":        res.get("server", {}).get("sponsor", ""),
        }
    except Exception as e:
        return {"error": str(e)}
