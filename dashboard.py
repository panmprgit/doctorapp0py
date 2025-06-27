"""Dashboard window displaying upcoming appointments."""

from __future__ import annotations

from PySide6.QtWidgets import QListWidget, QVBoxLayout, QWidget, QLabel

import database


class DashboardPage(QWidget):
    """Dashboard page showing a simple list of upcoming appointments."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_appointments()

    def _create_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Upcoming Appointments")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.list_widget = QListWidget()

        layout.addWidget(title)
        layout.addWidget(self.list_widget)
        layout.addStretch()

    def load_appointments(self) -> None:
        """Load appointments from the database into the list widget."""
        self.list_widget.clear()
        appointments = database.get_upcoming_appointments()
        if not appointments:
            self.list_widget.addItem("No upcoming appointments.")
            return
        for row in appointments:
            self.list_widget.addItem(f"{row['appointment_date']} - {row['patient_name']}")

