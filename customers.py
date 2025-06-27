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
    QInputDialog,
    QFileDialog,
)
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter

import database


class CustomersPage(QWidget):
    """Page for managing customers."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_ui()
        self.load_customers()

    def _create_ui(self) -> None:
        layout = QVBoxLayout(self)

        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or phone ...")
        self.search_edit.textChanged.connect(self.search_customers)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_customer)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_customer)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_customer)

        pdf_btn = QPushButton("Print PDF")
        pdf_btn.clicked.connect(self.print_pdf)

        search_row.addWidget(self.search_edit)
        search_row.addWidget(add_btn)
        search_row.addWidget(edit_btn)
        search_row.addWidget(delete_btn)
        search_row.addWidget(pdf_btn)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addLayout(search_row)
        layout.addWidget(self.table)
        layout.addStretch()

    def load_customers(self, customers: list | None = None) -> None:
        """Populate table with customers."""
        if customers is None:
            customers = database.get_all_customers()
        self.table.setRowCount(0)
        for row in customers:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(r, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(r, 2, QTableWidgetItem(row["phone"] or ""))
        if self.table.rowCount():
            self.table.resizeColumnsToContents()

    def search_customers(self) -> None:
        keyword = self.search_edit.text()
        results = database.search_customers(keyword)
        self.load_customers(results)

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def add_customer(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Customer", "Name:")
        if not ok or not name.strip():
            return
        phone, _ = QInputDialog.getText(self, "Add Customer", "Phone:")
        database.add_customer(name.strip(), phone.strip())
        self.search_customers()

    def edit_customer(self) -> None:
        cid = self._selected_id()
        if cid is None:
            return
        current_name = self.table.item(self.table.currentRow(), 1).text()
        current_phone = self.table.item(self.table.currentRow(), 2).text()
        name, ok = QInputDialog.getText(
            self, "Edit Customer", "Name:", text=current_name
        )
        if not ok or not name.strip():
            return
        phone, _ = QInputDialog.getText(
            self, "Edit Customer", "Phone:", text=current_phone
        )
        database.update_customer(cid, name.strip(), phone.strip())
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
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "customers.pdf", "PDF Files (*.pdf)"
        )
        if not path:
            return
        customers = database.get_all_customers()
        text = "<h1>Customers</h1><ul>"
        for c in customers:
            text += f"<li>{c['name']} - {c['phone'] or ''}</li>"
        text += "</ul>"
        doc = QTextDocument()
        doc.setHtml(text)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        doc.print_(printer)

