"""Streamlit maintenance UI for the microscopy plate library.

This script provides a deliberately simple local web UI for maintaining the
fast-moving tables in the plate library database:

- PLATE
- INVESTIGATION
- LOCATION

The application is intended to sit alongside Datasette:

- Streamlit is used for data entry and editing
- Datasette is used for browsing, querying and verifying the data

The rest of the lookup tables are assumed to change only occasionally and can
be maintained separately when needed. LOCATION is included because it is a
regular part of specimen and plate entry.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any
import argparse
import streamlit as st

from scheme_sql import *
from data_conversion_helpers import *
from sqlite_helpers import *
# from plate_numbering import *
# from plate_preview import *
from ui_helpers import *
from species_sql import *
from series_sql import *
# from objective_sql import *
# from camera_sql import *
# from stain_sql import *
from location_sql import *
from investigation_sql import *
from plate_sql import *

from plate_form_renderer import render_plate_form
from investigation_form_renderer import render_investigation_form
from location_form_renderer import render_location_form
from scheme_form_renderer import render_scheme_form


PROGRAM_NAME = "Microscopy Plate Library Maintenance UI"
PROGRAM_VERSION = "1.6.0"
PROGRAM_DESCRIPTION = "Maintenance UI for a simple microscopy plate library"

# Default location for the local Datasette instance and database name
DEFAULT_DATASETTE_URL = "http://127.0.0.1:8001"
DB_NAME = "plate_library.db"

# Root folder of the project
PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))

# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------


def datasette_series_url(base_url: str, db_file: Path, series_id: int) -> str:
    """Build the Datasette URL for a SERIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SERIES/{series_id}"


