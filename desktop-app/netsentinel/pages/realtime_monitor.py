"""Realtime bandwidth + live packet statistics."""
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGridLayout, QLabel, QHBoxLayout

from ._base import Page
from ..widgets.glass_card import GlassCard
from ..widgets.animated_chart import AnimatedChart
from ..core.monitor import BandwidthMonitor, PacketCounter


class RealtimeMonitorPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Realtime Monitor",
                   "Live bandwidth + per-protocol packet rate (Scapy passive sniffer).")

        grid = QGridLayout(); grid.setSpacing(16)
        self.root.addLayout(grid)

        self.up_card = GlassCard("Upload (kbps)")
        self.up_chart = AnimatedChart(color="#4dffa6")
        self.up_card.add(self.up_chart)

        self.down_card = GlassCard("Download (kbps)")
        self.down_chart = AnimatedChart(color="#00d4ff")
        self.down_card.add(self.down_chart)

        self.pkt_card = GlassCard("Packets / second (by protocol)")
        self.pkt_chart_tcp = AnimatedChart(color="#00d4ff", y_label="TCP")
        self.pkt_chart_udp = AnimatedChart(color="#4dffa6", y_label="UDP")
        self.pkt_chart_icmp = AnimatedChart(color="#ffb84d", y_label="ICMP/ARP")
        row = QHBoxLayout()
        row.addWidget(self.pkt_chart_tcp); row.addWidget(self.pkt_chart_udp); row.addWidget(self.pkt_chart_icmp)
        self.pkt_card.body.addLayout(row)

        self.status = QLabel(""); self.status.setObjectName("muted")
        self.pkt_card.add(self.status)

        grid.addWidget(self.up_card,   0, 0)
        grid.addWidget(self.down_card, 0, 1)
        grid.addWidget(self.pkt_card,  1, 0, 1, 2)

        self.bw = BandwidthMonitor(interval=1.0); self.bw.start()
        self.pkt = PacketCounter(); self.pkt.start()
        if not self.pkt.available:
            self.status.setText("Scapy unavailable — packet stats disabled. "
                                "Install Npcap on Windows and run as Administrator.")

        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(1000)

    def _tick(self):
        s = self.bw.latest()
        if s:
            self.up_chart.push(s.up_kbps)
            self.down_chart.push(s.down_kbps)
        snap = self.pkt.snapshot_and_reset()
        self.pkt_chart_tcp.push(snap.get("TCP", 0))
        self.pkt_chart_udp.push(snap.get("UDP", 0))
        self.pkt_chart_icmp.push(snap.get("ICMP", 0) + snap.get("ARP", 0))
