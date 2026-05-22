"""Glassmorphism card container."""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


class GlassCard(QFrame):
    def __init__(self, title: str = ""):
        super().__init__()
        self.setObjectName("glassCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)
        if title:
            lbl = QLabel(title)
            lbl.setObjectName("h2")
            lay.addWidget(lbl)
        self.body = lay

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 212, 255, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def add(self, w):
        self.body.addWidget(w)
        return w
