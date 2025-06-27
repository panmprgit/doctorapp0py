from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

DARK_THEME = """
/* Base */
QWidget {
    background-color: #353535;
    color: #ffffff;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 10pt;
}

QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QComboBox {
    background-color: #454545;
    border: 1px solid #555555;
    padding: 4px;
    border-radius: 4px;
}

QPushButton {
    background-color: #2d89ef;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #358ef2;
}

QPushButton:pressed {
    background-color: #1b6dbf;
}

QTableWidget {
    gridline-color: #404040;
}

QHeaderView::section {
    background-color: #353535;
    font-weight: bold;
    padding: 4px;
}

QScrollBar:vertical {
    background: #404040;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #606060;
    min-height: 20px;
    border-radius: 6px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f0f0f0;
    color: #000000;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 10pt;
}

QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    padding: 4px;
    border-radius: 4px;
}

QPushButton {
    background-color: #0078d7;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    color: white;
}

QPushButton:hover {
    background-color: #248afd;
}

QPushButton:pressed {
    background-color: #005499;
}

QTableWidget {
    gridline-color: #e0e0e0;
}

QHeaderView::section {
    background-color: #e0e0e0;
    font-weight: bold;
    padding: 4px;
}

QScrollBar:vertical {
    background: #e0e0e0;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border-radius: 6px;
}
"""


class Theme:
    DARK = "dark"
    LIGHT = "light"


def apply_theme(app: QApplication, theme: str = Theme.DARK) -> None:
    """Apply the chosen QSS theme to the QApplication."""
    if theme == Theme.LIGHT:
        app.setStyleSheet(LIGHT_THEME)
    else:
        app.setStyleSheet(DARK_THEME)
    # Set default font
    app.setFont(QFont("Segoe UI", 10))
