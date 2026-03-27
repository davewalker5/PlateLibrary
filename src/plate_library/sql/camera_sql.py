import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_cameras(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return camera records formatted for the select box."""
    return fetch_lookup(conn, QUERIES["fetch_cameras"]["sql"])

def fetch_camera_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of cameras for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_camera_list"]["sql"])


def fetch_camera_record(conn: sqlite3.Connection, camera_id: int) -> dict[str, Any] | None:
    """Fetch a single CAMERA row for editing."""
    row = conn.execute(QUERIES["fetch_camera_record"]["sql"], (camera_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_camera(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new CAMERA record."""
    conn.execute(
        QUERIES["insert_camera"]["sql"],
        (
            values["Description"],
            values["Lower_Effective_Magnification"],
            values["Upper_Effective_Magnification"],
        ),
    )
    conn.commit()


def update_camera(conn: sqlite3.Connection, camera_id: int, values: dict[str, Any]) -> None:
    """Update an existing CAMERA record."""
    conn.execute(
        QUERIES["update_camera"]["sql"],
        (
            values["Description"],
            values["Lower_Effective_Magnification"],
            values["Upper_Effective_Magnification"],
            camera_id,
        ),
    )
    conn.commit()


def delete_camera(conn: sqlite3.Connection, camera_id: int) -> None:
    """Delete a CAMERA record."""
    conn.execute(QUERIES["delete_camera"]["sql"], (camera_id,))
    conn.commit()
