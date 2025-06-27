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

    # Customers table with extended information
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            birth_date TEXT,
            register_date TEXT,
            last_visit_date TEXT,
            referral TEXT,
            medical_history TEXT,
            extra_info TEXT
        )
        """
    )

    # Therapies table linked to customers
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS therapies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            visit_date TEXT NOT NULL,
            tooth TEXT,
            description TEXT,
            payment REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            comment TEXT
        )
        """
    )

    # Migrate older database schemas that used different customer fields.
    # Collect existing column names and add any missing ones so that the
    # application queries work without errors.
    cur.execute("PRAGMA table_info(customers)")
    columns = {row[1] for row in cur.fetchall()}
    expected = {
        "first_name": "TEXT",
        "last_name": "TEXT",
        "phone": "TEXT",
        "address": "TEXT",
        "birth_date": "TEXT",
        "register_date": "TEXT",
        "last_visit_date": "TEXT",
        "referral": "TEXT",
        "medical_history": "TEXT",
        "extra_info": "TEXT",
    }
    for col, ctype in expected.items():
        if col not in columns:
            cur.execute(f"ALTER TABLE customers ADD COLUMN {col} {ctype}")
            # Populate newly added first/last name columns from the legacy
            # ``name`` field if present.
            if col in {"first_name", "last_name"} and "name" in columns:
                if col == "first_name":
                    cur.execute("UPDATE customers SET first_name = name WHERE first_name IS NULL OR first_name = ''")
                else:
                    cur.execute("UPDATE customers SET last_name = '' WHERE last_name IS NULL")

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


def get_total_customers() -> int:
    """Return the number of unique customers based on appointments."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT patient_name) AS count FROM appointments")
    row = cur.fetchone()
    conn.close()
    return row["count"] if row else 0


def _customer_select_clause(show_balance: bool = False) -> str:
    base = (
        "SELECT c.id, c.first_name || ' ' || c.last_name AS name, c.phone, "
        "c.register_date, c.last_visit_date"
    )
    if show_balance:
        base += (
            ", IFNULL(SUM(t.cost - t.payment - t.discount), 0) AS balance "
            "FROM customers c LEFT JOIN therapies t ON c.id = t.customer_id"
            " GROUP BY c.id"
        )
    else:
        base += " FROM customers c"
    return base + " ORDER BY c.last_name, c.first_name"


def get_all_customers(show_balance: bool = False) -> Iterable[sqlite3.Row]:
    """Return all customers ordered by name."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_customer_select_clause(show_balance))
    rows = cur.fetchall()
    conn.close()
    return rows


def search_customers(keyword: str, show_balance: bool = False) -> Iterable[sqlite3.Row]:
    """Return customers matching ``keyword`` in name or phone."""
    conn = get_connection()
    cur = conn.cursor()
    like = f"%{keyword}%"
    query = _customer_select_clause(show_balance)
    query = query.replace("FROM customers c", "FROM customers c")  # no-op to keep patch simple
    query += " HAVING name LIKE ? OR c.phone LIKE ?" if show_balance else " WHERE name LIKE ? OR phone LIKE ?"
    cur.execute(query, (like, like))
    rows = cur.fetchall()
    conn.close()
    return rows


def add_customer(
    first_name: str,
    last_name: str,
    phone: str,
    address: str,
    birth_date: str,
    register_date: str,
    last_visit_date: str,
    referral: str,
    medical_history: str,
    extra_info: str,
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    # Check if legacy ``name`` column exists so inserts don't fail on older
    # databases that still require it.
    cur.execute("PRAGMA table_info(customers)")
    cols = {row[1] for row in cur.fetchall()}
    has_name = "name" in cols

    if has_name:
        cur.execute(
            """
            INSERT INTO customers (
                name, first_name, last_name, phone, address, birth_date,
                register_date, last_visit_date, referral, medical_history,
                extra_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{first_name} {last_name}",
                first_name,
                last_name,
                phone,
                address,
                birth_date,
                register_date,
                last_visit_date,
                referral,
                medical_history,
                extra_info,
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO customers (
                first_name, last_name, phone, address, birth_date,
                register_date, last_visit_date, referral, medical_history,
                extra_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                phone,
                address,
                birth_date,
                register_date,
                last_visit_date,
                referral,
                medical_history,
                extra_info,
            ),
        )

    cid = cur.lastrowid
    conn.commit()
    conn.close()
    return cid


def update_customer(
    cid: int,
    first_name: str,
    last_name: str,
    phone: str,
    address: str,
    birth_date: str,
    register_date: str,
    last_visit_date: str,
    referral: str,
    medical_history: str,
    extra_info: str,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(customers)")
    cols = {row[1] for row in cur.fetchall()}
    has_name = "name" in cols

    if has_name:
        cur.execute(
            """
            UPDATE customers SET name=?, first_name=?, last_name=?, phone=?, address=?,
                birth_date=?, register_date=?, last_visit_date=?, referral=?,
                medical_history=?, extra_info=? WHERE id=?
            """,
            (
                f"{first_name} {last_name}",
                first_name,
                last_name,
                phone,
                address,
                birth_date,
                register_date,
                last_visit_date,
                referral,
                medical_history,
                extra_info,
                cid,
            ),
        )
    else:
        cur.execute(
            """
            UPDATE customers SET first_name=?, last_name=?, phone=?, address=?,
                birth_date=?, register_date=?, last_visit_date=?, referral=?,
                medical_history=?, extra_info=? WHERE id=?
            """,
            (
                first_name,
                last_name,
                phone,
                address,
                birth_date,
                register_date,
                last_visit_date,
                referral,
                medical_history,
                extra_info,
                cid,
            ),
        )
    conn.commit()
    conn.close()


def delete_customer(cid: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM customers WHERE id = ?", (cid,))
    conn.commit()
    conn.close()


def get_customer(cid: int) -> Optional[sqlite3.Row]:
    """Return a single customer by id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id = ?", (cid,))
    row = cur.fetchone()
    conn.close()
    return row


def get_customer_balance(cid: int) -> float:
    """Return the outstanding balance for a customer."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT IFNULL(SUM(cost - payment - discount), 0) AS bal
        FROM therapies WHERE customer_id = ?
        """,
        (cid,),
    )
    row = cur.fetchone()
    conn.close()
    return row["bal"] if row else 0.0


def get_therapies(cid: int) -> Iterable[sqlite3.Row]:
    """Return all therapy entries for a customer."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM therapies WHERE customer_id = ? ORDER BY visit_date",
        (cid,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def add_therapy(
    cid: int,
    visit_date: str,
    tooth: str,
    description: str,
    payment: float,
    cost: float,
    discount: float,
    comment: str,
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO therapies (
            customer_id, visit_date, tooth, description, payment,
            cost, discount, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (cid, visit_date, tooth, description, payment, cost, discount, comment),
    )
    tid = cur.lastrowid
    conn.commit()
    conn.close()
    return tid


def delete_therapy(tid: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM therapies WHERE id = ?", (tid,))
    conn.commit()
    conn.close()


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
    "get_total_customers",
    "get_all_customers",
    "search_customers",
    "add_customer",
    "update_customer",
    "delete_customer",
    "get_customer",
    "get_customer_balance",
    "get_therapies",
    "add_therapy",
    "delete_therapy",
    "export_database",
    "import_database",
]

