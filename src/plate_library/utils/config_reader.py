import json
import tomllib
from pathlib import Path

_CONFIG = {}


def get_application_version(project_folder: str) -> str:
    file_path = (Path(project_folder) / "pyproject.toml").resolve()
    with file_path.open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def load_config(project_folder: str):
    """Load the JSON configuration file """
    global _CONFIG
    file_path = (Path(project_folder) / "config.json").resolve()
    with open(file_path, "r") as file:
        _CONFIG = json.load(file)


def get_property(section: str, property: str) -> str:
    """Return a property from a config section """
    global _CONFIG
    return _CONFIG[section][property]


def get_location_property(property: str) -> str:
    """Return a location property """
    return get_property("location", property)
