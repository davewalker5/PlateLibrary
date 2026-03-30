import sqlite3
from typing import Any
from plate_library.sql.sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_plate_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of plates for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_plate_list"]["sql"])


def fetch_plate(conn: sqlite3.Connection, plate_id: int) -> dict[str, Any] | None:
    """Fetch a single PLATE row for editing."""
    row = conn.execute(QUERIES["fetch_plate"]["sql"], (plate_id,)).fetchone()
    if not row:
        return None

    plate = dict(row)

    stain_ids_raw = plate.get("Stain_Ids")
    if stain_ids_raw:
        plate["Stain_Ids"] = [int(value) for value in stain_ids_raw.split(",")]
    else:
        plate["Stain_Ids"] = []

    return plate


# -----------------------------------------------------------------------------
# PLATE_STAIN helpers
# -----------------------------------------------------------------------------
def _replace_plate_stains(
    conn: sqlite3.Connection,
    plate_id: int,
    stain_ids: list[int] | None,
) -> None:
    """Replace all stain mappings for a plate."""
    conn.execute(
        QUERIES["delete_plate_stains_for_plate"]["sql"],
        (plate_id,),
    )

    if not stain_ids:
        return

    for stain_id in stain_ids:
        conn.execute(
            QUERIES["insert_plate_stain"]["sql"],
            (plate_id, stain_id),
        )


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_plate(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new PLATE record and any PLATE_STAIN links."""
    cursor = conn.cursor()

    cursor.execute(
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
            values["Location_Id"],
            values["Investigation_Id"],
        ),
    )

    plate_id = cursor.lastrowid
    _replace_plate_stains(conn, plate_id, values.get("Stain_Ids"))
    conn.commit()


def update_plate(conn: sqlite3.Connection, plate_id: int, values: dict[str, Any]) -> None:
    """Update an existing PLATE record and replace its PLATE_STAIN links."""
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
            values["Location_Id"],
            values["Investigation_Id"],
            plate_id,
        ),
    )

    _replace_plate_stains(conn, plate_id, values.get("Stain_Ids"))
    conn.commit()


def delete_plate(conn: sqlite3.Connection, plate_id: int) -> None:
    """Delete a PLATE record and its PLATE_STAIN links."""
    conn.execute(
        QUERIES["delete_plate_stains_for_plate"]["sql"],
        (plate_id,),
    )
    conn.execute(QUERIES["delete_plate"]["sql"], (plate_id,))
    conn.commit()