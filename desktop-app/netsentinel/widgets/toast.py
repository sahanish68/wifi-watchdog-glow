"""Lightweight toast notifications anchored to bottom-right of main window."""
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import QLabel, QWidget

COLORS = {
    "info":    ("#0a1a24", "#00d4ff"),
    "success": ("#0a241a", "#4dffa6"),
    "warn":    ("#241c0a", "#ffb84d"),
    "error":   ("#240a14", "#ff4d6d"),
}


class ToastManager:
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.active = []

    def show(self, message: str, level: str = "info", ms: int = 3200):
        bg, fg = COLORS.get(level, COLORS["info"])
        t = QLabel(message, self.parent)
        t.setStyleSheet(
            f"background:{bg}; color:{fg}; border:1px solid {fg};"
            f"border-radius:10px; padding:10px 16px; font-weight:600;"
        )
        t.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        t.adjustSize()
        self._place(t)
        t.show()
        self.active.append(t)

        anim = QPropertyAnimation(t, b"windowOpacity", t)
        anim.setDuration(220); anim.setStartValue(0.0); anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic); anim.start()

        QTimer.singleShot(ms, lambda: self._dismiss(t))

    def _place(self, t: QLabel):
        margin = 18
        offset = sum(w.height() + 8 for w in self.active)
        pw = self.parent.width(); ph = self.parent.height()
        t.move(pw - t.width() - margin, ph - t.height() - margin - offset)

    def _dismiss(self, t: QLabel):
        anim = QPropertyAnimation(t, b"windowOpacity", t)
        anim.setDuration(220); anim.setStartValue(1.0); anim.setEndValue(0.0)
        anim.finished.connect(lambda: (t.deleteLater(),
                                       self.active.remove(t) if t in self.active else None))
        anim.start()
