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


import database
from dashboard import DashboardPage
from customers import CustomersPage
from reports import ReportsPage
from settings import SettingsPage
from style import apply_theme, Theme




class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Doctor App")
        self.resize(1024, 768)
        self.current_theme = Theme.DARK
        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar with navigation buttons
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(150)
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setSpacing(10)
        sidebar.setContentsMargins(8, 8, 8, 8)
        root_layout.addWidget(sidebar_widget)

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

        # Theme toggle button
        self.theme_btn = QPushButton("Light Mode")
        self.theme_btn.clicked.connect(self._toggle_theme)
        sidebar.addWidget(self.theme_btn)

        sidebar.addStretch()

    def _toggle_theme(self) -> None:
        """Switch between dark and light themes."""
        app = QApplication.instance()
        if not app:
            return
        if self.current_theme == Theme.DARK:
            self.current_theme = Theme.LIGHT
            self.theme_btn.setText("Dark Mode")
        else:
            self.current_theme = Theme.DARK
            self.theme_btn.setText("Light Mode")
        apply_theme(app, self.current_theme)


def main() -> None:
    """Application entry point."""
    database.initialize_database()
    app = QApplication(sys.argv)
    apply_theme(app, Theme.DARK)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

