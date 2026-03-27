from pathlib import Path
from datetime import date
from typing import Any
import os
import streamlit as st
from plate_library.utils.data_conversion_helpers import parse_db_date


# The plate images and, where appropriate, movies are stored in the following folder structure:
#
# $MICROSCOPY_PLATE_LIBRARY/YYYY/XX MMM
#
# Where
# - $MICROSCOPY_PLATE_LIBRARY is an environment variable pointing to the root folder
# - YYYY is the year
# - XX is the 2-digit month number (01, 02 ... 12)
# - MMM is the 3-letter month abbreviation (Jan, Feb, Mar etc.)
#
# So, for example, a plate SI-VI-005.png dated 12/03/26 in the plate library will be in this folder:
#
# $MICROSCOPY_PLATE_LIBRARY/2026/03 Mar
#
# The following are the month abbreviations used in the plate preview. They are hard-coded here rather
# than determined using, for example, strftime("%m %b") to avoid locale-related issues
MONTH_ABBR = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

ALLOWED_MEDIA_TYPES = [".png", ".mp4"]


# -----------------------------------------------------------------------------
# Plate Preview Helpers
# -----------------------------------------------------------------------------
def plate_media_folder_for_date(plate_date: date) -> Path | None:
    """Return the expected media folder for a plate date.

    Folder layout:
        $MICROSCOPY_PLATE_LIBRARY/YYYY/XX MMM
    Example:
        /root/2026/03 Mar
    """
    root = os.getenv("MICROSCOPY_PLATE_LIBRARY")
    if not root:
        return None

    month_folder = f"{plate_date.month:02d} {MONTH_ABBR[plate_date.month]}"
    return Path(root) / f"{plate_date.year:04d}" / month_folder


def plate_media_path(plate_date_value: Any, plate_file: str | None) -> dict[str, Path]:
    """Return the path to a plate media file given the date and plate file name."""
    if not plate_file:
        return None

    plate_date = parse_db_date(plate_date_value)
    folder = plate_media_folder_for_date(plate_date)
    if folder is None:
        return None

    return folder / plate_file


def render_plate_media_preview(plate: dict[str, Any]) -> None:
    """Show plate media preview on the edit page if files exist."""
    plate_file = plate.get("Plate")
    extension = Path(plate_file).suffix
    if not extension in ALLOWED_MEDIA_TYPES:
        st.caption(
            f"Unsupported media type for plate: `{plate_file}`"
        )

    media_path = plate_media_path(plate.get("Date"), plate_file)

    if not media_path:
        st.info("Unable to resolve media path for this plate")
        return

    if not media_path.exists():
        st.caption(
            f"No media file found for this plate in: `{media_path.parent}`"
        )
        return

    st.markdown("### Plate media")

    if extension.casefold() == ".png":
        st.image(str(media_path), caption=plate_file, use_container_width=True)
    else:
        st.video(str(media_path))
        st.caption(plate_file)