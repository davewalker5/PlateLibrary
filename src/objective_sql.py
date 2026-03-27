import sqlite3
from typing import Any
from sqlite_helpers import fetch_lookup, QUERIES

# -----------------------------------------------------------------------------
# Data retrieval queries
# -----------------------------------------------------------------------------
def fetch_objectives(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope objectives formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_objectives"]["sql"])

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
