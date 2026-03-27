import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_stains(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return stains formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_stains"]["sql"])


def fetch_stain_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of stains for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_stain_list"]["sql"])


def fetch_stain_record(conn: sqlite3.Connection, stain_id: int) -> dict[str, Any] | None:
    """Fetch a single STAIN row for editing."""
    row = conn.execute(QUERIES["fetch_stain_record"]["sql"], (stain_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_stain(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new STAIN record."""
    conn.execute(
        QUERIES["insert_stain"]["sql"],
        (
            values["Description"],
        ),
    )
    conn.commit()


def update_stain(conn: sqlite3.Connection, stain_id: int, values: dict[str, Any]) -> None:
    """Update an existing STAIN record."""
    conn.execute(
        QUERIES["update_stain"]["sql"],
        (
            values["Description"],
            stain_id,
        ),
    )
    conn.commit()


def delete_stain(conn: sqlite3.Connection, stain_id: int) -> None:
    """Delete a STAIN record."""
    conn.execute(QUERIES["delete_stain"]["sql"], (stain_id,))
    conn.commit()