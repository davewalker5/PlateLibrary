# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path
from data_conversion_helpers import form_key_base

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from camera_sql import delete_camera, insert_camera, update_camera


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_camera_url(base_url: str, db_file: Path, camera_id: int) -> str:
    """Build the Datasette URL for a CAMERA record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/CAMERA/{camera_id}"


# -----------------------------------------------------------------------------
# Local helpers
# -----------------------------------------------------------------------------
def parse_nullable_int(value: str, field_name: str) -> tuple[int | None, str | None]:
    """Parse a nullable integer form field."""
    text = (value or "").strip()
    if not text:
        return None, None

    try:
        return int(text), None
    except ValueError:
        return None, f"{field_name} must be an integer."


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
def render_camera_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    camera: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for CAMERA records."""
    camera = camera or {}
    camera_id = int(camera["Id"]) if camera.get("Id") is not None else None
    key_base = form_key_base("camera", mode, camera_id)

    lower_default = (
        "" if camera.get("Lower_Effective_Magnification") is None
        else str(camera["Lower_Effective_Magnification"])
    )
    upper_default = (
        "" if camera.get("Upper_Effective_Magnification") is None
        else str(camera["Upper_Effective_Magnification"])
    )

    with st.form(
        f"{mode}_camera_form_{camera_id if camera_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        description = st.text_input(
            "Description *",
            value=camera.get("Description") or "",
            key=f"{key_base}_description",
        )

        lower_effective_magnification = st.text_input(
            "Lower Effective Magnification",
            value=lower_default,
            key=f"{key_base}_lower_effective_magnification",
            help="Optional integer value.",
        )

        upper_effective_magnification = st.text_input(
            "Upper Effective Magnification",
            value=upper_default,
            key=f"{key_base}_upper_effective_magnification",
            help="Optional integer value.",
        )

        submitted = st.form_submit_button(
            "Add camera" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and camera.get("Id") is not None:
        camera_id = int(camera["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_camera_url(datasette_url, db_file, camera_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this camera",
            key=f"confirm_delete_camera_{camera_id}",
        )

        if st.button(
            "Delete camera",
            type="secondary",
            key=f"delete_camera_{camera_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_camera(conn, camera_id)
                    st.success("Camera deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete camera: {exc}")

    if not submitted:
        return

    errors: list[str] = []

    if not description.strip():
        errors.append("Description is required.")

    lower_value, lower_error = parse_nullable_int(
        lower_effective_magnification,
        "Lower Effective Magnification",
    )
    upper_value, upper_error = parse_nullable_int(
        upper_effective_magnification,
        "Upper Effective Magnification",
    )

    if lower_error:
        errors.append(lower_error)
    if upper_error:
        errors.append(upper_error)

    if (
        lower_value is not None
        and upper_value is not None
        and lower_value > upper_value
    ):
        errors.append(
            "Lower Effective Magnification cannot be greater than Upper Effective Magnification."
        )

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Description": description.strip(),
        "Lower_Effective_Magnification": lower_value,
        "Upper_Effective_Magnification": upper_value,
    }

    try:
        if mode == "add":
            insert_camera(conn, payload)
            st.success("Camera added.")
        else:
            assert camera.get("Id") is not None
            update_camera(conn, int(camera["Id"]), payload)
            st.success("Camera updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save camera: {exc}")
