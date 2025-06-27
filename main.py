"""Doctor application entry point.

Installation:
    pip install PySide6

Run the application:
    python main.py
"""

from __future__ import annotations

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QStackedWidget,
    QStyle,
)
from PySide6.QtGui import QPalette, QColor, QFont
from PySide6.QtCore import Qt

import database
from dashboard import DashboardPage
from customers import CustomersPage
from reports import ReportsPage
from settings import SettingsPage


def apply_modern_style(app: QApplication) -> None:
    """Apply a modern dark theme and font to the application."""
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    app.setFont(QFont("Segoe UI", 10))


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Doctor App")
        self.resize(800, 600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar with navigation buttons
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        root_layout.addLayout(sidebar)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        # Pages
        self.dashboard_page = DashboardPage()
        self.customers_page = CustomersPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.customers_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.settings_page)

        style = self.style()
        buttons = [
            ("Dashboard", QStyle.SP_DesktopIcon, self.dashboard_page),
            ("Customers", QStyle.SP_FileIcon, self.customers_page),
            ("Reports", QStyle.SP_DirIcon, self.reports_page),
            ("Settings", QStyle.SP_FileDialogDetailedView, self.settings_page),
        ]

        for text, icon_type, page in buttons:
            icon = style.standardIcon(icon_type)
            btn = QPushButton(icon, text)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, p=page: self.stack.setCurrentWidget(p))
            sidebar.addWidget(btn)

        sidebar.addStretch()


def main() -> None:
    """Application entry point."""
    database.initialize_database()
    app = QApplication(sys.argv)
    apply_modern_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

