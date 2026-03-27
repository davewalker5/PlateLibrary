"""Streamlit maintenance UI for the microscopy plate library.

This script provides a deliberately simple local web UI for maintaining the
fast-moving tables in the plate library database:

- PLATE
- INVESTIGATION
- LOCATION

The application is intended to sit alongside Datasette:

- Streamlit is used for data entry and editing
- Datasette is used for browsing, querying and verifying the data

The rest of the lookup tables are assumed to change only occasionally and can
be maintained separately when needed. LOCATION is included because it is a
regular part of specimen and plate entry.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any
import argparse
import re
import streamlit as st


PROGRAM_NAME = "Microscopy Plate Library Maintenance UI"
PROGRAM_VERSION = "1.0.0"
PROGRAM_DESCRIPTION = "Maintenance UI for the microscopy plate library"

# Default location for the local Datasette instance and database name
DEFAULT_DATASETTE_URL = "http://127.0.0.1:8001"
DB_NAME = "plate_library.db"

# Root folder of the project
PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))

QUERIES = {
    "fetch_species": None,
    "fetch_objectives": None,
    "fetch_cameras": None,
    "fetch_stains": None,
    "fetch_locations": None,
    "fetch_series": None,
    "fetch_investigations": None,
    "fetch_plate_list": None,
    "fetch_plate": None,
    "fetch_investigation_list": None,
    "fetch_investigation": None,
    "fetch_location_list": None,
    "fetch_location": None,
    "load_plate_format_for_investigation": None,
    "load_existing_plate_references": None,
    "insert_plate": None,
    "update_plate": None,
    "delete_plate": None,
    "insert_location": None,
    "update_investigation": None,
    "update_location": None,
    "delete_location": None,
    "insert_investigation": None,
}

# -----------------------------------------------------------------------------
# SQLite helpers
# -----------------------------------------------------------------------------
def database_path():
    """Return the default location for the database
    
    If the microscopy plate library environment variable is set, assume the database is in that
    folder. Otherwise, assume a copy of the database in the data folder of the project.
    """
    db_folder = os.getenv("MICROSCOPY_PLATE_LIBRARY")
    if not db_folder:
        db_folder = Path(PROJECT_FOLDER) / "data"

    return (Path(db_folder) / DB_NAME).absolute()


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


def fetch_lookup(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    """Execute a lookup query and return the rows as ordinary dictionaries."""
    rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]


def load_sql_queries():
    """Load the SQL queries"""
    for key in QUERIES.keys():
        file_name = key + ".sql"
        file_path = (Path(PROJECT_FOLDER) / "sql" / file_name).resolve()
        with open(file_path, "r") as f:
            QUERIES[key] = f.read()


# -----------------------------------------------------------------------------
# Lookup queries used by the PLATE, INVESTIGATION and LOCATION forms
# -----------------------------------------------------------------------------
def fetch_species(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return species records formatted for a select box."""
    return fetch_lookup(conn, QUERIES["fetch_species"])


