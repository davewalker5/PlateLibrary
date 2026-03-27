import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_series(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return series values formatted for investigation maintenance."""
    return fetch_lookup(conn, QUERIES["fetch_series"]["sql"])


def fetch_series_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of series for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_series_list"]["sql"])


def fetch_series_record(conn: sqlite3.Connection, series_id: int) -> dict[str, Any] | None:
    """Fetch a single SERIES row for editing."""
    row = conn.execute(QUERIES["fetch_series_record"]["sql"], (series_id,)).fetchone()
    return dict(row) if row else None

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_series(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new SERIES record."""
    conn.execute(
        QUERIES["insert_series"]["sql"],
        (
            values["Name"],
            values["Scheme_Id"],
            values["Code"],
            values["Plate_Format"],
        ),
    )
    conn.commit()


def update_series(conn: sqlite3.Connection, series_id: int, values: dict[str, Any]) -> None:
    """Update an existing SERIES record."""
    conn.execute(
        QUERIES["update_series"]["sql"],
        (
            values["Name"],
            values["Scheme_Id"],
            values["Code"],
            values["Plate_Format"],
            series_id,
        ),
    )
    conn.commit()


def delete_series(conn: sqlite3.Connection, series_id: int) -> None:
    """Delete a SERIES record."""
    conn.execute(QUERIES["delete_series"]["sql"], (series_id,))
    conn.commit()