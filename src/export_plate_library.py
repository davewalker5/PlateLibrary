#!/usr/bin/env python3
"""
Export the microscopy plate library from SQLite to CSV.

This script is intentionally small and dependency-free so it can be used
comfortably in a build pipeline. It reads a SQL query from a .sql file,
executes that query against the SQLite database, and writes the result set
to a CSV file using the column names returned by the query itself.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

PROGRAM_NAME = "Microscopy Plate Library Exporter"
PROGRAM_VERSION = "1.0.0"
PROGRAM_DESCRIPTION = "Export the microscopy plate library as a CSV file"


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    The default export SQL is expected to live in sql/export.sql relative to
    the repository root, while this script itself is expected to live in a
    scripts/ directory one level below that root.
    """
    repo_root = Path(__file__).resolve().parent.parent
    default_sql = repo_root / "sql" / "export.sql"

    parser = argparse.ArgumentParser(
        prog=f"{PROGRAM_NAME} v{PROGRAM_VERSION}",
        description=PROGRAM_DESCRIPTION
    )

    parser.add_argument("--db", required=True, help="Path to the input SQLite database file.")
    parser.add_argument("--csv", required=True, help="Path to the output CSV file.")
    parser.add_argument("--sql", default=str(default_sql), help=f"Path to the SQL file to execute (default: {default_sql}).")
    return parser.parse_args()


def read_sql(sql_path: Path) -> str:
    """
    Read and return the SQL text to execute.

    A separate SQL file keeps the export contract visible and easy to tweak
    without editing Python code.
    """
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    return sql_path.read_text(encoding="utf-8")


def export_to_csv(db_path: Path, sql: str, csv_path: Path) -> int:
    """
    Execute the supplied SQL against the SQLite database and write the results
    to the requested CSV file.

    Returns the number of exported rows so the caller can report progress.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Create the output directory automatically so the caller does not need
    # to prepare it in advance.
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    # Fetch all rows first so we can read cursor.description before leaving
    # the database context manager.
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        headers = [description[0] for description in cursor.description]

    # Write a simple UTF-8 CSV with a header row.
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([row[h] for h in headers])

    return len(rows)


def main() -> int:
    """
    Script entry point.

    Returns a process exit code so __main__ can raise SystemExit cleanly.
    """
    args = parse_args()

    db_path = Path(args.db).expanduser().resolve()
    csv_path = Path(args.csv).expanduser().resolve()
    sql_path = Path(args.sql).expanduser().resolve()

    try:
        sql = read_sql(sql_path)
        row_count = export_to_csv(db_path, sql, csv_path)
    except Exception as exc:
        # Keep error handling straightforward for command-line use.
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Exported {row_count} row(s) to {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
