# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path
from data_conversion_helpers import make_nullable_options, form_key_base, parse_db_date, option_index, selected_fk

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from location_sql import delete_location, insert_location, update_location

# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_location_url(base_url: str, db_file: Path, location_id: int) -> str:
    """Build the Datasette URL for a LOCATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/LOCATION/{location_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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