"""Local password strength checker."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QLineEdit, QHBoxLayout, QPushButton, QLabel,
                             QProgressBar, QVBoxLayout, QTextEdit, QCheckBox)

from ._base import Page
from ..widgets.glass_card import GlassCard
from ..core import password


class PasswordCheckerPage(Page):
    def __init__(self, app):
        super().__init__(app)
        self.title("Password Strength",
                   "Entirely local — your password never leaves this machine.")

        card = GlassCard()
        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setPlaceholderText("Type a password…")
        self.show = QCheckBox("Show")
        self.btn = QPushButton("Analyze")
        row.addWidget(self.input, 1); row.addWidget(self.show); row.addWidget(self.btn)
        card.body.addLayout(row)

        self.bar = QProgressBar(); self.bar.setRange(0, 100); self.bar.setValue(0)
        card.add(self.bar)

        info = QHBoxLayout()
        self.label = QLabel("—"); self.label.setObjectName("h2")
        self.entropy = QLabel("entropy: —"); self.entropy.setObjectName("muted")
        self.crack = QLabel("crack time: —"); self.crack.setObjectName("muted")
        info.addWidget(self.label); info.addStretch(1)
        info.addWidget(self.entropy); info.addSpacing(20); info.addWidget(self.crack)
        card.body.addLayout(info)

        self.tips = QTextEdit(); self.tips.setReadOnly(True)
        self.tips.setStyleSheet("background:#0f151c; border:1px solid rgba(0,212,255,0.25); border-radius:10px; padding:10px;")
        card.add(self.tips)

        self.root.addWidget(card)

        self.show.toggled.connect(lambda on: self.input.setEchoMode(
            QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password))
        self.btn.clicked.connect(self.analyze)
        self.input.textChanged.connect(self.analyze)

    def analyze(self):
        r = password.analyze(self.input.text())
        self.bar.setValue(r["strength"])
        color = ("#ff4d6d" if r["strength"] < 25 else
                 "#ffb84d" if r["strength"] < 65 else "#4dffa6")
        self.bar.setStyleSheet(
            f"QProgressBar::chunk {{ background:{color}; border-radius:6px; }}"
            "QProgressBar { border:1px solid rgba(0,212,255,0.25); border-radius:6px;"
            " background:#0f151c; text-align:center; }")
        self.label.setText(r["label"])
        self.entropy.setText(f"entropy: {r['entropy']} bits")
        self.crack.setText(f"crack time: {r['crack_time']}")
        self.tips.setHtml("<ul>" + "".join(f"<li>{t}</li>" for t in r["tips"]) + "</ul>")
