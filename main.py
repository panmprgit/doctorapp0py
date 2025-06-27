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
)

import database
from dashboard import DashboardPage
from transactions import TransactionsPage
from reports import ReportsPage
from settings import SettingsPage


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

        # Sidebar with navigation buttons
        sidebar = QVBoxLayout()
        root_layout.addLayout(sidebar)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack, 1)

        # Pages
        self.dashboard_page = DashboardPage()
        self.transactions_page = TransactionsPage()
        self.reports_page = ReportsPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.transactions_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.settings_page)

        buttons = [
            ("Dashboard", self.dashboard_page),
            ("Transactions", self.transactions_page),
            ("Reports", self.reports_page),
            ("Settings", self.settings_page),
        ]

        for text, page in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, p=page: self.stack.setCurrentWidget(p))
            sidebar.addWidget(btn)

        sidebar.addStretch()


def main() -> None:
    """Application entry point."""
    database.initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

