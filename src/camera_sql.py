import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_cameras(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return camera records formatted for the select box."""
    return fetch_lookup(conn, QUERIES["fetch_cameras"]["sql"])

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
