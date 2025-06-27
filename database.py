"""Database utilities for the doctor application.

This module handles creation of the SQLite database and provides helper
functions to access and update data. The database file is stored locally as
``data.db`` in the application directory.
"""

from __future__ import annotations

import sqlite3
import shutil
from pathlib import Path
from typing import Iterable, Optional


# Path to the SQLite database file
DB_FILE = Path(__file__).resolve().parent / "data.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    """Create required tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()

    # Table for doctor's information (single row with id=1)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS doctor (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            speciality TEXT,
            telephone TEXT
        )
        """
    )

    # Basic appointments table for demonstrating upcoming appointments
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            appointment_date TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def get_doctor_info() -> Optional[sqlite3.Row]:
    """Return the doctor's information row or ``None`` if not set."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctor WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row


def save_doctor_info(
    first_name: str,
    last_name: str,
    address: str,
    speciality: str,
    telephone: str,
) -> None:
    """Insert or update the doctor's information."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM doctor WHERE id = 1")
    exists = cur.fetchone() is not None
    if exists:
        cur.execute(
            """
            UPDATE doctor
            SET first_name = ?, last_name = ?, address = ?,
                speciality = ?, telephone = ?
            WHERE id = 1
            """,
            (first_name, last_name, address, speciality, telephone),
        )
    else:
        cur.execute(
            """
            INSERT INTO doctor (id, first_name, last_name, address, speciality, telephone)
            VALUES (1, ?, ?, ?, ?, ?)
            """,
            (first_name, last_name, address, speciality, telephone),
        )
    conn.commit()
    conn.close()


def get_upcoming_appointments(limit: int = 5) -> Iterable[sqlite3.Row]:
    """Return upcoming appointments ordered by date."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT patient_name, appointment_date FROM appointments ORDER BY appointment_date LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def export_database(target_path: str | Path) -> None:
    """Copy the database file to ``target_path``."""
    shutil.copy(DB_FILE, target_path)


def import_database(source_path: str | Path) -> None:
    """Replace the current database with ``source_path``."""
    shutil.copy(source_path, DB_FILE)


__all__ = [
    "get_connection",
    "initialize_database",
    "get_doctor_info",
    "save_doctor_info",
    "get_upcoming_appointments",
    "export_database",
    "import_database",
]

