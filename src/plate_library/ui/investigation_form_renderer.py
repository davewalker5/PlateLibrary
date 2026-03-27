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
from plate_library.sql.series_sql import fetch_series
from plate_library.sql.investigation_sql import insert_investigation, update_investigation

# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_investigation_url(
    base_url: str, db_file: Path, investigation_id: int
) -> str:
    """Build the Datasette URL for an INVESTIGATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/INVESTIGATION/{investigation_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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
