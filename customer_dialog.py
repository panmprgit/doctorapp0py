from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QDateEdit,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import QDate

import database


class TherapyDialog(QDialog):
    """Dialog to add or edit a therapy entry."""

    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Therapy")
        form = QFormLayout(self)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.tooth_edit = QLineEdit()
        self.desc_edit = QLineEdit()
        self.payment_edit = QLineEdit("0")
        self.cost_edit = QLineEdit("0")
        self.discount_edit = QLineEdit("0")
        self.comment_edit = QLineEdit()
        form.addRow("Date", self.date_edit)
        form.addRow("Tooth", self.tooth_edit)
        form.addRow("Description", self.desc_edit)
        form.addRow("Payment", self.payment_edit)
        form.addRow("Cost", self.cost_edit)
        form.addRow("Discount", self.discount_edit)
        form.addRow("Comment", self.comment_edit)
        btn_row = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        form.addRow(btn_row)

    def data(self) -> dict:
        return {
            "visit_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "tooth": self.tooth_edit.text(),
            "description": self.desc_edit.text(),
            "payment": float(self.payment_edit.text() or 0),
            "cost": float(self.cost_edit.text() or 0),
            "discount": float(self.discount_edit.text() or 0),
            "comment": self.comment_edit.text(),
        }


class CustomerDialog(QDialog):
    """Dialog for adding/editing a customer with therapy data."""

    def __init__(self, data: dict | None = None, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Customer")
        self._create_ui()
        if data:
            self.load_data(data)

    def _create_ui(self) -> None:
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs)
        # Personal tab
        personal = QWidget()
        form = QFormLayout(personal)
        self.first_edit = QLineEdit()
        self.last_edit = QLineEdit()
        self.birth_edit = QDateEdit()
        self.birth_edit.setCalendarPopup(True)
        self.age_label = QLabel()
        self.birth_edit.dateChanged.connect(self._update_age)
        self.address_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.register_edit = QDateEdit(QDate.currentDate())
        self.register_edit.setCalendarPopup(True)
        self.last_visit_edit = QDateEdit(QDate.currentDate())
        self.last_visit_edit.setCalendarPopup(True)
        self.referral_edit = QLineEdit()
        self.med_history = QTextEdit()
        self.extra_info = QTextEdit()
        form.addRow("First Name", self.first_edit)
        form.addRow("Last Name", self.last_edit)
        row = QHBoxLayout()
        row.addWidget(self.birth_edit)
        row.addWidget(self.age_label)
        form.addRow("Birth Date", row)
        form.addRow("Address", self.address_edit)
        form.addRow("Telephone", self.phone_edit)
        form.addRow("Register Date", self.register_edit)
        form.addRow("Last Visit", self.last_visit_edit)
        form.addRow("Referral", self.referral_edit)
        form.addRow("Medical History", self.med_history)
        form.addRow("Extra Info", self.extra_info)
        self.tabs.addTab(personal, "Personal Details")
        # Therapy tab
        therapy_tab = QWidget()
        t_layout = QVBoxLayout(therapy_tab)
        t_layout.setContentsMargins(0, 0, 0, 0)
        self.therapy_table = QTableWidget(0, 7)
        self.therapy_table.setHorizontalHeaderLabels([
            "Date", "Tooth", "Description", "Payment", "Cost", "Discount", "Comment"
        ])
        self.therapy_table.verticalHeader().setVisible(False)
        self.therapy_table.horizontalHeader().setStretchLastSection(True)
        self.therapy_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.therapy_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.therapy_table.setAlternatingRowColors(True)
        t_layout.addWidget(self.therapy_table)
        add_btn = QPushButton("Add Entry")
        add_btn.clicked.connect(self.add_therapy)
        t_layout.addWidget(add_btn)
        self.total_label = QLabel()
        t_layout.addWidget(self.total_label)
        self.tabs.addTab(therapy_tab, "Therapy")
        # Buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _update_age(self) -> None:
        bdate = self.birth_edit.date()
        years = bdate.daysTo(QDate.currentDate()) // 365
        self.age_label.setText(f"- {years} years old")

    def add_therapy(self) -> None:
        dlg = TherapyDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.data()
            r = self.therapy_table.rowCount()
            self.therapy_table.insertRow(r)
            for c, key in enumerate(["visit_date", "tooth", "description", "payment", "cost", "discount", "comment"]):
                self.therapy_table.setItem(r, c, QTableWidgetItem(str(data[key])))
            self._update_totals()

    def _update_totals(self) -> None:
        payments = costs = discounts = 0.0
        for r in range(self.therapy_table.rowCount()):
            payments += float(self.therapy_table.item(r, 3).text())
            costs += float(self.therapy_table.item(r, 4).text())
            discounts += float(self.therapy_table.item(r, 5).text())
        owe = costs - payments - discounts
        self.total_label.setText(
            f"Payments: {payments}  Costs: {costs}  Discounts: {discounts}  Owe: {owe}"
        )

    def data(self) -> dict:
        therapies = []
        for r in range(self.therapy_table.rowCount()):
            row = {
                "visit_date": self.therapy_table.item(r, 0).text(),
                "tooth": self.therapy_table.item(r, 1).text(),
                "description": self.therapy_table.item(r, 2).text(),
                "payment": float(self.therapy_table.item(r, 3).text()),
                "cost": float(self.therapy_table.item(r, 4).text()),
                "discount": float(self.therapy_table.item(r, 5).text()),
                "comment": self.therapy_table.item(r, 6).text(),
            }
            therapies.append(row)
        return {
            "first_name": self.first_edit.text(),
            "last_name": self.last_edit.text(),
            "birth_date": self.birth_edit.date().toString("yyyy-MM-dd"),
            "address": self.address_edit.text(),
            "phone": self.phone_edit.text(),
            "register_date": self.register_edit.date().toString("yyyy-MM-dd"),
            "last_visit_date": self.last_visit_edit.date().toString("yyyy-MM-dd"),
            "referral": self.referral_edit.text(),
            "medical_history": self.med_history.toPlainText(),
            "extra_info": self.extra_info.toPlainText(),
            "therapies": therapies,
        }

    def load_data(self, data: dict) -> None:
        self.first_edit.setText(data.get("first_name", ""))
        self.last_edit.setText(data.get("last_name", ""))
        if data.get("birth_date"):
            self.birth_edit.setDate(QDate.fromString(data["birth_date"], "yyyy-MM-dd"))
        if data.get("register_date"):
            self.register_edit.setDate(QDate.fromString(data["register_date"], "yyyy-MM-dd"))
        if data.get("last_visit_date"):
            self.last_visit_edit.setDate(QDate.fromString(data["last_visit_date"], "yyyy-MM-dd"))
        self.address_edit.setText(data.get("address", ""))
        self.phone_edit.setText(data.get("phone", ""))
        self.referral_edit.setText(data.get("referral", ""))
        self.med_history.setPlainText(data.get("medical_history", ""))
        self.extra_info.setPlainText(data.get("extra_info", ""))
        for t in data.get("therapies", []):
            r = self.therapy_table.rowCount()
            self.therapy_table.insertRow(r)
            for c, key in enumerate(["visit_date", "tooth", "description", "payment", "cost", "discount", "comment"]):
                self.therapy_table.setItem(r, c, QTableWidgetItem(str(t.get(key, ""))))
        self._update_totals()

