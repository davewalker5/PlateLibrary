import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_investigations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return investigations formatted for use in the PLATE form."""
    return fetch_lookup(conn, QUERIES["fetch_investigations"]["sql"])

def fetch_investigation(
    conn: sqlite3.Connection, investigation_id: int
) -> dict[str, Any] | None:
    """Fetch a single INVESTIGATION row for editing."""
    row = conn.execute(QUERIES["fetch_investigation"]["sql"], (investigation_id,)).fetchone()
    return dict(row) if row else None

def fetch_investigation_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of investigations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_investigation_list"]["sql"])


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_investigation(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new INVESTIGATION record."""
    conn.execute(
       QUERIES["insert_investigation"]["sql"],
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
        ),
    )
    conn.commit()


def update_investigation(
    conn: sqlite3.Connection,
    investigation_id: int,
    values: dict[str, Any],
) -> None:
    """Update an existing INVESTIGATION record."""
    conn.execute(QUERIES["update_investigation"]["sql"],
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
            investigation_id,
        ),
    )
    conn.commit()
