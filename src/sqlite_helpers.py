import os
import sqlite3
import streamlit as st
from pathlib import Path
from typing import Any

# List of tables expected to be in the target database
TABLES = [
    "CAMERA",
    "INVESTIGATION",
    "LOCATION",
    "MICROSCOPE",
    "OBJECTIVE",
    "PLATE",
    "SCHEME",
    "SERIES",
    "SPECIES",
    "STAIN"
]


# Dictionary of SQL queries used to load, insert, update and delete data
QUERIES = {
    "fetch_species": { "section": "species" },
    "fetch_species_list": { "section": "species" },
    "fetch_species_record": { "section": "species" },
    "fetch_objectives": { "section": "objective" },
    "fetch_cameras": { "section": "camera" },
    "fetch_camera_list": { "section": "camera" },
    "fetch_camera_record": { "section": "camera" },
    "fetch_stains": { "section": "stain" },
    "fetch_locations": { "section": "location" },
    "fetch_series": { "section": "series" },
    "fetch_investigations": { "section": "investigation" },
    "fetch_plate_list": { "section": "plate" },
    "fetch_plate": { "section": "plate" },
    "fetch_investigation_list": { "section": "investigation" },
    "fetch_investigation": { "section": "investigation" },
    "fetch_location_list": { "section": "location" },
    "fetch_location": { "section": "location" },
    "fetch_scheme_list": { "section": "scheme" },
    "fetch_scheme": { "section": "scheme" },
    "fetch_series_list": { "section": "series" },
    "fetch_series_record": { "section": "series" },
    "load_plate_format_for_investigation": { "section": "investigation" },
    "load_existing_plate_references": { "section": "plate" },
    "insert_plate": { "section": "plate" },
    "update_plate": { "section": "plate" },
    "delete_plate": { "section": "plate" },
    "insert_location": { "section": "location" },
    "update_location": { "section": "location" },
    "delete_location": { "section": "location" },
    "insert_investigation": { "section": "investigation" },
    "update_investigation": { "section": "investigation" },
    "insert_scheme": { "section": "scheme" },
    "update_scheme": { "section": "scheme" },
    "delete_scheme": { "section": "scheme" },
    "insert_series": { "section": "series" },
    "update_series": { "section": "series" },
    "delete_series": { "section": "series" },
    "insert_camera": { "section": "camera" },
    "update_camera": { "section": "camera" },
    "delete_camera": { "section": "camera" },
    "insert_species": { "section": "species" },
    "update_species": { "section": "species" },
    "delete_species": { "section": "species" },
    "fetch_microscopes": { "section": "microscope" },
    "fetch_microscope_list": { "section": "microscope" },
    "fetch_microscope_record": { "section": "microscope" },
    "insert_microscope": { "section": "microscope" },
    "update_microscope": { "section": "microscope" },
    "delete_microscope": { "section": "microscope" },
    "fetch_objective_list": { "section": "objective" },
    "fetch_objective_record": { "section": "objective" },
    "insert_objective": { "section": "objective" },
    "update_objective": { "section": "objective" },
    "delete_objective": { "section": "objective" },
    "fetch_stain_list": { "section": "stain" },
    "fetch_stain_record": { "section": "stain" },
    "insert_stain": { "section": "stain" },
    "update_stain": { "section": "stain" },
    "delete_stain": { "section": "stain" },
}

# -----------------------------------------------------------------------------
# SQLite helpers
# -----------------------------------------------------------------------------
def database_path(project_folder: str, db_name: str):
    """Return the default location for the database
    
    If the microscopy plate library environment variable is set, assume the database is in that
    folder. Otherwise, assume a copy of the database in the data folder of the project.
    """
    db_folder = os.getenv("MICROSCOPY_PLATE_LIBRARY")
    if not db_folder:
        db_folder = Path(project_folder) / "data"

    return (Path(db_folder) / db_name).absolute()


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection configured for dictionary-style row access."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Return True if the given table or view exists in the database."""
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type IN ('table', 'view') AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def confirm_schema(conn: sqlite3.Connection) -> bool:
    """Check the schema for the target database is intact"""
    for table in TABLES:
        if not table_exists(conn, table):
            st.error(f"This database does not contain a {table} table.")
            return False
    return True


def fetch_lookup(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    """Execute a lookup query and return the rows as ordinary dictionaries."""
    rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]


def load_sql_queries(project_folder: str):
    """Load the SQL queries"""
    for key in QUERIES.keys():
        file_name = key + ".sql"
        file_path = (Path(project_folder) / "sql" / QUERIES[key]["section"] / file_name).resolve()
        with open(file_path, "r") as f:
            QUERIES[key]["sql"] = f.read()
