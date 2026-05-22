"""Overview dashboard with security score + quick stats."""
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout

import psutil

from ._base import Page
from ..widgets.glass_card import GlassCard
from ..widgets.animated_chart import AnimatedChart
from ..widgets.status_dot import StatusDot
from ..core.monitor import BandwidthMonitor


class DashboardPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Security Dashboard", "Live overview of your network posture.")

        grid = QGridLayout(); grid.setSpacing(16)
        self.root.addLayout(grid)

        self.score_card = GlassCard("Security Score")
        self.score_lbl = QLabel("—")
        self.score_lbl.setStyleSheet("font-size:48px; font-weight:800; color:#00d4ff;")
        self.score_sub = QLabel("Run an audit on the WiFi page.")
        self.score_sub.setObjectName("muted")
        self.score_card.add(self.score_lbl); self.score_card.add(self.score_sub)

        self.up_card = GlassCard("Upload (kbps)")
        self.up_chart = AnimatedChart(color="#4dffa6", y_label="kbps")
        self.up_card.add(self.up_chart)

        self.down_card = GlassCard("Download (kbps)")
        self.down_chart = AnimatedChart(color="#00d4ff", y_label="kbps")
        self.down_card.add(self.down_chart)

        self.status_card = GlassCard("System Status")
        row = QVBoxLayout()
        self.cpu = QLabel("CPU: —"); self.mem = QLabel("Memory: —")
        self.ifaces = QLabel("Interfaces: —"); self.ifaces.setWordWrap(True)
        for w in (self.cpu, self.mem, self.ifaces): row.addWidget(w)
        self.status_card.body.addLayout(row)

        grid.addWidget(self.score_card,   0, 0)
        grid.addWidget(self.status_card,  0, 1)
        grid.addWidget(self.up_card,      1, 0)
        grid.addWidget(self.down_card,    1, 1)

        self.bw = BandwidthMonitor(interval=1.0); self.bw.start()
        self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(1000)

    def set_score(self, score: int, label: str = ""):
        self.score_lbl.setText(str(score))
        self.score_sub.setText(label or f"Overall: {score}/100")

    def _tick(self):
        s = self.bw.latest()
        if s:
            self.up_chart.push(s.up_kbps)
            self.down_chart.push(s.down_kbps)
        self.cpu.setText(f"CPU: {psutil.cpu_percent()}%")
        m = psutil.virtual_memory()
        self.mem.setText(f"Memory: {m.percent}%  ({m.used // (1024**2)} MB used)")
        names = [n for n, addrs in psutil.net_if_addrs().items() if addrs]
        self.ifaces.setText("Interfaces: " + ", ".join(names))
