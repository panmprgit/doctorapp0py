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
    QStyle,
)
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

import database


class SettingsPage(QWidget):
    """UI for editing doctor information and managing the database."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_doctor_info()

    def _create_ui(self) -> None:
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("John")
        self.first_name_edit.setToolTip("Doctor's first name")
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Doe")
        self.last_name_edit.setToolTip("Doctor's last name")
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Street, City")
        self.address_edit.setToolTip("Office address")
        self.speciality_edit = QLineEdit()
        self.speciality_edit.setPlaceholderText("Dentist")
        self.speciality_edit.setToolTip("Medical speciality")
        self.telephone_edit = QLineEdit()
        self.telephone_edit.setPlaceholderText("123456789")
        self.telephone_edit.setToolTip("Contact phone number")
        phone_validator = QRegularExpressionValidator(QRegularExpression(r"^[0-9+\- ]{3,}$"))
        self.telephone_edit.setValidator(phone_validator)

        form = QFormLayout()
        form.setVerticalSpacing(6)
        form.addRow("First Name", self.first_name_edit)
        form.addRow("Last Name", self.last_name_edit)
        form.addRow("Address", self.address_edit)
        form.addRow("Speciality", self.speciality_edit)
        form.addRow("Telephone", self.telephone_edit)

        style = self.style()
        save_btn = QPushButton(style.standardIcon(QStyle.SP_DialogSaveButton), "Save")
        save_btn.clicked.connect(self.save_doctor_info)

        export_btn = QPushButton(style.standardIcon(QStyle.SP_DialogOpenButton), "Export Database")
        export_btn.clicked.connect(self.export_database)

        import_btn = QPushButton(style.standardIcon(QStyle.SP_DialogOpenButton), "Import Database")
        import_btn.clicked.connect(self.import_database)

        btn_row = QHBoxLayout()
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        btn_row.addWidget(export_btn)
        btn_row.addWidget(import_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
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

