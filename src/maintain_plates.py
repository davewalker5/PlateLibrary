"""Streamlit maintenance UI for the microscopy plate library.

This script provides a deliberately simple local web UI for maintaining the
fast-moving tables in the plate library database:

- PLATE
- INVESTIGATION

The application is intended to sit alongside Datasette:

- Streamlit is used for data entry and editing
- Datasette is used for browsing, querying and verifying the data

The rest of the lookup tables are assumed to change only occasionally and can
be maintained separately when needed.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Default locations for the SQLite database and the local Datasette instance.
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_DB_PATH = Path(PROJECT_DIR) / "data" / "plate_library.db"
DEFAULT_DATASETTE_URL = "http://127.0.0.1:8001"


# -----------------------------------------------------------------------------
# SQLite helpers
# -----------------------------------------------------------------------------
def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a SQLite connection configured for dictionary-style row access."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """Return True if the given table or view exists in the database."""
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type IN ('table', 'view') AND name = ?
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def fetch_lookup(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    """Execute a lookup query and return the rows as ordinary dictionaries."""
    rows = conn.execute(sql).fetchall()
    return [dict(row) for row in rows]


# -----------------------------------------------------------------------------
# Lookup queries used by the PLATE and INVESTIGATION forms
# -----------------------------------------------------------------------------
def fetch_species(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return species records formatted for a select box."""
    return fetch_lookup(
        conn,
        """
        SELECT
            Id,
            CASE
                WHEN Common_Name IS NOT NULL AND Scientific_Name IS NOT NULL
                    THEN Common_Name || ' — ' || Scientific_Name
                WHEN Common_Name IS NOT NULL
                    THEN Common_Name
                WHEN Scientific_Name IS NOT NULL
                    THEN Scientific_Name
                ELSE '(Unnamed species record #' || Id || ')'
            END AS Label
        FROM SPECIES
        ORDER BY
            CASE WHEN Common_Name IS NULL THEN 1 ELSE 0 END,
            Common_Name,
            Scientific_Name
        """,
    )


