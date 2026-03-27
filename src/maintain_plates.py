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
import streamlit as st

from data_conversion_helpers import *
from sqlite_helpers import *
from plate_numbering import *
from plate_preview import *
from ui_helpers import *
from species_sql import *

PROGRAM_NAME = "Microscopy Plate Library Maintenance UI"
PROGRAM_VERSION = "1.6.0"
PROGRAM_DESCRIPTION = "Maintenance UI for a simple microscopy plate library"

# Default location for the local Datasette instance and database name
DEFAULT_DATASETTE_URL = "http://127.0.0.1:8001"
DB_NAME = "plate_library.db"

# Root folder of the project
PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))


# -----------------------------------------------------------------------------
# Lookup queries used by the PLATE, INVESTIGATION and LOCATION forms
# -----------------------------------------------------------------------------
def fetch_objectives(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope objectives formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_objectives"]["sql"])


def fetch_cameras(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return camera records formatted for the select box."""
    return fetch_lookup(conn, QUERIES["fetch_cameras"]["sql"])


def fetch_stains(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return stains formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_stains"]["sql"])


def fetch_locations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return locations formatted for display in the UI."""
    return fetch_lookup(conn, QUERIES["fetch_locations"]["sql"])


def fetch_series(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return series values formatted for investigation maintenance."""
    return fetch_lookup(conn, QUERIES["fetch_series"]["sql"])


def fetch_investigations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return investigations formatted for use in the PLATE form."""
    return fetch_lookup(conn, QUERIES["fetch_investigations"]["sql"])


def fetch_scheme_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of schemes for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_scheme_list"]["sql"])


def fetch_scheme(conn: sqlite3.Connection, scheme_id: int) -> dict[str, Any] | None:
    """Fetch a single SCHEME row for editing."""
    row = conn.execute(QUERIES["fetch_scheme"]["sql"], (scheme_id,)).fetchone()
    return dict(row) if row else None


def fetch_series_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of series for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_series_list"]["sql"])


def fetch_series_record(conn: sqlite3.Connection, series_id: int) -> dict[str, Any] | None:
    """Fetch a single SERIES row for editing."""
    row = conn.execute(QUERIES["fetch_series_record"]["sql"], (series_id,)).fetchone()
    return dict(row) if row else None


def fetch_plate_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of plates for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_plate_list"]["sql"])


def fetch_plate(conn: sqlite3.Connection, plate_id: int) -> dict[str, Any] | None:
    """Fetch a single PLATE row for editing."""
    row = conn.execute(QUERIES["fetch_plate"]["sql"], (plate_id,)).fetchone()
    return dict(row) if row else None


def fetch_investigation_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of investigations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_investigation_list"]["sql"])


def fetch_investigation(
    conn: sqlite3.Connection, investigation_id: int
) -> dict[str, Any] | None:
    """Fetch a single INVESTIGATION row for editing."""
    row = conn.execute(QUERIES["fetch_investigation"]["sql"], (investigation_id,)).fetchone()
    return dict(row) if row else None


def fetch_location_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of locations for browsing and selection."""
    return fetch_lookup(conn, QUERIES["fetch_location_list"]["sql"])


def fetch_location(conn: sqlite3.Connection, location_id: int) -> dict[str, Any] | None:
    """Fetch a single LOCATION row for editing."""
    row = conn.execute(QUERIES["fetch_location"]["sql"], (location_id,)).fetchone()
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


def insert_investigation(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new INVESTIGATION record."""
    conn.execute(
       QUERIES["insert_investigation"]["sql"],
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
    conn.execute(QUERIES["update_investigation"]["sql"],
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
    conn.execute(QUERIES["insert_location"]["sql"],
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
        QUERIES["update_location"]["sql"],
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
    conn.execute(QUERIES["delete_location"]["sql"], (location_id,))
    conn.commit()


def insert_scheme(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new SCHEME record."""
    conn.execute(
        QUERIES["insert_scheme"]["sql"],
        (
            values["Name"],
            values["Code"],
        ),
    )
    conn.commit()


def update_scheme(conn: sqlite3.Connection, scheme_id: int, values: dict[str, Any]) -> None:
    """Update an existing SCHEME record."""
    conn.execute(
        QUERIES["update_scheme"]["sql"],
        (
            values["Name"],
            values["Code"],
            scheme_id,
        ),
    )
    conn.commit()


def delete_scheme(conn: sqlite3.Connection, scheme_id: int) -> None:
    """Delete a SCHEME record."""
    conn.execute(QUERIES["delete_scheme"]["sql"], (scheme_id,))
    conn.commit()


def insert_series(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new SERIES record."""
    conn.execute(
        QUERIES["insert_series"]["sql"],
        (
            values["Name"],
            values["Scheme_Id"],
            values["Code"],
            values["Plate_Format"],
        ),
    )
    conn.commit()


def update_series(conn: sqlite3.Connection, series_id: int, values: dict[str, Any]) -> None:
    """Update an existing SERIES record."""
    conn.execute(
        QUERIES["update_series"]["sql"],
        (
            values["Name"],
            values["Scheme_Id"],
            values["Code"],
            values["Plate_Format"],
            series_id,
        ),
    )
    conn.commit()


def delete_series(conn: sqlite3.Connection, series_id: int) -> None:
    """Delete a SERIES record."""
    conn.execute(QUERIES["delete_series"]["sql"], (series_id,))
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


def datasette_scheme_url(base_url: str, db_file: Path, scheme_id: int) -> str:
    """Build the Datasette URL for a SCHEME record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SCHEME/{scheme_id}"


def datasette_series_url(base_url: str, db_file: Path, series_id: int) -> str:
    """Build the Datasette URL for a SERIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SERIES/{series_id}"


def datasette_species_url(base_url: str, db_file: Path, species_id: int) -> str:
    """Build the Datasette URL for a SPECIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SPECIES/{species_id}"

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

        render_plate_media_preview(plate)

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


def render_scheme_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    scheme: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for SCHEME records."""
    scheme = scheme or {}
    scheme_id = int(scheme["Id"]) if scheme.get("Id") is not None else None
    key_base = form_key_base("scheme", mode, scheme_id)

    with st.form(
        f"{mode}_scheme_form_{scheme_id if scheme_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        name = st.text_input(
            "Name *",
            value=scheme.get("Name") or "",
            key=f"{key_base}_name",
        )

        code = st.text_input(
            "Code *",
            value=scheme.get("Code") or "",
            key=f"{key_base}_code",
        )

        submitted = st.form_submit_button(
            "Add scheme" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and scheme.get("Id") is not None:
        scheme_id = int(scheme["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_scheme_url(datasette_url, db_file, scheme_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this scheme",
            key=f"confirm_delete_scheme_{scheme_id}",
        )

        if st.button(
            "Delete scheme",
            type="secondary",
            key=f"delete_scheme_{scheme_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_scheme(conn, scheme_id)
                    st.success("Scheme deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete scheme: {exc}")

    if not submitted:
        return

    errors: list[str] = []
    if not name.strip():
        errors.append("Name is required.")
    if not code.strip():
        errors.append("Code is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Name": name.strip(),
        "Code": code.strip(),
    }

    try:
        if mode == "add":
            insert_scheme(conn, payload)
            st.success("Scheme added.")
        else:
            assert scheme.get("Id") is not None
            update_scheme(conn, int(scheme["Id"]), payload)
            st.success("Scheme updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save scheme: {exc}")


def render_series_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    series: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for SERIES records."""
    scheme_options = fetch_scheme_list(conn)

    if not scheme_options:
        st.error("SCHEME must contain data before you can add or edit series.")
        return

    series = series or {}
    series_id = int(series["Id"]) if series.get("Id") is not None else None
    key_base = form_key_base("series", mode, series_id)

    if mode == "add":
        scheme_form_options = make_nullable_options(
            scheme_options, placeholder="— Select scheme —"
        )
        default_scheme_id = None
    else:
        scheme_form_options = scheme_options
        default_scheme_id = series.get("Scheme_Id")

    plate_format_options = ["simple", "subsequence"]

    existing_plate_format = series.get("Plate_Format")
    if existing_plate_format not in plate_format_options:
        existing_plate_format = "simple"

    with st.form(
        f"{mode}_series_form_{series_id if series_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        name = st.text_input(
            "Name *",
            value=series.get("Name") or "",
            key=f"{key_base}_name",
        )

        scheme = st.selectbox(
            "Scheme *",
            options=scheme_form_options,
            index=option_index(scheme_form_options, default_scheme_id),
            format_func=lambda x: x["Label"],
            key=f"{key_base}_scheme",
        )

        code = st.text_input(
            "Code",
            value=series.get("Code") or "",
            key=f"{key_base}_code",
        )

        plate_format = st.selectbox(
            "Plate Format *",
            options=plate_format_options,
            index=plate_format_options.index(existing_plate_format),
            key=f"{key_base}_plate_format",
        )

        submitted = st.form_submit_button(
            "Add series" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and series.get("Id") is not None:
        series_id = int(series["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_series_url(datasette_url, db_file, series_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this series",
            key=f"confirm_delete_series_{series_id}",
        )

        if st.button(
            "Delete series",
            type="secondary",
            key=f"delete_series_{series_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_series(conn, series_id)
                    st.success("Series deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete series: {exc}")

    if not submitted:
        return

    errors: list[str] = []
    if not name.strip():
        errors.append("Name is required.")
    if selected_fk(scheme) is None:
        errors.append("Scheme is required.")
    if plate_format not in {"simple", "subsequence"}:
        errors.append("Plate Format must be either 'simple' or 'subsequence'.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Name": name.strip(),
        "Scheme_Id": selected_fk(scheme),
        "Code": code.strip() or None,
        "Plate_Format": plate_format,
    }

    try:
        if mode == "add":
            insert_series(conn, payload)
            st.success("Series added.")
        else:
            assert series.get("Id") is not None
            update_series(conn, int(series["Id"]), payload)
            st.success("Series updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save series: {exc}")


def render_species_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    species: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for SPECIES records."""
    species = species or {}
    species_id = int(species["Id"]) if species.get("Id") is not None else None
    key_base = form_key_base("species", mode, species_id)

    with st.form(
        f"{mode}_species_form_{species_id if species_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        scientific_name = st.text_input(
            "Scientific Name",
            value=species.get("Scientific_Name") or "",
            key=f"{key_base}_scientific_name",
        )

        common_name = st.text_input(
            "Common Name",
            value=species.get("Common_Name") or "",
            key=f"{key_base}_common_name",
        )

        submitted = st.form_submit_button(
            "Add species" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and species.get("Id") is not None:
        species_id = int(species["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_species_url(datasette_url, db_file, species_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this species",
            key=f"confirm_delete_species_{species_id}",
        )

        if st.button(
            "Delete species",
            type="secondary",
            key=f"delete_species_{species_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_species(conn, species_id)
                    st.success("Species deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete species: {exc}")

    if not submitted:
        return

    scientific_name_clean = scientific_name.strip() or None
    common_name_clean = common_name.strip() or None

    errors: list[str] = []
    if scientific_name_clean is None and common_name_clean is None:
        errors.append("At least one of Scientific Name or Common Name is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Scientific_Name": scientific_name_clean,
        "Common_Name": common_name_clean,
    }

    try:
        if mode == "add":
            insert_species(conn, payload)
            st.success("Species added.")
        else:
            assert species.get("Id") is not None
            update_species(conn, int(species["Id"]), payload)
            st.success("Species updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save species: {exc}")


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

    default_db_path = database_path(PROJECT_FOLDER, DB_NAME)
    parser.add_argument("--db", default=default_db_path)

    return parser.parse_args()


def main() -> None:
    """Run the Streamlit application."""
    title = f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)
    st.caption(PROGRAM_DESCRIPTION)

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
            if not confirm_schema(conn):
                return

            load_sql_queries(PROJECT_FOLDER)

            top_plate_tab, top_investigation_tab, top_location_tab, top_scheme_tab, top_series_tab, top_species_tab = st.tabs([
                "Plates",
                "Investigations",
                "Locations",
                "Schemes",
                "Series",
                "Species",
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

            with top_scheme_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="scheme",
                    add_title="Add scheme",
                    edit_title="Edit scheme",
                    browse_title="Browse",
                    fetch_list=fetch_scheme_list,
                    fetch_record=fetch_scheme,
                    render_form=render_scheme_form,
                    edit_select_label="Choose a scheme to edit",
                    edit_select_key="scheme_edit_select",
                    search_key="scheme_search",
                    search_label="Search schemes",
                    option_label_builder=lambda row: (
                        f'{row["Code"]} | {row["Title"]}'
                        if row.get("Title")
                        else row["Code"]
                    ),
                )

            with top_series_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="series",
                    add_title="Add series",
                    edit_title="Edit series",
                    browse_title="Browse",
                    fetch_list=fetch_series_list,
                    fetch_record=fetch_series_record,
                    render_form=render_series_form,
                    edit_select_label="Choose a series to edit",
                    edit_select_key="series_edit_select",
                    search_key="series_search",
                    search_label="Search series",
                    option_label_builder=lambda row: (
                        f'{row["Scheme_Code"]} | {row["Code"] or "—"} | {row["Name"]} | {row["Plate_Format"]}'
                    ),
                )

            with top_species_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="species",
                    add_title="Add species",
                    edit_title="Edit species",
                    browse_title="Browse",
                    fetch_list=fetch_species_list,
                    fetch_record=fetch_species_record,
                    render_form=render_species_form,
                    edit_select_label="Choose a species to edit",
                    edit_select_key="species_edit_select",
                    search_key="species_search",
                    search_label="Search species",
                    option_label_builder=lambda row: row["Label"],
                )

    except sqlite3.Error as exc:
        st.error(f"SQLite error: {exc}")


if __name__ == "__main__":
    main()
