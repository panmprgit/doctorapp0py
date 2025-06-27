"""Stub for the transactions window."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TransactionsPage(QWidget):
    """Simple placeholder for the transactions page."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Transactions"))
        layout.addStretch()

