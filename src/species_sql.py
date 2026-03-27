import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_species(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return species records formatted for a select box."""
    return fetch_lookup(conn, QUERIES["fetch_species"]["sql"])


def fetch_species_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of species for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_species_list"]["sql"])


def fetch_species_record(conn: sqlite3.Connection, species_id: int) -> dict[str, Any] | None:
    """Fetch a single SPECIES row for editing."""
    row = conn.execute(QUERIES["fetch_species_record"]["sql"], (species_id,)).fetchone()
    return dict(row) if row else None

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_species(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new SPECIES record."""
    conn.execute(
        QUERIES["insert_species"]["sql"],
        (
            values["Scientific_Name"],
            values["Common_Name"],
        ),
    )
    conn.commit()


def update_species(conn: sqlite3.Connection, species_id: int, values: dict[str, Any]) -> None:
    """Update an existing SPECIES record."""
    conn.execute(
        QUERIES["update_species"]["sql"],
        (
            values["Scientific_Name"],
            values["Common_Name"],
            species_id,
        ),
    )
    conn.commit()


def delete_species(conn: sqlite3.Connection, species_id: int) -> None:
    """Delete a SPECIES record."""
    conn.execute(QUERIES["delete_species"]["sql"], (species_id,))
    conn.commit()
