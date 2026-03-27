# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path
from data_conversion_helpers import make_nullable_options, form_key_base, option_index, selected_fk

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from objective_sql import delete_objective, insert_objective, update_objective
from microscope_sql import fetch_microscope_list


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_objective_url(base_url: str, db_file: Path, objective_id: int) -> str:
    """Build the Datasette URL for an OBJECTIVE record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/OBJECTIVE/{objective_id}"


# -----------------------------------------------------------------------------
# Local helpers
# -----------------------------------------------------------------------------
def microscope_option_label(row: dict[str, Any]) -> str:
    """Render a readable microscope option label."""
    if row.get("Id") is None:
        return row.get("Label", "— Select microscope —")

    return (
        f'{row["Manufacturer"]} | {row["Description"]} | '
        f'{row["Manufactured"]} | {row["Serial_Number"]}'
    )


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
def render_objective_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    objective: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for OBJECTIVE records."""
    microscope_options = fetch_microscope_list(conn)

    if not microscope_options:
        st.error("MICROSCOPE must contain data before you can add or edit objectives.")
        return

    objective = objective or {}
    objective_id = int(objective["Id"]) if objective.get("Id") is not None else None
    key_base = form_key_base("objective", mode, objective_id)

    if mode == "add":
        microscope_form_options = make_nullable_options(
            microscope_options, placeholder="— Select microscope —"
        )
        default_microscope_id = None
    else:
        microscope_form_options = microscope_options
        default_microscope_id = objective.get("Microscope_Id")

    with st.form(
        f"{mode}_objective_form_{objective_id if objective_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        microscope = st.selectbox(
            "Microscope *",
            options=microscope_form_options,
            index=option_index(microscope_form_options, default_microscope_id),
            format_func=microscope_option_label,
            key=f"{key_base}_microscope",
        )

        description = st.text_input(
            "Description *",
            value=objective.get("Description") or "",
            key=f"{key_base}_description",
        )

        magnification = st.number_input(
            "Magnification *",
            min_value=1,
            step=1,
            value=int(objective.get("Magnification")) if objective.get("Magnification") is not None else 1,
            key=f"{key_base}_magnification",
        )

        submitted = st.form_submit_button(
            "Add objective" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and objective.get("Id") is not None:
        objective_id = int(objective["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_objective_url(datasette_url, db_file, objective_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this objective",
            key=f"confirm_delete_objective_{objective_id}",
        )

        if st.button(
            "Delete objective",
            type="secondary",
            key=f"delete_objective_{objective_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_objective(conn, objective_id)
                    st.success("Objective deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete objective: {exc}")

    if not submitted:
        return

    errors: list[str] = []

    if selected_fk(microscope) is None:
        errors.append("Microscope is required.")

    if not description.strip():
        errors.append("Description is required.")

    if int(magnification) < 1:
        errors.append("Magnification must be a positive integer.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Microscope_Id": selected_fk(microscope),
        "Description": description.strip(),
        "Magnification": int(magnification),
    }

    try:
        if mode == "add":
            insert_objective(conn, payload)
            st.success("Objective added.")
        else:
            assert objective.get("Id") is not None
            update_objective(conn, int(objective["Id"]), payload)
            st.success("Objective updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save objective: {exc}")
