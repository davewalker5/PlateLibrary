import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_microscopes(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope values formatted for lookup usage."""
    return fetch_lookup(conn, QUERIES["fetch_microscopes"]["sql"])


def fetch_microscope_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of microscopes for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_microscope_list"]["sql"])


def fetch_microscope_record(conn: sqlite3.Connection, microscope_id: int) -> dict[str, Any] | None:
    """Fetch a single MICROSCOPE row for editing."""
    row = conn.execute(QUERIES["fetch_microscope_record"]["sql"], (microscope_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_microscope(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new MICROSCOPE record."""
    conn.execute(
        QUERIES["insert_microscope"]["sql"],
        (
            values["Description"],
            values["Manufacturer"],
            values["Manufactured"],
            values["Serial_Number"],
        ),
    )
    conn.commit()


def update_microscope(conn: sqlite3.Connection, microscope_id: int, values: dict[str, Any]) -> None:
    """Update an existing MICROSCOPE record."""
    conn.execute(
        QUERIES["update_microscope"]["sql"],
        (
            values["Description"],
            values["Manufacturer"],
            values["Manufactured"],
            values["Serial_Number"],
            microscope_id,
        ),
    )
    conn.commit()


def delete_microscope(conn: sqlite3.Connection, microscope_id: int) -> None:
    """Delete a MICROSCOPE record."""
    conn.execute(QUERIES["delete_microscope"]["sql"], (microscope_id,))
    conn.commit()
