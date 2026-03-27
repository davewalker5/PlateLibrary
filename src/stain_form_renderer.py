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
from stain_sql import delete_stain, insert_stain, update_stain


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_stain_url(base_url: str, db_file: Path, stain_id: int) -> str:
    """Build the Datasette URL for a STAIN record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/STAIN/{stain_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
def render_stain_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    stain: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for STAIN records."""
    stain = stain or {}
    stain_id = int(stain["Id"]) if stain.get("Id") is not None else None
    key_base = form_key_base("stain", mode, stain_id)

    with st.form(
        f"{mode}_stain_form_{stain_id if stain_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        description = st.text_input(
            "Description *",
            value=stain.get("Description") or "",
            key=f"{key_base}_description",
        )

        submitted = st.form_submit_button(
            "Add stain" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and stain.get("Id") is not None:
        stain_id = int(stain["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_stain_url(datasette_url, db_file, stain_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this stain",
            key=f"confirm_delete_stain_{stain_id}",
        )

        if st.button(
            "Delete stain",
            type="secondary",
            key=f"delete_stain_{stain_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_stain(conn, stain_id)
                    st.success("Stain deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete stain: {exc}")

    if not submitted:
        return

    errors: list[str] = []

    if not description.strip():
        errors.append("Description is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Description": description.strip(),
    }

    try:
        if mode == "add":
            insert_stain(conn, payload)
            st.success("Stain added.")
        else:
            assert stain.get("Id") is not None
            update_stain(conn, int(stain["Id"]), payload)
            st.success("Stain updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save stain: {exc}")
