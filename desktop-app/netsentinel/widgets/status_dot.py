"""Small colored status dot (online/offline/warn)."""
from PyQt6.QtWidgets import QLabel


class StatusDot(QLabel):
    COLORS = {"on": "#4dffa6", "off": "#7d8ea1", "warn": "#ffb84d", "bad": "#ff4d6d"}

    def __init__(self, state: str = "off"):
        super().__init__("●")
        self.set_state(state)

    def set_state(self, state: str):
        c = self.COLORS.get(state, self.COLORS["off"])
        self.setStyleSheet(f"color:{c}; font-size:14px;")
