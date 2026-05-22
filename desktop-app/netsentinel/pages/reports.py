"""Scan history, alerts, whitelist, and PDF export."""
import time
from pathlib import Path

from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFileDialog,
                             QLabel, QTabWidget, QWidget, QVBoxLayout)

from ._base import Page
from ..widgets.glass_card import GlassCard
from ..core import pdf_report
from .. import db


class ReportsPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Reports & History", "Browse past scans, alerts and whitelist; export to PDF.")

        tabs = QTabWidget()
        self.history = self._table(["When", "Kind", "Summary"])
        self.alerts  = self._table(["When", "Level", "Message"])
        self.wl      = self._table(["MAC", "Label", "Added"])
        for t, label in [(self.history, "Scan history"),
                         (self.alerts, "Alerts"),
                         (self.wl, "Whitelist")]:
            w = QWidget(); v = QVBoxLayout(w); v.addWidget(t); tabs.addTab(w, label)

        bar = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_pdf = QPushButton("Export PDF…")
        bar.addWidget(self.btn_refresh); bar.addStretch(1); bar.addWidget(self.btn_pdf)

        card = GlassCard()
        card.body.addLayout(bar)
        card.add(tabs)
        self.root.addWidget(card)

        self.btn_refresh.clicked.connect(self.reload)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.reload()

    def _table(self, headers):
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return t

    def reload(self):
        self._fill(self.history, [(time.strftime("%Y-%m-%d %H:%M", time.localtime(r["ts"])),
                                   r["kind"], r["summary"]) for r in db.list_scans()])
        self._fill(self.alerts,  [(time.strftime("%Y-%m-%d %H:%M", time.localtime(r["ts"])),
                                   r["level"], r["message"]) for r in db.list_alerts()])
        self._fill(self.wl,      [(r["mac"], r["label"] or "—",
                                   time.strftime("%Y-%m-%d", time.localtime(r["added"] or 0)))
                                  for r in db.whitelist_all()])

    def _fill(self, t, rows):
        t.setRowCount(0)
        for row in rows:
            r = t.rowCount(); t.insertRow(r)
            for c, v in enumerate(row):
                t.setItem(r, c, QTableWidgetItem(str(v)))

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export report",
                                              str(Path.home() / "netsentinel-report.pdf"),
                                              "PDF Files (*.pdf)")
        if not path: return
        sections = [
            ("Scan history",
             [["When", "Kind", "Summary"]] +
             [[time.strftime("%Y-%m-%d %H:%M", time.localtime(r["ts"])), r["kind"], r["summary"]]
              for r in db.list_scans()]),
            ("Alerts",
             [["When", "Level", "Message"]] +
             [[time.strftime("%Y-%m-%d %H:%M", time.localtime(r["ts"])), r["level"], r["message"]]
              for r in db.list_alerts()]),
            ("Whitelist",
             [["MAC", "Label"]] +
             [[r["mac"], r["label"] or ""] for r in db.whitelist_all()]),
        ]
        try:
            pdf_report.export(path, sections)
            self.app.notify(f"Saved {Path(path).name}", "success")
        except Exception as e:
            self.app.notify(f"PDF export failed: {e}", "error")
