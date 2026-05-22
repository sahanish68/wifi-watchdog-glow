"""Speedtest / ping / DNS."""
from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QLabel, QGridLayout,
                             QLineEdit, QVBoxLayout)

from ._base import Page, Worker
from ..widgets.glass_card import GlassCard
from ..core import speed
from .. import db


class InternetTestPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Internet Testing", "Speed, ping, DNS, and packet-loss checks.")

        # speedtest card
        s = GlassCard("Speed Test")
        self.btn_speed = QPushButton("Run speed test")
        self.lbl_down = QLabel("Download: —")
        self.lbl_up   = QLabel("Upload: —")
        self.lbl_pingst = QLabel("Ping: —")
        self.lbl_srv  = QLabel("Server: —"); self.lbl_srv.setObjectName("muted")
        grid = QGridLayout()
        grid.addWidget(self.btn_speed, 0, 0, 1, 2)
        grid.addWidget(self.lbl_down, 1, 0); grid.addWidget(self.lbl_up, 1, 1)
        grid.addWidget(self.lbl_pingst, 2, 0); grid.addWidget(self.lbl_srv, 2, 1)
        s.body.addLayout(grid)

        # ping card
        p = GlassCard("Ping & Packet Loss")
        row = QHBoxLayout()
        self.host = QLineEdit("8.8.8.8")
        self.btn_ping = QPushButton("Ping 10x")
        row.addWidget(self.host, 1); row.addWidget(self.btn_ping)
        p.body.addLayout(row)
        self.ping_out = QLabel("—"); self.ping_out.setWordWrap(True)
        p.add(self.ping_out)

        # dns card
        d = GlassCard("DNS Lookup")
        row2 = QHBoxLayout()
        self.dns_host = QLineEdit("cloudflare.com")
        self.btn_dns = QPushButton("Resolve")
        row2.addWidget(self.dns_host, 1); row2.addWidget(self.btn_dns)
        d.body.addLayout(row2)
        self.dns_out = QLabel("—"); self.dns_out.setWordWrap(True)
        d.add(self.dns_out)

        self.root.addWidget(s); self.root.addWidget(p); self.root.addWidget(d)

        self.btn_speed.clicked.connect(self.run_speed)
        self.btn_ping.clicked.connect(self.run_ping)
        self.btn_dns.clicked.connect(self.run_dns)

    def run_speed(self):
        self.btn_speed.setEnabled(False); self.btn_speed.setText("Testing…")
        self.w = Worker(speed.speedtest)
        self.w.done.connect(self._speed_done)
        self.w.fail.connect(lambda e: (self.app.notify(f"Speed test failed: {e}", "error"),
                                       self._speed_done({"error": e})))
        self.w.start()

    def _speed_done(self, r):
        self.btn_speed.setEnabled(True); self.btn_speed.setText("Run speed test")
        if "error" in r:
            self.lbl_down.setText(f"Download: error ({r['error']})")
            return
        self.lbl_down.setText(f"Download: {r['download_mbps']} Mbps")
        self.lbl_up.setText(f"Upload: {r['upload_mbps']} Mbps")
        self.lbl_pingst.setText(f"Ping: {r['ping_ms']} ms")
        self.lbl_srv.setText(f"Server: {r['server']}")
        db.add_scan("speedtest", f"{r['download_mbps']}↓ / {r['upload_mbps']}↑ Mbps")
        self.app.notify("Speed test complete", "success")

    def run_ping(self):
        host = self.host.text().strip() or "8.8.8.8"
        self.btn_ping.setEnabled(False)
        self.w2 = Worker(speed.ping, host, 10)
        self.w2.done.connect(self._ping_done)
        self.w2.fail.connect(lambda e: (self.app.notify(str(e), "error"),
                                        self.btn_ping.setEnabled(True)))
        self.w2.start()

    def _ping_done(self, r):
        self.btn_ping.setEnabled(True)
        if "error" in r:
            self.ping_out.setText(f"Error: {r['error']}"); return
        self.ping_out.setText(
            f"{r['host']}: sent {r['sent']}, recv {r['received']}, "
            f"loss {r['loss_pct']}% | min {r['min_ms']} / avg {r['avg_ms']} / "
            f"max {r['max_ms']} ms, jitter {r['jitter']} ms")

    def run_dns(self):
        host = self.dns_host.text().strip()
        self.w3 = Worker(speed.dns_lookup, host)
        self.w3.done.connect(lambda r: self.dns_out.setText(
            f"{r.get('host')} → {r.get('ip','-')} in {r.get('ms','—')} ms"
            if 'ip' in r else f"Error: {r.get('error')}"))
        self.w3.start()
