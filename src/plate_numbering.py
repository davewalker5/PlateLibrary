import re
import sqlite3
from sqlite_helpers import QUERIES

# -----------------------------------------------------------------------------
# Plate number suggestion helpers
# -----------------------------------------------------------------------------
def extract_plate_sequence(value: str | None, prefix: str) -> int | None:
    """Extract the main sequence number immediately after PREFIX.

    Supported formats:
        PREFIX + XXX
        PREFIX + XXX + '-' + NNN

    Examples:
        prefix = "SI-II-"
        "SI-II-001" -> 1

        prefix = "PS-LAK-"
        "PS-LAK-003-014" -> 3

    Returns None if the value does not match either supported pattern exactly.
    """
    if value is None:
        return None

    text = str(value).strip()
    pattern = rf"^{re.escape(prefix)}(\d+)(?:-(\d+))?$"
    match = re.match(pattern, text)
    if not match:
        return None

    return int(match.group(1))


def format_plate_code(prefix: str, sequence_number: int, plate_format: str) -> str:
    """Format a suggested plate/reference code for the given series format."""
    main_part = f"{sequence_number:03d}"

    if plate_format == "subsequence":
        return f"{prefix}{main_part}-001"

    return f"{prefix}{main_part}"


def suggest_next_plate_for_investigation(
    conn: sqlite3.Connection, investigation_id: int
) -> str | None:
    """Suggest the next plate/reference code for the selected investigation.

    Numbering is shared across the whole series, not just one investigation.

    Supported formats:
      - simple:      SCHEME-SERIES-XXX
      - subsequence: SCHEME-SERIES-XXX-NNN

    For subsequence series, XXX is incremented and NNN resets to 001.
    """
    row = conn.execute(QUERIES["load_plate_format_for_investigation"]["sql"], (investigation_id,)).fetchone()

    if row is None:
        return None

    scheme_code = (row["Scheme_Code"] or "").strip()
    series_code = (row["Series_Code"] or "").strip()
    series_id = row["Series_Id"]
    plate_format = (row["Plate_Format"] or "simple").strip().lower()

    if not scheme_code or not series_code or series_id is None:
        return None

    prefix = f"{scheme_code}-{series_code}-"

    existing_rows = conn.execute(QUERIES["load_existing_plate_references"]["sql"], (series_id,)).fetchall()

    max_sequence = 0

    for existing_row in existing_rows:
        for candidate in (existing_row["Plate"], existing_row["Reference"]):
            number = extract_plate_sequence(candidate, prefix)
            if number is not None and number > max_sequence:
                max_sequence = number

    next_sequence = max_sequence + 1
    return format_plate_code(prefix, next_sequence, plate_format)