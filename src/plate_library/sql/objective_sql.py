import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_objectives(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope objectives formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_objectives"]["sql"])
def fetch_objective_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of objectives for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_objective_list"]["sql"])


def fetch_objective_record(conn: sqlite3.Connection, objective_id: int) -> dict[str, Any] | None:
    """Fetch a single OBJECTIVE row for editing."""
    row = conn.execute(QUERIES["fetch_objective_record"]["sql"], (objective_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_objective(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new OBJECTIVE record."""
    conn.execute(
        QUERIES["insert_objective"]["sql"],
        (
            values["Microscope_Id"],
            values["Description"],
            values["Magnification"],
        ),
    )
    conn.commit()


def update_objective(conn: sqlite3.Connection, objective_id: int, values: dict[str, Any]) -> None:
    """Update an existing OBJECTIVE record."""
    conn.execute(
        QUERIES["update_objective"]["sql"],
        (
            values["Microscope_Id"],
            values["Description"],
            values["Magnification"],
            objective_id,
        ),
    )
    conn.commit()


def delete_objective(conn: sqlite3.Connection, objective_id: int) -> None:
    """Delete an OBJECTIVE record."""
    conn.execute(QUERIES["delete_objective"]["sql"], (objective_id,))
    conn.commit()
