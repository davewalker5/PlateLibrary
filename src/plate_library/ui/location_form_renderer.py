# -----------------------------------------------------------------------------
# Generic imports
# -----------------------------------------------------------------------------
import sqlite3
from pathlib import Path
from typing import Any

import streamlit as st
import folium
from streamlit_folium import st_folium

from plate_library.utils.data_conversion_helpers import form_key_base

# -----------------------------------------------------------------------------
# Entity specific imports
# -----------------------------------------------------------------------------
from plate_library.sql.location_sql import delete_location, insert_location, update_location
from plate_library.utils.coordinate_transformer import latitude_longitude_to_reference
from plate_library.utils.config_reader import get_location_property

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
COORDINATE_SYSTEM_OPTIONS = ["BNG", "UTM", "MGRS"]
DEFAULT_COORDINATE_SYSTEM = "BNG"
LAST_COORDINATE_SYSTEM_KEY = "location_last_coordinate_system"
DEFAULT_MAP_STYLE = "OpenStreetMap"
DEFAULT_MAP_ATTRIBUTION = None

# -----------------------------------------------------------------------------
# Datasette links
# -----------------------------------------------------------------------------
def datasette_location_url(base_url: str, db_file: Path, location_id: int) -> str:
    """Build the Datasette URL for a LOCATION record."""
    db_name = db_file.stem
    return f"{base_url.rstrip('/')}/{db_name}/LOCATION/{location_id}"


# -----------------------------------------------------------------------------
# Small helpers
# -----------------------------------------------------------------------------
def _parse_optional_float(value: str, field_name: str, errors: list[str]) -> float | None:
    """
    Parse a text field into a float or None.
    Append a validation message to errors if parsing fails.
    """
    if not str(value).strip():
        return None

    try:
        return float(str(value).strip())
    except ValueError:
        errors.append(f"{field_name} must be a valid number.")
        return None


