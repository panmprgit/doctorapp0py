"""Dashboard window displaying upcoming appointments."""

from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QVBoxLayout, QWidget, QLabel, QFrame

import database


class DashboardPage(QWidget):
    """Dashboard page showing a simple list of upcoming appointments."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_appointments()

    def _create_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QLabel("Dashboard")
        header.setStyleSheet(
            "font-weight: bold; font-size: 24px; padding: 4px; margin-bottom: 8px;"
        )

        self.total_label = QLabel()
        self.total_label.setStyleSheet("font-size: 18px; color: #007acc; margin: 4px 0;")

        upcoming_title = QLabel("Upcoming Appointments")
        upcoming_title.setStyleSheet(
            "font-weight: bold; font-size: 16px; margin-top: 12px;"
        )

        self.list_widget = QListWidget()
        self.list_widget.setFrameShape(QFrame.NoFrame)

        layout.addWidget(header)
        layout.addWidget(self.total_label)
        layout.addWidget(upcoming_title)
        layout.addWidget(self.list_widget)
        layout.addStretch()

    def load_appointments(self) -> None:
        """Load appointments from the database into the list widget."""
        self.list_widget.clear()
        appointments = database.get_upcoming_appointments()
        total_customers = database.get_total_customers()
        self.total_label.setText(f"Total Customers: {total_customers}")
        if not appointments:
            self.list_widget.addItem("No upcoming appointments.")
            return
        for row in appointments:
            self.list_widget.addItem(f"{row['appointment_date']} - {row['patient_name']}")

