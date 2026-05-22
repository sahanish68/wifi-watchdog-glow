"""Audit nearby networks for weak security configurations."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QTextEdit)

from ._base import Page, Worker
from ..widgets.glass_card import GlassCard
from ..core import wifi, audit
from .. import db

COLS = ["SSID", "Security", "Verdict", "Score"]


class SecurityAuditPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Security Audit", "Classifies nearby networks and suggests hardening steps.")

        card = GlassCard()
        bar = QHBoxLayout()
        self.btn = QPushButton("Run audit")
        self.status = QLabel("Idle."); self.status.setObjectName("muted")
        bar.addWidget(self.btn); bar.addStretch(1); bar.addWidget(self.status)
        card.body.addLayout(bar)

        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._show_recs)
        card.add(self.table)

        self.recs = QTextEdit(); self.recs.setReadOnly(True)
        self.recs.setPlaceholderText("Select a row to see recommendations.")
        self.recs.setStyleSheet("background:#0f151c; border:1px solid rgba(0,212,255,0.25); border-radius:10px; padding:10px;")
        self.recs.setMaximumHeight(180)
        card.add(self.recs)

        self.root.addWidget(card)
        self.btn.clicked.connect(self.run)
        self._last: list = []

    def run(self):
        self.btn.setEnabled(False); self.status.setText("Scanning…")
        self.worker = Worker(wifi.scan)
        self.worker.done.connect(self._done)
        self.worker.fail.connect(lambda e: (self.app.notify(f"Audit failed: {e}", "error"),
                                            self._reset()))
        self.worker.start()

    def _reset(self):
        self.btn.setEnabled(True); self.status.setText("Idle.")

    def _done(self, nets):
        self._last = nets
        self.table.setRowCount(0)
        for n in nets:
            verdict, score, _ = audit.assess(n.security)
            r = self.table.rowCount(); self.table.insertRow(r)
            values = [n.ssid, n.security, verdict, str(score)]
            for c, v in enumerate(values):
                it = QTableWidgetItem(v)
                if c == 2:
                    it.setForeground(QColor({
                        "Critical": "#ff4d6d", "Weak": "#ffb84d",
                        "Good": "#4dffa6", "Strong": "#4dffa6"}.get(verdict, "#7d8ea1")))
                self.table.setItem(r, c, it)
        self._reset()
        score = audit.overall_score(nets)
        self.status.setText(f"Average security score: {score}/100")
        db.add_scan("audit", f"Audited {len(nets)} networks, avg score {score}")
        self.app.notify("Audit complete", "success")

    def _show_recs(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows: return
        idx = rows[0].row()
        if idx >= len(self._last): return
        n = self._last[idx]
        verdict, score, recs = audit.assess(n.security)
        body = [f"<b>{n.ssid}</b> — {verdict} ({score}/100)<br>",
                "<ul>"] + [f"<li>{r}</li>" for r in recs] + ["</ul>"]
        self.recs.setHtml("".join(body))