def fetch_objectives(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope objectives formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_objectives"])


def fetch_cameras(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return camera records formatted for the select box."""
    return fetch_lookup(conn, QUERIES["fetch_cameras"])


def fetch_stains(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return stains formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_stains"])


def fetch_locations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return locations formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_locations"])


def fetch_series(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return series values formatted for investigation maintenance."""
    return fetch_lookup(conn, QUERIES["fetch_series"])


def fetch_investigations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return investigations formatted for use in the PLATE form."""
    return fetch_lookup(conn, QUERIES["fetch_investigations"])


# -----------------------------------------------------------------------------
# Record queries for browsing and editing
# -----------------------------------------------------------------------------
def fetch_plate_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of plates for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_plate_list"])


def fetch_plate(conn: sqlite3.Connection, plate_id: int) -> dict[str, Any] | None:
    """Fetch a single PLATE row for editing."""
    row = conn.execute(QUERIES["fetch_plate"], (plate_id,)).fetchone()
    return dict(row) if row else None


def fetch_investigation_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of investigations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_investigation_list"])


def fetch_investigation(
    conn: sqlite3.Connection, investigation_id: int
) -> dict[str, Any] | None:
    """Fetch a single INVESTIGATION row for editing."""
    row = conn.execute(QUERIES["fetch_investigation"], (investigation_id,)).fetchone()
    return dict(row) if row else None


def fetch_location_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of locations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_location_list"])


def fetch_location(conn: sqlite3.Connection, location_id: int) -> dict[str, Any] | None:
    """Fetch a single LOCATION row for editing."""
    row = conn.execute(QUERIES["fetch_location"], (location_id,)).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# Data conversion helpers
# -----------------------------------------------------------------------------
def parse_db_date(value: Any) -> date:
    """Convert a database date value into a Python date for Streamlit.

    The database may contain plain ISO dates, ISO datetimes or dates from older
    import steps, so this function accepts several common formats.
    """
    if value is None:
        return date.today()

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    text = str(value).strip()
    if not text:
        return date.today()

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return date.today()


def option_index(options: list[dict[str, Any]], selected_id: int | None) -> int:
    """Return the select-box index for the given foreign key value."""
    if selected_id is None:
        return 0

    for idx, option in enumerate(options):
        if option["Id"] == selected_id:
            return idx
    return 0


def selected_fk(option: dict[str, Any] | None) -> int | None:
    """Extract the foreign-key Id from a selected option dictionary."""
    if option is None:
        return None
    return option["Id"]


def make_nullable_options(
    options: list[dict[str, Any]], placeholder: str = "— None —"
) -> list[dict[str, Any]]:
    """Prepend a null option to a lookup list for optional relationships."""
    return [{"Id": None, "Label": placeholder}] + options


def form_key_base(entity: str, mode: str, record_id: int | None = None) -> str:
    """Return a stable widget-key prefix for one rendered form instance.

    Including the record id for edit forms forces Streamlit to treat each
    selected record as a fresh set of widgets, which prevents values from a
    previously edited record from lingering in optional fields.
    """
    suffix = "new" if record_id is None else str(record_id)
    return f"{entity}_{mode}_{suffix}"


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
    row = conn.execute(QUERIES["load_plate_format_for_investigation"], (investigation_id,)).fetchone()

    if row is None:
        return None

    scheme_code = (row["Scheme_Code"] or "").strip()
    series_code = (row["Series_Code"] or "").strip()
    series_id = row["Series_Id"]
    plate_format = (row["Plate_Format"] or "simple").strip().lower()

    if not scheme_code or not series_code or series_id is None:
        return None

    prefix = f"{scheme_code}-{series_code}-"

    existing_rows = conn.execute(QUERIES["load_existing_plate_references"], (series_id,)).fetchall()

    max_sequence = 0

    for existing_row in existing_rows:
        for candidate in (existing_row["Plate"], existing_row["Reference"]):
            number = extract_plate_sequence(candidate, prefix)
            if number is not None and number > max_sequence:
                max_sequence = number

    next_sequence = max_sequence + 1
    return format_plate_code(prefix, next_sequence, plate_format)


# -----------------------------------------------------------------------------
# Generic UI helpers used by the repeated maintenance screens
# -----------------------------------------------------------------------------
def filter_rows(rows: list[dict[str, Any]], search_text: str) -> list[dict[str, Any]]:
    """Return rows filtered by a simple case-insensitive free-text search.

    This deliberately searches across the string representation of each value so
    that the browse tabs stay lightweight and easy to understand. For a small
    local maintenance UI, the simplicity is more valuable than building a more
    elaborate per-column filter system.
    """
    if not search_text.strip():
        return rows

    needle = search_text.strip().lower()
    return [
        row
        for row in rows
        if any(needle in str(value).lower() for value in row.values())
    ]


def build_edit_options(
    rows: list[dict[str, Any]],
    label_builder,
) -> list[dict[str, Any]]:
    """Convert browse rows into select-box options for the edit tab.

    Each entity uses a slightly different human-readable label, so the caller
    supplies a small label-building function while the common wrapping logic
    lives here.
    """
    return [{"Id": row["Id"], "Label": label_builder(row)} for row in rows]


def render_browse_table(
    rows: list[dict[str, Any]],
    *,
    entity_name: str,
    search_key: str,
    search_label: str,
) -> int | None:
    """Render a searchable selectable table and return the selected record Id."""
    search = st.text_input(search_label, key=search_key)

    if not rows:
        st.info(f"No {entity_name} found.")
        return None

    filtered_rows = filter_rows(rows, search)

    event = st.dataframe(
        filtered_rows,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"{entity_name}_browse_table",
    )
    st.caption(f"{len(filtered_rows)} {entity_name}(s) shown")

    selected_rows = event.selection.rows
    if not selected_rows:
        return None

    selected_idx = selected_rows[0]
    return int(filtered_rows[selected_idx]["Id"])


def render_maintenance_section(
    *,
    conn: sqlite3.Connection,
    db_file: Path,
    datasette_url: str,
    entity_name: str,
    add_title: str,
    edit_title: str,
    browse_title: str,
    fetch_list,
    fetch_record,
    render_form,
    edit_select_label: str,
    edit_select_key: str,
    search_key: str,
    search_label: str,
    option_label_builder,
) -> None:
    """Render the repeated add/edit/browse pattern for one entity type.

    Uses a segmented control instead of st.tabs so the active view can be
    driven reliably from session state after a row is selected in Browse.
    """
    view_key = f"{entity_name}_view"
    pending_view_key = f"{entity_name}_pending_view"
    selected_id_key = f"{entity_name}_selected_id"

    views = [add_title, edit_title, browse_title]

    # Apply any deferred view change BEFORE the widget is instantiated.
    if pending_view_key in st.session_state:
        st.session_state[view_key] = st.session_state.pop(pending_view_key)

    if view_key not in st.session_state:
        st.session_state[view_key] = add_title

    active_view = st.segmented_control(
        "Mode",
        options=views,
        default=st.session_state[view_key],
        key=view_key,
        selection_mode="single",
        label_visibility="collapsed",
    )

    if active_view == add_title:
        st.subheader(add_title)
        render_form(
            conn,
            mode="add",
            db_file=db_file,
            datasette_url=datasette_url,
        )

    elif active_view == edit_title:
        st.subheader(edit_title)
        rows = fetch_list(conn)

        if not rows:
            st.info(f"No {entity_name} yet.")
        else:
            edit_options = build_edit_options(rows, option_label_builder)

            default_index = 0
            selected_id = st.session_state.get(selected_id_key)

            if selected_id is not None:
                for idx, option in enumerate(edit_options):
                    if option["Id"] == selected_id:
                        default_index = idx
                        break

            selected = st.selectbox(
                edit_select_label,
                options=edit_options,
                index=default_index,
                format_func=lambda x: x["Label"],
                key=edit_select_key,
            )

            st.session_state[selected_id_key] = int(selected["Id"])

            record = fetch_record(conn, int(selected["Id"]))
            if record is not None:
                render_form(
                    conn,
                    mode="edit",
                    db_file=db_file,
                    datasette_url=datasette_url,
                    **{entity_name: record},
                )

    elif active_view == browse_title:
        st.subheader(f"Current {entity_name}s")
        rows = fetch_list(conn)
        clicked_id = render_browse_table(
            rows,
            entity_name=entity_name,
            search_key=search_key,
            search_label=search_label,
        )

        if clicked_id is not None:
            st.session_state[selected_id_key] = clicked_id
            st.session_state[pending_view_key] = edit_title
            st.rerun()

# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_plate(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new PLATE record."""
    conn.execute(
        QUERIES["insert_plate"],
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
       QUERIES["update_plate"],
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
    conn.execute(QUERIES["delete_plate"], (plate_id,))
    conn.commit()


def insert_investigation(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new INVESTIGATION record."""
    conn.execute(
       QUERIES["insert_investigation"],
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
        ),
    )
    conn.commit()


def update_investigation(
    conn: sqlite3.Connection,
    investigation_id: int,
    values: dict[str, Any],
) -> None:
    """Update an existing INVESTIGATION record."""
    conn.execute(QUERIES["update_investigation"],
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
            investigation_id,
        ),
    )
    conn.commit()


def insert_location(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new LOCATION record."""
    conn.execute(QUERIES["insert_location"],
        (
            values["Name"],
            values["Grid_Reference"],
            values["Latitude"],
            values["Longitude"],
        ),
    )
    conn.commit()


def update_location(conn: sqlite3.Connection, location_id: int, values: dict[str, Any]) -> None:
    """Update an existing LOCATION record."""
    conn.execute(
        QUERIES["update_location"],
        (
            values["Name"],
            values["Grid_Reference"],
            values["Latitude"],
            values["Longitude"],
            location_id,
        ),
    )
    conn.commit()


def delete_location(conn: sqlite3.Connection, location_id: int) -> None:
    """Delete a LOCATION record."""
    conn.execute(QUERIES["delete_location"], (location_id,))
    conn.commit()


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_plate_url(base_url: str, db_file: Path, plate_id: int) -> str:
    """Build the Datasette URL for a PLATE record.

    Datasette uses the database filename stem as the database name in the URL.
    For example, plate_library.db becomes /plate_library/PLATE/123.
    """
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/PLATE/{plate_id}"


def datasette_investigation_url(
    base_url: str, db_file: Path, investigation_id: int
) -> str:
    """Build the Datasette URL for an INVESTIGATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/INVESTIGATION/{investigation_id}"


def datasette_location_url(base_url: str, db_file: Path, location_id: int) -> str:
    """Build the Datasette URL for a LOCATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/LOCATION/{location_id}"


# -----------------------------------------------------------------------------
# Streamlit form renderers
# -----------------------------------------------------------------------------
def apply_plate_defaults_from_investigation(
    key_base: str,
    investigation_id: int | None,
    suggested_plate: str | None,
) -> None:
    """Populate Plate and Reference defaults when the investigation changes.

    This only auto-fills when the values are blank or still match the previous
    auto-generated suggestion, so manual edits are preserved.
    """
    plate_key = f"{key_base}_plate"
    reference_key = f"{key_base}_reference"
    tracking_key = f"{key_base}_last_suggested_plate"
    investigation_key = f"{key_base}_last_investigation_id"

    previous_suggestion = st.session_state.get(tracking_key)
    previous_investigation_id = st.session_state.get(investigation_key)

    investigation_changed = previous_investigation_id != investigation_id

    if investigation_changed and suggested_plate:
        current_plate = st.session_state.get(plate_key, "")
        current_reference = st.session_state.get(reference_key, "")

        if not current_plate or current_plate == previous_suggestion:
            st.session_state[plate_key] = suggested_plate

        if not current_reference or current_reference == previous_suggestion:
            st.session_state[reference_key] = suggested_plate

    st.session_state[investigation_key] = investigation_id
    st.session_state[tracking_key] = suggested_plate or ""


def render_plate_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    plate: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for PLATE records."""
    species_options = make_nullable_options(fetch_species(conn))
    objective_options = fetch_objectives(conn)
    camera_options = fetch_cameras(conn)
    stain_options = make_nullable_options(fetch_stains(conn))
    location_options = make_nullable_options(fetch_locations(conn))
    investigation_options = fetch_investigations(conn)

    if not objective_options or not camera_options or not investigation_options:
        st.error(
            "OBJECTIVE, CAMERA and INVESTIGATION must contain data before you can add or edit plates."
        )
        return

    plate = plate or {}
    plate_id = int(plate["Id"]) if plate.get("Id") is not None else None
    key_base = form_key_base("plate", mode, plate_id)

    default_date = parse_db_date(plate.get("Date")) if mode == "edit" else None

    if mode == "add":
        objective_form_options = make_nullable_options(
            objective_options,
            placeholder="— Select objective —",
        )
        camera_form_options = make_nullable_options(
            camera_options,
            placeholder="— Select camera —",
        )
        investigation_form_options = make_nullable_options(
            investigation_options,
            placeholder="— Select investigation —",
        )
        default_objective_id = None
        default_camera_id = None
        default_investigation_id = None
    else:
        objective_form_options = objective_options
        camera_form_options = camera_options
        investigation_form_options = investigation_options
        default_objective_id = plate.get("Objective_Id")
        default_camera_id = plate.get("Camera_Id")
        default_investigation_id = plate.get("Investigation_Id")

    # In add mode, place Investigation outside the form so that changing it
    # triggers a rerun and can refresh the suggested Plate / Reference values.
    if mode == "add":
        investigation = st.selectbox(
            "Investigation *",
            options=investigation_form_options,
            index=option_index(investigation_form_options, default_investigation_id),
            format_func=lambda x: x["Label"],
            key=f"{key_base}_investigation",
        )

        selected_investigation_id = selected_fk(investigation)
        suggested_plate = None
        if selected_investigation_id is not None:
            suggested_plate = suggest_next_plate_for_investigation(
                conn,
                selected_investigation_id,
            )

        apply_plate_defaults_from_investigation(
            key_base=key_base,
            investigation_id=selected_investigation_id,
            suggested_plate=suggested_plate,
        )

        if suggested_plate:
            st.caption(f"Suggested next plate/reference: {suggested_plate}")
    else:
        selected_investigation_id = plate.get("Investigation_Id")
        suggested_plate = None

    with st.form(
        f"{mode}_plate_form_{plate_id if plate_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        col1, col2 = st.columns(2)

        with col1:
            plate_date = st.date_input(
                "Date",
                value=default_date,
                key=f"{key_base}_date",
            )
            specimen = st.text_input(
                "Specimen",
                value=plate.get("Specimen") or "",
                key=f"{key_base}_specimen",
            )
            plate_code = st.text_input(
                "Plate",
                value=plate.get("Plate") or "",
                key=f"{key_base}_plate",
            )
            reference = st.text_input(
                "Reference",
                value=plate.get("Reference") or "",
                key=f"{key_base}_reference",
            )

        with col2:
            notebook_reference = st.text_input(
                "Notebook Reference",
                value=plate.get("Notebook_Reference") or "",
                key=f"{key_base}_notebook_reference",
            )
            species = st.selectbox(
                "Species",
                options=species_options,
                index=option_index(species_options, plate.get("Species_Id")),
                format_func=lambda x: x["Label"],
                key=f"{key_base}_species",
            )
            objective = st.selectbox(
                "Objective *",
                options=objective_form_options,
                index=option_index(objective_form_options, default_objective_id),
                format_func=lambda x: x["Label"],
                key=f"{key_base}_objective",
            )
            camera = st.selectbox(
                "Camera *",
                options=camera_form_options,
                index=option_index(camera_form_options, default_camera_id),
                format_func=lambda x: x["Label"],
                key=f"{key_base}_camera",
            )

        stain = st.selectbox(
            "Stain",
            options=stain_options,
            index=option_index(stain_options, plate.get("Stain_Id")),
            format_func=lambda x: x["Label"],
            key=f"{key_base}_stain",
        )

        location = st.selectbox(
            "Location",
            options=location_options,
            index=option_index(location_options, plate.get("Location_Id")),
            format_func=lambda x: x["Label"],
            key=f"{key_base}_location",
        )

        if mode == "edit":
            investigation = st.selectbox(
                "Investigation *",
                options=investigation_form_options,
                index=option_index(investigation_form_options, default_investigation_id),
                format_func=lambda x: x["Label"],
                key=f"{key_base}_investigation",
            )

        notes = st.text_area(
            "Notes",
            value=plate.get("Notes") or "",
            height=150,
            key=f"{key_base}_notes",
        )

        submitted = st.form_submit_button(
            "Add plate" if mode == "add" else "Save changes",
            type="primary",
        )

    # Edit-only utilities sit outside the form so that they can use ordinary
    # buttons without interacting with the save button logic.
    if mode == "edit" and plate.get("Id") is not None:
        plate_id = int(plate["Id"])
        st.markdown(
            f"[View in Datasette]({datasette_plate_url(datasette_url, db_file, plate_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this plate",
            key=f"confirm_delete_{plate_id}",
        )
        if st.button("Delete plate", type="secondary", key=f"delete_plate_{plate_id}"):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_plate(conn, plate_id)
                    st.success("Plate deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete plate: {exc}")

    if not submitted:
        return

    # Perform lightweight validation in the UI before attempting the INSERT or
    # UPDATE. The database still remains the final source of truth.
    errors: list[str] = []
    if plate_date is None:
        errors.append("Date is required.")
    if not specimen.strip():
        errors.append("Specimen is required.")
    if not plate_code.strip():
        errors.append("Plate is required.")
    if not reference.strip():
        errors.append("Reference is required.")
    if selected_fk(objective) is None:
        errors.append("Objective is required.")
    if selected_fk(camera) is None:
        errors.append("Camera is required.")
    if selected_fk(investigation) is None:
        errors.append("Investigation is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Date": plate_date.isoformat(),
        "Specimen": specimen.strip(),
        "Plate": plate_code.strip(),
        "Reference": reference.strip(),
        "Notebook_Reference": notebook_reference.strip() or None,
        "Notes": notes.strip() or None,
        "Species_Id": selected_fk(species),
        "Objective_Id": selected_fk(objective),
        "Camera_Id": selected_fk(camera),
        "Stain_Id": selected_fk(stain),
        "Location_Id": selected_fk(location),
        "Investigation_Id": selected_fk(investigation),
    }

    try:
        if mode == "add":
            insert_plate(conn, payload)
            st.success("Plate added.")
        else:
            assert plate.get("Id") is not None
            update_plate(conn, int(plate["Id"]), payload)
            st.success("Plate updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save plate: {exc}")


def render_investigation_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    investigation: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for INVESTIGATION records."""
    series_options = fetch_series(conn)

    if not series_options:
        st.error("SERIES must contain data before you can add or edit investigations.")
        return

    investigation = investigation or {}
    investigation_id = int(investigation["Id"]) if investigation.get("Id") is not None else None
    key_base = form_key_base("investigation", mode, investigation_id)

    if mode == "add":
        series_form_options = make_nullable_options(series_options, placeholder="— Select series —")
        default_series_id = None
    else:
        series_form_options = series_options
        default_series_id = investigation.get("Series_Id")

    with st.form(f"{mode}_investigation_form_{investigation_id if investigation_id is not None else 'new'}", clear_on_submit=(mode == "add")):
        reference = st.text_input("Reference", value=investigation.get("Reference") or "", key=f"{key_base}_reference")
        title = st.text_input("Title", value=investigation.get("Title") or "", key=f"{key_base}_title")
        series = st.selectbox(
            "Series *",
            options=series_form_options,
            index=option_index(series_form_options, default_series_id),
            format_func=lambda x: x["Label"],
            key=f"{key_base}_series",
        )

        submitted = st.form_submit_button(
            "Add investigation" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and investigation.get("Id") is not None:
        st.markdown(
            f"[View in Datasette]({datasette_investigation_url(datasette_url, db_file, int(investigation['Id']))})"
        )

    if not submitted:
        return

    errors: list[str] = []
    if not reference.strip():
        errors.append("Reference is required.")
    if not title.strip():
        errors.append("Title is required.")
    if selected_fk(series) is None:
        errors.append("Series is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Reference": reference.strip(),
        "Title": title.strip(),
        "Series_Id": selected_fk(series),
    }

    try:
        if mode == "add":
            insert_investigation(conn, payload)
            st.success("Investigation added.")
        else:
            assert investigation.get("Id") is not None
            update_investigation(conn, int(investigation["Id"]), payload)
            st.success("Investigation updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save investigation: {exc}")


def render_location_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    location: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for LOCATION records."""
    location = location or {}
    location_id = int(location["Id"]) if location.get("Id") is not None else None
    key_base = form_key_base("location", mode, location_id)

    # Streamlit text_input is used for latitude and longitude so that empty
    # values remain genuinely null in SQLite rather than being forced to 0.0.
    with st.form(f"{mode}_location_form_{location_id if location_id is not None else 'new'}", clear_on_submit=(mode == "add")):
        name = st.text_input("Name *", value=location.get("Name") or "", key=f"{key_base}_name")
        grid_reference = st.text_input(
            "Grid Reference",
            value=location.get("Grid_Reference") or "",
            key=f"{key_base}_grid_reference",
        )

        col1, col2 = st.columns(2)
        with col1:
            latitude_text = st.text_input(
                "Latitude",
                value="" if location.get("Latitude") is None else str(location.get("Latitude")),
                help="Leave blank if the location does not yet have a coordinate.",
                key=f"{key_base}_latitude",
            )
        with col2:
            longitude_text = st.text_input(
                "Longitude",
                value="" if location.get("Longitude") is None else str(location.get("Longitude")),
                help="Leave blank if the location does not yet have a coordinate.",
                key=f"{key_base}_longitude",
            )

        submitted = st.form_submit_button(
            "Add location" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and location.get("Id") is not None:
        location_id = int(location["Id"])
        st.markdown(
            f"[View in Datasette]({datasette_location_url(datasette_url, db_file, location_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this location",
            key=f"confirm_delete_location_{location_id}",
        )
        if st.button(
            "Delete location",
            type="secondary",
            key=f"delete_location_{location_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_location(conn, location_id)
                    st.success("Location deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete location: {exc}")

    if not submitted:
        return

    errors: list[str] = []
    if not name.strip():
        errors.append("Name is required.")

    # Parse numeric inputs carefully so that users can leave them blank while
    # still getting a clear validation message for malformed values.
    latitude: float | None = None
    longitude: float | None = None

    if latitude_text.strip():
        try:
            latitude = float(latitude_text.strip())
        except ValueError:
            errors.append("Latitude must be a valid number.")

    if longitude_text.strip():
        try:
            longitude = float(longitude_text.strip())
        except ValueError:
            errors.append("Longitude must be a valid number.")

    if latitude is not None and not -90 <= latitude <= 90:
        errors.append("Latitude must be between -90 and 90.")

    if longitude is not None and not -180 <= longitude <= 180:
        errors.append("Longitude must be between -180 and 180.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Name": name.strip(),
        "Grid_Reference": grid_reference.strip() or None,
        "Latitude": latitude,
        "Longitude": longitude,
    }

    try:
        if mode == "add":
            insert_location(conn, payload)
            st.success("Location added.")
        else:
            assert location.get("Id") is not None
            update_location(conn, int(location["Id"]), payload)
            st.success("Location updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save location: {exc}")


# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------

@st.cache_resource
def parse_args() -> argparse.Namespace:
    """Parse command line arguments. These are passed using e.g. the following syntax:
    
    streamlit run -- --db data/plate_library.db
    """
    parser = argparse.ArgumentParser(
        prog=f"{PROGRAM_NAME} v{PROGRAM_VERSION}",
        description=PROGRAM_DESCRIPTION
    )

    default_db_path = database_path()
    parser.add_argument("--db", default=default_db_path)

    return parser.parse_args()


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Plate Library", layout="wide")
    st.title("Plate Library")
    st.caption("Simple local maintenance UI for the PLATE, INVESTIGATION and LOCATION tables")

    args = parse_args()

    with st.sidebar:
        st.header("Database")
        db_path = st.text_input("SQLite DB path", value=args.db)

        st.header("Datasette")
        datasette_url = st.text_input("Datasette base URL", value=DEFAULT_DATASETTE_URL)

    if not db_path.strip():
        st.warning("Enter a database path to continue.")
        return

    db_file = Path(db_path)
    if not db_file.exists():
        st.error(f"Database file not found: {db_file}")
        return

    try:
        with closing(get_connection(str(db_file))) as conn:
            if not table_exists(conn, "PLATE"):
                st.error("This database does not contain a PLATE table.")
                return

            if not table_exists(conn, "INVESTIGATION"):
                st.error("This database does not contain an INVESTIGATION table.")
                return

            if not table_exists(conn, "LOCATION"):
                st.error("This database does not contain a LOCATION table.")
                return
            
            load_sql_queries()

            top_plate_tab, top_investigation_tab, top_location_tab = st.tabs([
                "Plates",
                "Investigations",
                "Locations",
            ])

            with top_plate_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="plate",
                    add_title="Add plate",
                    edit_title="Edit plate",
                    browse_title="Browse",
                    fetch_list=fetch_plate_list,
                    fetch_record=fetch_plate,
                    render_form=render_plate_form,
                    edit_select_label="Choose a plate to edit",
                    edit_select_key="plate_edit_select",
                    search_key="plate_search",
                    search_label="Search plates",
                    option_label_builder=lambda row: (
                        f'{row["Date"]} | {row["Plate"]} | {row["Reference"]} | {row["Specimen"]}'
                    ),
                )

            with top_investigation_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="investigation",
                    add_title="Add investigation",
                    edit_title="Edit investigation",
                    browse_title="Browse",
                    fetch_list=fetch_investigation_list,
                    fetch_record=fetch_investigation,
                    render_form=render_investigation_form,
                    edit_select_label="Choose an investigation to edit",
                    edit_select_key="investigation_edit_select",
                    search_key="investigation_search",
                    search_label="Search investigations",
                    option_label_builder=lambda row: (
                        f'{row["Reference"]} | {row["Title"]} | {row["Series"]}'
                    ),
                )

            with top_location_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="location",
                    add_title="Add location",
                    edit_title="Edit location",
                    browse_title="Browse",
                    fetch_list=fetch_location_list,
                    fetch_record=fetch_location,
                    render_form=render_location_form,
                    edit_select_label="Choose a location to edit",
                    edit_select_key="location_edit_select",
                    search_key="location_search",
                    search_label="Search locations",
                    option_label_builder=lambda row: row["Name"]
                    if not row["Grid_Reference"]
                    else f'{row["Name"]} | {row["Grid_Reference"]}',
                )

    except sqlite3.Error as exc:
        st.error(f"SQLite error: {exc}")


if __name__ == "__main__":
    main()
