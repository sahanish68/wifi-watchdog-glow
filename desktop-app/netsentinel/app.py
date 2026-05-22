"""QApplication bootstrap + main window with sidebar navigation."""
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
)

from . import db, theme
from .widgets.sidebar import Sidebar
from .widgets.toast import ToastManager
from .pages.dashboard import DashboardPage
from .pages.wifi_scanner import WifiScannerPage
from .pages.network_analyzer import NetworkAnalyzerPage
from .pages.security_audit import SecurityAuditPage
from .pages.password_checker import PasswordCheckerPage
from .pages.internet_test import InternetTestPage
from .pages.realtime_monitor import RealtimeMonitorPage
from .pages.reports import ReportsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetSentinel — Network Security Analyzer")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 640)

        root = QWidget(objectName="root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toasts = ToastManager(self)

        self.stack = QStackedWidget()
        self.pages = [
            ("Dashboard",         "■", DashboardPage(self)),
            ("WiFi Scanner",      "≋", WifiScannerPage(self)),
            ("Network Analyzer",  "⌬", NetworkAnalyzerPage(self)),
            ("Security Audit",    "⚑", SecurityAuditPage(self)),
            ("Password Strength", "✦", PasswordCheckerPage(self)),
            ("Internet Test",     "↯", InternetTestPage(self)),
            ("Realtime Monitor",  "◉", RealtimeMonitorPage(self)),
            ("Reports & History", "▤", ReportsPage(self)),
        ]
        for _, _, page in self.pages:
            self.stack.addWidget(page)

        self.sidebar = Sidebar([(n, i) for n, i, _ in self.pages])
        self.sidebar.navigated.connect(self.stack.setCurrentIndex)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)

    def notify(self, message: str, level: str = "info"):
        self.toasts.show(message, level)


def run():
    db.init()
    app = QApplication(sys.argv)
    app.setStyleSheet(theme.QSS)
    app.setWindowIcon(QIcon())  # placeholder
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
