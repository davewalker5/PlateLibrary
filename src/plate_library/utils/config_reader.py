import json
import tomllib
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version

_CONFIG = {}


def get_application_version(package_name: str, project_folder: str) -> str:
    """
    Return the application version.

    Priority:
    1. Installed package metadata (works in wheel/container installs)
    2. pyproject.toml fallback (works in local development)
    """

    try:
        return version(package_name)
    except PackageNotFoundError:
        pass

    # Fallback to using pyproject.toml
    file_path = Path(project_folder) / "pyproject.toml"
    if file_path.exists():
        with file_path.resolve().open("rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]

    return "0+unknown"


def load_config(config_file: str):
    """Load the JSON configuration file """
    global _CONFIG
    file_path = Path(config_file).resolve()
    with open(file_path, "r") as file:
        _CONFIG = json.load(file)


def get_property(section: str, property: str) -> str:
    """Return a property from a config section """
    global _CONFIG
    return _CONFIG[section][property]


def get_location_property(property: str) -> str:
    """Return a location property """
    return get_property("location", property)
