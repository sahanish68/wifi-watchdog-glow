"""Helpers shared by pages."""
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Page(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(24, 24, 24, 24)
        self.root.setSpacing(16)

    def title(self, text: str, subtitle: str = ""):
        t = QLabel(text); t.setObjectName("h1")
        self.root.addWidget(t)
        if subtitle:
            s = QLabel(subtitle); s.setObjectName("muted")
            self.root.addWidget(s)


class Worker(QThread):
    """Run a callable in a background thread and emit its result."""
    done = pyqtSignal(object)
    fail = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn, self.args, self.kwargs = fn, args, kwargs

    def run(self):
        try:
            self.done.emit(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.fail.emit(str(e))
