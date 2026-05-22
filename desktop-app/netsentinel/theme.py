"""Kali-inspired dark theme with neon-blue accents and glassmorphism."""

NEON = "#00d4ff"
NEON_DIM = "#0096b8"
BG = "#0b0f14"
BG_ALT = "#0f151c"
PANEL = "rgba(20, 28, 38, 0.65)"
BORDER = "rgba(0, 212, 255, 0.25)"
TEXT = "#e6f1ff"
MUTED = "#7d8ea1"
DANGER = "#ff4d6d"
WARN = "#ffb84d"
OK = "#4dffa6"

QSS = f"""
* {{
    font-family: "Segoe UI", "Inter", "JetBrains Mono", sans-serif;
    color: {TEXT};
    font-size: 13px;
}}

QMainWindow, QWidget#root {{
    background-color: {BG};
    background-image: qradialgradient(cx:0.1, cy:0.0, radius:1.0,
        stop:0 #0e1822, stop:1 {BG});
}}

QFrame#sidebar {{
    background-color: {BG_ALT};
    border-right: 1px solid {BORDER};
}}

QPushButton#navBtn {{
    background: transparent;
    color: {MUTED};
    border: none;
    padding: 12px 18px;
    text-align: left;
    border-left: 3px solid transparent;
}}
QPushButton#navBtn:hover {{
    color: {TEXT};
    background: rgba(0, 212, 255, 0.06);
}}
QPushButton#navBtn:checked {{
    color: {NEON};
    background: rgba(0, 212, 255, 0.10);
    border-left: 3px solid {NEON};
    font-weight: 600;
}}

QFrame#glassCard {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QLabel#h1 {{ font-size: 22px; font-weight: 700; color: {TEXT}; }}
QLabel#h2 {{ font-size: 16px; font-weight: 600; color: {TEXT}; }}
QLabel#muted {{ color: {MUTED}; }}
QLabel#neon  {{ color: {NEON}; font-weight: 600; }}

QPushButton {{
    background: rgba(0, 212, 255, 0.12);
    color: {NEON};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background: rgba(0, 212, 255, 0.20); }}
QPushButton:pressed {{ background: rgba(0, 212, 255, 0.30); }}
QPushButton:disabled {{ color: {MUTED}; border-color: #1c2630; background: transparent; }}

QLineEdit, QComboBox, QSpinBox {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {NEON_DIM};
}}

QTableWidget, QTreeWidget {{
    background: {BG_ALT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: #1c2630;
    selection-background-color: rgba(0, 212, 255, 0.18);
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background: #0f1722;
    color: {NEON};
    border: none;
    padding: 8px;
    font-weight: 600;
}}

QProgressBar {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    background: {BG_ALT};
    text-align: center;
    color: {TEXT};
}}
QProgressBar::chunk {{
    background-color: {NEON};
    border-radius: 6px;
}}

QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {NEON_DIM}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""
