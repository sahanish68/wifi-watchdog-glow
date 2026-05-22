"""WiFi scanner page with auto-refresh."""
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QCheckBox, QSpinBox, QLabel,
                             QHeaderView)

from ._base import Page, Worker
from ..widgets.glass_card import GlassCard
from ..core import wifi, audit
from .. import db


COLS = ["SSID", "BSSID", "Signal", "Security", "Channel", "Band", "Verdict"]


class WifiScannerPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("WiFi Scanner", "Lists nearby networks via your OS-native WiFi APIs.")

        card = GlassCard()
        controls = QHBoxLayout()
        self.btn = QPushButton("Scan now")
        self.auto = QCheckBox("Auto-refresh every"); self.auto.setChecked(False)
        self.every = QSpinBox(); self.every.setRange(5, 120); self.every.setValue(15); self.every.setSuffix(" s")
        self.status = QLabel("Idle."); self.status.setObjectName("muted")
        controls.addWidget(self.btn); controls.addSpacing(20)
        controls.addWidget(self.auto); controls.addWidget(self.every)
        controls.addStretch(1); controls.addWidget(self.status)
        card.body.addLayout(controls)

        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        card.add(self.table)

        self.root.addWidget(card)

        self.btn.clicked.connect(self.scan)
        self.timer = QTimer(self); self.timer.timeout.connect(self.scan)
        self.auto.toggled.connect(self._toggle_auto)
        self.every.valueChanged.connect(lambda v: self.timer.setInterval(v * 1000))

    def _toggle_auto(self, on: bool):
        if on: self.timer.start(self.every.value() * 1000)
        else:  self.timer.stop()

    def scan(self):
        self.btn.setEnabled(False); self.status.setText("Scanning…")
        self.worker = Worker(wifi.scan)
        self.worker.done.connect(self._done)
        self.worker.fail.connect(lambda e: (self.app.notify(f"Scan failed: {e}", "error"),
                                            self._reset()))
        self.worker.start()

    def _reset(self):
        self.btn.setEnabled(True); self.status.setText("Idle.")

    def _done(self, nets):
        self.table.setRowCount(0)
        for n in nets:
            verdict, score, _ = audit.assess(n.security)
            r = self.table.rowCount(); self.table.insertRow(r)
            values = [n.ssid, n.bssid, f"{n.signal}", n.security,
                      n.channel, n.frequency, f"{verdict} ({score})"]
            for c, v in enumerate(values):
                item = QTableWidgetItem(str(v))
                if c == 6:
                    color = {"Critical": "#ff4d6d", "Weak": "#ffb84d",
                             "Good": "#4dffa6", "Strong": "#4dffa6"}.get(verdict, "#7d8ea1")
                    item.setForeground(Qt.GlobalColor.white)
                    item.setData(Qt.ItemDataRole.UserRole, color)
                    item.setForeground(__import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(color))
                self.table.setItem(r, c, item)
        self._reset()
        self.status.setText(f"Found {len(nets)} networks.")
        db.add_scan("wifi", f"Found {len(nets)} networks")
        # Update dashboard score if present
        try:
            dash = self.app.pages[0][2]
            dash.set_score(audit.overall_score(nets), "Average across visible networks")
        except Exception:
            pass
        self.app.notify(f"WiFi scan complete — {len(nets)} networks", "success")
