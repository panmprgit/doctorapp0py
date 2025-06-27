from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QCheckBox, QStyle, QHeaderView, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter

from customer_dialog import CustomerDialog
import database

class PdfOptionsDialog(QDialog):
    """Dialog allowing the user to choose which customer fields to include in the PDF."""

    FIELDS = [
        ("phone", "Phone"),
        ("address", "Address"),
        ("birth_date", "Birth Date"),
        ("register_date", "Register Date"),
        ("last_visit_date", "Last Visit"),
        ("referral", "Referral"),
        ("medical_history", "Medical History"),
        ("extra_info", "Extra Info"),
        ("therapies", "Therapies"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Fields for PDF Export")
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
    """Page for managing customers with full CRUD and PDF export functionality."""

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
            "ID", "Name", "Phone", "Registered", "Last Visit", "Balance",
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

    def _safe(self, row, key):
        return row[key] if key in row.keys() and row[key] is not None else ""

    def load_customers(self, customers: list | None = None) -> None:
        """Populate table with customers."""
        show_balance = self.balance_check.isChecked()
        if customers is None:
            customers = database.get_all_customers(show_balance)
        self.table.setRowCount(0)
        for row in customers:
            r = self.table.rowCount()
            self.table.insertRow(r)
            first = self._safe(row, "first_name")
            last = self._safe(row, "last_name")
            if first or last:
                name = f"{first} {last}".strip()
            elif "name" in row.keys() and row["name"]:
                name = row["name"]
            else:
                name = "(No Name)"
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(self._safe(row, "phone")))
            self.table.setItem(r, 3, QTableWidgetItem(self._safe(row, "register_date")))
            self.table.setItem(r, 4, QTableWidgetItem(self._safe(row, "last_visit_date")))
            self.table.setItem(r, 5, QTableWidgetItem(""))
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
        try:
            return int(item.text()) if item else None
        except ValueError:
            return None

    def add_customer(self) -> None:
        dlg = CustomerDialog(parent=self)
        if dlg.exec() == CustomerDialog.Accepted:
            data = dlg.data()
            cid = database.add_customer(
                data.get("first_name", ""),
                data.get("last_name", ""),
                data.get("phone", ""),
                data.get("address", ""),
                data.get("birth_date", ""),
                data.get("register_date", ""),
                data.get("last_visit_date", ""),
                data.get("referral", ""),
                data.get("medical_history", ""),
                data.get("extra_info", ""),
            )
            for t in data.get("therapies", []):
                database.add_therapy(
                    cid,
                    t.get("visit_date", ""),
                    t.get("tooth", ""),
                    t.get("description", ""),
                    t.get("payment", ""),
                    t.get("cost", ""),
                    t.get("discount", ""),
                    t.get("comment", ""),
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
            "first_name": self._safe(info, "first_name"),
            "last_name": self._safe(info, "last_name"),
            "phone": self._safe(info, "phone"),
            "address": self._safe(info, "address"),
            "birth_date": self._safe(info, "birth_date"),
            "register_date": self._safe(info, "register_date"),
            "last_visit_date": self._safe(info, "last_visit_date"),
            "referral": self._safe(info, "referral"),
            "medical_history": self._safe(info, "medical_history"),
            "extra_info": self._safe(info, "extra_info"),
            "therapies": [dict(t) for t in therapies],
        }
        dlg = CustomerDialog(data, self)
        if dlg.exec() == CustomerDialog.Accepted:
            new = dlg.data()
            database.update_customer(
                cid,
                new.get("first_name", ""),
                new.get("last_name", ""),
                new.get("phone", ""),
                new.get("address", ""),
                new.get("birth_date", ""),
                new.get("register_date", ""),
                new.get("last_visit_date", ""),
                new.get("referral", ""),
                new.get("medical_history", ""),
                new.get("extra_info", ""),
            )
            for t in database.get_therapies(cid):
                database.delete_therapy(t["id"])
            for t in new.get("therapies", []):
                database.add_therapy(
                    cid,
                    t.get("visit_date", ""),
                    t.get("tooth", ""),
                    t.get("description", ""),
                    t.get("payment", ""),
                    t.get("cost", ""),
                    t.get("discount", ""),
                    t.get("comment", ""),
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
        """Export selected customer data to a well-styled PDF, skipping empty fields."""
        cid = self._selected_id()
        if cid is None:
            QMessageBox.warning(self, "No Selection", "Please select a customer first.")
            return

        info = database.get_customer(cid)
        if info is None:
            QMessageBox.warning(self, "Error", "Could not retrieve customer data.")
            return

        def getf(key):
            return info[key] if key in info.keys() and info[key] is not None else ""

        options_dlg = PdfOptionsDialog(self)
        if options_dlg.exec() != QDialog.Accepted:
            return

        # Display name logic (always print at top)
        first = getf("first_name")
        last = getf("last_name")
        if first or last:
            display_name = f"{first} {last}".strip()
        elif getf("name"):
            display_name = getf("name")
        else:
            display_name = "(No Name)"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            f"{display_name}.pdf",
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        selected = options_dlg.selected_fields()
        labels = dict(PdfOptionsDialog.FIELDS)

        text = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #2E7D32; }}
            table.data-table {{ border-collapse: collapse; margin-top:16px; }}
            table.data-table td, table.data-table th {{ border:1px solid #888; padding:6px 10px; }}
            table.data-table th {{ background:#f0f0f0; }}
        </style>
        </head>
        <body>
        """

        text += f"<h1>{display_name}</h1>"

        nonempty_found = False
        table_rows = ""
        for field in selected:
            if field == "therapies":
                continue
            value = getf(field)
            if value:
                nonempty_found = True
                label = labels.get(field, field.capitalize())
                table_rows += f"<tr><th>{label}:</th><td>{value}</td></tr>"
        if nonempty_found:
            text += f"<table class='data-table'>{table_rows}</table>"

        if "therapies" in selected:
            therapies = list(database.get_therapies(cid))
            if therapies:
                text += (
                    "<h2 style='margin-top:32px;'>Therapies</h2>"
                    "<table class='data-table'><tr>"
                    "<th>Date</th><th>Tooth</th><th>Description</th><th>Payment</th>"
                    "<th>Cost</th><th>Discount</th><th>Comment</th></tr>"
                )
                for t in therapies:
                    text += (
                        f"<tr>"
                        f"<td>{t.get('visit_date', '')}</td>"
                        f"<td>{t.get('tooth', '')}</td>"
                        f"<td>{t.get('description', '')}</td>"
                        f"<td>{t.get('payment', '')}</td>"
                        f"<td>{t.get('cost', '')}</td>"
                        f"<td>{t.get('discount', '')}</td>"
                        f"<td>{t.get('comment', '')}</td>"
                        f"</tr>"
                    )
                text += "</table>"
            else:
                text += "<p>No therapies recorded.</p>"

        doctor = database.get_doctor_info()
        if doctor:
            def docf(key): return doctor[key] if key in doctor.keys() and doctor[key] is not None else ""
            doctor_name = ""
            if docf("first_name") or docf("last_name"):
                doctor_name = f"{docf('first_name')} {docf('last_name')}".strip()
            elif docf("name"):
                doctor_name = docf("name")
            text += (
                "<div style='margin-top:40px; font-size:13px;'>"
                f"<b>Doctor:</b> {doctor_name}<br>"
                f"{docf('speciality')}<br>"
                f"{docf('address')}<br>"
                f"{docf('telephone')}"
                "</div>"
            )

        text += "</body></html>"

        doc = QTextDocument()
        doc.setHtml(text)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        try:
            doc.print_(printer)
            QMessageBox.information(self, "Success", f"PDF exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not export PDF:\n{e}")
