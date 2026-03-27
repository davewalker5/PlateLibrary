import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_plate_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of plates for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_plate_list"]["sql"])


def fetch_plate(conn: sqlite3.Connection, plate_id: int) -> dict[str, Any] | None:
    """Fetch a single PLATE row for editing."""
    row = conn.execute(QUERIES["fetch_plate"]["sql"], (plate_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_plate(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new PLATE record."""
    conn.execute(
        QUERIES["insert_plate"]["sql"],
        (
            values["Date"],
            values["Specimen"],
            values["Plate"],
            values["Reference"],
            values["Notebook_Reference"],
            values["Notes"],
            values["Species_Id"],
            values["Objective_Id"],
            values["Camera_Id"],
            values["Stain_Id"],
            values["Location_Id"],
            values["Investigation_Id"],
        ),
    )
    conn.commit()


def update_plate(conn: sqlite3.Connection, plate_id: int, values: dict[str, Any]) -> None:
    """Update an existing PLATE record."""
    conn.execute(
       QUERIES["update_plate"]["sql"],
        (
            values["Date"],
            values["Specimen"],
            values["Plate"],
            values["Reference"],
            values["Notebook_Reference"],
            values["Notes"],
            values["Species_Id"],
            values["Objective_Id"],
            values["Camera_Id"],
            values["Stain_Id"],
            values["Location_Id"],
            values["Investigation_Id"],
            plate_id,
        ),
    )
    conn.commit()


def delete_plate(conn: sqlite3.Connection, plate_id: int) -> None:
    """Delete a PLATE record."""
    conn.execute(QUERIES["delete_plate"]["sql"], (plate_id,))
    conn.commit()
