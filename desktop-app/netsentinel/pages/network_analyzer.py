"""LAN devices + fingerprinting."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel)
from PyQt6.QtGui import QColor

from ._base import Page, Worker
from ..widgets.glass_card import GlassCard
from ..core import lan
from .. import db

COLS = ["IP", "MAC", "Vendor", "Hostname", "OS guess", "Status", "Whitelist"]


class NetworkAnalyzerPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Network Analyzer", "ARP-sweep of your local subnet with passive fingerprinting.")

        card = GlassCard()
        bar = QHBoxLayout()
        self.btn = QPushButton("Scan LAN")
        self.btn_wl = QPushButton("Add selected to whitelist")
        self.status = QLabel("Idle."); self.status.setObjectName("muted")
        bar.addWidget(self.btn); bar.addWidget(self.btn_wl); bar.addStretch(1); bar.addWidget(self.status)
        card.body.addLayout(bar)

        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        card.add(self.table)
        self.root.addWidget(card)

        self.btn.clicked.connect(self.scan)
        self.btn_wl.clicked.connect(self.add_whitelist)

    def scan(self):
        self.btn.setEnabled(False); self.status.setText("Scanning LAN…")
        self.worker = Worker(lan.discover)
        self.worker.done.connect(self._done)
        self.worker.fail.connect(lambda e: (self.app.notify(f"LAN scan failed: {e}", "error"),
                                            self._reset()))
        self.worker.start()

    def _reset(self):
        self.btn.setEnabled(True); self.status.setText("Idle.")

    def _done(self, devices):
        whitelist = {w["mac"] for w in db.whitelist_all()}
        self.table.setRowCount(0)
        for d in devices:
            r = self.table.rowCount(); self.table.insertRow(r)
            wl = "✓" if d.mac in whitelist else "—"
            values = [d.ip, d.mac, d.vendor, d.hostname, d.os_guess,
                      "Online" if d.online else "Offline", wl]
            for c, v in enumerate(values):
                it = QTableWidgetItem(str(v))
                if c == 5:
                    it.setForeground(QColor("#4dffa6" if d.online else "#7d8ea1"))
                self.table.setItem(r, c, it)
            # alert on unknown device
            if d.online and d.mac not in whitelist:
                db.add_alert("warn", f"Unknown device online: {d.ip} ({d.mac})")
        self._reset()
        self.status.setText(f"{len(devices)} devices.")
        db.add_scan("lan", f"{len(devices)} devices discovered")
        self.app.notify(f"LAN scan complete — {len(devices)} devices", "success")

    def add_whitelist(self):
        rows = {i.row() for i in self.table.selectedItems()}
        if not rows:
            self.app.notify("Select a row first.", "warn"); return
        added = 0
        for r in rows:
            mac = self.table.item(r, 1).text()
            label = self.table.item(r, 3).text()
            db.whitelist_add(mac, label); added += 1
        self.app.notify(f"Added {added} device(s) to whitelist.", "success")
