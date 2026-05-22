"""Realtime bandwidth + packet stats (psutil + optional Scapy sniffing)."""
from __future__ import annotations
import threading
import time
from collections import deque
from dataclasses import dataclass

import psutil

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP   # type: ignore
    _HAS_SCAPY = True
except Exception:
    _HAS_SCAPY = False


@dataclass
class Sample:
    ts: float
    up_kbps: float
    down_kbps: float


class BandwidthMonitor:
    def __init__(self, interval: float = 1.0, maxlen: int = 300):
        self.interval = interval
        self.samples: deque[Sample] = deque(maxlen=maxlen)
        self._last = psutil.net_io_counters()
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._loop, daemon=True)

    def start(self): self._t.start()
    def stop(self):  self._stop.set()

    def _loop(self):
        while not self._stop.is_set():
            time.sleep(self.interval)
            cur = psutil.net_io_counters()
            up   = (cur.bytes_sent - self._last.bytes_sent) * 8 / 1000 / self.interval
            down = (cur.bytes_recv - self._last.bytes_recv) * 8 / 1000 / self.interval
            self.samples.append(Sample(time.time(), up, down))
            self._last = cur

    def latest(self) -> Sample | None:
        return self.samples[-1] if self.samples else None


class PacketCounter:
    """Counts TCP/UDP/ICMP/ARP packets per second using Scapy (if available)."""
    def __init__(self):
        self.counts = {"TCP": 0, "UDP": 0, "ICMP": 0, "ARP": 0, "Other": 0}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.available = _HAS_SCAPY
        self._t: threading.Thread | None = None

    def start(self):
        if not _HAS_SCAPY: return
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def stop(self): self._stop.set()

    def _classify(self, pkt):
        with self._lock:
            if TCP in pkt:    self.counts["TCP"]  += 1
            elif UDP in pkt:  self.counts["UDP"]  += 1
            elif ICMP in pkt: self.counts["ICMP"] += 1
            elif ARP in pkt:  self.counts["ARP"]  += 1
            else:             self.counts["Other"] += 1

    def _run(self):
        try:
            sniff(prn=self._classify, store=False,
                  stop_filter=lambda *_: self._stop.is_set())
        except Exception:
            self.available = False

    def snapshot_and_reset(self) -> dict:
        with self._lock:
            snap = dict(self.counts)
            for k in self.counts: self.counts[k] = 0
        return snap
