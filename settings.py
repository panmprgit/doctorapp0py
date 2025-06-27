"""Settings window to manage doctor's information and database import/export."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
)

import database


class SettingsPage(QWidget):
    """UI for editing doctor information and managing the database."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_doctor_info()

    def _create_ui(self) -> None:
        self.first_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.speciality_edit = QLineEdit()
        self.telephone_edit = QLineEdit()

        form = QFormLayout()
        form.addRow("First Name", self.first_name_edit)
        form.addRow("Last Name", self.last_name_edit)
        form.addRow("Address", self.address_edit)
        form.addRow("Speciality", self.speciality_edit)
        form.addRow("Telephone", self.telephone_edit)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_doctor_info)

        export_btn = QPushButton("Export Database")
        export_btn.clicked.connect(self.export_database)

        import_btn = QPushButton("Import Database")
        import_btn.clicked.connect(self.import_database)

        btn_row = QHBoxLayout()
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        btn_row.addWidget(export_btn)
        btn_row.addWidget(import_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch()
        layout.addLayout(btn_row)

    def load_doctor_info(self) -> None:
        """Populate fields from the database."""
        row = database.get_doctor_info()
        if not row:
            return
        self.first_name_edit.setText(row["first_name"] or "")
        self.last_name_edit.setText(row["last_name"] or "")
        self.address_edit.setText(row["address"] or "")
        self.speciality_edit.setText(row["speciality"] or "")
        self.telephone_edit.setText(row["telephone"] or "")

    def save_doctor_info(self) -> None:
        """Save doctor information back to the database."""
        database.save_doctor_info(
            self.first_name_edit.text(),
            self.last_name_edit.text(),
            self.address_edit.text(),
            self.speciality_edit.text(),
            self.telephone_edit.text(),
        )
        QMessageBox.information(self, "Saved", "Doctor information saved.")

    def export_database(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Database", "data.db")
        if path:
            database.export_database(path)

    def import_database(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Database", "data.db")
        if path:
            database.import_database(path)
            self.load_doctor_info()

