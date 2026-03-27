# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path
from plate_library.utils.data_conversion_helpers import make_nullable_options, form_key_base, parse_db_date, option_index, selected_fk

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from plate_library.sql.species_sql import fetch_species, fetch_species_list
from plate_library.sql.objective_sql import fetch_objectives
from plate_library.sql.camera_sql import fetch_cameras
from plate_library.sql.investigation_sql import fetch_investigations
from plate_library.sql.stain_sql import fetch_stains
from plate_library.sql.location_sql import fetch_locations
from plate_library.utils.plate_numbering import suggest_next_plate_for_investigation
from plate_library.ui.plate_preview import render_plate_media_preview
from plate_library.sql.plate_sql import delete_plate, insert_plate, update_plate

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


# -----------------------------------------------------------------------------
# Form initialisation
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


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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