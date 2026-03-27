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
from species_sql import delete_species, insert_species, update_species


# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_species_url(base_url: str, db_file: Path, species_id: int) -> str:
    """Build the Datasette URL for a SPECIES record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/SPECIES/{species_id}"


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
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