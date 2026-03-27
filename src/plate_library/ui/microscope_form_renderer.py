# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path
from plate_library.utils.data_conversion_helpers import form_key_base

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from plate_library.sql.microscope_sql import delete_microscope, insert_microscope, update_microscope


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_microscope_url(base_url: str, db_file: Path, microscope_id: int) -> str:
    """Build the Datasette URL for a MICROSCOPE record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/MICROSCOPE/{microscope_id}"


# -----------------------------------------------------------------------------
# Local helpers
# -----------------------------------------------------------------------------
def parse_required_int(value: str, field_name: str) -> tuple[int | None, str | None]:
    """Parse a required integer form field."""
    text = (value or "").strip()

    if not text:
        return None, f"{field_name} is required."

    try:
        return int(text), None
    except ValueError:
        return None, f"{field_name} must be an integer."


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
def render_microscope_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    microscope: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for MICROSCOPE records."""
    microscope = microscope or {}
    microscope_id = int(microscope["Id"]) if microscope.get("Id") is not None else None
    key_base = form_key_base("microscope", mode, microscope_id)

    with st.form(
        f"{mode}_microscope_form_{microscope_id if microscope_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        description = st.text_input(
            "Description *",
            value=microscope.get("Description") or "",
            key=f"{key_base}_description",
        )

        manufacturer = st.text_input(
            "Manufacturer *",
            value=microscope.get("Manufacturer") or "",
            key=f"{key_base}_manufacturer",
        )

        manufactured = st.text_input(
            "Manufactured *",
            value="" if microscope.get("Manufactured") is None else str(microscope.get("Manufactured")),
            key=f"{key_base}_manufactured",
            help="Year of manufacture.",
        )

        serial_number = st.text_input(
            "Serial Number *",
            value=microscope.get("Serial_Number") or "",
            key=f"{key_base}_serial_number",
        )

        submitted = st.form_submit_button(
            "Add microscope" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and microscope.get("Id") is not None:
        microscope_id = int(microscope["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_microscope_url(datasette_url, db_file, microscope_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this microscope",
            key=f"confirm_delete_microscope_{microscope_id}",
        )

        if st.button(
            "Delete microscope",
            type="secondary",
            key=f"delete_microscope_{microscope_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_microscope(conn, microscope_id)
                    st.success("Microscope deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete microscope: {exc}")

    if not submitted:
        return

    errors: list[str] = []

    if not description.strip():
        errors.append("Description is required.")

    if not manufacturer.strip():
        errors.append("Manufacturer is required.")

    manufactured_value, manufactured_error = parse_required_int(
        manufactured,
        "Manufactured",
    )
    if manufactured_error:
        errors.append(manufactured_error)

    if not serial_number.strip():
        errors.append("Serial Number is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Description": description.strip(),
        "Manufacturer": manufacturer.strip(),
        "Manufactured": manufactured_value,
        "Serial_Number": serial_number.strip(),
    }

    try:
        if mode == "add":
            insert_microscope(conn, payload)
            st.success("Microscope added.")
        else:
            assert microscope.get("Id") is not None
            update_microscope(conn, int(microscope["Id"]), payload)
            st.success("Microscope updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save microscope: {exc}")
