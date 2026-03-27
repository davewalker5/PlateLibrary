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
from pathlib import Path
import argparse
import streamlit as st


# -----------------------------------------------------------------------------
# Database query helpers
# -----------------------------------------------------------------------------
from sqlite_helpers import database_path, get_connection, confirm_schema, load_sql_queries
from scheme_sql import fetch_scheme, fetch_scheme_list
from series_sql import fetch_series_list, fetch_series_record
from investigation_sql import fetch_investigation, fetch_investigation_list
from plate_sql import fetch_plate, fetch_plate_list
from species_sql import fetch_species_record, fetch_species_list
from location_sql import fetch_location, fetch_location_list
from camera_sql import fetch_camera_list, fetch_camera_record
from microscope_sql import fetch_microscope_list, fetch_microscope_record
from objective_sql import fetch_objective_list, fetch_objective_record


# -----------------------------------------------------------------------------
# Form rendering helpers
# -----------------------------------------------------------------------------
from ui_helpers import render_maintenance_section
from plate_form_renderer import render_plate_form
from investigation_form_renderer import render_investigation_form
from location_form_renderer import render_location_form
from scheme_form_renderer import render_scheme_form
from series_form_renderer import render_series_form
from species_form_renderer import render_species_form
from camera_form_renderer import render_camera_form
from microscope_form_renderer import render_microscope_form
from objective_form_renderer import render_objective_form


PROGRAM_NAME = "Microscopy Plate Library Maintenance UI"
PROGRAM_VERSION = "1.6.0"
PROGRAM_DESCRIPTION = "Maintenance UI for a simple microscopy plate library"

# Default location for the local Datasette instance and database name
DEFAULT_DATASETTE_URL = "http://127.0.0.1:8001"
DB_NAME = "plate_library.db"

# Root folder of the project
PROJECT_FOLDER = os.path.dirname(os.path.dirname(__file__))

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

            top_plate_tab, top_investigation_tab, top_location_tab, top_scheme_tab, top_series_tab, top_species_tab, top_camera_tab, top_microscope_tab, top_objective_tab = st.tabs([
                "Plates",
                "Investigations",
                "Locations",
                "Schemes",
                "Series",
                "Species",
                "Cameras",
                "Microscopes",
                "Objectives"
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

            with top_camera_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="camera",
                    add_title="Add camera",
                    edit_title="Edit camera",
                    browse_title="Browse",
                    fetch_list=fetch_camera_list,
                    fetch_record=fetch_camera_record,
                    render_form=render_camera_form,
                    edit_select_label="Choose a camera to edit",
                    edit_select_key="camera_edit_select",
                    search_key="camera_search",
                    search_label="Search cameras",
                    option_label_builder=lambda row: (
                        f'{row["Description"]}'
                        if row["Lower_Effective_Magnification"] is None and row["Upper_Effective_Magnification"] is None
                        else f'{row["Description"]} | {row["Lower_Effective_Magnification"] or "—"}–{row["Upper_Effective_Magnification"] or "—"}'
                    ),
                )

            with top_microscope_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="microscope",
                    add_title="Add microscope",
                    edit_title="Edit microscope",
                    browse_title="Browse",
                    fetch_list=fetch_microscope_list,
                    fetch_record=fetch_microscope_record,
                    render_form=render_microscope_form,
                    edit_select_label="Choose a microscope to edit",
                    edit_select_key="microscope_edit_select",
                    search_key="microscope_search",
                    search_label="Search microscopes",
                    option_label_builder=lambda row: (
                        f'{row["Manufacturer"]} | {row["Description"]} | {row["Manufactured"]} | {row["Serial_Number"]}'
                    ),
                )

            with top_objective_tab:
                render_maintenance_section(
                    conn=conn,
                    db_file=db_file,
                    datasette_url=datasette_url,
                    entity_name="objective",
                    add_title="Add objective",
                    edit_title="Edit objective",
                    browse_title="Browse",
                    fetch_list=fetch_objective_list,
                    fetch_record=fetch_objective_record,
                    render_form=render_objective_form,
                    edit_select_label="Choose an objective to edit",
                    edit_select_key="objective_edit_select",
                    search_key="objective_search",
                    search_label="Search objectives",
                    option_label_builder=lambda row: (
                        f'{row["Microscope_Description"]} | {row["Description"]} | {row["Magnification"]}x'
                    ),
                )

    except sqlite3.Error as exc:
        st.error(f"SQLite error: {exc}")


if __name__ == "__main__":
    main()