def datasette_species_url(base_url: str, db_file: Path, species_id: int) -> str:
    """Build the Datasette URL for a SPECIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SPECIES/{species_id}"

# -----------------------------------------------------------------------------
# Streamlit form renderers
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


def render_species_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    species: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for SPECIES records."""
    species = species or {}
    species_id = int(species["Id"]) if species.get("Id") is not None else None
    key_base = form_key_base("species", mode, species_id)

    with st.form(
        f"{mode}_species_form_{species_id if species_id is not None else 'new'}",
        clear_on_submit=(mode == "add"),
    ):
        scientific_name = st.text_input(
            "Scientific Name",
            value=species.get("Scientific_Name") or "",
            key=f"{key_base}_scientific_name",
        )

        common_name = st.text_input(
            "Common Name",
            value=species.get("Common_Name") or "",
            key=f"{key_base}_common_name",
        )

        submitted = st.form_submit_button(
            "Add species" if mode == "add" else "Save changes",
            type="primary",
        )

    if mode == "edit" and species.get("Id") is not None:
        species_id = int(species["Id"])

        st.markdown(
            f"[View in Datasette]({datasette_species_url(datasette_url, db_file, species_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this species",
            key=f"confirm_delete_species_{species_id}",
        )

        if st.button(
            "Delete species",
            type="secondary",
            key=f"delete_species_{species_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_species(conn, species_id)
                    st.success("Species deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete species: {exc}")

    if not submitted:
        return

    scientific_name_clean = scientific_name.strip() or None
    common_name_clean = common_name.strip() or None

    errors: list[str] = []
    if scientific_name_clean is None and common_name_clean is None:
        errors.append("At least one of Scientific Name or Common Name is required.")

    if errors:
        for error in errors:
            st.error(error)
        return

    payload = {
        "Scientific_Name": scientific_name_clean,
        "Common_Name": common_name_clean,
    }

    try:
        if mode == "add":
            insert_species(conn, payload)
            st.success("Species added.")
        else:
            assert species.get("Id") is not None
            update_species(conn, int(species["Id"]), payload)
            st.success("Species updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save species: {exc}")


# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------

@st.cache_resource
def parse_args() -> argparse.Namespace:
    """Parse command line arguments. These are passed using e.g. the following syntax:
    
    streamlit run -- --db data/plate_library.db
    """
    parser = argparse.ArgumentParser(
        prog=f"{PROGRAM_NAME} v{PROGRAM_VERSION}",
        description=PROGRAM_DESCRIPTION
    )

    default_db_path = database_path(PROJECT_FOLDER, DB_NAME)
    parser.add_argument("--db", default=default_db_path)

    return parser.parse_args()


def main() -> None:
    """Run the Streamlit application."""
    title = f"{PROGRAM_NAME} {PROGRAM_VERSION}"
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)
    st.caption(PROGRAM_DESCRIPTION)

    args = parse_args()

    with st.sidebar:
        st.header("Database")
        db_path = st.text_input("SQLite DB path", value=args.db)

        st.header("Datasette")
        datasette_url = st.text_input("Datasette base URL", value=DEFAULT_DATASETTE_URL)

    if not db_path.strip():
        st.warning("Enter a database path to continue.")
        return

    db_file = Path(db_path)
    if not db_file.exists():
        st.error(f"Database file not found: {db_file}")
        return

    try:
        with closing(get_connection(str(db_file))) as conn:
            if not confirm_schema(conn):
                return

            load_sql_queries(PROJECT_FOLDER)

            top_plate_tab, top_investigation_tab, top_location_tab, top_scheme_tab, top_series_tab, top_species_tab = st.tabs([
                "Plates",
                "Investigations",
                "Locations",
                "Schemes",
                "Series",
                "Species",
            ])

            with top_plate_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="plate",
                    add_title="Add plate",
                    edit_title="Edit plate",
                    browse_title="Browse",
                    fetch_list=fetch_plate_list,
                    fetch_record=fetch_plate,
                    render_form=render_plate_form,
                    edit_select_label="Choose a plate to edit",
                    edit_select_key="plate_edit_select",
                    search_key="plate_search",
                    search_label="Search plates",
                    option_label_builder=lambda row: (
                        f'{row["Date"]} | {row["Plate"]} | {row["Reference"]} | {row["Specimen"]}'
                    ),
                )

            with top_investigation_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="investigation",
                    add_title="Add investigation",
                    edit_title="Edit investigation",
                    browse_title="Browse",
                    fetch_list=fetch_investigation_list,
                    fetch_record=fetch_investigation,
                    render_form=render_investigation_form,
                    edit_select_label="Choose an investigation to edit",
                    edit_select_key="investigation_edit_select",
                    search_key="investigation_search",
                    search_label="Search investigations",
                    option_label_builder=lambda row: (
                        f'{row["Reference"]} | {row["Title"]} | {row["Series"]}'
                    ),
                )

            with top_location_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="location",
                    add_title="Add location",
                    edit_title="Edit location",
                    browse_title="Browse",
                    fetch_list=fetch_location_list,
                    fetch_record=fetch_location,
                    render_form=render_location_form,
                    edit_select_label="Choose a location to edit",
                    edit_select_key="location_edit_select",
                    search_key="location_search",
                    search_label="Search locations",
                    option_label_builder=lambda row: row["Name"]
                    if not row["Grid_Reference"]
                    else f'{row["Name"]} | {row["Grid_Reference"]}',
                )

            with top_scheme_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="scheme",
                    add_title="Add scheme",
                    edit_title="Edit scheme",
                    browse_title="Browse",
                    fetch_list=fetch_scheme_list,
                    fetch_record=fetch_scheme,
                    render_form=render_scheme_form,
                    edit_select_label="Choose a scheme to edit",
                    edit_select_key="scheme_edit_select",
                    search_key="scheme_search",
                    search_label="Search schemes",
                    option_label_builder=lambda row: (
                        f'{row["Code"]} | {row["Title"]}'
                        if row.get("Title")
                        else row["Code"]
                    ),
                )

            with top_series_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="series",
                    add_title="Add series",
                    edit_title="Edit series",
                    browse_title="Browse",
                    fetch_list=fetch_series_list,
                    fetch_record=fetch_series_record,
                    render_form=render_series_form,
                    edit_select_label="Choose a series to edit",
                    edit_select_key="series_edit_select",
                    search_key="series_search",
                    search_label="Search series",
                    option_label_builder=lambda row: (
                        f'{row["Scheme_Code"]} | {row["Code"] or "—"} | {row["Name"]} | {row["Plate_Format"]}'
                    ),
                )

            with top_species_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="species",
                    add_title="Add species",
                    edit_title="Edit species",
                    browse_title="Browse",
                    fetch_list=fetch_species_list,
                    fetch_record=fetch_species_record,
                    render_form=render_species_form,
                    edit_select_label="Choose a species to edit",
                    edit_select_key="species_edit_select",
                    search_key="species_search",
                    search_label="Search species",
                    option_label_builder=lambda row: row["Label"],
                )

    except sqlite3.Error as exc:
        st.error(f"SQLite error: {exc}")


if __name__ == "__main__":
    main()
