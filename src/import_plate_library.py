#!/usr/bin/env python3
"""
Import plate-library records from an XLSX spreadsheet into the SQLite database.

This importer is deliberately conservative:
- it validates required spreadsheet columns,
- it looks up foreign keys in the database rather than trusting text values,
- it can either skip/report bad rows or fail fast in strict mode,
- and it can optionally clear PLATE before re-importing.

The script currently imports into PLATE only. Lookup tables such as SPECIES,
OBJECTIVE and INVESTIGATION are expected to have been seeded already.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

PROGRAM_NAME = "Microscopy Plate Library Importer"
PROGRAM_VERSION = "1.0.0"
PROGRAM_DESCRIPTION = "Import the microscopy plate library from a spreadsheet"


@dataclass
class PlateRow:
    """
    Simple in-memory representation of one spreadsheet row.

    Using a dataclass keeps the later import logic readable and avoids passing
    raw pandas row objects around the rest of the script.
    """
    date: str
    common_name: str
    specimen: str
    plate: str
    reference: str
    investigation: str
    objective: str
    notebook_reference: str
    notes: str


def clean(value: object) -> str:
    """
    Normalise a value read from pandas.

    Empty cells, NaN values and None are all converted to an empty string so the
    rest of the import code can treat them consistently.
    """
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def parse_date(value) -> str:
    """
    Convert the spreadsheet date value into a SQLite-friendly timestamp string.

    Accepted inputs:
    - pandas Timestamp / Excel datetime
    - string in DD/MM/YYYY
    - string in DD/MM/YY
    - string in ISO form YYYY-MM-DD HH:MM:SS
    - string in ISO date form YYYY-MM-DD

    The returned format is always YYYY-MM-DD HH:MM:SS for consistency.
    """
    if value is None:
        raise ValueError("Date is empty")

    # Handle pandas/Excel datetime values directly.
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    value = str(value).strip()
    if not value:
        raise ValueError("Date is empty")

    for fmt in (
        "%d/%m/%Y",
        "%d/%m/%y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    raise ValueError(f"Unrecognised date format: {value!r}")


def get_first_camera_id(conn: sqlite3.Connection) -> int:
    """
    Return the first CAMERA.Id in the database.

    The current importer applies a single camera to all imported rows. That is
    intentional for now, because the source spreadsheet does not carry camera
    information per row.
    """
    row = conn.execute(
        "SELECT Id FROM CAMERA ORDER BY Id ASC LIMIT 1"
    ).fetchone()
    if row is None:
        raise RuntimeError("No rows found in CAMERA; seed CAMERA first.")
    return int(row[0])


def lookup_species_id(conn: sqlite3.Connection, common_name: str) -> Optional[int]:
    """
    Look up SPECIES.Id by Common_Name.

    Returns None for a blank common name or when no matching record exists.
    """
    common_name = clean(common_name)
    if not common_name:
        return None

    row = conn.execute(
        "SELECT Id FROM SPECIES WHERE Common_Name = ?",
        (common_name,),
    ).fetchone()

    return None if row is None else int(row[0])


def lookup_investigation_id(
    conn: sqlite3.Connection, investigation_reference: str
) -> Optional[int]:
    """
    Look up INVESTIGATION.Id by Reference.
    """
    investigation_reference = clean(investigation_reference)
    if not investigation_reference:
        return None

    row = conn.execute(
        "SELECT Id FROM INVESTIGATION WHERE Reference = ?",
        (investigation_reference,),
    ).fetchone()

    return None if row is None else int(row[0])


def lookup_objective_id(conn: sqlite3.Connection, objective_description: str) -> Optional[int]:
    """
    Look up OBJECTIVE.Id by Description.
    """
    objective_description = clean(objective_description)
    if not objective_description:
        return None

    row = conn.execute(
        "SELECT Id FROM OBJECTIVE WHERE Description = ?",
        (objective_description,),
    ).fetchone()

    return None if row is None else int(row[0])


def load_rows(xlsx_path: Path) -> list[PlateRow]:
    """
    Read the spreadsheet and convert each row into a PlateRow instance.

    Column names are treated as part of the import contract. If a required
    column is missing, the import stops immediately with a clear error.
    """
    df = pd.read_excel(xlsx_path)

    required_columns = [
        "Date",
        "Common Name",
        "Specimen",
        "Plate",
        "Reference",
        "Investigation",
        "Objective",
        "Notebook Reference",
        "Notes",
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise RuntimeError(f"XLSX is missing required columns: {missing}")

    rows: list[PlateRow] = []

    for _, r in df.iterrows():
        rows.append(
            PlateRow(
                date=clean(r.get("Date")),
                common_name=clean(r.get("Common Name")),
                specimen=clean(r.get("Specimen")),
                plate=clean(r.get("Plate")),
                reference=clean(r.get("Reference")),
                investigation=clean(r.get("Investigation")),
                objective=clean(r.get("Objective")),
                notebook_reference=clean(r.get("Notebook Reference")),
                notes=clean(r.get("Notes")),
            )
        )

    return rows


def import_rows(
    conn: sqlite3.Connection,
    rows: list[PlateRow],
    *,
    truncate_plate: bool,
    strict: bool,
) -> None:
    """
    Import the supplied rows into PLATE.

    In non-strict mode, bad rows are collected and reported at the end while the
    rest of the import continues. In strict mode, the first bad row aborts the
    whole import immediately.
    """
    conn.execute("PRAGMA foreign_keys = ON")

    if truncate_plate:
        print("Clearing PLATE table...")
        conn.execute("DELETE FROM PLATE")

    camera_id = get_first_camera_id(conn)
    print(f"Using CAMERA.Id = {camera_id} for all imported rows.")

    inserted = 0
    skipped = 0
    errors: list[str] = []

    for i, row in enumerate(rows, start=2):  # Header is row 1 in Excel.
        try:
            plate_date = parse_date(row.date)
            species_id = lookup_species_id(conn, row.common_name)
            investigation_id = lookup_investigation_id(conn, row.investigation)
            objective_id = lookup_objective_id(conn, row.objective)

            if row.common_name and species_id is None:
                raise ValueError(
                    f"Unknown species Common_Name {row.common_name!r}"
                )

            if row.investigation and investigation_id is None:
                raise ValueError(
                    f"Unknown investigation Reference {row.investigation!r}"
                )

            if objective_id is None:
                raise ValueError(
                    f"Unknown objective Description {row.objective!r}"
                )

            conn.execute(
                """
                INSERT INTO PLATE (
                    Date,
                    Specimen,
                    Plate,
                    Reference,
                    Notebook_Reference,
                    Notes,
                    Species_Id,
                    Objective_Id,
                    Camera_Id,
                    Investigation_Id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plate_date,
                    row.specimen,
                    row.plate,
                    row.reference,
                    row.notebook_reference or None,
                    row.notes or None,
                    species_id,
                    objective_id,
                    camera_id,
                    investigation_id,
                ),
            )
            inserted += 1

        except Exception as exc:
            message = f"XLSX row {i}: {exc}"
            if strict:
                raise RuntimeError(message) from exc
            errors.append(message)
            skipped += 1

    conn.commit()

    print(f"Inserted: {inserted}")
    print(f"Skipped:  {skipped}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"- {err}")


def main() -> None:
    """
    Parse command-line arguments, validate file paths and run the import.
    """
    parser = argparse.ArgumentParser(
        prog=f"{PROGRAM_NAME} v{PROGRAM_VERSION}",
        description=PROGRAM_DESCRIPTION
    )

    parser.add_argument("--db", required=True, help="Path to SQLite database file, e.g. data/plate_library.db")
    parser.add_argument("--xlsx", required=True, help="Path to source XLSX file")
    parser.add_argument("--truncate-plate", action="store_true", help="Delete all rows from PLATE before import")
    parser.add_argument("--strict", action="store_true", help="Abort on first bad row instead of skipping/reporting errors")

    args = parser.parse_args()

    db_path = Path(args.db)
    xlsx_path = Path(args.xlsx)

    if not db_path.exists():
        raise SystemExit(f"Database file not found: {db_path}")

    if not xlsx_path.exists():
        raise SystemExit(f"XLSX file not found: {xlsx_path}")

    rows = load_rows(xlsx_path)
    print(f"Loaded {len(rows)} rows from {xlsx_path}")

    with sqlite3.connect(db_path) as conn:
        import_rows(
            conn,
            rows,
            truncate_plate=args.truncate_plate,
            strict=args.strict,
        )


if __name__ == "__main__":
    main()
