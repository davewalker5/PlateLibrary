
from datetime import date, datetime
from typing import Any


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


def form_key_base(entity: str, mode: str, record_id: int | None = None) -> str:
    """Return a stable widget-key prefix for one rendered form instance.

    Including the record id for edit forms forces Streamlit to treat each
    selected record as a fresh set of widgets, which prevents values from a
    previously edited record from lingering in optional fields.
    """
    suffix = "new" if record_id is None else str(record_id)
    return f"{entity}_{mode}_{suffix}"
