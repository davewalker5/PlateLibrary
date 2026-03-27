import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_scheme_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of schemes for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_scheme_list"]["sql"])


def fetch_scheme(conn: sqlite3.Connection, scheme_id: int) -> dict[str, Any] | None:
    """Fetch a single SCHEME row for editing."""
    row = conn.execute(QUERIES["fetch_scheme"]["sql"], (scheme_id,)).fetchone()
    return dict(row) if row else None

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_scheme(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new SCHEME record."""
    conn.execute(
        QUERIES["insert_scheme"]["sql"],
        (
            values["Name"],
            values["Code"],
        ),
    )
    conn.commit()


def update_scheme(conn: sqlite3.Connection, scheme_id: int, values: dict[str, Any]) -> None:
    """Update an existing SCHEME record."""
    conn.execute(
        QUERIES["update_scheme"]["sql"],
        (
            values["Name"],
            values["Code"],
            scheme_id,
        ),
    )
    conn.commit()


def delete_scheme(conn: sqlite3.Connection, scheme_id: int) -> None:
    """Delete a SCHEME record."""
    conn.execute(QUERIES["delete_scheme"]["sql"], (scheme_id,))
    conn.commit()