def _valid_lat_lon(latitude: float | None, longitude: float | None) -> bool:
    """Return True if latitude/longitude are both present and within valid bounds."""
    return (
        latitude is not None
        and longitude is not None
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def _calculate_gridref_into_session(
    latitude_key: str,
    longitude_key: str,
    gridref_key: str,
    coordinate_system_key: str,
    message_key: str,
) -> None:
    """
    Read latitude/longitude from session state, calculate a coordinate reference
    in the selected system, and write it back into the reference field.
    """
    errors: list[str] = []

    latitude_text = st.session_state.get(latitude_key, "")
    longitude_text = st.session_state.get(longitude_key, "")
    coordinate_system = st.session_state.get(coordinate_system_key, DEFAULT_COORDINATE_SYSTEM)

    latitude = _parse_optional_float(latitude_text, "Latitude", errors)
    longitude = _parse_optional_float(longitude_text, "Longitude", errors)

    if str(latitude_text).strip() == "":
        errors.append("Latitude is required to calculate the reference.")
    if str(longitude_text).strip() == "":
        errors.append("Longitude is required to calculate the reference.")

    if latitude is not None and not -90 <= latitude <= 90:
        errors.append("Latitude must be between -90 and 90.")

    if longitude is not None and not -180 <= longitude <= 180:
        errors.append("Longitude must be between -180 and 180.")

    if errors:
        st.session_state[message_key] = ("error", errors)
        return

    try:
        st.session_state[gridref_key] = latitude_longitude_to_reference(
            latitude=latitude,
            longitude=longitude,
            system=coordinate_system,
            os_digits=8,
            utm_include_band=True,
            utm_precision=0,
            mgrs_precision=5,
        )
        st.session_state[LAST_COORDINATE_SYSTEM_KEY] = coordinate_system
        st.session_state[message_key] = (
            "success",
            [f"{coordinate_system} reference calculated."],
        )
    except Exception as exc:
        st.session_state[message_key] = ("error", [f"Could not calculate reference: {exc}"])


# -----------------------------------------------------------------------------
# Form renderer
# -----------------------------------------------------------------------------
def render_location_form(
    conn: sqlite3.Connection,
    mode: str,
    db_file: Path,
    datasette_url: str,
    location: dict[str, Any] | None = None,
) -> None:
    """Render the add/edit form for LOCATION records."""
    location = location or {}
    location_id = int(location["Id"]) if location.get("Id") is not None else None
    key_base = form_key_base("location", mode, location_id)
    form_key = f"{mode}_location_form_{location_id if location_id is not None else 'new'}"

    # Widget / state keys
    name_key = f"{key_base}_name"
    latitude_key = f"{key_base}_latitude"
    longitude_key = f"{key_base}_longitude"
    gridref_key = f"{key_base}_grid_reference"
    coordinate_system_key = f"{key_base}_coordinate_system"
    message_key = f"{key_base}_message"
    clear_form_key = f"{key_base}_clear_form"

    # Map interaction keys
    map_key = f"{key_base}_map"
    map_click_signature_key = f"{key_base}_map_click_signature"
    map_center_lat_key = f"{key_base}_map_center_lat"
    map_center_lon_key = f"{key_base}_map_center_lon"
    map_zoom_key = f"{key_base}_map_zoom"
    map_style_key = f"{key_base}_map_style"

    # Get the default map parameters
    initial_map_latitude = get_location_property("default_latitude")
    initial_map_longitude = get_location_property("default_longitude")
    initial_map_zoom = get_location_property("map_zoom")
    map_style = get_location_property("map_style") or DEFAULT_MAP_STYLE
    attribution = get_location_property("attribution") or DEFAULT_MAP_ATTRIBUTION

    # Sticky default for coordinate system
    if LAST_COORDINATE_SYSTEM_KEY not in st.session_state:
        st.session_state[LAST_COORDINATE_SYSTEM_KEY] = DEFAULT_COORDINATE_SYSTEM

    # Clear add form on rerun after successful insert
    if st.session_state.get(clear_form_key, False):
        st.session_state[name_key] = ""
        st.session_state[latitude_key] = ""
        st.session_state[longitude_key] = ""
        st.session_state[gridref_key] = ""
        st.session_state[coordinate_system_key] = st.session_state.get(
            LAST_COORDINATE_SYSTEM_KEY,
            DEFAULT_COORDINATE_SYSTEM,
        )
        st.session_state[clear_form_key] = False

    # Seed widget state once
    if name_key not in st.session_state:
        st.session_state[name_key] = location.get("Name") or ""

    if latitude_key not in st.session_state:
        st.session_state[latitude_key] = (
            "" if location.get("Latitude") is None else str(location.get("Latitude"))
        )

    if longitude_key not in st.session_state:
        st.session_state[longitude_key] = (
            "" if location.get("Longitude") is None else str(location.get("Longitude"))
        )

    if gridref_key not in st.session_state:
        st.session_state[gridref_key] = location.get("Grid_Reference") or ""

    if coordinate_system_key not in st.session_state:
        st.session_state[coordinate_system_key] = (
            location.get("Coordinate_System") or st.session_state[LAST_COORDINATE_SYSTEM_KEY]
        )

    # Seed map state once
    map_parse_errors: list[str] = []
    current_lat = _parse_optional_float(
        st.session_state.get(latitude_key, ""), "Latitude", map_parse_errors
    )
    current_lon = _parse_optional_float(
        st.session_state.get(longitude_key, ""), "Longitude", map_parse_errors
    )

    if map_center_lat_key not in st.session_state:
        if _valid_lat_lon(current_lat, current_lon):
            st.session_state[map_center_lat_key] = current_lat
            st.session_state[map_center_lon_key] = current_lon
            st.session_state[map_zoom_key] = 14
        else:
            st.session_state[map_center_lat_key] = initial_map_latitude
            st.session_state[map_center_lon_key] = initial_map_longitude
            st.session_state[map_zoom_key] = initial_map_zoom

    if map_style_key not in st.session_state:
        st.session_state[map_style_key] = map_style

    # -------------------------------------------------------------------------
    # Map picker (outside the form)
    # -------------------------------------------------------------------------
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.4, 1.2, 1.0, 1.4])

    with ctrl1:
        st.markdown("<div style='height: 1.8em'></div>", unsafe_allow_html=True)
        if st.button("Go To Pin", use_container_width=True):
            lat_for_map = _parse_optional_float(
                st.session_state.get(latitude_key, ""), "Latitude", []
            )
            lon_for_map = _parse_optional_float(
                st.session_state.get(longitude_key, ""), "Longitude", []
            )

            if _valid_lat_lon(lat_for_map, lon_for_map):
                st.session_state[map_center_lat_key] = lat_for_map
                st.session_state[map_center_lon_key] = lon_for_map
                st.session_state[map_zoom_key] = 14
            else:
                st.session_state[message_key] = (
                    "error",
                    ["No valid current coordinates to centre on."],
                )
            st.rerun()

    with ctrl2:
        st.markdown("<div style='height: 1.8em'></div>", unsafe_allow_html=True)
        if st.button("Reset", use_container_width=True):
            st.session_state[map_center_lat_key] = initial_map_latitude
            st.session_state[map_center_lon_key] = initial_map_longitude
            st.session_state[map_zoom_key] = initial_map_zoom
            st.rerun()

    with ctrl3:
        st.markdown("<div style='height: 1.8em'></div>", unsafe_allow_html=True)
        if st.button("Clear Pin", use_container_width=True):
            st.session_state[latitude_key] = ""
            st.session_state[longitude_key] = ""
            st.session_state[gridref_key] = ""
            st.session_state[map_click_signature_key] = None
            st.session_state[message_key] = ("success", ["Coordinates cleared."])
            st.rerun()

    with ctrl4:
        st.selectbox(
            "Map style",
            ["OpenStreetMap", "CartoDB positron", "CartoDB Voyager"],
            key=map_style_key,
        )

    map_center_lat = st.session_state[map_center_lat_key]
    map_center_lon = st.session_state[map_center_lon_key]
    map_zoom = st.session_state[map_zoom_key]
    current_map_style = st.session_state[map_style_key]

    if current_map_style == "OpenStreetMap":
        current_attr = None
    elif current_map_style == "CartoDB positron":
        current_attr = None
    elif current_map_style == "CartoDB Voyager":
        current_attr = None
    else:
        current_attr = attribution

    m = folium.Map(
        location=[map_center_lat, map_center_lon],
        zoom_start=map_zoom,
        tiles=current_map_style,
        attr=current_attr,
    )

    current_lat = _parse_optional_float(st.session_state.get(latitude_key, ""), "Latitude", [])
    current_lon = _parse_optional_float(st.session_state.get(longitude_key, ""), "Longitude", [])

    if _valid_lat_lon(current_lat, current_lon):
        folium.Marker(
            [current_lat, current_lon],
            tooltip="Current location",
        ).add_to(m)

    map_data = st_folium(
        m,
        width=None,
        height=360,
        key=map_key,
    )

    last_clicked = map_data.get("last_clicked") if map_data else None
    if last_clicked:
        clicked_lat = float(last_clicked["lat"])
        clicked_lon = float(last_clicked["lng"])
        click_signature = f"{clicked_lat:.8f},{clicked_lon:.8f}"

        if st.session_state.get(map_click_signature_key) != click_signature:
            st.session_state[latitude_key] = f"{clicked_lat:.8f}"
            st.session_state[longitude_key] = f"{clicked_lon:.8f}"
            st.session_state[map_center_lat_key] = clicked_lat
            st.session_state[map_center_lon_key] = clicked_lon

            if map_data.get("zoom") is not None:
                st.session_state[map_zoom_key] = map_data["zoom"]

            st.session_state[map_click_signature_key] = click_signature
            st.session_state[message_key] = (
                "success",
                [f"Coordinates selected from map: {clicked_lat:.8f}, {clicked_lon:.8f}"],
            )
            st.rerun()

    # -------------------------------------------------------------------------
    # Form
    # -------------------------------------------------------------------------
    with st.form(form_key, clear_on_submit=False):
        name = st.text_input("Name *", key=name_key)

        # Show callback messages inside the form area
        if message_key in st.session_state:
            message_type, messages = st.session_state[message_key]

            if message_type == "success":
                for message in messages:
                    st.success(message)
            elif message_type == "error":
                for message in messages:
                    st.error(message)

            del st.session_state[message_key]

        col1, col2 = st.columns(2)
        with col1:
            latitude_text = st.text_input(
                "Latitude",
                key=latitude_key,
                help="Leave blank if the location does not yet have coordinates.",
            )
        with col2:
            longitude_text = st.text_input(
                "Longitude",
                key=longitude_key,
                help="Leave blank if the location does not yet have coordinates.",
            )

        grid_col, system_col, button_col = st.columns([3.2, 1.2, 1.2])

        with grid_col:
            grid_reference = st.text_input(
                "Coordinate Reference",
                key=gridref_key,
            )

        with system_col:
            coordinate_system = st.selectbox(
                "System",
                COORDINATE_SYSTEM_OPTIONS,
                key=coordinate_system_key,
            )

        with button_col:
            st.markdown("<div style='height: 1.8em'></div>", unsafe_allow_html=True)
            st.form_submit_button(
                "Calculate",
                on_click=_calculate_gridref_into_session,
                args=(
                    latitude_key,
                    longitude_key,
                    gridref_key,
                    coordinate_system_key,
                    message_key,
                ),
                use_container_width=True,
            )

        submitted = st.form_submit_button(
            "Add location" if mode == "add" else "Save changes",
            type="primary",
        )

    # -------------------------------------------------------------------------
    # Edit-only actions
    # -------------------------------------------------------------------------
    if mode == "edit" and location.get("Id") is not None:
        location_id = int(location["Id"])
        st.markdown(
            f"[View in Datasette]({datasette_location_url(datasette_url, db_file, location_id)})"
        )

        confirm_delete = st.checkbox(
            "Confirm delete of this location",
            key=f"confirm_delete_location_{location_id}",
        )
        if st.button(
            "Delete location",
            type="secondary",
            key=f"delete_location_{location_id}",
        ):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting.")
            else:
                try:
                    delete_location(conn, location_id)
                    st.success("Location deleted.")
                    st.rerun()
                except sqlite3.IntegrityError as exc:
                    st.error(f"Could not delete location: {exc}")

    if not submitted:
        return

    # -------------------------------------------------------------------------
    # Validation for save
    # -------------------------------------------------------------------------
    errors: list[str] = []

    if not name.strip():
        errors.append("Name is required.")

    latitude = _parse_optional_float(latitude_text, "Latitude", errors)
    longitude = _parse_optional_float(longitude_text, "Longitude", errors)

    if latitude is not None and not -90 <= latitude <= 90:
        errors.append("Latitude must be between -90 and 90.")

    if longitude is not None and not -180 <= longitude <= 180:
        errors.append("Longitude must be between -180 and 180.")

    if errors:
        for error in errors:
            st.error(error)
        return

    # Retain the selected system for the next add/edit form in this session
    st.session_state[LAST_COORDINATE_SYSTEM_KEY] = coordinate_system

    payload = {
        "Name": name.strip(),
        "Grid_Reference": grid_reference.strip() or None,
        "Coordinate_System": coordinate_system,
        "Latitude": latitude,
        "Longitude": longitude,
    }

    try:
        if mode == "add":
            insert_location(conn, payload)
            st.session_state[message_key] = ("success", ["Location added."])
            st.session_state[clear_form_key] = True

        else:
            assert location.get("Id") is not None
            update_location(conn, int(location["Id"]), payload)
            st.session_state[message_key] = ("success", ["Location updated."])

        st.rerun()

    except sqlite3.IntegrityError as exc:
        st.error(f"Could not save location: {exc}")
 