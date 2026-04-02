# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import re
import sqlite3
import streamlit as st
from datetime import date
from typing import Any
from pathlib import Path
from plate_library.utils.data_conversion_helpers import (
    make_nullable_options,
    form_key_base,
    option_index,
    selected_fk,
)

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
# Reference numbering helpers
# -----------------------------------------------------------------------------
def suggest_next_investigation_reference(conn: sqlite3.Connection, year: int | None = None) -> str:
    """Return the next investigation reference in the form IN-YYYY-NNN."""
    year = year or date.today().year
    prefix = f"IN-{year}-"

    rows = conn.execute(
        """
        SELECT Reference
        FROM INVESTIGATION
        WHERE Reference LIKE ?
        """,
        (f"{prefix}%",),
    ).fetchall()

    highest_sequence = 0
    pattern = re.compile(rf"^IN-{year}-(\d{{3}})$")

    for row in rows:
        reference = row[0] if not isinstance(row, sqlite3.Row) else row["Reference"]
        if not reference:
            continue

        match = pattern.match(str(reference).strip())
        if match:
            highest_sequence = max(highest_sequence, int(match.group(1)))

    next_sequence = highest_sequence + 1
    return f"IN-{year}-{next_sequence:03d}"


# -----------------------------------------------------------------------------
# Form state helpers
# -----------------------------------------------------------------------------
def apply_pending_investigation_form_state(key_base: str) -> None:
    """Apply deferred widget state updates before widgets are instantiated."""
    pending_key = f"{key_base}_post_save_values"
    pending = st.session_state.get(pending_key)
    if not pending:
        return

    for suffix, value in pending.items():
        st.session_state[f"{key_base}_{suffix}"] = value

    del st.session_state[pending_key]


def initialise_add_investigation_form_state(
    conn: sqlite3.Connection,
    key_base: str,
    series_form_options: list[dict[str, Any]],
) -> None:
    """Initialise add-form widget state once, before widgets are created."""
    reference_key = f"{key_base}_reference"
    title_key = f"{key_base}_title"
    series_key = f"{key_base}_series"

    if reference_key not in st.session_state:
        st.session_state[reference_key] = suggest_next_investigation_reference(conn)

    if title_key not in st.session_state:
        st.session_state[title_key] = ""

    if series_key not in st.session_state:
        st.session_state[series_key] = series_form_options[0]


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

    apply_pending_investigation_form_state(key_base)

    if mode == "add":
        series_form_options = make_nullable_options(
            series_options,
            placeholder="— Select series —",
        )
        initialise_add_investigation_form_state(conn, key_base, series_form_options)
    else:
        series_form_options = series_options

    with st.form(
        f"{mode}_investigation_form_{investigation_id if investigation_id is not None else 'new'}",
        clear_on_submit=False,
    ):
        if mode == "add":
            reference = st.text_input(
                "Reference",
                key=f"{key_base}_reference",
            )
            title = st.text_input(
                "Title",
                key=f"{key_base}_title",
            )
            series = st.selectbox(
                "Series *",
                options=series_form_options,
                format_func=lambda x: x["Label"],
                key=f"{key_base}_series",
            )
        else:
            reference = st.text_input(
                "Reference",
                value=investigation.get("Reference") or "",
                key=f"{key_base}_reference",
            )
            title = st.text_input(
                "Title",
                value=investigation.get("Title") or "",
                key=f"{key_base}_title",
            )
            series = st.selectbox(
                "Series *",
                options=series_form_options,
                index=option_index(series_form_options, investigation.get("Series_Id")),
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

            next_reference = suggest_next_investigation_reference(conn)

            st.session_state[f"{key_base}_post_save_values"] = {
                "reference": next_reference,
                "title": "",
                "series": series,
            }

            st.success("Investigation added.")
        else:
            assert investigation.get("Id") is not None
            update_investigation(conn, int(investigation["Id"]), payload)
            st.success("Investigation updated.")

        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save investigation: {exc}")
