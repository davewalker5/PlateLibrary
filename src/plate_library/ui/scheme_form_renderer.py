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
from plate_library.sql.scheme_sql import delete_scheme, insert_scheme, update_scheme


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_scheme_url(base_url: str, db_file: Path, scheme_id: int) -> str:
    """Build the Datasette URL for a SCHEME record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SCHEME/{scheme_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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