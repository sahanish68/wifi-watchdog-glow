"""Left navigation sidebar."""
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QButtonGroup


class Sidebar(QFrame):
    navigated = pyqtSignal(int)

    def __init__(self, items):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 18, 0, 18)
        lay.setSpacing(2)

        brand = QLabel("◢ NETSENTINEL")
        brand.setObjectName("neon")
        brand.setStyleSheet("font-size:16px; letter-spacing:2px; padding:0 18px 18px;")
        lay.addWidget(brand)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        for idx, (name, icon) in enumerate(items):
            btn = QPushButton(f"  {icon}   {name}")
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, i=idx: self.navigated.emit(i))
            self.group.addButton(btn, idx)
            lay.addWidget(btn)
            if idx == 0:
                btn.setChecked(True)

        lay.addStretch(1)
        footer = QLabel("v1.0 · defensive use only")
        footer.setObjectName("muted")
        footer.setStyleSheet("padding:12px 18px; font-size:11px;")
        lay.addWidget(footer)
