"""Customers management page with search and CRUD operations."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QCheckBox,
    QStyle,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter

from customer_dialog import CustomerDialog

import database


class PdfOptionsDialog(QDialog):
    """Dialog allowing the user to choose which customer fields to include."""

    FIELDS = [
        ("phone", "Phone"),
        ("address", "Address"),
        ("birth_date", "Birth Date"),
        ("register_date", "Register Date"),
        ("last_visit_date", "Last Visit"),
        ("referral", "Referral"),
        ("medical_history", "Medical History"),
        ("extra_info", "Extra Info"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Fields")
        layout = QVBoxLayout(self)
        self.checks: dict[str, QCheckBox] = {}
        for key, label in self.FIELDS:
            cb = QCheckBox(label)
            cb.setChecked(True)
            self.checks[key] = cb
            layout.addWidget(cb)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_fields(self) -> list[str]:
        """Return list of selected field keys."""
        return [k for k, cb in self.checks.items() if cb.isChecked()]


class CustomersPage(QWidget):
    """Page for managing customers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_customers()

    def _create_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        search_row = QHBoxLayout()
        search_row.setSpacing(6)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or phone ...")
        self.search_edit.textChanged.connect(self.search_customers)
        self.balance_check = QCheckBox("Show Balance")
        self.balance_check.stateChanged.connect(self.search_customers)

        style = self.style()
        add_btn = QPushButton(style.standardIcon(QStyle.SP_FileDialogNewFolder), "Add")
        add_btn.clicked.connect(self.add_customer)

        edit_btn = QPushButton(style.standardIcon(QStyle.SP_FileDialogContentsView), "Edit")
        edit_btn.clicked.connect(self.edit_customer)

        delete_btn = QPushButton(style.standardIcon(QStyle.SP_TrashIcon), "Delete")
        delete_btn.clicked.connect(self.delete_customer)

        pdf_btn = QPushButton(style.standardIcon(QStyle.SP_DriveDVDIcon), "Print PDF")
        pdf_btn.clicked.connect(self.print_pdf)

        search_row.addWidget(self.search_edit)
        search_row.addWidget(add_btn)
        search_row.addWidget(edit_btn)
        search_row.addWidget(delete_btn)
        search_row.addWidget(pdf_btn)
        search_row.addWidget(self.balance_check)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Name",
            "Phone",
            "Registered",
            "Last Visit",
            "Balance",
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { border: 1px solid #404040; }"
            "QHeaderView::section { background-color: #353535; font-weight: bold; }"
        )

        layout.addLayout(search_row)
        layout.addWidget(self.table)
        layout.addStretch()

    def load_customers(self, customers: list | None = None) -> None:
        """Populate table with customers."""
        show_balance = self.balance_check.isChecked()
        if customers is None:
            customers = database.get_all_customers(show_balance)
        self.table.setRowCount(0)
        for row in customers:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["phone"] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(row["register_date"] or ""))
            self.table.setItem(r, 4, QTableWidgetItem(row["last_visit_date"] or ""))
            if show_balance:
                self.table.setItem(r, 5, QTableWidgetItem(str(row["balance"])))
        if self.table.rowCount():
            self.table.resizeColumnsToContents()

    def search_customers(self) -> None:
        keyword = self.search_edit.text()
        show_balance = self.balance_check.isChecked()
        results = database.search_customers(keyword, show_balance)
        self.load_customers(results)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def add_customer(self) -> None:
        dlg = CustomerDialog(parent=self)
        if dlg.exec() == CustomerDialog.Accepted:
            data = dlg.data()
            cid = database.add_customer(
                data["first_name"],
                data["last_name"],
                data["phone"],
                data["address"],
                data["birth_date"],
                data["register_date"],
                data["last_visit_date"],
                data["referral"],
                data["medical_history"],
                data["extra_info"],
            )
            for t in data["therapies"]:
                database.add_therapy(
                    cid,
                    t["visit_date"],
                    t["tooth"],
                    t["description"],
                    t["payment"],
                    t["cost"],
                    t["discount"],
                    t["comment"],
                )
            self.search_customers()

    def edit_customer(self) -> None:
        cid = self._selected_id()
        if cid is None:
            return
        info = database.get_customer(cid)
        if info is None:
            return
        therapies = list(database.get_therapies(cid))
        data = {
            "first_name": info["first_name"],
            "last_name": info["last_name"],
            "phone": info["phone"],
            "address": info["address"] or "",
            "birth_date": info["birth_date"] or "",
            "register_date": info["register_date"] or "",
            "last_visit_date": info["last_visit_date"] or "",
            "referral": info["referral"] or "",
            "medical_history": info["medical_history"] or "",
            "extra_info": info["extra_info"] or "",
            "therapies": [dict(t) for t in therapies],
        }
        dlg = CustomerDialog(data, self)
        if dlg.exec() == CustomerDialog.Accepted:
            new = dlg.data()
            database.update_customer(
                cid,
                new["first_name"],
                new["last_name"],
                new["phone"],
                new["address"],
                new["birth_date"],
                new["register_date"],
                new["last_visit_date"],
                new["referral"],
                new["medical_history"],
                new["extra_info"],
            )
            # replace therapies
            for t in database.get_therapies(cid):
                database.delete_therapy(t["id"])
            for t in new["therapies"]:
                database.add_therapy(
                    cid,
                    t["visit_date"],
                    t["tooth"],
                    t["description"],
                    t["payment"],
                    t["cost"],
                    t["discount"],
                    t["comment"],
                )
            self.search_customers()

    def delete_customer(self) -> None:
        cid = self._selected_id()
        if cid is None:
            return
        if (
            QMessageBox.question(
                self, "Delete", "Delete selected customer?"
            )
            == QMessageBox.Yes
        ):
            database.delete_customer(cid)
            self.search_customers()

    def print_pdf(self) -> None:
        cid = self._selected_id()
        if cid is None:
            return

        info = database.get_customer(cid)
        if info is None:
            return

        options_dlg = PdfOptionsDialog(self)
        if options_dlg.exec() != QDialog.Accepted:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            f"{info['first_name']}_{info['last_name']}.pdf",
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        selected = options_dlg.selected_fields()
        labels = dict(PdfOptionsDialog.FIELDS)
        text = f"<h1>{info['first_name']} {info['last_name']}</h1><ul>"
        for field in selected:
            value = info[field] or ""
            text += f"<li><b>{labels[field]}:</b> {value}</li>"
        text += "</ul>"

        doctor = database.get_doctor_info()
        if doctor:
            text += (
                "<p style='margin-top:40px'>"
                f"Doctor: {doctor['first_name']} {doctor['last_name']}<br>"
                f"{doctor['speciality'] or ''}<br>"
                f"{doctor['address'] or ''}<br>"
                f"{doctor['telephone'] or ''}"
                "</p>"
            )

        doc = QTextDocument()
        doc.setHtml(text)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        doc.print_(printer)

