"""Animated line chart powered by pyqtgraph for smooth realtime updates."""
from collections import deque
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPen


pg.setConfigOptions(antialias=True, background=None, foreground="#7d8ea1")


class AnimatedChart(pg.PlotWidget):
    def __init__(self, title: str = "", color: str = "#00d4ff",
                 maxlen: int = 120, y_label: str = ""):
        super().__init__()
        self.setMenuEnabled(False)
        self.hideButtons()
        self.showGrid(x=True, y=True, alpha=0.15)
        self.setLabel("left", y_label)
        if title:
            self.setTitle(title, color="#e6f1ff", size="10pt")

        self.x = deque(maxlen=maxlen)
        self.y = deque(maxlen=maxlen)
        pen = QPen(QColor(color)); pen.setWidth(2)
        self.curve = self.plot([], [], pen=pen, fillLevel=0,
                               brush=pg.mkBrush(0, 212, 255, 40))
        self._tick = 0

    def push(self, value: float):
        self._tick += 1
        self.x.append(self._tick)
        self.y.append(value)
        self.curve.setData(list(self.x), list(self.y))

    def auto_demo(self, supplier, interval_ms: int = 1000):
        """Drive the chart from a callable returning a float."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: self.push(float(supplier() or 0)))
        self._timer.start(interval_ms)
