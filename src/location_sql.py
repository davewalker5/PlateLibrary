import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_locations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return locations formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_locations"]["sql"])


def fetch_location_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of locations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_location_list"]["sql"])


def fetch_location(conn: sqlite3.Connection, location_id: int) -> dict[str, Any] | None:
    """Fetch a single LOCATION row for editing."""
    row = conn.execute(QUERIES["fetch_location"]["sql"], (location_id,)).fetchone()
    return dict(row) if row else None

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_location(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new LOCATION record."""
    conn.execute(QUERIES["insert_location"]["sql"],
        (
            values["Name"],
            values["Grid_Reference"],
            values["Latitude"],
            values["Longitude"],
        ),
    )
    conn.commit()


def update_location(conn: sqlite3.Connection, location_id: int, values: dict[str, Any]) -> None:
    """Update an existing LOCATION record."""
    conn.execute(
        QUERIES["update_location"]["sql"],
        (
            values["Name"],
            values["Grid_Reference"],
            values["Latitude"],
            values["Longitude"],
            location_id,
        ),
    )
    conn.commit()


def delete_location(conn: sqlite3.Connection, location_id: int) -> None:
    """Delete a LOCATION record."""
    conn.execute(QUERIES["delete_location"]["sql"], (location_id,))
    conn.commit()