def fetch_objectives(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return microscope objectives formatted for display in the UI."""
    return fetch_lookup(
        conn,
        """
        SELECT
            o.Id,
            m.Description || ' | ' || o.Description || ' | ' || o.Magnification || 'x' AS Label
        FROM OBJECTIVE o
        INNER JOIN MICROSCOPE m ON m.Id = o.Microscope_Id
        ORDER BY m.Description, o.Magnification, o.Description
        """,
    )


def fetch_cameras(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return camera records formatted for the select box."""
    return fetch_lookup(
        conn,
        """
        SELECT
            Id,
            CASE
                WHEN Lower_Effective_Magnification IS NOT NULL AND Upper_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. ' || Lower_Effective_Magnification || 'x–' || Upper_Effective_Magnification || 'x'
                WHEN Lower_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. from ' || Lower_Effective_Magnification || 'x'
                WHEN Upper_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. to ' || Upper_Effective_Magnification || 'x'
                ELSE Description
            END AS Label
        FROM CAMERA
        ORDER BY Description
        """,
    )


def fetch_stains(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return stains formatted for display in the UI."""
    return fetch_lookup(
        conn,
        """
        SELECT
            Id,
            Description AS Label
        FROM STAIN
        ORDER BY Description
        """,
    )


def fetch_locations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return locations formatted for display in the UI."""
    return fetch_lookup(
        conn,
        """
        SELECT
            Id,
            CASE
                WHEN Grid_Reference IS NOT NULL AND TRIM(Grid_Reference) <> ''
                    THEN Name || ' | ' || Grid_Reference
                ELSE Name
            END AS Label
        FROM LOCATION
        ORDER BY Name
        """,
    )


def fetch_series(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return series values formatted for investigation maintenance."""
    return fetch_lookup(
        conn,
        """
        SELECT
            se.Id,
            sc.Code || ' ' || se.Name AS Label
        FROM SERIES se
        INNER JOIN SCHEME sc ON sc.Id = se.Scheme_Id
        ORDER BY sc.Code, se.Name
        """,
    )


def fetch_investigations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return investigations formatted for use in the PLATE form."""
    return fetch_lookup(
        conn,
        """
        SELECT
            i.Id,
            sc.Code || ' ' || se.Name || ' | ' || i.Reference || ' | ' || i.Title AS Label
        FROM INVESTIGATION i
        INNER JOIN SERIES se ON se.Id = i.Series_Id
        INNER JOIN SCHEME sc ON sc.Id = se.Scheme_Id
        ORDER BY sc.Code, se.Name, i.Reference
        """,
    )


# -----------------------------------------------------------------------------
# Record queries for browsing and editing
# -----------------------------------------------------------------------------
def fetch_plate_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of plates for browsing and selection."""
    return fetch_lookup(
        conn,
        """
        SELECT
            p.Id,
            p.Date,
            p.Plate,
            p.Reference,
            p.Specimen,
            COALESCE(sp.Common_Name, sp.Scientific_Name, '') AS Species,
            i.Reference AS Investigation
        FROM PLATE p
        LEFT JOIN SPECIES sp ON sp.Id = p.Species_Id
        INNER JOIN INVESTIGATION i ON i.Id = p.Investigation_Id
        ORDER BY p.Date DESC, p.Plate
        """,
    )


def fetch_plate(conn: sqlite3.Connection, plate_id: int) -> dict[str, Any] | None:
    """Fetch a single PLATE row for editing."""
    row = conn.execute(
        """
        SELECT
            Id,
            Date,
            Specimen,
            Plate,
            Reference,
            Notebook_Reference,
            Notes,
            Species_Id,
            Objective_Id,
            Camera_Id,
            Stain_Id,
            Location_Id,
            Investigation_Id
        FROM PLATE
        WHERE Id = ?
        """,
        (plate_id,),
    ).fetchone()
    return dict(row) if row else None


def fetch_investigation_list(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Return a compact list of investigations for browsing and selection."""
    return fetch_lookup(
        conn,
        """
        SELECT
            i.Id,
            i.Reference,
            i.Title,
            sc.Code || ' ' || se.Name AS Series,
            (
                SELECT COUNT(*)
                FROM PLATE p
                WHERE p.Investigation_Id = i.Id
            ) AS Plate_Count
        FROM INVESTIGATION i
        INNER JOIN SERIES se ON se.Id = i.Series_Id
        INNER JOIN SCHEME sc ON sc.Id = se.Scheme_Id
        ORDER BY i.Reference
        """,
    )


def fetch_investigation(
    conn: sqlite3.Connection, investigation_id: int
) -> dict[str, Any] | None:
    """Fetch a single INVESTIGATION row for editing."""
    row = conn.execute(
        """
        SELECT
            Id,
            Reference,
            Title,
            Series_Id
        FROM INVESTIGATION
        WHERE Id = ?
        """,
        (investigation_id,),
    ).fetchone()
    return dict(row) if row else None


# -----------------------------------------------------------------------------
# Data conversion helpers
# -----------------------------------------------------------------------------
def parse_db_date(value: Any) -> date:
    """Convert a database date value into a Python date for Streamlit.

    The database may contain plain ISO dates, ISO datetimes or dates from older
    import steps, so this function accepts several common formats.
    """
    if value is None:
        return date.today()

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    text = str(value).strip()
    if not text:
        return date.today()

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return date.today()


def option_index(options: list[dict[str, Any]], selected_id: int | None) -> int:
    """Return the select-box index for the given foreign key value."""
    if selected_id is None:
        return 0

    for idx, option in enumerate(options):
        if option["Id"] == selected_id:
            return idx
    return 0


def selected_fk(option: dict[str, Any] | None) -> int | None:
    """Extract the foreign-key Id from a selected option dictionary."""
    if option is None:
        return None
    return option["Id"]


def make_nullable_options(
    options: list[dict[str, Any]], placeholder: str = "— None —"
) -> list[dict[str, Any]]:
    """Prepend a null option to a lookup list for optional relationships."""
    return [{"Id": None, "Label": placeholder}] + options


def store_last_used_plate_values(payload: dict[str, Any]) -> None:
    """Remember commonly repeated PLATE selections between submissions."""
    st.session_state["last_objective_id"] = payload["Objective_Id"]
    st.session_state["last_camera_id"] = payload["Camera_Id"]
    st.session_state["last_investigation_id"] = payload["Investigation_Id"]


def store_last_used_investigation_values(payload: dict[str, Any]) -> None:
    """Remember the last selected series for adding multiple investigations."""
    st.session_state["last_series_id"] = payload["Series_Id"]


# -----------------------------------------------------------------------------
# INSERT / UPDATE / DELETE helpers
# -----------------------------------------------------------------------------
def insert_plate(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new PLATE record."""
    conn.execute(
        """
        INSERT INTO PLATE (
            Date,
            Specimen,
            Plate,
            Reference,
            Notebook_Reference,
            Notes,
            Species_Id,
            Objective_Id,
            Camera_Id,
            Stain_Id,
            Location_Id,
            Investigation_Id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            values["Date"],
            values["Specimen"],
            values["Plate"],
            values["Reference"],
            values["Notebook_Reference"],
            values["Notes"],
            values["Species_Id"],
            values["Objective_Id"],
            values["Camera_Id"],
            values["Stain_Id"],
            values["Location_Id"],
            values["Investigation_Id"],
        ),
    )
    conn.commit()


def update_plate(conn: sqlite3.Connection, plate_id: int, values: dict[str, Any]) -> None:
    """Update an existing PLATE record."""
    conn.execute(
        """
        UPDATE PLATE
        SET
            Date = ?,
            Specimen = ?,
            Plate = ?,
            Reference = ?,
            Notebook_Reference = ?,
            Notes = ?,
            Species_Id = ?,
            Objective_Id = ?,
            Camera_Id = ?,
            Stain_Id = ?,
            Location_Id = ?,
            Investigation_Id = ?
        WHERE Id = ?
        """,
        (
            values["Date"],
            values["Specimen"],
            values["Plate"],
            values["Reference"],
            values["Notebook_Reference"],
            values["Notes"],
            values["Species_Id"],
            values["Objective_Id"],
            values["Camera_Id"],
            values["Stain_Id"],
            values["Location_Id"],
            values["Investigation_Id"],
            plate_id,
        ),
    )
    conn.commit()


def delete_plate(conn: sqlite3.Connection, plate_id: int) -> None:
    """Delete a PLATE record."""
    conn.execute("DELETE FROM PLATE WHERE Id = ?", (plate_id,))
    conn.commit()


def insert_investigation(conn: sqlite3.Connection, values: dict[str, Any]) -> None:
    """Insert a new INVESTIGATION record."""
    conn.execute(
        """
        INSERT INTO INVESTIGATION (
            Reference,
            Title,
            Series_Id
        )
        VALUES (?, ?, ?)
        """,
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
        ),
    )
    conn.commit()


def update_investigation(
    conn: sqlite3.Connection,
    investigation_id: int,
    values: dict[str, Any],
) -> None:
    """Update an existing INVESTIGATION record."""
    conn.execute(
        """
        UPDATE INVESTIGATION
        SET
            Reference = ?,
            Title = ?,
            Series_Id = ?
        WHERE Id = ?
        """,
        (
            values["Reference"],
            values["Title"],
            values["Series_Id"],
            investigation_id,
        ),
    )
    conn.commit()


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


def datasette_investigation_url(
    base_url: str, db_file: Path, investigation_id: int
) -> str:
    """Build the Datasette URL for an INVESTIGATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/INVESTIGATION/{investigation_id}"


# -----------------------------------------------------------------------------
# Streamlit form renderers
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
    default_date = parse_db_date(plate.get("Date"))

    # For new records, reuse the last selections to speed up repetitive entry.
    if mode == "add":
        default_objective_id = st.session_state.get("last_objective_id")
        default_camera_id = st.session_state.get("last_camera_id")
        default_investigation_id = st.session_state.get("last_investigation_id")
    else:
        default_objective_id = plate.get("Objective_Id")
        default_camera_id = plate.get("Camera_Id")
        default_investigation_id = plate.get("Investigation_Id")

    with st.form(f"{mode}_plate_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            plate_date = st.date_input("Date", value=default_date)
            specimen = st.text_input("Specimen", value=plate.get("Specimen") or "")
            plate_code = st.text_input("Plate", value=plate.get("Plate") or "")
            reference = st.text_input("Reference", value=plate.get("Reference") or "")

        with col2:
            notebook_reference = st.text_input(
                "Notebook Reference",
                value=plate.get("Notebook_Reference") or "",
            )
            species = st.selectbox(
                "Species",
                options=species_options,
                index=option_index(species_options, plate.get("Species_Id")),
                format_func=lambda x: x["Label"],
            )
            objective = st.selectbox(
                "Objective *",
                options=objective_options,
                index=option_index(objective_options, default_objective_id),
                format_func=lambda x: x["Label"],
            )
            camera = st.selectbox(
                "Camera *",
                options=camera_options,
                index=option_index(camera_options, default_camera_id),
                format_func=lambda x: x["Label"],
            )

        stain = st.selectbox(
            "Stain",
            options=stain_options,
            index=option_index(stain_options, plate.get("Stain_Id")),
            format_func=lambda x: x["Label"],
        )

        location = st.selectbox(
            "Location",
            options=location_options,
            index=option_index(location_options, plate.get("Location_Id")),
            format_func=lambda x: x["Label"],
        )

        investigation = st.selectbox(
            "Investigation *",
            options=investigation_options,
            index=option_index(investigation_options, default_investigation_id),
            format_func=lambda x: x["Label"],
        )

        notes = st.text_area("Notes", value=plate.get("Notes") or "", height=150)

        submitted = st.form_submit_button(
            "Add plate" if mode == "add" else "Save changes",
            type="primary",
        )

    # Edit-only utilities sit outside the form so that they can use ordinary
    # buttons without interacting with the save button logic.
    if mode == "edit" and plate.get("Id") is not None:
        plate_id = int(plate["Id"])
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
            store_last_used_plate_values(payload)
            st.success("Plate added.")
        else:
            assert plate.get("Id") is not None
            update_plate(conn, int(plate["Id"]), payload)
            store_last_used_plate_values(payload)
            st.success("Plate updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save plate: {exc}")


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

    if mode == "add":
        default_series_id = st.session_state.get("last_series_id")
    else:
        default_series_id = investigation.get("Series_Id")

    with st.form(f"{mode}_investigation_form", clear_on_submit=False):
        reference = st.text_input("Reference", value=investigation.get("Reference") or "")
        title = st.text_input("Title", value=investigation.get("Title") or "")
        series = st.selectbox(
            "Series *",
            options=series_options,
            index=option_index(series_options, default_series_id),
            format_func=lambda x: x["Label"],
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
            store_last_used_investigation_values(payload)
            st.success("Investigation added.")
        else:
            assert investigation.get("Id") is not None
            update_investigation(conn, int(investigation["Id"]), payload)
            store_last_used_investigation_values(payload)
            st.success("Investigation updated.")
        st.rerun()
    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save investigation: {exc}")


# -----------------------------------------------------------------------------
# Main UI
# -----------------------------------------------------------------------------
def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Plate Library", layout="wide")
    st.title("Plate Library")
    st.caption("Simple local maintenance UI for the PLATE and INVESTIGATION tables")

    with st.sidebar:
        st.header("Database")
        db_path = st.text_input("SQLite DB path", value=DEFAULT_DB_PATH.absolute())

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
            if not table_exists(conn, "PLATE"):
                st.error("This database does not contain a PLATE table.")
                return

            if not table_exists(conn, "INVESTIGATION"):
                st.error("This database does not contain an INVESTIGATION table.")
                return

            top_plate_tab, top_investigation_tab = st.tabs(["Plates", "Investigations"])

            with top_plate_tab:
                add_tab, edit_tab, browse_tab = st.tabs(
                    ["Add plate", "Edit plate", "Browse"]
                )

                with add_tab:
                    st.subheader("Add plate")
                    render_plate_form(
                        conn,
                        mode="add",
                        db_file=db_file,
                        datasette_url=datasette_url,
                    )

                with edit_tab:
                    st.subheader("Edit plate")
                    plate_rows = fetch_plate_list(conn)

                    if not plate_rows:
                        st.info("No plates yet.")
                    else:
                        edit_options = [
                            {
                                "Id": row["Id"],
                                "Label": f'{row["Date"]} | {row["Plate"]} | {row["Reference"]} | {row["Specimen"]}',
                            }
                            for row in plate_rows
                        ]

                        selected = st.selectbox(
                            "Choose a plate to edit",
                            options=edit_options,
                            format_func=lambda x: x["Label"],
                            key="plate_edit_select",
                        )
                        plate = fetch_plate(conn, int(selected["Id"]))
                        if plate is not None:
                            render_plate_form(
                                conn,
                                mode="edit",
                                db_file=db_file,
                                datasette_url=datasette_url,
                                plate=plate,
                            )

                with browse_tab:
                    st.subheader("Current plates")
                    plate_rows = fetch_plate_list(conn)
                    search = st.text_input("Search plates", key="plate_search")

                    if plate_rows:
                        if search.strip():
                            search_text = search.strip().lower()
                            filtered_rows = [
                                row
                                for row in plate_rows
                                if any(search_text in str(value).lower() for value in row.values())
                            ]
                        else:
                            filtered_rows = plate_rows

                        st.dataframe(
                            filtered_rows,
                            use_container_width=True,
                            hide_index=True,
                        )
                        st.caption(f"{len(filtered_rows)} plate(s) shown")
                    else:
                        st.info("No plates found.")

            with top_investigation_tab:
                add_tab, edit_tab, browse_tab = st.tabs(
                    ["Add investigation", "Edit investigation", "Browse"]
                )

                with add_tab:
                    st.subheader("Add investigation")
                    render_investigation_form(
                        conn,
                        mode="add",
                        db_file=db_file,
                        datasette_url=datasette_url,
                    )

                with edit_tab:
                    st.subheader("Edit investigation")
                    investigation_rows = fetch_investigation_list(conn)

                    if not investigation_rows:
                        st.info("No investigations yet.")
                    else:
                        edit_options = [
                            {
                                "Id": row["Id"],
                                "Label": f'{row["Reference"]} | {row["Title"]} | {row["Series"]}',
                            }
                            for row in investigation_rows
                        ]

                        selected = st.selectbox(
                            "Choose an investigation to edit",
                            options=edit_options,
                            format_func=lambda x: x["Label"],
                            key="investigation_edit_select",
                        )
                        investigation = fetch_investigation(conn, int(selected["Id"]))
                        if investigation is not None:
                            render_investigation_form(
                                conn,
                                mode="edit",
                                db_file=db_file,
                                datasette_url=datasette_url,
                                investigation=investigation,
                            )

                with browse_tab:
                    st.subheader("Current investigations")
                    investigation_rows = fetch_investigation_list(conn)
                    search = st.text_input(
                        "Search investigations",
                        key="investigation_search",
                    )

                    if investigation_rows:
                        if search.strip():
                            search_text = search.strip().lower()
                            filtered_rows = [
                                row
                                for row in investigation_rows
                                if any(search_text in str(value).lower() for value in row.values())
                            ]
                        else:
                            filtered_rows = investigation_rows

                        st.dataframe(
                            filtered_rows,
                            use_container_width=True,
                            hide_index=True,
                        )
                        st.caption(f"{len(filtered_rows)} investigation(s) shown")
                    else:
                        st.info("No investigations found.")

    except sqlite3.Error as exc:
        st.error(f"SQLite error: {exc}")


if __name__ == "__main__":
    main()
