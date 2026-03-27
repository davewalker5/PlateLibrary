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
from series_sql import delete_series, insert_series, update_series
from scheme_sql import fetch_scheme_list


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_series_url(base_url: str, db_file: Path, series_id: int) -> str:
    """Build the Datasette URL for a SERIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SERIES/{series_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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