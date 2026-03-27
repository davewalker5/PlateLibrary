import sqlite3
import streamlit as st
from typing import Any
from pathlib import Path


# -----------------------------------------------------------------------------
# Generic UI helpers used by the repeated maintenance screens
# -----------------------------------------------------------------------------
def filter_rows(rows: list[dict[str, Any]], search_text: str) -> list[dict[str, Any]]:
    """Return rows filtered by a simple case-insensitive free-text search.

    This deliberately searches across the string representation of each value so
    that the browse tabs stay lightweight and easy to understand. For a small
    local maintenance UI, the simplicity is more valuable than building a more
    elaborate per-column filter system.
    """
    if not search_text.strip():
        return rows

    needle = search_text.strip().lower()
    return [
        row
        for row in rows
        if any(needle in str(value).lower() for value in row.values())
    ]


def build_edit_options(
    rows: list[dict[str, Any]],
    label_builder,
) -> list[dict[str, Any]]:
    """Convert browse rows into select-box options for the edit tab.

    Each entity uses a slightly different human-readable label, so the caller
    supplies a small label-building function while the common wrapping logic
    lives here.
    """
    return [{"Id": row["Id"], "Label": label_builder(row)} for row in rows]


def render_browse_table(
    rows: list[dict[str, Any]],
    *,
    entity_name: str,
    search_key: str,
    search_label: str,
) -> int | None:
    """Render a searchable selectable table and return the selected record Id."""
    search = st.text_input(search_label, key=search_key)

    if not rows:
        st.info(f"No {entity_name} found.")
        return None

    filtered_rows = filter_rows(rows, search)

    event = st.dataframe(
        filtered_rows,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"{entity_name}_browse_table",
    )
    st.caption(f"{len(filtered_rows)} {entity_name}(s) shown")

    selected_rows = event.selection.rows
    if not selected_rows:
        return None

    selected_idx = selected_rows[0]
    return int(filtered_rows[selected_idx]["Id"])


def render_maintenance_section(
    *,
    conn: sqlite3.Connection,
    db_file: Path,
    datasette_url: str,
    entity_name: str,
    add_title: str,
    edit_title: str,
    browse_title: str,
    fetch_list,
    fetch_record,
    render_form,
    edit_select_label: str,
    edit_select_key: str,
    search_key: str,
    search_label: str,
    option_label_builder,
) -> None:
    """Render the repeated add/edit/browse pattern for one entity type.

    Uses a segmented control instead of st.tabs so the active view can be
    driven reliably from session state after a row is selected in Browse.
    """
    view_key = f"{entity_name}_view"
    pending_view_key = f"{entity_name}_pending_view"
    selected_id_key = f"{entity_name}_selected_id"

    views = [add_title, edit_title, browse_title]

    # Apply any deferred view change BEFORE the widget is instantiated.
    if pending_view_key in st.session_state:
        st.session_state[view_key] = st.session_state.pop(pending_view_key)

    if view_key not in st.session_state:
        st.session_state[view_key] = add_title

    active_view = st.segmented_control(
        "Mode",
        options=views,
        default=st.session_state[view_key],
        key=view_key,
        selection_mode="single",
        label_visibility="collapsed",
    )

    if active_view == add_title:
        st.subheader(add_title)
        render_form(
            conn,
            mode="add",
            db_file=db_file,
            datasette_url=datasette_url,
        )

    elif active_view == edit_title:
        st.subheader(edit_title)
        rows = fetch_list(conn)

        if not rows:
            st.info(f"No {entity_name} yet.")
        else:
            edit_options = build_edit_options(rows, option_label_builder)

            default_index = 0
            selected_id = st.session_state.get(selected_id_key)

            if selected_id is not None:
                for idx, option in enumerate(edit_options):
                    if option["Id"] == selected_id:
                        default_index = idx
                        break

            selected = st.selectbox(
                edit_select_label,
                options=edit_options,
                index=default_index,
                format_func=lambda x: x["Label"],
                key=edit_select_key,
            )

            st.session_state[selected_id_key] = int(selected["Id"])

            record = fetch_record(conn, int(selected["Id"]))
            if record is not None:
                render_form(
                    conn,
                    mode="edit",
                    db_file=db_file,
                    datasette_url=datasette_url,
                    **{entity_name: record},
                )

    elif active_view == browse_title:
        st.subheader(f"Current {entity_name}s")
        rows = fetch_list(conn)
        clicked_id = render_browse_table(
            rows,
            entity_name=entity_name,
            search_key=search_key,
            search_label=search_label,
        )

        if clicked_id is not None:
            st.session_state[selected_id_key] = clicked_id
            st.session_state[pending_view_key] = edit_title
            st.rerun()